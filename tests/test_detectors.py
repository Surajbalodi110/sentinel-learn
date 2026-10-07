from src.detectors.brute_force import detect_brute_force
from src.detectors.web_attacks import detect_web_attacks
from src.detectors.phishing import score_url

def test_brute_force():
    lines = ["Failed password for root from 1.2.3.4 port 1"] * 6
    assert detect_brute_force(lines, threshold=5)[0]["ip"] == "1.2.3.4"

def test_sqli():
    assert any(f["type"] == "sqli" for f in detect_web_attacks(["GET /?q=' OR '1'='1"]))

def test_phishing_scores_bad_high():
    assert score_url("http://192.168.0.1.verify-login.tk/secure@evil.com")["score"] >= 70
