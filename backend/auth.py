import secrets
import string
import hashlib
import os
from datetime import timedelta
from dotenv import load_dotenv
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.auth import PasswordAuthenticator

load_dotenv()

def get_cluster():
    auth = PasswordAuthenticator(
        os.getenv("COUCHBASE_USER"),     # your Couchbase username
        os.getenv("COUCHBASE_PASSWORD")  # your Couchbase password
    )
    cluster = Cluster(
        os.getenv("COUCHBASE_URL"),      # couchbases://cb.xxxxxx.cloud.couchbase.com
        ClusterOptions(auth)
    )
    cluster.wait_until_ready(timedelta(seconds=10))
    return cluster

def get_collection():
    cluster = get_cluster()
    bucket = cluster.bucket(os.getenv("COUCHBASE_BUCKET"))  # agentlogs
    return bucket.default_collection()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_api_key() -> str:
    chars = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(chars) for _ in range(32))
    return f"agentlogs_{random_part}"

def create_user(email: str, password: str, company: str, api_key: str):
    collection = get_collection()
    collection.upsert(f"user::{email}", {
        "type": "user",
        "email": email,
        "password": hash_password(password),
        "company": company,
        "api_key": api_key
    })

def get_user_by_email(email: str):
    try:
        cluster = get_cluster()
        bucket_name = os.getenv("COUCHBASE_BUCKET")
        result = cluster.query(
            f"SELECT * FROM `{bucket_name}` WHERE type='user' AND email=$email",
            QueryOptions(named_parameters={"email": email})
        )
        rows = list(result.rows())
        return rows[0][bucket_name] if rows else None
    except Exception as e:
        print(f"Error get_user_by_email: {e}")
        return None

def verify_api_key(api_key: str):
    try:
        cluster = get_cluster()
        bucket_name = os.getenv("COUCHBASE_BUCKET")
        result = cluster.query(
            f"SELECT * FROM `{bucket_name}` WHERE type='user' AND api_key=$api_key",
            QueryOptions(named_parameters={"api_key": api_key})
        )
        rows = list(result.rows())
        return rows[0][bucket_name] if rows else None
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
