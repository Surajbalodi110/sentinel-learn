from src.osint.lookup import (clean_domain, is_domain, is_ip, vt_link,
                                   abuse_link, USER_RE, EMAIL_RE, PROFILE_LINKS)

def test_clean_domain():
    assert clean_domain("https://Example.COM:443/a") == "example.com"
    assert clean_domain("example.com.") == "example.com"

def test_is_domain_ip():
    assert is_domain("example.com") and not is_domain("not a domain!!")
    assert is_ip("8.8.8.8") and not is_ip("999.1.1.1")

def test_validators():
    assert USER_RE.match("octocat") and not USER_RE.match("x")
    assert EMAIL_RE.match("a@b.com") and not EMAIL_RE.match("nope")

def test_links():
    assert "virustotal" in vt_link("example.com")
    assert "abuseipdb" in abuse_link("1.2.3.4")
    assert len(PROFILE_LINKS) >= 4

def test_gps_helpers():
    from src.detectors.imagecheck import _dms, extract_gps
    assert abs(_dms((28, 36, 0)) - 28.6) < 0.01
    assert _dms("bad") is None
    assert extract_gps(b"not an image") is None

def test_plate():
    from src.osint.lookup import parse_plate
    p = parse_plate("DL 8C A1234")
    assert p["ok"] and p["state"] == "Delhi"
    assert not parse_plate("XX 99 Z9999")["ok"]
    assert not parse_plate("hello")["ok"]

def test_number_and_smishing():
    from src.osint.lookup import classify_number, smishing_score
    assert classify_number("+919876543210")["ok"]
    assert "telemarketing" in classify_number("1401234567")["kind"]
    assert not classify_number("123")["ok"]
    s = smishing_score("Your KYC suspended, verify immediately http://bit.ly/x")
    assert s["level"] == "HIGH"
    assert smishing_score("see you at 5pm")["level"] == "LOW"
