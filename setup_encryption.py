from cryptography.fernet import Fernet

def generate_security_details():
    # 1. Generate a Key
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    
    print("--- SECURITY SETUP ---")
    print(f"1. Set this Environment Variable (Keep this secret!):\nAPP_ENCRYPTION_KEY={key.decode()}\n")

    # 2. Encrypt Passwords
    # Replace these with your actual passwords before running, or input them when prompted
    db_pass = input("Enter your Database Password: ")
    email_pass = input("Enter your Email Password: ")

    enc_db_pass = cipher_suite.encrypt(db_pass.encode()).decode()
    enc_email_pass = cipher_suite.encrypt(email_pass.encode()).decode()

    print("\n--- COPY INTO CONFIG.PY ---")
    print(f"ENC_DB_PASSWORD = '{enc_db_pass}'")
    print(f"ENC_EMAIL_PASSWORD = '{enc_email_pass}'")
    print("---------------------------")

if __name__ == "__main__":
    generate_security_details()