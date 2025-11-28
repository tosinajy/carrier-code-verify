import os
import json
import pandas as pd
import io  # Added for CSV export
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response # Added Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER, MAIL_ADMIN_RECEIVER

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

# --- Authentication Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login' 

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database Error: {e}")
        return None

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return User(user['user_id'], user['username'], user['role'])
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Helper: Fetch Full Carrier Data ---
def get_full_carrier_data(carrier_id):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    
    query_core = """
        SELECT 
            c.carrier_id, c.legal_name, c.state_domicile, c.am_best_rating, c.update_dt, 
            c.other_carrier_names, c.company_type, c.sbs_company_number, c.sbs_legacy_number,
            n.cocode, n.company_licensed_in, n.company_name, n.full_company_name, n.short_name, n.business_type_code, n.insurance_types,
            p.payer_code, p.enrollment, p.attachment, p.transaction, p.wc_auto, p.available, p.non_par, p.other_payer_names
        FROM carriers c
        LEFT JOIN naic n ON c.naic_id = n.naic_id
        LEFT JOIN payers p ON c.payer_id = p.payer_id
        WHERE c.carrier_id = %s
    """
    cursor.execute(query_core, (carrier_id,))
    carrier = cursor.fetchone()
    
    if carrier:
        # Normalize BITs
        for key in ['enrollment', 'attachment', 'wc_auto', 'available', 'non_par']:
            val = carrier.get(key)
            if isinstance(val, bytes):
                carrier[key] = int.from_bytes(val, byteorder='big')
            elif val is None:
                carrier[key] = 0

        # Fetch Lists
        tables = ['phones', 'emails', 'websites', 'addresses', 'line_of_business']
        for t in tables:
            cursor.execute(f"SELECT * FROM {t} WHERE carrier_id = %s", (carrier_id,))
            carrier[t] = cursor.fetchall()
            
    conn.close()
    return carrier

# --- Public Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    search_term = request.args.get('q', '').strip()
    if not search_term or len(search_term) < 2:
        return jsonify([])

    conn = get_db_connection()
    if not conn: return jsonify([])
    
    cursor = conn.cursor(dictionary=True)
    wildcard = f"%{search_term}%"
    suggestions = []
    try:
        cursor.execute("SELECT legal_name as label, 'Carrier' as category FROM carriers WHERE legal_name LIKE %s LIMIT 5", (wildcard,))
        suggestions.extend(cursor.fetchall())
        cursor.execute("SELECT cocode as label, 'NAIC' as category FROM naic WHERE cocode LIKE %s LIMIT 3", (wildcard,))
        suggestions.extend(cursor.fetchall())
        cursor.execute("SELECT payer_code as label, 'Payer ID' as category FROM payers WHERE payer_code LIKE %s LIMIT 3", (wildcard,))
        suggestions.extend(cursor.fetchall())
    except Exception as e:
        print(f"Autocomplete Error: {e}")
    finally:
        conn.close()
    return jsonify(suggestions)

@app.route('/api/search', methods=['GET'])
def search_carriers():
    search_term = request.args.get('q', '').strip()
    if not search_term: return jsonify([])
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT DISTINCT c.legal_name, c.state_domicile, n.cocode as naic_code, p.payer_code as payer_id
        FROM carriers c
        LEFT JOIN naic n ON c.naic_id = n.naic_id
        LEFT JOIN payers p ON c.payer_id = p.payer_id
        WHERE c.legal_name LIKE %s OR n.cocode LIKE %s OR p.payer_code LIKE %s
        LIMIT 50
    """
    wildcard = f"%{search_term}%"
    cursor.execute(query, (wildcard, wildcard, wildcard))
    results = cursor.fetchall()
    conn.close()
    return jsonify(results)

@app.route('/directory')
def directory():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    per_page = 50
    offset = (page - 1) * per_page
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT c.legal_name, n.cocode as naic_code, p.payer_code, p.transaction, CAST(p.wc_auto AS UNSIGNED) as wc_auto,
            GROUP_CONCAT(DISTINCT ch.clearing_house SEPARATOR ', ') as clearing_houses
        FROM carriers c
        LEFT JOIN naic n ON c.naic_id = n.naic_id
        LEFT JOIN payers p ON c.payer_id = p.payer_id
        LEFT JOIN clearing_houses ch ON p.payer_id = ch.payer_id
    """
    count_query = "SELECT COUNT(DISTINCT c.carrier_id) as total FROM carriers c LEFT JOIN naic n ON c.naic_id = n.naic_id LEFT JOIN payers p ON c.payer_id = p.payer_id"
    params = []
    if search_query:
        where_clause = " WHERE c.legal_name LIKE %s OR n.cocode LIKE %s OR p.payer_code LIKE %s"
        query += where_clause
        count_query += where_clause
        wildcard = f"%{search_query}%"
        params.extend([wildcard, wildcard, wildcard])
    query += " GROUP BY c.carrier_id ORDER BY c.legal_name ASC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    cursor.execute(query, tuple(params))
    carriers = cursor.fetchall()
    cursor.execute(count_query, tuple(params[:3]) if search_query else ())
    total_res = cursor.fetchone()
    total = total_res['total'] if total_res else 0
    total_pages = (total + per_page - 1) // per_page
    conn.close()
    return render_template('directory.html', carriers=carriers, page=page, total_pages=total_pages, search=search_query)

