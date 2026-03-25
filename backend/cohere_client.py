import os
import cohere
from dotenv import load_dotenv

load_dotenv()

def convert_log(raw_log: dict) -> str:
    """
    Send a single raw agent log to Cohere Command model.
    Returns a plain English summary for business owners.
    """
    co = cohere.Client(os.getenv("COHERE_API_KEY"))

    prompt = f"""
You are converting an AI agent log into simple business language.
A non-technical business owner will read this. Be concise and direct.

Raw log data:
- Agent Name: {raw_log.get('agent_name', 'Unknown')}
- Status: {raw_log.get('status', 'Unknown')}
- Input: {raw_log.get('input', '')}
- Output: {raw_log.get('output', '')}
- Error: {raw_log.get('error') or 'None'}
- Duration: {raw_log.get('duration_seconds', 0)} seconds

Write a 2-3 sentence summary that:
1. Says what the agent did in plain English
2. Says if it succeeded or failed and why
3. Mentions how long it took

Do not use technical terms. No bullet points. Just plain sentences.
"""

    response = co.generate(
        model="command-r",
        prompt=prompt,
        max_tokens=200
    )

    return response.generations[0].text.strip()