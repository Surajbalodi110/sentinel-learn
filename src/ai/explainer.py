"""Hybrid AI explainer: offline templates + optional LLM. Never requires internet."""
import os

OFFLINE_COACH = {
    "brute_force": ("Brute-force login", "T1110", "Someone is guessing passwords against an account/service.",
        ["Block/throttle the IP at firewall", "Enforce MFA + lockout policy", "Check for successful logins from that IP"]),
    "sqli": ("SQL injection probe", "T1190", "Attacker tries to break your database query to steal or corrupt data.",
        ["Use parameterized queries/ORM, never string-concat SQL", "Patch + WAF rule, review DB logs for success", "Least-privilege DB user"]),
    "xss": ("Cross-site scripting probe", "T1189", "Attacker tries to inject JavaScript to hijack other users.",
        ["HTML-escape output, Content-Security-Policy header", "Validate/sanitize inputs", "Scan for stored payloads"]),
    "path_traversal": ("Path traversal probe", "T1083", "Attacker tries ../../ to read files outside the web root.",
        ["Normalize + allowlist file paths", "Run as low-priv user, patch framework", "Block ../ at WAF"]),
    "phishing": ("Phishing URL", "T1566.002", "Link uses deception (look-alike domain, urgency) to steal credentials.",
        ["Do not click/enter creds; verify sender out-of-band", "Report + block domain", "Enable MFA + password manager"]),
}

def offline_explain(finding: dict) -> str:
    t = finding.get("type", "unknown")
    name, mitre, what, fixes = OFFLINE_COACH.get(t, ("Unknown", "—", "Suspicious pattern.", ["Isolate, investigate logs"]))
    lines = [
        f"Finding: {finding.get('title', name)} [severity={finding.get('severity', finding.get('level', '?'))}]",
        f"What: {what}",
        f"MITRE ATT&CK: {mitre}",
        f"Evidence: {finding.get('evidence', finding.get('url', ''))}",
    ]
    if "reasons" in finding:
        lines.append("Why flagged: " + "; ".join(finding["reasons"]))
    lines.append("Fix (beginner, enterprise-ready):")
    lines += [f"  {i+1}. {f}" for i, f in enumerate(fixes)]
    return "\n".join(lines)

def llm_explain(finding: dict, context: str = "") -> str | None:
    """Returns LLM text or None if no key / no internet."""
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        return None
    try:
        import httpx
        base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        prompt = (f"You are a patient SOC mentor for beginners. Explain this defensive finding "
                  f"in plain English with 3 fix steps.\nFinding: {finding}\n{context}")
        r = httpx.post(f"{base}/chat/completions", timeout=30,
            headers={"Authorization": f"Bearer {key}"},
            json={"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 350})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None

def explain(finding: dict, context: str = "") -> str:
    llm = llm_explain(finding, context)
    base = offline_explain(finding)
    if llm:
        return base + f"\n\n--- AI coach (online) ---\n{llm}"
    return base + "\n\n(tip: set OPENAI_API_KEY for richer AI coaching; offline explanation shown)"
