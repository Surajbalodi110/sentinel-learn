"""Optional AI photo description (vision model). Needs OPENAI_API_KEY. Offline-safe."""
import base64
import os

LENS = [
    ("Google Lens", "https://lens.google.com/uploadbyurl (or lens.google.com → upload)"),
    ("TinEye", "https://tineye.com/search"),
    ("Bing Visual Search", "https://www.bing.com/visualsearch"),
    ("Yandex Images", "https://yandex.com/images/search"),
]

def describe_image(data: bytes, mime: str = "image/jpeg") -> str | None:
    """Describe scene/landmark for OSINT. Refuses private-person identification."""
    key = os.getenv("OPENAI_API_KEY", "")
    if not key or len(data) > 4_000_000:
        return None
    try:
        import httpx
        b = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        m = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        b64 = base64.b64encode(data).decode()
        r = httpx.post(f"{b}/chat/completions", timeout=40,
            headers={"Authorization": f"Bearer {key}"},
            json={"model": m, "max_tokens": 250, "messages": [{
                "role": "user", "content": [
                    {"type": "text", "text": "Defensive OSINT helper. Describe this photo for investigation: setting, visible landmarks/signs/text, likely place clues. Do NOT identify private individuals. End with 2 suggested next steps."},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}]}]})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None
