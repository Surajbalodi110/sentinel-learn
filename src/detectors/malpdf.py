"""Suspicious-PDF triage. Static flags only — never executes anything. Offline."""
import re

TOKENS = {
    b"/JavaScript": (25, "embedded JavaScript"),
    b"/JS ": (25, "embedded JS action"),
    b"/OpenAction": (25, "auto-run action on open"),
    b"/AA": (20, "automatic actions"),
    b"/Launch": (30, "can launch external programs"),
    b"/EmbeddedFile": (20, "embedded files"),
    b"/EmbeddedFiles": (20, "embedded files"),
    b"/XFA": (15, "XFA forms (often abused)"),
    b"/Encrypt": (10, "encrypted (hides content)"),
    b"/ObjStm": (5, "compressed objects (obfuscation possible)"),
}

def analyze_pdf(data: bytes, filename: str = "") -> dict:
    reasons, score = [], 0
    meta = {"size_kb": round(len(data) / 1024, 1)}
    if not data.startswith(b"%PDF"):
        reasons.append("not a real PDF (magic bytes mismatch — possible spoofing)")
        score += 30
    for tok, (pts, why) in TOKENS.items():
        if tok in data:
            reasons.append(f"contains {why} ({tok.decode(errors='ignore').strip()})")
            score += pts
    try:
        from pypdf import PdfReader
        import io
        r = PdfReader(io.BytesIO(data))
        meta["pages"] = len(r.pages)
        if r.metadata:
            for k in ("author", "producer", "creator"):
                v = getattr(r.metadata, k, None)
                if v:
                    meta[k] = str(v)[:80]
        if r.metadata and not getattr(r.metadata, "producer", None):
            reasons.append("missing producer metadata (unusual for legit tools)")
            score += 5
    except Exception:
        meta["pages"] = "?"
    score = min(100, score)
    level = "HIGH" if score >= 70 else ("MEDIUM" if score >= 35 else "LOW")
    if not reasons:
        reasons = ["no classic malicious flags (still: only open from trusted senders)"]
    return {"kind": "pdf", "file": filename, "score": score, "level": level,
            "reasons": reasons, "meta": meta}
