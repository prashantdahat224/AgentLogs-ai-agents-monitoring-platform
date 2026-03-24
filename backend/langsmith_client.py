import os
from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

def fetch_logs(project_name: str) -> list:
    """
    Fetch raw agent run logs from user's LangSmith project
    """
    try:
        client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

        runs = client.list_runs(
            project_name=project_name,
            execution_order=1,  # top level runs only
            limit=20            # last 20 runs
        )

        logs = []
        for run in runs:
            logs.append({
                "run_id": str(run.id),
                "name": run.name,
                "status": run.status,
                "inputs": str(run.inputs) if run.inputs else "",
                "outputs": str(run.outputs) if run.outputs else "",
                "error": str(run.error) if run.error else None,
                "start_time": str(run.start_time) if run.start_time else "",
                "end_time": str(run.end_time) if run.end_time else "",
                "total_tokens": run.total_tokens if hasattr(run, "total_tokens") else 0,
            })

        return logs

    except Exception as e:
        print(f"LangSmith error: {e}")
        return []