@app.route('/carrier/<naic_code>')
def carrier_details(naic_code):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT carrier_id FROM naic WHERE cocode = %s", (naic_code,))
    res = cursor.fetchone()
    conn.close()
    
    if not res:
        flash("Carrier not found", "danger")
        return redirect(url_for('index'))
    
    carrier = get_full_carrier_data(res['carrier_id'])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM audit_log WHERE carrier_id = %s ORDER BY changed_at DESC LIMIT 10", (res['carrier_id'],))
    history = cursor.fetchall()
    conn.close()
    
    return render_template('carrier_details.html', carrier=carrier, history=history)

@app.route('/suggest-edit/<int:carrier_id>', methods=['GET', 'POST'])
def suggest_edit_form(carrier_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch current state for both GET and to capture 'old_value' on POST
    current_carrier_data = get_full_carrier_data(carrier_id)
    if not current_carrier_data:
        flash("Carrier not found.", "danger")
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'GET':
        # Fetch Lookups for Dropdowns
        lookups = {}
        cursor.execute("SELECT phone_type FROM phone_types ORDER BY phone_type")
        lookups['phone_types'] = cursor.fetchall()
        cursor.execute("SELECT state_id FROM us_states ORDER BY state_id")
        lookups['states'] = cursor.fetchall()
        cursor.execute("SELECT email_type FROM email_types ORDER BY email_type")
        lookups['email_types'] = cursor.fetchall()
        cursor.execute("SELECT website_type FROM website_types ORDER BY website_type")
        lookups['website_types'] = cursor.fetchall()
        cursor.execute("SELECT company_type FROM company_types ORDER BY company_type")
        lookups['company_types'] = cursor.fetchall()
        cursor.execute("SELECT address_type FROM address_types ORDER BY address_type")
        lookups['address_types'] = cursor.fetchall()
        
        conn.close()
        return render_template('suggest_edit.html', carrier=current_carrier_data, lookups=lookups)
    
    # POST Handling
    # Capture Old State as JSON
    
    # Helper to serialize old data
    def serialize_for_json(obj):
        if isinstance(obj, (pd.Timestamp, pd.Timedelta)):
            return str(obj)
        if isinstance(obj, bytes):
            return 1 if obj == b'\x01' else 0 # simplify for comparison
        return obj

    # We need a clean dictionary of the old data to compare against
    # Simple approach: Use the keys we care about from get_full_carrier_data
    # Note: `current_carrier_data` has date objects that need string conversion for JSON
    old_json_ready = {}
    for k, v in current_carrier_data.items():
        if k in ['phones', 'emails', 'websites', 'addresses', 'line_of_business']:
            # Handle lists
            old_list = []
            for item in v:
                # Flatten dict items
                flat_item = {ik: serialize_for_json(iv) for ik, iv in item.items()}
                old_list.append(flat_item)
            old_json_ready[k] = old_list
        else:
            old_json_ready[k] = serialize_for_json(v)
    
    old_value_json = json.dumps(old_json_ready, default=str)

    # Clean Data Construction (New Value)
    clean_data = {
        'submitter_name': request.form.get('submitter_name'),
        'submitter_email': request.form.get('submitter_email'),
        'legal_name': request.form.get('legal_name'),
        'am_best_rating': request.form.get('am_best_rating'),
        'state_domicile': request.form.get('state_domicile'),
        
        # NAIC Section
        'cocode': request.form.get('cocode'),
        'company_name': request.form.get('company_name'),
        'short_name': request.form.get('short_name'),
        'company_licensed_in': request.form.get('company_licensed_in'),
        'insurance_types': request.form.get('insurance_types'),
        
        # Payer Section
        'payer_code': request.form.get('payer_code'),
        'enrollment': 1 if request.form.get('enrollment') else 0,
        'attachment': 1 if request.form.get('attachment') else 0,
        'wc_auto': 1 if request.form.get('wc_auto') else 0,
        'available': 1 if request.form.get('available') else 0,
        'non_par': 1 if request.form.get('non_par') else 0,
        'transaction': request.form.get('transaction'),
        'other_payer_names': request.form.get('other_payer_names'),

        'company_type': request.form.get('company_type'),
        'sbs_company_number': request.form.get('sbs_company_number'),
        'sbs_legacy_number': request.form.get('sbs_legacy_number'),
        'other_carrier_names': request.form.get('other_carrier_names'),
        
        'phones': [],
        'emails': [],
        'websites': [],
        'addresses': [],
        'lobs': []
    }
    
    # Process Lists
    p_types = request.form.getlist('phone_type[]')
    p_nums = request.form.getlist('phone_number[]')
    for i in range(len(p_nums)):
        if p_nums[i]: clean_data['phones'].append({'phone_type': p_types[i], 'phone_number': p_nums[i]})

    e_types = request.form.getlist('email_type[]')
    e_addrs = request.form.getlist('email_address[]')
    for i in range(len(e_addrs)):
        if e_addrs[i]: clean_data['emails'].append({'email_type': e_types[i], 'email_address': e_addrs[i]})

    w_types = request.form.getlist('website_type[]')
    w_urls = request.form.getlist('website_url[]')
    for i in range(len(w_urls)):
        if w_urls[i]: clean_data['websites'].append({'website_type': w_types[i], 'website_url': w_urls[i]})

    lob_vals = request.form.getlist('lob[]')
    for l in lob_vals:
        if l: clean_data['lobs'].append(l)
        
    a_types = request.form.getlist('address_type[]')
    a_lines = request.form.getlist('address_line1[]')
    a_cities = request.form.getlist('city[]')
    a_states = request.form.getlist('state[]')
    a_zips = request.form.getlist('zip_code[]')
    for i in range(len(a_lines)):
        if a_lines[i]:
            clean_data['addresses'].append({
                'address_type': a_types[i], 
                'address_line1': a_lines[i],
                'city': a_cities[i],
                'state': a_states[i],
                'zip_code': a_zips[i]
            })

    json_payload = json.dumps(clean_data)
    
    cursor.execute("""
        INSERT INTO carrier_edits 
        (carrier_id, submitter_name, submitter_email, field_name, old_value, new_value, status)
        VALUES (%s, %s, %s, 'FULL_RECORD', %s, %s, 'pending')
    """, (carrier_id, clean_data['submitter_name'], clean_data['submitter_email'], old_value_json, json_payload))
    conn.commit()
    conn.close()
    
    flash(f"Success! Your edits for {clean_data['legal_name']} have been submitted for review.", "success")
    return redirect(url_for('carrier_details', naic_code=request.form.get('cocode') or current_carrier_data['cocode']))

# --- Admin Routes ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            login_user(User(user['user_id'], user['username'], user['role']))
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Tiles Data
    cursor.execute("SELECT COUNT(*) as count FROM carriers")
    total_carriers = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM naic")
    total_naic = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM payers")
    total_payers = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM carrier_edits WHERE status='pending'")
    pending_count = cursor.fetchone()['count']

    # 2. Chart: Daily Contributions (Last 30 Days)
    cursor.execute("""
        SELECT DATE(submitted_at) as log_date, COUNT(*) as cnt 
        FROM carrier_edits 
        WHERE submitted_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY log_date 
        ORDER BY log_date
    """)
    contributions_raw = cursor.fetchall()
    
    # Process into lists for Chart.js
    contributions_labels = [x['log_date'].strftime('%Y-%m-%d') for x in contributions_raw]
    contributions_data = [x['cnt'] for x in contributions_raw]

    # 3. Data Quality Report (Datasets with carrier_id)
    dq_tables = ['naic', 'payers', 'websites', 'phones', 'emails', 'addresses', 'line_of_business']
    dq_report = []

    if total_carriers > 0:
        for tbl in dq_tables:
            # Check how many unique carriers have at least one record in this table
            cursor.execute(f"SELECT COUNT(DISTINCT carrier_id) as cnt FROM {tbl}")
            cnt = cursor.fetchone()['cnt']
            
            dq_report.append({
                'dataset': tbl.replace('_', ' ').title(),
                'count': cnt,
                'total': total_carriers,
                'percentage': round((cnt / total_carriers) * 100, 1)
            })

    conn.close()
    return render_template(
        'admin/dashboard.html', 
        total_carriers=total_carriers,
        total_naic=total_naic,
        total_payers=total_payers,
        pending_count=pending_count,
        chart_labels=contributions_labels,
        chart_data=contributions_data,
        dq_report=dq_report
    )

@app.route('/admin/queue')
@login_required
@admin_required
def admin_queue():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Edits
    cursor.execute("""
        SELECT e.*, c.legal_name, n.cocode as naic_code
        FROM carrier_edits e
        JOIN carriers c ON e.carrier_id = c.carrier_id
        LEFT JOIN naic n ON c.naic_id = n.naic_id
        WHERE e.status = 'pending'
        ORDER BY e.submitted_at DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    edits = cursor.fetchall()
    
    # Count
    cursor.execute("SELECT COUNT(*) as total FROM carrier_edits WHERE status = 'pending'")
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page
    
    conn.close()
    return render_template('admin/queue.html', edits=edits, page=page, total_pages=total_pages)
@app.route('/admin/leads')
@login_required
@admin_required
def admin_leads():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # MODIFIED QUERY: Added MAX(submitter_name) to satisfy ONLY_FULL_GROUP_BY
    base_query = """
        SELECT MAX(submitter_name) as submitter_name, submitter_email, COUNT(*) as contribution_count, MAX(submitted_at) as last_active 
        FROM carrier_edits 
    """
    where_clause = ""
    params = []
    
    if search:
        where_clause = " WHERE submitter_name LIKE %s OR submitter_email LIKE %s"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard])
        
    group_order = " GROUP BY submitter_email ORDER BY last_active DESC LIMIT %s OFFSET %s"

    # Execute Main Query
    cursor.execute(base_query + where_clause + group_order, tuple(params + [per_page, offset]))
    leads = cursor.fetchall()
    
    # Execute Count Query
    count_sql = "SELECT COUNT(DISTINCT submitter_email) as total FROM carrier_edits" + where_clause
    cursor.execute(count_sql, tuple(params) if search else ())
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page
    
    conn.close()
    return render_template('admin/leads.html', leads=leads, page=page, total_pages=total_pages, search=search)

@app.route('/admin/leads/export')
@login_required
@admin_required
def export_leads():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
# MODIFIED QUERY: Added MAX(submitter_name) to satisfy ONLY_FULL_GROUP_BY
    cursor.execute("""
        SELECT MAX(submitter_name) as Name, submitter_email as Email, COUNT(*) as Contributions, MAX(submitted_at) as Last_Active 
        FROM carrier_edits 
        GROUP BY submitter_email 
        ORDER BY Last_Active DESC
    """)
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        flash("No leads to export.", "warning")
        return redirect(url_for('admin_leads'))
        
    # Use Pandas to generate CSV
    df = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=leads_export.csv"}
    )

# --- NEW: Line of Business (LOB) Routes ---

@app.route('/admin/lobs')
@login_required
@admin_required
def admin_lobs():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    per_page = 20
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Fetch LOBs
    base_query = """
        SELECT l.lob_id, l.carrier_id, l.lob, l.update_dt, c.legal_name 
        FROM line_of_business l
        JOIN carriers c ON l.carrier_id = c.carrier_id
    """
    count_query = "SELECT COUNT(*) as total FROM line_of_business l JOIN carriers c ON l.carrier_id = c.carrier_id"
    
    params = []
    if search:
        where_clause = " WHERE l.lob LIKE %s OR c.legal_name LIKE %s OR CAST(l.carrier_id AS CHAR) LIKE %s"
        base_query += where_clause
        count_query += where_clause
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])
        
    base_query += " ORDER BY c.legal_name ASC, l.lob ASC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(base_query, tuple(params))
    lobs = cursor.fetchall()

    cursor.execute(count_query, tuple(params[:3]) if search else ())
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page

    # 2. Fetch All Carriers for Dropdown (Optimized: Only ID and Name)
    cursor.execute("SELECT carrier_id, legal_name FROM carriers ORDER BY legal_name ASC")
    all_carriers = cursor.fetchall()

    conn.close()
    return render_template('admin/lob.html', lobs=lobs, page=page, total_pages=total_pages, search=search, all_carriers=all_carriers)

@app.route('/admin/lobs/add', methods=['POST'])
@login_required
@admin_required
def add_lob():
    carrier_id = request.form.get('carrier_id')
    lob = request.form.get('lob')
    
    if not carrier_id or not lob:
        flash("Carrier and LOB are required.", "danger")
        return redirect(url_for('admin_lobs'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if carrier exists first
        cursor.execute("SELECT carrier_id FROM carriers WHERE carrier_id = %s", (carrier_id,))
        if not cursor.fetchone():
            flash(f"Carrier ID {carrier_id} does not exist.", "danger")
        else:
            sql = "INSERT INTO line_of_business (carrier_id, lob, update_by, update_dt) VALUES (%s, %s, %s, CURDATE())"
            cursor.execute(sql, (carrier_id, lob, current_user.username))
            conn.commit()
            flash("Line of Business added successfully.", "success")
    except Exception as e:
        flash(f"Error adding LOB: {e}", "danger")
    finally:
        conn.close()
    
    return redirect(url_for('admin_lobs'))

@app.route('/admin/lobs/edit', methods=['POST'])
@login_required
@admin_required
def edit_lob():
    # Note: ID is passed in form body for single modal design
    lob_id = request.form.get('lob_id')
    carrier_id = request.form.get('carrier_id')
    lob = request.form.get('lob')
    
    if not lob_id:
         flash("Error: Missing LOB ID.", "danger")
         return redirect(url_for('admin_lobs'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT carrier_id FROM carriers WHERE carrier_id = %s", (carrier_id,))
        if not cursor.fetchone():
             flash(f"Carrier ID {carrier_id} does not exist.", "danger")
        else:
            sql = "UPDATE line_of_business SET carrier_id=%s, lob=%s, update_by=%s, update_dt=CURDATE() WHERE lob_id=%s"
            cursor.execute(sql, (carrier_id, lob, current_user.username, lob_id))
            conn.commit()
            flash("Line of Business updated.", "success")
    except Exception as e:
        flash(f"Error updating LOB: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for('admin_lobs'))

@app.route('/admin/lobs/delete/<int:lob_id>')
@login_required
@admin_required
def delete_lob(lob_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM line_of_business WHERE lob_id = %s", (lob_id,))
        conn.commit()
        flash("Line of Business deleted.", "info")
    except Exception as e:
        flash(f"Error deleting LOB: {e}", "danger")
    finally:
        conn.close()
    
    return redirect(url_for('admin_lobs'))

@app.route('/admin/review/<int:edit_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def review_edit(edit_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM carrier_edits WHERE edit_id = %s", (edit_id,))
    edit_request = cursor.fetchone()
    
    if not edit_request:
        conn.close()
        return redirect(url_for('admin_queue'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'reject':
            cursor.execute("UPDATE carrier_edits SET status='rejected', reviewed_by=%s, reviewed_at=NOW() WHERE edit_id=%s", 
                           (current_user.id, edit_id))
            conn.commit()
            flash("Edit rejected.", "info")
            
        elif action == 'approve':
            final_json = request.form.get('final_json')
            data = json.loads(final_json)
            cid = edit_request['carrier_id']
            
            try:
                # Update Main
                cursor.execute("""
                    UPDATE carriers SET 
                    legal_name=%s, company_type=%s, sbs_company_number=%s, sbs_legacy_number=%s, other_carrier_names=%s, 
                    am_best_rating=%s, state_domicile=%s, update_dt=CURDATE()
                    WHERE carrier_id=%s
                """, (data.get('legal_name'), data.get('company_type'), data.get('sbs_company_number'), 
                      data.get('sbs_legacy_number'), data.get('other_carrier_names'), data.get('am_best_rating'), 
                      data.get('state_domicile'), cid))
                
                # Update Payer
                cursor.execute("SELECT payer_id FROM carriers WHERE carrier_id=%s", (cid,))
                pid_res = cursor.fetchone()
                if pid_res:
                    pid = pid_res['payer_id']
                    cursor.execute("""
                        UPDATE payers SET payer_code=%s, enrollment=%s, attachment=%s, wc_auto=%s, available=%s, non_par=%s, 
                        transaction=%s, other_payer_names=%s WHERE payer_id=%s
                    """, (data.get('payer_code'), data.get('enrollment'), data.get('attachment'), data.get('wc_auto'),
                          data.get('available'), data.get('non_par'), data.get('transaction'), data.get('other_payer_names'), pid))
                
                # Update NAIC
                cursor.execute("SELECT naic_id FROM carriers WHERE carrier_id=%s", (cid,))
                nid_res = cursor.fetchone()
                if nid_res:
                    nid = nid_res['naic_id']
                    cursor.execute("""
                        UPDATE naic SET cocode=%s, company_name=%s, short_name=%s, company_licensed_in=%s, insurance_types=%s 
                        WHERE naic_id=%s
                    """, (data.get('cocode'), data.get('company_name'), data.get('short_name'), 
                          data.get('company_licensed_in'), data.get('insurance_types'), nid))
                
                # Full Replace: Phones
                cursor.execute("DELETE FROM phones WHERE carrier_id=%s", (cid,))
                for p in data.get('phones', []):
                    cursor.execute("INSERT INTO phones (carrier_id, phone_type, phone_number, update_dt) VALUES (%s, %s, %s, CURDATE())",
                                   (cid, p['phone_type'], p['phone_number']))
                
                # Full Replace: Emails
                cursor.execute("DELETE FROM emails WHERE carrier_id=%s", (cid,))
                for e in data.get('emails', []):
                    cursor.execute("INSERT INTO emails (carrier_id, email_type, email_address, update_dt) VALUES (%s, %s, %s, CURDATE())",
                                   (cid, e['email_type'], e['email_address']))
                                   
                # Full Replace: Websites
                cursor.execute("DELETE FROM websites WHERE carrier_id=%s", (cid,))
                for w in data.get('websites', []):
                    cursor.execute("INSERT INTO websites (carrier_id, website_type, website_url, update_dt) VALUES (%s, %s, %s, CURDATE())",
                                   (cid, w['website_type'], w['website_url']))
                
                # Full Replace: Addresses
                cursor.execute("DELETE FROM addresses WHERE carrier_id=%s", (cid,))
                for a in data.get('addresses', []):
                    cursor.execute("""INSERT INTO addresses (carrier_id, address_type, address_line1, city, state, zip_code, update_dt) 
                                      VALUES (%s, %s, %s, %s, %s, %s, CURDATE())""",
                                   (cid, a['address_type'], a['address_line1'], a['city'], a['state'], a['zip_code']))
                
                # Full Replace: LOBs
                cursor.execute("DELETE FROM line_of_business WHERE carrier_id=%s", (cid,))
                for l in data.get('lobs', []):
                    cursor.execute("INSERT INTO line_of_business (carrier_id, lob, update_dt) VALUES (%s, %s, CURDATE())",
                                   (cid, l))

                # Log
                cursor.execute("INSERT INTO audit_log (carrier_id, action_type, description, changed_by) VALUES (%s, 'full_update', %s, %s)",
                               (cid, "Full Record Update via Admin Panel", f"Submitter: {edit_request['submitter_name']}"))
                
                cursor.execute("UPDATE carrier_edits SET status='approved', reviewed_by=%s, reviewed_at=NOW() WHERE edit_id=%s", 
                               (current_user.id, edit_id))
                
                conn.commit()
                flash("Changes approved and database updated successfully.", "success")
                
            except Exception as e:
                conn.rollback()
                flash(f"Error applying changes: {e}", "danger")
                print(e)
        
        conn.close()
        return redirect(url_for('admin_queue'))

    try:
        proposed_data = json.loads(edit_request['new_value'])
        original_data = json.loads(edit_request['old_value']) if edit_request['old_value'] else {}
    except:
        proposed_data = {}
        original_data = {}
        
    conn.close()
    return render_template('admin/edit_review.html', edit=edit_request, data=proposed_data, original=original_data)

@app.route('/admin/bulk-upload', methods=['POST'])
@login_required
@admin_required
def bulk_upload():
    flash("Bulk upload requires update for new schema.", "warning")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

@app.route('/admin/config')
@login_required
@admin_required
def admin_config():
    return render_template('admin/email_config.html', config=app.config)

if __name__ == '__main__':
    app.run(debug=True, port=5000)