"""Enterprise risk scoring: 0-100 from findings. Simple, explainable, offline."""
SEV_WEIGHTS = {"HIGH": 25, "MEDIUM": 10, "LOW": 3}

def score_findings(findings: list[dict]) -> dict:
    total = sum(SEV_WEIGHTS.get(str(f.get("severity", "LOW")).upper(), 3) for f in findings)
    score = min(100, total)
    highs = sum(1 for f in findings if str(f.get("severity")).upper() == "HIGH")
    meds = sum(1 for f in findings if str(f.get("severity")).upper() == "MEDIUM")
    if score >= 75 or highs >= 3:
        level, action = "CRITICAL", "Isolate + patch now, alert SOC lead."
    elif score >= 40 or highs >= 1:
        level, action = "HIGH", "Triage today, block IOCs, review logs."
    elif score >= 15:
        level, action = "MEDIUM", "Review this week, harden configs."
    else:
        level, action = "LOW", "Monitor, keep patches current."
    return {"score": score, "level": level, "action": action,
            "counts": {"total": len(findings), "high": highs, "medium": meds}}
