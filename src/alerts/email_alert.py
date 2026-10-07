"""SMTP email alerts with dry-run fallback (so demos work offline).
Gmail preset: host=smtp.gmail.com port=587 user=you@gmail.com pass=<16-char App Password>.
Get App Password: Google Account > Security > 2-Step Verification ON > App passwords > Mail.
"""
import os
import smtplib
from email.mime.text import MIMEText

def _cfg():
    host = os.getenv("SMTP_HOST", "") or "smtp.gmail.com"
    port = int(os.getenv("SMTP_PORT", "587") or 587)
    user = os.getenv("SMTP_USER", "")
    pw = os.getenv("SMTP_PASS", "")
    to = os.getenv("ALERT_TO", user)
    frm = os.getenv("SMTP_FROM", user)
    return host, port, user, pw, frm, to

def send_alert(subject: str, body: str) -> str:
    host, port, user, pw, frm, to = _cfg()
    if not (host and user and pw and to):
        print(f"[DRY-RUN email] To={to or '(not set)'} Subject={subject}\n{body}\n")
        return "dry-run"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = frm
    msg["To"] = to
    with smtplib.SMTP(host, port, timeout=20) as s:
        s.starttls()
        s.login(user, pw)
        s.sendmail(frm, [to], msg.as_string())
    print(f"[sent email] {subject} -> {to}")
    return "sent"

def test_email() -> str:
    host, port, user, pw, frm, to = _cfg()
    print(f"SMTP config: host={host} port={port} user={user or '(missing)'} to={to or '(missing)'}")
    if not (user and pw):
        print("Set SMTP_USER + SMTP_PASS (Gmail App Password) in .env. Dry-run:")
        return send_alert("[SentinelLearn] test", "Dry-run OK. Set Gmail App Password to send real mail.")
    return send_alert("[SentinelLearn] test alert", "Wiring OK. HIGH findings will email you here.")
