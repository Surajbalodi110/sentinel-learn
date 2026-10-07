from src.ai.local_llm import SYSTEM, base_url, default_model, status

def test_guardrails_in_prompt():
    assert "defensive only" in SYSTEM
    assert "150 words" in SYSTEM or "150" in SYSTEM
    assert "MITRE" in SYSTEM

def test_status_offline_graceful():
    import src.ai.local_llm as L
    L._cache.update(ok=False, models=[], ts=0.0)
    import os
    os.environ["OLLAMA_URL"] = "http://127.0.0.1:1"
    try:
        s = status(timeout=1, refresh=True)
        assert s == {"ok": False, "models": []}
    finally:
        del os.environ["OLLAMA_URL"]
        L._cache.update(ok=False, models=[], ts=0.0)

def test_ask_none_when_down():
    import src.ai.local_llm as L
    import os
    L._cache.update(ok=False, models=[], ts=0.0)
    os.environ["OLLAMA_URL"] = "http://127.0.0.1:1"
    try:
        assert L.ask("what is phishing", timeout=2) is None
    finally:
        del os.environ["OLLAMA_URL"]
        L._cache.update(ok=False, models=[], ts=0.0)

def test_answer_falls_back_without_ollama():
    import src.ai.local_llm as L
    import src.learn.chatbot as C
    import os
    L._cache.update(ok=False, models=[], ts=0.0)
    os.environ["OLLAMA_URL"] = "http://127.0.0.1:1"
    try:
        C.LAST_ENGINE = "built-in"
        r = C.answer("What is the Pyramid of Pain")
        assert "Pyramid of Pain" in r and C.LAST_ENGINE == "built-in"
    finally:
        del os.environ["OLLAMA_URL"]
        L._cache.update(ok=False, models=[], ts=0.0)

def test_stream_parser():
    from src.ai.local_llm import _content_of
    assert _content_of({"message": {"content": "hi"}}) == "hi"
    assert _content_of({}) == ""
    assert _content_of({"message": {}}) == ""

def test_answer_stream_empty_when_down():
    import src.ai.local_llm as L
    import src.learn.chatbot as C
    import os
    L._cache.update(ok=False, models=[], ts=0.0)
    os.environ["OLLAMA_URL"] = "http://127.0.0.1:1"
    try:
        C.LAST_ENGINE = "built-in"
        assert list(C.answer_stream("hello")) == []
        assert C.LAST_ENGINE == "built-in"
    finally:
        del os.environ["OLLAMA_URL"]
        L._cache.update(ok=False, models=[], ts=0.0)
