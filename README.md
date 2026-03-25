# AgentLogs

> Full transparency into what your AI agents decided and why — in plain English.

## What It Does

Business owners who run AI agents have no idea what those agents are actually doing.
AgentLogs monitors every agent run and translates it into plain English on a simple dashboard.
No technical knowledge needed.

```
Customer triggers agent
        ↓
AgentLogs SDK captures input/output/errors silently
        ↓
SDK sends raw data → POST /ingest
        ↓
Backend verifies API key → Cohere converts to plain English
        ↓
Summary saved to database
        ↓
Business owner opens dashboard → sees everything clearly
```

## Project Structure

```
agentlogs/
├── backend/
│   ├── main.py          → /signup /login /ingest /logs
│   ├── auth.py          → signup, login, verify api_key
│   ├── storage.py       → save and fetch logs per user
│   ├── cohere_client.py → convert raw log to plain English
│   ├── requirements.txt
│   └── .env
│
├── sdk/
│   ├── agentlogs/
│   │   ├── __init__.py
│   │   └── tracker.py   → the @track decorator
│   └── setup.py
│
└── frontend/
    └── index.html       → signup + dashboard
```

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
# Add COHERE_API_KEY to .env
python main.py
```

### SDK (for your clients)
```bash
cd sdk
pip install .
```

### Frontend
Open `frontend/index.html` in a browser.
Update `const API = "..."` to your deployed backend URL.

## Client Integration (2 lines)

```python
from agentlogs import track

@track(api_key="agentlogs_abc123")
def my_agent(user_input):
    # agent logic here
    return response
```

That's it. Every run is automatically captured and sent to the dashboard.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /signup | Create account, get API key |
| POST | /login | Login, get API key back |
| POST | /ingest | SDK sends raw log (auth via x-api-key header) |
| GET | /logs | Dashboard fetches plain English logs |
