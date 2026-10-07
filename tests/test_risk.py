from src.scoring.risk import score_findings

def test_risk_critical():
    fs = [{"severity": "HIGH"}] * 4
    r = score_findings(fs)
    assert r["score"] == 100 and r["level"] == "CRITICAL"

def test_risk_low_empty():
    assert score_findings([])["level"] == "LOW"
