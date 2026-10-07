"""SentinelLearn CLI: learn / scan / trending / watch. Beginner-friendly, offline-first."""
import argparse
import csv
import os
import time
from dotenv import load_dotenv

def _load_cfg(path="config.yaml"):
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def cmd_learn(_args):
    from src.learn.lessons import print_lessons
    print("=== SentinelLearn: defensive basics ===")
    print_lessons()
    print("\nNext: python main.py scan --auth data/sample_auth.log --web data/sample_web.log --urls data/sample_urls.csv")

def _read_lines(path):
    with open(path, errors="ignore") as f:
        return [l.rstrip("\n") for l in f if l.strip()]

def cmd_scan(args):
    from src.detectors.brute_force import detect_brute_force
    from src.detectors.web_attacks import detect_web_attacks
    from src.detectors.phishing import score_url
    from src.ai.explainer import explain
    from src.alerts.email_alert import send_alert
    cfg = _load_cfg(args.config)
    det = cfg.get("detection", {})
    findings = []
    if args.auth:
        lines = _read_lines(args.auth)
        findings += detect_brute_force(lines, threshold=int(det.get("brute_force_threshold", 5)))
    if args.web:
        findings += detect_web_attacks(_read_lines(args.web))
    if args.urls:
        with open(args.urls, errors="ignore") as f:
            for row in csv.DictReader(f):
                u = (row.get("url") or "").strip()
                if u:
                    s = score_url(u)
                    if s["level"] in ("HIGH", "MEDIUM"):
                        findings.append({"type": "phishing", "severity": s["level"], **s,
                                         "title": f"Phishing {s['level']} ({s['score']}): {u}"})
    if not findings:
        print("No findings. Clean (or thresholds high).")
        return
    highs = [f for f in findings if f.get("severity") == "HIGH"]
    from src.scoring.risk import score_findings
    risk = score_findings(findings)
    print(f"Found {len(findings)} issue(s), {len(highs)} HIGH. Risk {risk['score']}/100 ({risk['level']}) — {risk['action']}\n")
    for f in findings:
        print("=" * 70)
        print(explain(f))
    if highs and not args.no_alert:
        body = "\n".join(f"- {f['title']}" for f in highs)
        send_alert(f"[SentinelLearn] {len(highs)} HIGH finding(s)", body)

def cmd_trending(args):
    from src.intel.trending import fetch_trending
    items, mode = fetch_trending(top=args.top, cache_file="data/kev_cache.json")
    print(f"Trending exploited vulns (source=CISA KEV, mode={mode}):")
    for it in items:
        print(f"- {it['cveID']} | {it.get('vendorProject','')} {it.get('product','')} | {it.get('vuln','')} | added {it.get('dateAdded','')}")

def cmd_watch(args):
    from src.detectors.brute_force import detect_brute_force
    from src.detectors.web_attacks import detect_web_attacks
    from src.ai.explainer import explain
    from src.alerts.email_alert import send_alert
    print(f"Watching {args.file} every {args.interval}s — simulates victim-device monitoring. Ctrl+C to stop.")
    seen = set()
    while True:
        try:
            lines = _read_lines(args.file)
        except FileNotFoundError:
            print(f"File not found: {args.file}")
            return
        findings = detect_brute_force(lines) + detect_web_attacks(lines)
        fresh = [f for f in findings if f["title"] not in seen]
        for f in fresh:
            seen.add(f["title"])
            print("!" * 20, "NEW", "!" * 20)
            print(explain(f))
            if f.get("severity") == "HIGH":
                send_alert(f"[SentinelLearn WATCH] {f['title']}", explain(f))
        time.sleep(args.interval)

def main():
    load_dotenv()
    ap = argparse.ArgumentParser(description="SentinelLearn — beginner defensive SOC lab")
    ap.add_argument("--config", default="config.yaml")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("learn", help="beginner lessons")
    s = sub.add_parser("scan", help="scan logs/urls (offline)")
    s.add_argument("--auth", default="data/sample_auth.log")
    s.add_argument("--web", default="data/sample_web.log")
    s.add_argument("--urls", default="data/sample_urls.csv")
    s.add_argument("--no-alert", action="store_true")
    t = sub.add_parser("trending", help="trending exploited vulns (caches offline)")
    t.add_argument("--top", type=int, default=10)
    w = sub.add_parser("watch", help="monitor a log file, email on HIGH")
    w.add_argument("--file", default="data/sample_auth.log")
    w.add_argument("--interval", type=int, default=15)
    sub.add_parser("test-email", help="verify Gmail/SMTP wiring (dry-run if unset)")
    args = ap.parse_args()
    if args.cmd == "test-email":
        from src.alerts.email_alert import test_email
        print(test_email())
        return
    {"learn": cmd_learn, "scan": cmd_scan, "trending": cmd_trending, "watch": cmd_watch}[args.cmd](args)

if __name__ == "__main__":
    main()
