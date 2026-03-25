import secrets
import string
import json
import os
import hashlib

DB_FILE = "users.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_api_key() -> str:
    chars = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(chars) for _ in range(32))
    return f"agentlogs_{random_part}"

def create_user(email: str, password: str, company: str, api_key: str):
    users = load_db()
    users.append({
        "email": email,
        "password": hash_password(password),
        "company": company,
        "api_key": api_key
    })
    save_db(users)

def get_user_by_email(email: str):
    users = load_db()
    for user in users:
        if user["email"] == email:
            return user
    return None

def verify_api_key(api_key: str):
    users = load_db()
    for user in users:
        if user["api_key"] == api_key:
            return user
    return None

def verify_login(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None
    if user["password"] == hash_password(password):
        return user
    return None