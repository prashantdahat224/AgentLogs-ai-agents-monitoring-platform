import os
import uuid
from datetime import timedelta
from dotenv import load_dotenv
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.auth import PasswordAuthenticator

load_dotenv()

def get_cluster():
    auth = PasswordAuthenticator(
        os.getenv("COUCHBASE_USER"),
        os.getenv("COUCHBASE_PASSWORD")
    )
    cluster = Cluster(
        os.getenv("COUCHBASE_URL"),
        ClusterOptions(auth)
    )
    cluster.wait_until_ready(timedelta(seconds=10))
    return cluster

def get_collection():
    cluster = get_cluster()
    bucket = cluster.bucket(os.getenv("COUCHBASE_BUCKET"))
    return bucket.default_collection()

def store_log(api_key: str, log_entry: dict):
    """Save a log entry linked to the user's API key."""
    collection = get_collection()
    doc_id = f"log::{api_key}::{uuid.uuid4()}"
    log_entry["type"] = "log"
    log_entry["api_key"] = api_key
    collection.upsert(doc_id, log_entry)

def get_logs(api_key: str) -> list:
    """Fetch all logs for a given API key, newest first."""
    try:
        cluster = get_cluster()
        bucket_name = os.getenv("COUCHBASE_BUCKET")
        result = cluster.query(
            f"SELECT * FROM `{bucket_name}` WHERE type='log' AND api_key=$api_key ORDER BY timestamp DESC",
            QueryOptions(named_parameters={"api_key": api_key})
        )
        return [row[bucket_name] for row in result.rows()]
    except Exception as e:
        print(f"Error get_logs: {e}")
        return []

def get_summary(api_key: str) -> dict:
    """Return summary stats for a user's logs."""
    logs = get_logs(api_key)
    total = len(logs)
    successful = len([l for l in logs if l.get("status") == "success"])
    failed = len([l for l in logs if l.get("status") == "error"])
    return {
        "total_runs": total,
        "successful": successful,
        "failed": failed,
        "success_rate": f"{round((successful / total) * 100)}%" if total > 0 else "0%"
    }
