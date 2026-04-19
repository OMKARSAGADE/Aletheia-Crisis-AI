import os

_langfuse = None
_langfuse_available = False
_initialized = False

def _init_langfuse():
    global _langfuse, _langfuse_available, _initialized
    if _initialized:
        return
    _initialized = True
    try:
        from langfuse import get_client
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
        host = os.getenv("LANGFUSE_BASE_URL", os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"))
        
        if public_key and secret_key:
            _langfuse = get_client()
            _langfuse_available = True
        else:
            _langfuse_available = False
    except Exception as e:
        print(f"Langfuse init warning: {e}")
        _langfuse_available = False

def get_langfuse():
    _init_langfuse()
    return _langfuse

def is_available():
    _init_langfuse()
    return _langfuse_available

def flush():
    client = get_langfuse()
    if client:
        try:
            client.flush()
        except Exception:
            pass

def fetch_recent_traces(limit=10):
    """Fetch recent traces from Langfuse for the AI Trace dashboard tab."""
    client = get_langfuse()
    if not client:
        return []
    try:
        # v4 SDK uses the REST API under the hood
        import httpx
        host = os.getenv("LANGFUSE_BASE_URL", os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"))
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
        
        resp = httpx.get(
            f"{host}/api/public/traces",
            params={"limit": limit},
            auth=(public_key, secret_key),
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for t in data.get("data", []):
                results.append({
                    "id": t.get("id", ""),
                    "name": t.get("name", "pipeline_run"),
                    "input": t.get("input", {}),
                    "output": t.get("output", {}),
                    "timestamp": str(t.get("timestamp", "")),
                    "user_id": t.get("userId", "citizen"),
                })
            return results
        return []
    except Exception as e:
        print(f"Langfuse fetch traces error: {e}")
        return []
