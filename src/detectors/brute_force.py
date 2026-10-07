"""Brute-force detector. 100% offline. Parses auth-style logs."""
import re
from collections import Counter

FAILED_RE = re.compile(r"[Ff]ailed (?:password|login).*?from (\d{1,3}(?:\.\d{1,3}){3})")
IP_RE = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3})")

def detect_brute_force(lines: list[str], threshold: int = 5) -> list[dict]:
    fails: Counter = Counter()
    examples: dict[str, str] = {}
    for line in lines:
        m = FAILED_RE.search(line)
        if m:
            ip = m.group(1)
            fails[ip] += 1
            examples.setdefault(ip, line.strip())
        elif "Failed" in line:
            m2 = IP_RE.search(line)
            if m2:
                ip = m2.group(1)
                fails[ip] += 1
                examples.setdefault(ip, line.strip())
    findings = []
    for ip, count in fails.most_common():
        if count >= threshold:
            findings.append({
                "type": "brute_force",
                "severity": "HIGH" if count >= threshold else "MEDIUM",
                "ip": ip,
                "count": count,
                "evidence": examples[ip],
                "title": f"Possible brute-force from {ip} ({count} failures)",
            })
    return findings
