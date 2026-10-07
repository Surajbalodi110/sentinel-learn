"""Phishing URL scorer. Heuristic, 100% offline. Score 0-100."""
import re
from urllib.parse import urlparse

SUSPICIOUS_WORDS = ["login", "verify", "secure", "account", "update", "free",
    "winner", "prize", "urgent", "suspend", "password", "bank", "paypal"]
SUSPICIOUS_TLDS = (".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".buzz")
SHORTENERS = ("bit.ly", "tinyurl.", "t.co", "goo.gl", "ow.ly", "is.gd")

def score_url(url: str) -> dict:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    score, reasons = 0, []
    try:
        p = urlparse(url)
    except Exception:
        return {"url": url, "score": 90, "level": "HIGH", "reasons": ["unparseable URL"]}
    host = (p.hostname or "").lower()

    def add(n, reason):
        nonlocal score
        score += n
        reasons.append(reason)

    if p.scheme == "http":
        add(10, "uses http, not https")
    if "@" in url:
        add(25, "contains @ (credential redirect trick)")
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
        add(25, "uses bare IP instead of domain")
    if host.startswith("xn--") or "xn--" in host:
        add(20, "punycode (look-alike domain)")
    if host.count(".") >= 3:
        add(15, "many subdomains (typosquat pattern)")
    if any(host.endswith(t) for t in SUSPICIOUS_TLDS):
        add(20, "suspicious cheap/free TLD")
    if any(s in host for s in SHORTENERS):
        add(15, "URL shortener hides destination")
    lowered = url.lower()
    hits = [w for w in SUSPICIOUS_WORDS if w in lowered]
    if hits:
        add(min(25, 10 + 5 * len(hits)), f"urgency/credential words: {', '.join(hits[:3])}")
    if len(url) > 120:
        add(10, "very long URL (obfuscation)")
    if re.search(r"%[0-9a-f]{2}.*%[0-9a-f]{2}", lowered):
        add(10, "heavy URL encoding")
    if "-" in host and any(b in host for b in ["paypaI", "micros0ft", "g00gle", "arnazon"]):
        add(20, "possible look-alike brand")
    score = min(100, score)
    level = "HIGH" if score >= 70 else ("MEDIUM" if score >= 40 else "LOW")
    return {"url": url, "score": score, "level": level, "reasons": reasons or ["no obvious tricks"]}
