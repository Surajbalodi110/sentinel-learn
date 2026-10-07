import os
import re

DASH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "dashboard.py"))
DATA = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))

def test_nav_keys_all_have_sections():
    s = open(DASH, encoding="utf-8").read()
    keys = re.findall(r'^\s*\("([a-z]+)", "', s, re.M)
    sections = set(re.findall(r'^if nav == "([a-z]+)":', s, re.M))
    for k in keys:
        assert f'if nav == "{k}":' in s, f"nav '{k}' has no section"
    assert sections == set(keys), f"mismatch: {sections} vs {set(keys)}"

def test_default_nav_exists():
    s = open(DASH, encoding="utf-8").read()
    m = re.search(r'get\("nav", "([a-z]+)"\)', s)
    assert m and m.group(1) in re.findall(r'^\s*\("([a-z]+)", "', s, re.M)

def test_sample_pipeline_end_to_end():
    from src.detectors.brute_force import detect_brute_force
    from src.detectors.web_attacks import detect_web_attacks
    from src.detectors.phishing import score_url
    from src.scoring.risk import score_findings
    auth = open(os.path.join(DATA, "sample_auth.log"), errors="ignore").read().splitlines()
    web = open(os.path.join(DATA, "sample_web.log"), errors="ignore").read().splitlines()
    bf = detect_brute_force(auth)
    assert any(f["ip"] == "203.0.113.9" and f["severity"] == "HIGH" for f in bf)
    wa = detect_web_attacks(web)
    assert {f["type"] for f in wa} >= {"sqli", "xss"}
    ph = score_url("http://192.168.1.100.verify-login.tk/secure/update")
    assert ph["level"] == "HIGH"
    risk = score_findings(bf + wa)
    assert risk["level"] == "CRITICAL" and risk["score"] == 100

def test_footer_links_point_at_real_pages():
    s = open(DASH, encoding="utf-8").read()
    for m in re.findall(r'href="\?nav=([a-z]+)', s):
        assert f'if nav == "{m}":' in s, f"footer links to missing page {m}"
