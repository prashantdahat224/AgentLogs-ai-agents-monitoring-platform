import requests

requests.post(
    "https://agentlogs-ai-agents-monitoring-platform.onrender.com",
    json={
        "agent_name": "test_agent",
        "status": "success",
        "input": "hello",
        "output": "hi there",
        "duration_seconds": 1.2
    },
    headers={"x-api-key": "agentlogs_F6d4oF6mW8rrsiBLWmADLSdjo5iMjdvK"}
)