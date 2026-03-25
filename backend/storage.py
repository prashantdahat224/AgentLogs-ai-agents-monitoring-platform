import json
import os
from datetime import datetime

LOGS_FILE = "logs.json"

def load_logs():
    if not os.path.exists(LOGS_FILE):
        return {}
    with open(LOGS_FILE, "r") as f:
        return json.load(f)

def save_logs(data):
    with open(LOGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def store_log(api_key: str, log_entry: dict):
    """Save a converted log entry linked to the user's API key."""
    logs = load_logs()
    if api_key not in logs:
        logs[api_key] = []
    logs[api_key].append(log_entry)
    save_logs(logs)

def get_logs(api_key: str) -> list:
    """Fetch all logs for a given API key, newest first."""
    logs = load_logs()
    user_logs = logs.get(api_key, [])
    return list(reversed(user_logs))

def get_summary(api_key: str) -> dict:
    """Return summary stats for a user's logs."""
    user_logs = get_logs(api_key)
    total = len(user_logs)
    successful = len([l for l in user_logs if l.get("status") == "success"])
    failed = len([l for l in user_logs if l.get("status") == "error"])
    return {
        "total_runs": total,
        "successful": successful,
        "failed": failed,
        "success_rate": f"{round((successful / total) * 100)}%" if total > 0 else "0%"
    }