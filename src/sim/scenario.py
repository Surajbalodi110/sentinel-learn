"""Night Shift: scripted SOC simulation. One action per tick, scored, debriefed."""

ACTIONS = ["Block IP / domain", "Reset passwords", "Isolate host",
           "Escalate to L2", "Mark FP & close", "Do nothing"]

TICKS = [
 {"title": "23:40 — Shift starts",
  "brief": "Friday night, you are L1. Baseline traffic only. Learn what normal looks like — it makes evil obvious.",
  "auth": ["Oct 7 23:31:02 soc sshd[11]: Accepted password for alice from 10.0.0.4 port 51001 ssh2"],
  "web": ['10.0.0.5 - - [07/Oct/2026] "GET /home HTTP/1.1" 200 2048'],
  "urls": [],
  "correct": ["Mark FP & close", "Do nothing"],
  "why": "All benign: office IP, normal pages. Good analysts close noise fast instead of escalating everything.",
  "rooms": []},
 {"title": "23:47 — Phish reported",
  "brief": "Helpdesk forwards a user report: 'IT-Desk says my mailbox is full, is this real?'",
  "auth": [],
  "web": [],
  "urls": ["http://192.0.2.9.verify-login.tk/inbox"],
  "correct": ["Block IP / domain"],
  "why": "Bare IP + look-alike domain + urgency = textbook phish (T1566). Block the domain, warn users.",
  "rooms": ["phish-email"]},
 {"title": "00:05 — Login storm",
  "brief": "Auth log explodes: same outside IP hammering accounts.",
  "auth": [f"Oct 7 00:05:{10+i:02d} soc sshd[2{i}]: Failed password for admin from 203.0.113.99 port 51{i:03d} ssh2" for i in range(6)],
  "web": [],
  "urls": [],
  "correct": ["Block IP / domain", "Reset passwords"],
  "why": "Classic brute-force (T1110). Block the source AND reset targeted accounts — guessing may have worked elsewhere.",
  "rooms": ["net-sec", "monitoring"]},
 {"title": "00:19 — Oh no: success",
  "brief": "One line changes everything: an 'Accepted' from the attacker IP — plus a web probe.",
  "auth": ["Oct 7 00:19:44 soc sshd[99]: Accepted password for admin from 203.0.113.99 port 51999 ssh2"],
  "web": ['203.0.113.99 - - [07/Oct/2026] "GET /item?id=1 UNION SELECT password FROM users HTTP/1.1" 200 1024'],
  "urls": [],
  "correct": ["Isolate host", "Reset passwords", "Escalate to L2"],
  "why": "Compromise confirmed: attacker session + active SQLi (T1190). Isolate first, kill sessions, escalate with timeline.",
  "rooms": ["soc-ops", "ir"]},
 {"title": "00:31 — VP lands in London?",
  "brief": "New alert: executive login from London at 00:31. Traveling VP or stolen session?",
  "auth": ["Oct 7 00:31:02 soc sshd[31]: Accepted password for vp-sales from 10.0.0.4 port 51200 ssh2"],
  "web": [],
  "urls": [],
  "correct": ["Mark FP & close"],
  "why": "TRAP: office IP, known user, no fails before it. Blocking the VP's laptop during a deal = self-inflicted outage. Verify, don't nuke.",
  "rooms": ["soc-ops"]},
 {"title": "00:44 — Export spike",
  "brief": "Web logs show bulk export queries from the compromised host's session.",
  "auth": [],
  "web": ['203.0.113.99 - - [07/Oct/2026] "GET /export?all=1 UNION SELECT * FROM customers HTTP/1.1" 200 8192'],
  "urls": [],
  "correct": ["Isolate host", "Escalate to L2"],
  "why": "Likely exfiltration in progress. Isolate NOW, escalate — every minute is records out the door.",
  "rooms": ["ir", "threat-det"]},
]

def score_action(tick: dict, action: str) -> int:
    if action in tick["correct"]:
        return 20
    if action == "Do nothing":
        return -15
    return -10

def grade(score: int, total: int) -> str:
    pct = 100 * score / max(1, total)
    if pct >= 90:
        return "S — SOC star"
    if pct >= 70:
        return "A — solid analyst"
    if pct >= 45:
        return "B — learning fast"
    return "C — replay + read the debrief"
