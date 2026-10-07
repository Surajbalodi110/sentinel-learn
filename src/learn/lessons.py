"""Beginner lessons mapped to each detector + MITRE."""

LESSONS = [
    {"id": "blue-team", "title": "What is defensive (blue-team) security?",
     "body": "Blue team = detect, triage, contain, recover. This lab does: log review -> detect -> explain (MITRE) -> fix -> alert."},
    {"id": "brute_force", "title": "Brute-force: guessing passwords (MITRE T1110)",
     "body": "Attackers try many passwords. Defend: MFA, lockout/throttle, strong passwords, monitor Failed logins. Try: scan sample_auth.log."},
    {"id": "sqli", "title": "SQL injection (MITRE T1190)",
     "body": "Input like ' OR '1'='1 breaks queries. Defend: parameterized queries, least-privilege DB, WAF. Try: scan sample_web.log."},
    {"id": "xss", "title": "XSS: malicious scripts (MITRE T1189)",
     "body": "Input like <script> runs in victims' browsers. Defend: escape output, CSP header, validate input."},
    {"id": "phishing", "title": "Phishing links (MITRE T1566.002)",
     "body": "Check: https? IP host? @? many subdomains? urgency words? shortener? Try: scan sample_urls.csv."},
    {"id": "intel", "title": "Trending threats: CISA KEV",
     "body": "CISA lists bugs actually exploited. Patch these first. This tool caches them for offline study."},
    {"id": "respond", "title": "Respond like an enterprise SOC",
     "body": "1.Triage severity 2.Contain IP/domain 3.Eradicate + patch 4.Recover 5.Lessons-learned + email alert for HIGH."},
]

def print_lessons():
    for l in LESSONS:
        print(f"\n## {l['title']}\n{l['body']}")
