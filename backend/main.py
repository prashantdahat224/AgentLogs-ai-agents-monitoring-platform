from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from auth import generate_api_key, verify_api_key, create_user, get_user_by_email
from langsmith_client import fetch_logs
from groq_client import convert_logs
import uvicorn

app = FastAPI(title="AgentLogs API", version="1.0.0")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Models ───
class SignupRequest(BaseModel):
    email: str
    password: str
    company: str

class LogRequest(BaseModel):
    project_name: str  # user's LangSmith project name

# ─── Routes ───

@app.get("/")
def home():
    return {"name": "AgentLogs API", "status": "running"}


@app.post("/signup")
def signup(data: SignupRequest):
    """
    Company signs up → gets unique API key
    """
    existing = get_user_by_email(data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    api_key = generate_api_key()
    create_user(data.email, data.password, data.company, api_key)

    return {
        "message": "Signup successful",
        "api_key": api_key,
        "company": data.company
    }


@app.post("/logs")
def get_logs(data: LogRequest, x_api_key: str = Header(...)):
    """
    Company sends their LangSmith project name
    AgentLogs fetches + converts + returns human readable logs
    """
    # Step 1 - verify their API key
    user = verify_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Step 2 - fetch raw logs from LangSmith
    raw_logs = fetch_logs(data.project_name)
    if not raw_logs:
        raise HTTPException(status_code=404, detail="No logs found for this project")

    # Step 3 - convert to human readable via Claude
    readable_logs = convert_logs(raw_logs)

    return {
        "company": user["company"],
        "project": data.project_name,
        "total_runs": len(raw_logs),
        "logs": readable_logs
    }


@app.get("/logs/summary")
def get_summary(project_name: str, x_api_key: str = Header(...)):
    """
    Quick summary of agent runs
    """
    user = verify_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    raw_logs = fetch_logs(project_name)
    if not raw_logs:
        raise HTTPException(status_code=404, detail="No logs found")

    total = len(raw_logs)
    successful = len([r for r in raw_logs if r.get("status") == "success"])
    failed = len([r for r in raw_logs if r.get("status") == "error"])

    return {
        "project": project_name,
        "total_runs": total,
        "successful": successful,
        "failed": failed,
        "success_rate": f"{round((successful/total)*100)}%" if total > 0 else "0%"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
