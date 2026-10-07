"""Honest scan reporting: what was checked, what was NOT, and what clean means."""

CHECKED = [
    "Brute-force login guessing (MITRE T1110) in auth logs",
    "SQL injection / XSS / path traversal probes (T1190, T1189, T1083) in web logs",
    "Phishing-URL heuristics (T1566.002): IP hosts, @ tricks, free TLDs, urgency words",
]

NOT_CHECKED = [
    "Malware behavior, C2 beacons, lateral movement",
    "Privilege escalation, persistence mechanisms",
    "Data exfiltration, zero-days, encrypted payloads",
    "Anything outside the pasted logs/URLs",
]

def scan_summary(auth_n: int, web_n: int, url_n: int, threshold: int) -> str:
    return (f"Checked {auth_n} auth lines (threshold {threshold}) + {web_n} web lines + "
            f"{url_n} URLs against {len(CHECKED)} detection families. "
            "'Clean' means no matching patterns — not proof of safety.")
