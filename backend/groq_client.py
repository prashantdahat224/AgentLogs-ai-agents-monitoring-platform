import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def convert_logs(raw_logs: list) -> list:
    """
    Send raw LangSmith logs to Groq LLaMA
    Returns human readable version for business owners
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    readable_logs = []

    for log in raw_logs:
        prompt = f"""
You are converting an AI agent log into simple business language.
A non-technical business owner will read this.

Raw log data:
- Agent Name: {log['name']}
- Status: {log['status']}
- Input: {log['inputs']}
- Output: {log['outputs']}
- Error: {log['error'] if log['error'] else 'None'}
- Start Time: {log['start_time']}
- End Time: {log['end_time']}

Convert this into a simple 3-4 line summary that:
1. Says what the agent did in plain English
2. Says what decision it made
3. Says if it succeeded or failed and why
4. Is easy for a business owner to understand

Do not use technical terms. Be direct and clear.
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )

        readable_logs.append({
            "run_id": log["run_id"],
            "status": log["status"],
            "start_time": log["start_time"],
            "summary": response.choices[0].message.content
        })

    return readable_logs
