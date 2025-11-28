import mysql.connector
from werkzeug.security import generate_password_hash
from config import DB_CONFIG

def reset_admin_password():
    print("--- Reset Admin Password ---")
    username = input("Enter Username (default: admin): ").strip() or 'admin'
    password = input("Enter New Password: ").strip()
    
    if not password:
        print("Error: Password cannot be empty.")
        return

    # 1. Generate the secure hash
    hashed_pw = generate_password_hash(password)
    
    try:
        # 2. Connect to Database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 3. Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        exists = cursor.fetchone()

        if exists:
            # Update existing user
            sql = "UPDATE users SET password_hash = %s WHERE username = %s"
            cursor.execute(sql, (hashed_pw, username))
            print(f"Success: Password for '{username}' has been updated.")
        else:
            # Create new user
            sql = "INSERT INTO users (username, password_hash, role, email) VALUES (%s, %s, 'admin', 'admin@example.com')"
            cursor.execute(sql, (username, hashed_pw))
            print(f"Success: New admin user '{username}' created.")

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_admin_password()