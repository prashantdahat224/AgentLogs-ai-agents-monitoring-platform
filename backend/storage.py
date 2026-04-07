import os
import uuid
import json
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

def store_log(api_key: str, log_entry: dict):
    """Save log entry and update the logs index for this user."""
    collection = get_collection()
    log_id = str(uuid.uuid4())
    log_entry["log_id"] = log_id

    # Save the individual log document
    collection.upsert(f"log::{api_key}::{log_id}", log_entry)

    # Update the index document (list of log IDs for this user)
    index_key = f"logindex::{api_key}"
    try:
        result = collection.get(index_key)
        index = result.content_as[dict]
        index["ids"].append(log_id)
    except DocumentNotFoundException:
        index = {"ids": [log_id]}
    collection.upsert(index_key, index)

def get_logs(api_key: str) -> list:
    """Fetch all logs for a given API key, newest first."""
    try:
        collection = get_collection()
        index_key = f"logindex::{api_key}"
        result = collection.get(index_key)
        index = result.content_as[dict]
        logs = []
        for log_id in index["ids"]:
            try:
                log_result = collection.get(f"log::{api_key}::{log_id}")
                logs.append(log_result.content_as[dict])
            except DocumentNotFoundException:
                continue
        return list(reversed(logs))
    except DocumentNotFoundException:
        return []
    except Exception as e:
        print(f"Error get_logs: {e}")
        return []

def get_summary(api_key: str) -> dict:
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
