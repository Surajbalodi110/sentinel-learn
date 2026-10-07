from src.learn.chatbot import offline_answer

def test_aaa():
    assert "Authentication" in offline_answer("What is AAA")

def test_cia():
    assert "Confidentiality" in offline_answer("explain CIA triad")

def test_ports():
    assert "3389" in offline_answer("what is RDP port")

def test_pyramid_and_siem():
    assert "Pyramid of Pain" in offline_answer("What is the Pyramid of Pain")
    assert "Splunk" in offline_answer("what is splunk")
    assert "T1110" in offline_answer("explain TTP")

def test_typos_and_tool_questions():
    assert "ransomware" in offline_answer("what is ransomeware").lower()
    assert "Phishing" in offline_answer("is this fishing link safe") or "phish" in offline_answer("is this fishing link safe").lower()
    tool = offline_answer("how do I use the analyze tab")
    assert "ANALYZE" in tool
    sms = offline_answer("analyze this sms text")
    assert "ANALYZE tab detects" not in sms

def test_fallback_suggests_never_refuses():
    r = offline_answer("blorpt quantum zebra")
    assert "out of scope" not in r.lower()
    assert "did you mean" in r.lower() or "Try asking" in r or "defensive-security" in r

def test_brute_force_intact():
    assert "T1110" in offline_answer("what is brute force")

def test_fallback_still_generic():
    assert "defensive-security" in offline_answer("xyzzy blorpt quantum")

def test_random_questions():
    from src.learn.chatbot import offline_answer as a
    assert "video call" in a("got a CBI video call, am I arrested")
    assert "1930" in a("someone asked my OTP")
    assert "VPN" in a("is public wifi safe")
    assert "white-hat" in a("what is ethical hacking")
    assert "1930" in a("where do I report fraud")
    assert "3-2-1" in a("how should I backup")

def test_every_answer_has_source():
    from src.learn.chatbot import KB
    missing = [keys[0] for keys, ans in KB if "http" not in ans]
    assert not missing, f"answers without source link: {missing}"
