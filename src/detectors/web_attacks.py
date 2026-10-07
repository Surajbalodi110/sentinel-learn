"""Web-attack detector (SQLi / XSS / traversal). 100% offline."""
import re

SQLI_PATTERNS = [
    r"union\s+select", r"'\s*or\s*'?\d'?\s*=\s*'?\d", r"'\s*or\s+'1'\s*=\s*'1",
    r"drop\s+table", r"insert\s+into", r"--\s*$", r";\s*--", r"sleep\s*\(",
    r"benchmark\s*\(", r"information_schema", r"@@version",
]
XSS_PATTERNS = [
    r"<script", r"javascript\s*:", r"onerror\s*=", r"onload\s*=",
    r"alert\s*\(", r"document\.cookie", r"<img[^>]+onerror",
]
TRAVERSAL_PATTERNS = [r"\.\./", r"\.\.\\", r"%2e%2e", r"/etc/passwd", r"boot\.ini"]

def _compile(pats):
    return [(p, re.compile(p, re.IGNORECASE)) for p in pats]

SQLI = _compile(SQLI_PATTERNS)
XSS = _compile(XSS_PATTERNS)
TRAV = _compile(TRAVERSAL_PATTERNS)

def detect_web_attacks(lines: list[str]) -> list[dict]:
    findings = []
    for i, line in enumerate(lines, 1):
        for pat, rx in SQLI:
            if rx.search(line):
                findings.append({"type": "sqli", "severity": "HIGH",
                    "line_no": i, "evidence": line.strip()[:300],
                    "title": f"Possible SQL injection (line {i}): `{pat}`"})
                break
        else:
            for pat, rx in XSS:
                if rx.search(line):
                    findings.append({"type": "xss", "severity": "HIGH",
                        "line_no": i, "evidence": line.strip()[:300],
                        "title": f"Possible XSS probe (line {i}): `{pat}`"})
                    break
            else:
                for pat, rx in TRAV:
                    if rx.search(line):
                        findings.append({"type": "path_traversal", "severity": "MEDIUM",
                            "line_no": i, "evidence": line.strip()[:300],
                            "title": f"Possible path traversal (line {i}): `{pat}`"})
                        break
    return findings
