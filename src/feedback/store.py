"""Feedback pipeline: validate → save locally → forward (endpoint/email)."""

import json
import os
import time
import uuid

REQUIRED = ("name", "love", "improve")


def validate(data: dict) -> list:
    errs = []
    if not (data.get("name") or "").strip():
        errs.append("Name is required.")
    if not (data.get("love") or "").strip():
        errs.append("Tell us at least one thing you'd love to have.")
    if not (data.get("improve") or "").strip():
        errs.append("Tell us at least one thing to improve.")
    r = data.get("rating", 0)
    try:
        if r and not (1 <= int(r) <= 5):
            errs.append("Rating must be 1-5.")
    except (TypeError, ValueError):
        errs.append("Rating must be 1-5.")
    return errs


def entry(name: str, contact: str, rating: int, love: str, improve: str) -> dict:
    return {"ref": "FB-" + uuid.uuid4().hex[:8].upper(),
            "ts": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "name": name.strip(), "contact": contact.strip(),
            "rating": int(rating or 0), "love": love.strip(), "improve": improve.strip()}


def save_local(e: dict, path: str = "data/feedback.jsonl") -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(e) + "\n")
    return "local"


def forward_endpoint(e: dict, timeout: int = 15) -> str:
    url = os.getenv("FEEDBACK_ENDPOINT", "")
    if not url:
        return "off"
    import httpx
    r = httpx.post(url, json=e, timeout=timeout)
    r.raise_for_status()
    return "endpoint"


def forward_email(e: dict) -> str:
    host = os.getenv("SMTP_HOST", "")
    user = os.getenv("SMTP_USER", "")
    pw = os.getenv("SMTP_PASS", "")
    to = os.getenv("FEEDBACK_TO", "") or os.getenv("ALERT_TO", "")
    if not (host and user and pw and to):
        return "off"
    import smtplib
    from email.mime.text import MIMEText
    body = (f"New SentinelLearn feedback {e['ref']}\nFrom: {e['name']} <{e['contact']}>\n"
            f"Rating: {e['rating']}/5\n\nLOVE TO HAVE:\n{e['love']}\n\nIMPROVE:\n{e['improve']}\n")
    msg = MIMEText(body)
    msg["Subject"] = f"[SentinelLearn feedback {e['ref']}] from {e['name']}"
    msg["From"] = os.getenv("SMTP_FROM", user)
    msg["To"] = to
    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587") or 587), timeout=20) as s:
        s.starttls()
        s.login(user, pw)
        s.sendmail(msg["From"], [to], msg.as_string())
    return "email"


def submit(name: str, contact: str, rating: int, love: str, improve: str) -> tuple:
    errs = validate({"name": name, "love": love, "improve": improve, "rating": rating})
    if errs:
        return None, errs, []
    e = entry(name, contact, rating, love, improve)
    channels = [save_local(e)]
    for fn in (forward_endpoint, forward_email):
        try:
            r = fn(e)
            if r != "off":
                channels.append(r)
        except Exception:
            pass
    return e, [], channels
