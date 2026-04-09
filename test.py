import requests

resp =requests.post(
    "https://agentlogs-ai-agents-monitoring-platform.onrender.com/ingest",
    json={
        "agent_name": "test_agent",
        "status": "success",
        "input": "hello",
        "output": "hi there",
        "duration_seconds": 1.2
    },
    headers={"x-api-key": "agentlogs_7tTRgVJq4NMELWHVCiXON1IN8UdlYyZD"}
)
print("Status code:", resp.status_code)
print("Response body:", resp.text)
print("Response body:", resp.json())