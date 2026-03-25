import time
import requests
import functools
import traceback

AGENTLOGS_ENDPOINT = "your-backend-url/ingest"  # change to deployed URL

def track(api_key: str, agent_name: str = None, endpoint: str = None):
    """
    Decorator to silently capture agent runs and send to AgentLogs.

    Usage:
        from agentlogs import track

        @track(api_key="agentlogs_abc123")
        def my_agent(input):
            ...
    """
    backend_url = endpoint or AGENTLOGS_ENDPOINT

    def decorator(func):
        name = agent_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Capture input
            input_str = str(args[0]) if args else str(kwargs)

            start = time.time()
            error_msg = None
            output_str = ""
            status = "success"

            try:
                result = func(*args, **kwargs)
                output_str = str(result)
                return result
            except Exception as e:
                status = "error"
                error_msg = str(e)
                traceback.print_exc()
                raise
            finally:
                duration = round(time.time() - start, 3)

                # Silently send log to AgentLogs backend
                try:
                    requests.post(
                        backend_url,
                        json={
                            "agent_name": name,
                            "status": status,
                            "input": input_str,
                            "output": output_str,
                            "error": error_msg,
                            "duration_seconds": duration
                        },
                        headers={"x-api-key": api_key},
                        timeout=5
                    )
                except Exception:
                    pass  # Never let logging break the agent

        return wrapper
    return decorator