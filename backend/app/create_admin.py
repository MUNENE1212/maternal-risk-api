# create_admin.py
import os
import getpass
from datetime import datetime
from pymongo import MongoClient
from passlib.hash import bcrypt

def create_admin():
    # Get credentials from environment
    db_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "maternal_db")
    
    client = MongoClient(db_uri)
    db = client[db_name]
    users = db.users
    
    # Check if admin exists
    if users.count_documents({"role": "admin"}) > 0:
        print("⛔ Admin account already exists!")
        return

    # Collect admin details
    print("\n=== ADMIN ACCOUNT SETUP ===")
    phone = input("Phone number (start with 07/71 etc): ").strip()
    full_name = input("Full name: ").strip()
    
    # Normalize phone
    if phone.startswith("0"):
        phone = "+254" + phone[1:]
    elif not phone.startswith("+254"):
        phone = "+254" + phone
    
    # Validate phone
    if not re.match(r'^\+2547\d{8}$', phone):
        print("⛔ Invalid Kenyan phone format")
        return

    # Password validation
    while True:
        password = getpass.getpass("Password (min 8 chars, mix letters/numbers): ")
        if len(password) < 8:
            print("Password too short!")
        elif not (any(c.isalpha() for c in password) and any(c.isdigit() for c in password)):
            print("Must contain both letters and numbers!")
        else:
            break

    # Create admin document
    admin_data = {
        "phone_number": phone,
        "full_name": full_name,
        "password": bcrypt.hash(password),
        "role": "admin",
        "created_at": datetime.utcnow(),
        "is_active": True
    }

    # Insert into DB
    result = users.insert_one(admin_data)
    if result.inserted_id:
        print("\n✅ Admin created successfully!")
        print(f"Phone: {phone}")
    else:
        print("⛔ Failed to create admin account")

if __name__ == "__main__":
    create_admin()