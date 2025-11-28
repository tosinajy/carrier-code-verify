import os
import json
import pandas as pd
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER, MAIL_ADMIN_RECEIVER

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

# --- Config Setup ---
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER
app.config['MAIL_ADMIN_RECEIVER'] = MAIL_ADMIN_RECEIVER
app.config['SHOW_ADS'] = True  # Default Ad Setting

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

# --- Context Processor for Global Variables ---
@app.context_processor
def inject_globals():
    return dict(show_ads=app.config.get('SHOW_ADS', False))

# --- Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# --- Public Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/carrier/<int:carrier_id>')
def carrier_details(carrier_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch Carrier details joining Payer and NAIC tables
    # Also fetching `carrier_id` specifically for audit logging relation
    query = """
        SELECT 
            c.carrier_id,
            p.payer_name, 
            p.payer_code, 
            p.clearing_house,
            p.mapping_status,
            n.cocode, 
            n.company_name
        FROM carriers c
        JOIN payers p ON c.payer_id = p.payer_id
        JOIN naic n ON c.naic_id = n.naic_id
        WHERE c.carrier_id = %s
    """
    cursor.execute(query, (carrier_id,))
    carrier = cursor.fetchone()
    
    if not carrier:
        conn.close()
        flash("Carrier not found", "danger")
        return redirect(url_for('index'))
    
    # Fetch Audit Logs
    cursor.execute("SELECT * FROM audit_log WHERE carrier_id = %s ORDER BY changed_at DESC LIMIT 10", (carrier_id,))
    audit_logs = cursor.fetchall()
    
    conn.close()
    
    return render_template('carrier_details.html', carrier=carrier, audit_logs=audit_logs)

@app.route('/directory')
def directory():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    per_page = 50
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            c.carrier_id,
            p.payer_code, 
            p.payer_name, 
            n.cocode,
            GROUP_CONCAT(DISTINCT p.clearing_house SEPARATOR ', ') as clearing_houses
        FROM carriers c
        JOIN payers p ON c.payer_id = p.payer_id
        JOIN naic n ON c.naic_id = n.naic_id
        WHERE 1=1
    """
    params = []
    
    if search:
        query += " AND (p.payer_name LIKE %s OR p.payer_code LIKE %s OR n.cocode LIKE %s)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])
    
    query += " GROUP BY c.carrier_id, p.payer_code, p.payer_name, n.cocode"
    
    count_query = f"SELECT COUNT(*) as total FROM ({query}) as sub"
    cursor.execute(count_query, tuple(params))
    total_res = cursor.fetchone()
    total = total_res['total'] if total_res else 0
    total_pages = (total + per_page - 1) // per_page
    
    query += " ORDER BY p.payer_name ASC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    
    cursor.execute(query, tuple(params))
    carriers = cursor.fetchall()
    conn.close()
    
    return render_template('directory.html', carriers=carriers, page=page, total_pages=total_pages, search=search)

@app.route('/api/search', methods=['GET'])
def search_api():
    search_term = request.args.get('q', '').strip()
    if not search_term: return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    wildcard = f"%{search_term}%"
    
    query = """
        SELECT 
            c.carrier_id, 
            p.payer_name, 
            p.payer_code, 
            n.cocode, 
            n.company_name
        FROM carriers c
        JOIN payers p ON c.payer_id = p.payer_id
        JOIN naic n ON c.naic_id = n.naic_id
        WHERE 
            p.payer_code LIKE %s OR 
            p.payer_name LIKE %s OR 
            n.cocode LIKE %s
        LIMIT 50
    """
    cursor.execute(query, (wildcard, wildcard, wildcard))
    results = cursor.fetchall()
    conn.close()
    return jsonify(results)

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
        cursor.execute("SELECT payer_name as label, 'Payer' as category FROM payers WHERE payer_name LIKE %s LIMIT 3", (wildcard,))
        suggestions.extend(cursor.fetchall())
        cursor.execute("SELECT payer_code as label, 'Payer ID' as category FROM payers WHERE payer_code LIKE %s LIMIT 3", (wildcard,))
        suggestions.extend(cursor.fetchall())
        cursor.execute("SELECT cocode as label, 'NAIC' as category FROM naic WHERE cocode LIKE %s LIMIT 3", (wildcard,))
        suggestions.extend(cursor.fetchall())
    except Exception as e:
        print(f"Autocomplete Error: {e}")
    finally:
        conn.close()
    return jsonify(suggestions)

@app.route('/api/naic-lookup', methods=['GET'])
@login_required
def naic_lookup():
    q = request.args.get('q', '').strip()
    if not q: return jsonify({'results': []})
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    wildcard = f"%{q}%"
    
    query = """
        SELECT naic_id as value, CONCAT(company_name, ' (', cocode, ')') as name, cocode as text 
        FROM naic 
        WHERE company_name LIKE %s OR cocode LIKE %s 
        LIMIT 20
    """
    cursor.execute(query, (wildcard, wildcard))
    rows = cursor.fetchall()
    conn.close()
    
    results = [{'name': r['name'], 'value': r['value'], 'text': r['text']} for r in rows]
    return jsonify({'success': True, 'results': results})

# --- Admin Routes ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    from werkzeug.security import check_password_hash
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
    cursor.execute("SELECT COUNT(*) as c FROM payers")
    total_payers = cursor.fetchone()['c'] or 0
    cursor.execute("SELECT COUNT(*) as c FROM naic")
    total_naic = cursor.fetchone()['c'] or 0
    cursor.execute("SELECT COUNT(*) as c FROM payers WHERE mapping_status='pending'")
    pending_approvals = cursor.fetchone()['c'] or 0
    cursor.execute("SELECT COUNT(*) as c FROM payers WHERE naic_id IS NULL AND mapping_status != 'approved'")
    unassigned_payers = cursor.fetchone()['c'] or 0
    conn.close()
    return render_template('admin/dashboard.html', 
                           total_payers=total_payers, 
                           total_naic=total_naic, 
                           pending_approvals=pending_approvals,
                           unassigned_payers=unassigned_payers)

@app.route('/admin/payers', methods=['GET'])
@login_required
@admin_required
def admin_payers():
    filter_status = request.args.get('status', 'unassigned')
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT p.*, n.cocode, n.company_name as naic_company FROM payers p LEFT JOIN naic n ON p.naic_id = n.naic_id WHERE 1=1"
    params = []
    if filter_status == 'assigned': query += " AND p.naic_id IS NOT NULL"
    elif filter_status == 'unassigned': query += " AND p.naic_id IS NULL"
    if search:
        query += " AND (p.payer_name LIKE %s OR p.payer_code LIKE %s OR p.clearing_house LIKE %s)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])
    count_query = f"SELECT COUNT(*) as total FROM ({query}) as sub"
    cursor.execute(count_query, tuple(params))
    total_res = cursor.fetchone()
    total = total_res['total'] if total_res else 0
    query += " ORDER BY p.payer_name ASC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    cursor.execute(query, tuple(params))
    payers = cursor.fetchall()
    conn.close()
    return render_template('admin/payers.html', payers=payers, filter_status=filter_status, search=search, page=page, total_pages=(total + per_page - 1) // per_page)

@app.route('/admin/payers/import', methods=['POST'])
@login_required
@admin_required
def import_payers():
    clearing_house = request.form.get('clearing_house')
    file = request.files.get('file')
    if not clearing_house or not file:
        flash("Clearing House and File are required.", "danger")
        return redirect(url_for('admin_payers'))
    try:
        df = pd.read_excel(file)
        inserted, updated, skipped = 0, 0, 0
        skip_reasons = []
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        for index, row in df.iterrows():
            row_lower = {str(k).lower().strip(): v for k, v in row.items()}
            payer_id = row_lower.get('payer id') or row_lower.get('payer_id') or row_lower.get('payerid')
            payer_name = row_lower.get('payer name') or row_lower.get('payer_name') or row_lower.get('payername')
            if pd.isna(payer_id) or pd.isna(payer_name):
                skipped += 1
                skip_reasons.append(f"Row {index+2}")
                continue
            payer_id = str(payer_id).strip()
            payer_name = str(payer_name).strip()
            cursor.execute("SELECT payer_id FROM payers WHERE payer_code = %s AND clearing_house = %s", (payer_id, clearing_house))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("UPDATE payers SET payer_name=%s WHERE payer_id=%s", (payer_name, existing['payer_id']))
                updated += 1
            else:
                cursor.execute("INSERT INTO payers (payer_code, payer_name, clearing_house, mapping_status) VALUES (%s, %s, %s, 'unassigned')", (payer_id, payer_name, clearing_house))
                inserted += 1
        conn.commit()
        conn.close()
        flash(f"Upload Results - Inserted: {inserted}, Updated: {updated}, Skipped: {skipped}", "info")
    except Exception as e:
        flash(f"Import Error: {str(e)}", "danger")
    return redirect(url_for('admin_payers'))

@app.route('/admin/payers/single', methods=['POST'])
@login_required
@admin_required
def add_single_payer():
    payer_name = request.form.get('payer_name')
    payer_code = request.form.get('payer_code')
    clearing_house = request.form.get('clearing_house')
    if not payer_name or not payer_code:
        flash("Payer Name and ID are required.", "danger")
        return redirect(url_for('admin_payers'))
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO payers (payer_name, payer_code, clearing_house, mapping_status) VALUES (%s, %s, %s, 'unassigned')", (payer_name, payer_code, clearing_house))
        conn.commit()
        flash("Payer added successfully.", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_payers'))

@app.route('/admin/assign_naic', methods=['POST'])
@login_required
@admin_required
def assign_naic():
    payer_id = request.form.get('payer_id')
    naic_id = request.form.get('naic_id')
    no_naic = request.form.get('no_naic')
    if not payer_id:
        flash("Invalid Payer ID.", "danger")
        return redirect(url_for('admin_payers'))
    status = 'pending'
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if no_naic:
             cursor.execute("UPDATE payers SET naic_id=NULL, mapping_status=%s WHERE payer_id=%s", (status, payer_id))
        elif naic_id:
             cursor.execute("UPDATE payers SET naic_id=%s, mapping_status=%s WHERE payer_id=%s", (naic_id, status, payer_id))
        else:
            flash("Selection required.", "warning")
            return redirect(url_for('admin_payers'))
        conn.commit()
        flash("Submitted for approval.", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_payers'))

@app.route('/admin/naic', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_naic():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash("File required.", "danger")
            return redirect(url_for('admin_naic'))
        try:
            df = pd.read_excel(file)
            inserted, updated, skipped = 0, 0, 0
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            for _, row in df.iterrows():
                row_lower = {str(k).lower().strip(): v for k, v in row.items()}
                cocode = row_lower.get('cocode') or row_lower.get('naic code')
                name = row_lower.get('company name') or row_lower.get('company_name')
                if pd.isna(cocode) or pd.isna(name):
                    skipped += 1
                    continue
                cocode = str(cocode).strip()
                name = str(name).strip()
                cursor.execute("SELECT naic_id FROM naic WHERE cocode = %s", (cocode,))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute("UPDATE naic SET company_name=%s WHERE naic_id=%s", (name, existing['naic_id']))
                    updated += 1
                else:
                    cursor.execute("INSERT INTO naic (cocode, company_name) VALUES (%s, %s)", (cocode, name))
                    inserted += 1
            conn.commit()
            conn.close()
            flash(f"NAIC Import - Inserted: {inserted}, Updated: {updated}, Skipped: {skipped}", "info")
        except Exception as e:
             flash(f"Error: {e}", "danger")
    return render_template('admin/naic.html')

@app.route('/admin/naic/single', methods=['POST'])
@login_required
@admin_required
def add_single_naic():
    cocode = request.form.get('cocode')
    company_name = request.form.get('company_name')
    if not cocode or not company_name:
         flash("Fields required.", "danger")
         return redirect(url_for('admin_naic'))
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO naic (cocode, company_name) VALUES (%s, %s)", (cocode, company_name))
        conn.commit()
        flash("Added.", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_naic'))

@app.route('/admin/approvals', methods=['GET'])
@login_required
@admin_required
def admin_approvals():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT p.payer_id, p.payer_name, p.payer_code, p.clearing_house, n.cocode, n.company_name, p.mapping_status FROM payers p LEFT JOIN naic n ON p.naic_id = n.naic_id WHERE p.mapping_status = 'pending'"
    cursor.execute(query)
    pendings = cursor.fetchall()
    conn.close()
    return render_template('admin/approvals.html', pendings=pendings)

@app.route('/admin/approvals/process', methods=['POST'])
@login_required
@admin_required
def process_approvals():
    action = request.form.get('action')
    payer_ids = request.form.getlist('payer_ids')
    if not payer_ids:
        flash("No items selected.", "warning")
        return redirect(url_for('admin_approvals'))
    new_status = 'approved' if action == 'approve' else 'rejected'
    conn = get_db_connection()
    cursor = conn.cursor()
    format_strings = ','.join(['%s'] * len(payer_ids))
    cursor.execute(f"UPDATE payers SET mapping_status=%s WHERE payer_id IN ({format_strings})", tuple([new_status] + payer_ids))
    conn.commit()
    conn.close()
    flash(f"Items {new_status}.", "success")
    return redirect(url_for('admin_approvals'))

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

@app.route('/admin/config', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_config():
    if request.method == 'POST':
        # In a real app, save to DB. For now, updating app.config
        app.config['SHOW_ADS'] = 'show_ads' in request.form
        flash("Configuration updated.", "success")
    return render_template('admin/email_config.html', config=app.config)

if __name__ == '__main__':
    app.run(debug=True, port=5000)