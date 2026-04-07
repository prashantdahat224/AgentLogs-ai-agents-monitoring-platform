import secrets
import string
import hashlib
import os
from datetime import timedelta
from dotenv import load_dotenv
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import DocumentNotFoundException

load_dotenv()

def get_collection():
    auth = PasswordAuthenticator(
        os.getenv("COUCHBASE_USER"),
        os.getenv("COUCHBASE_PASSWORD")
    )
    cluster = Cluster(os.getenv("COUCHBASE_URL"), ClusterOptions(auth))
    cluster.wait_until_ready(timedelta(seconds=10))
    bucket = cluster.bucket(os.getenv("COUCHBASE_BUCKET"))
    return bucket.default_collection()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_api_key() -> str:
    chars = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(chars) for _ in range(32))
    return f"agentlogs_{random_part}"

def create_user(email: str, password: str, company: str, api_key: str):
    collection = get_collection()
    # Store user by email
    collection.upsert(f"user::email::{email}", {
        "email": email,
        "password": hash_password(password),
        "company": company,
        "api_key": api_key
    })
    # Store reverse lookup by api_key
    collection.upsert(f"user::apikey::{api_key}", {
        "email": email,
        "password": hash_password(password),
        "company": company,
        "api_key": api_key
    })

def get_user_by_email(email: str):
    try:
        collection = get_collection()
        result = collection.get(f"user::email::{email}")
        return result.content_as[dict]
    except DocumentNotFoundException:
        return None
    except Exception as e:
        print(f"Error get_user_by_email: {e}")
        return None

def verify_api_key(api_key: str):
    try:
        collection = get_collection()
        result = collection.get(f"user::apikey::{api_key}")
        return result.content_as[dict]
    except DocumentNotFoundException:
        return None
    except Exception as e:
        print(f"Error verify_api_key: {e}")
        return None

def verify_login(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None
    if user["password"] == hash_password(password):
        return user
    return None
