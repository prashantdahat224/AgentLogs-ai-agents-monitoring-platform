from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from auth import generate_api_key, verify_api_key, create_user, get_user_by_email, verify_login
from storage import store_log, get_logs, get_summary
from cohere_client import convert_log
import uvicorn

# added
#from typing import Optional 
# added



app = FastAPI(title="AgentLogs API", version="2.0.0")

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

class LoginRequest(BaseModel):
    email: str
    password: str

class IngestRequest(BaseModel):
    agent_name: str
    status: str           # "success" or "error"
    input: str
    output: str
    error: str | None = None #error: Optional[str] = None    # before=>//error: str | None = None
    duration_seconds: float

# ─── Routes ───

@app.get("/")
def home():
    return {"name": "AgentLogs API", "version": "2.0.0", "status": "running"}


@app.post("/signup")
def signup(data: SignupRequest):
    """Business owner signs up → gets unique API key."""
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


@app.post("/login")
def login(data: LoginRequest):
    """Business owner logs in → gets their API key back."""
    user = verify_login(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "api_key": user["api_key"],
        "company": user["company"],
        "email": user["email"]
    }


@app.post("/ingest")
def ingest(data: IngestRequest, x_api_key: str = Header(...)):
    """
    SDK sends raw agent log here.
    We verify API key → convert via Cohere → save to DB.
    """
    # Step 1 — verify API key
    user = verify_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Step 2 — build raw log dict
    raw_log = {
        "agent_name": data.agent_name,
        "status": data.status,
        "input": data.input,
        "output": data.output,
        "error": data.error,
        "duration_seconds": data.duration_seconds
    }

    # Step 3 — convert to plain English via Cohere
    summary = convert_log(raw_log)

    # Step 4 — save to storage
    log_entry = {
        "agent_name": data.agent_name,
        "status": data.status,
        "duration_seconds": data.duration_seconds,
        "summary": summary,
        "timestamp": datetime.utcnow().isoformat()
    }
    store_log(user["api_key"], log_entry)

    return {"message": "Log ingested", "summary": summary}


@app.get("/logs")
def logs(x_api_key: str = Header(...)):
    """Business owner's dashboard calls this → returns all plain English logs."""
    user = verify_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    user_logs = get_logs(user["api_key"])
    stats = get_summary(user["api_key"])

    return {
        "company": user["company"],
        "stats": stats,
        "logs": user_logs
    }


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)