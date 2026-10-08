"""Local open-model tutor via Ollama (free, offline, private). Graceful when absent."""

SYSTEM = ("You are the Cyberguru Tutor. Answer questions about IT, computers, "
    "networking, and cybersecurity for absolute beginners. Rules: defensive only - "
    "never give attack instructions, malware code, exploit code, or bypass methods. "
    "Format: 30-second plain answer, why it matters, one example, what to do, "
    "one official source link (MITRE ATT&CK, CISA, CERT-In, OWASP, NVD). "
    "If asked something non-IT, give a one-line redirect to IT topics. "
    "Under 150 words.")

_cache = {"ok": False, "models": [], "ts": 0.0}

def base_url() -> str:
    import os
    return os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")

def default_model() -> str:
    import os
    return os.getenv("OLLAMA_MODEL", "llama3.1")

def status(timeout: int = 2, refresh: bool = False) -> dict:
    """Is Ollama reachable + which models are pulled? Cached 30s. Never raises."""
    import time
    import httpx
    now = time.time()
    if not refresh and now - _cache["ts"] < 30:
        return {"ok": _cache["ok"], "models": list(_cache["models"])}
    try:
        r = httpx.get(base_url() + "/api/tags", timeout=timeout, trust_env=False)
        r.raise_for_status()
        models = [m.get("name", "") for m in r.json().get("models", [])]
        _cache.update(ok=True, models=models, ts=now)
    except Exception:
        _cache.update(ok=False, models=[], ts=now)
    return {"ok": _cache["ok"], "models": list(_cache["models"])}

def ask(q: str, model: str = "", timeout: int = 120) -> str | None:
    """Ask the local model. Returns text or None (unreachable/no model/fail)."""
    import httpx
    st = status()
    if not st["ok"]:
        return None
    m = model or default_model()
    if st["models"] and not any(m in x for x in st["models"]):
        return None
    try:
        r = httpx.post(base_url() + "/api/chat", timeout=timeout, trust_env=False, json={
            "model": m, "stream": False,
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": q}]})
        r.raise_for_status()
        return (r.json().get("message", {}).get("content", "") or "").strip() or None
    except Exception:
        return None

def _content_of(obj: dict) -> str:
    try:
        return obj.get("message", {}).get("content", "") or ""
    except Exception:
        return ""

def stream(q: str, model: str = "", timeout: int = 300):
    """Yield text chunks as the local model generates. Yields nothing if unavailable."""
    import httpx
    import json
    st = status()
    if not st["ok"]:
        return
    m = model or default_model()
    if st["models"] and not any(m in x for x in st["models"]):
        return
    try:
        with httpx.stream("POST", base_url() + "/api/chat", timeout=timeout, trust_env=False, json={
                "model": m, "stream": True,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": q}]}) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    chunk = _content_of(json.loads(line))
                except Exception:
                    continue
                if chunk:
                    yield chunk
    except Exception:
        return
