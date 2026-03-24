# AgentLogs — Backend API

Full transparency into what your AI agents decided and why.

## What It Does

AgentLogs- AI agent observability tool 
that gives businesses full transparency and detailed understanding 
into what their AI agents did and why.

## Live Demo
 https://agent-logs-solution.netlify.app/

## Tech Stack
- Python + FastAPI
- LangSmith (log capture)
- Anthropic Claude (log conversion)
- JSON (simple database)

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/prashantdahat224/AgentLogs-ai-agents-monitoring-platform
cd agentlogs-backend
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API keys
```bash
# Open .env and add your keys
```

### 4. Run the server
```bash
python main.py
```

## API Endpoints

### Signup
```
POST /signup
{
  "email": "company@email.com",
  "password": "password",
  "company": "Company Name"
}
```

### Get Logs
```
POST /logs
Headers: x-api-key: agentlogs_abcd
{
  "project_name": "your_langsmith_project"
}
```

### Get Summary
```
GET /logs/summary?project_name=your_project
Headers: x-api-key: agentlogs_abcd
```

## How It Works

```
User's agent runs
      ↓
LangSmith captures every step
      ↓
AgentLogs fetches raw logs
      ↓
Claude converts to simple language
      ↓
Dashboard displays to business owner
```

## Deploy
Deploy on Railway.app or Render.com for free.
