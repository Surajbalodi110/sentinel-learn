# SentinelLearn — AI SOC Analyst Lab (beginner-friendly, defensive only)

Learn defensive cybersecurity *by doing*, with AI explanations. Protect a small enterprise / home lab.

## Why this is resume-worthy
- **Defensive security:** log analysis (brute-force, SQLi/XSS), phishing URL heuristics, MITRE ATT&CK mapping
- **AI usage:** hybrid explainer — offline rule-based templates + optional LLM (OpenAI-compatible) for richer coaching. Works with no internet, upgrades with internet.
- **Enterprise value:** trending threat intel (CISA KEV, no key), risk scoring, email alerts on high-severity events on a watched device/log
- **Beginner-friendly:** `learn` mode teaches each finding in plain English + fix steps

## Quickstart (Windows)
```
cd sentinel-learn
pip install -r requirements.txt
copy .env.example .env
# edit .env only if you want real email alerts + LLM

# 1. Learn
python main.py learn

# 2. Scan sample logs (100% offline)
python main.py scan --auth data/sample_auth.log --web data/sample_web.log --urls data/sample_urls.csv

# 3. Trending threats (online, caches for offline use)
python main.py trending --top 10

# 4. Watch a "victim device" log file and email on high severity
python main.py watch --file data/sample_auth.log --interval 15

# 5. Verify Gmail wiring (dry-run if .env unset)
python main.py test-email

# 6. Dashboard with risk score (new)
streamlit run dashboard.py
# Tabs: Analyze (risk 0-100) | Learn (lessons+quiz) | AI Tutor (offline chatbot) | Resources (MITRE/CERT-In in-tool)
```

## Email alerts (Gmail)
Set in `.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASS=xxxx-xxxx-xxxx-xxxx (16-char App Password, not login password)
ALERT_TO=you@gmail.com
```
Get App Password: Google Account > Security > turn ON 2-Step Verification > App passwords > Mail > copy 16 chars.
Test: `python main.py test-email`. If unset, alerts print as `[DRY-RUN]` — still demoable offline.

## AI explainer
- No key: uses built-in coaching templates (offline).
- With key: sets `OPENAI_API_KEY` + optional `OPENAI_MODEL` (default `gpt-4o-mini`) for deeper explanations. Falls back to offline if no internet.

## Project map
```
main.py                  CLI: learn / scan / trending / watch / test-email
dashboard.py             Streamlit UI: risk score 0-100 + findings + AI coach + trending
src/scoring/risk.py      enterprise risk scoring (HIGH=25, MED=10, LOW=3, cap 100)
src/detectors/           brute_force.py, web_attacks.py, phishing.py (pure Python, offline)
src/intel/trending.py    CISA KEV fetch + cache (data/kev_cache.json)
src/alerts/email_alert.py SMTP alerts with dry-run fallback
src/ai/explainer.py      hybrid offline + LLM explainer
src/learn/lessons.py     beginner lessons mapped to MITRE ATT&CK
data/sample_*            safe synthetic logs for practice
tests/                   pytest sanity checks
```

## Deploy publicly (free)
1. Push this folder to a **public GitHub repo**.
2. Go to **share.streamlit.io** → New app → pick repo/branch → main file `dashboard.py` (use path `sentinel-learn/dashboard.py` if repo root is the parent) → Deploy.
3. App settings → **Secrets**: paste `.streamlit/secrets.toml.example` values (SMTP for mail alerts + feedback-to-email).
4. Share the URL on LinkedIn/README; Google indexes public Community Cloud apps — post the link + a demo GIF for discovery.
Caveats: Ollama local AI is unavailable in cloud (built-in tutor answers apply); `data/progress.json` + `data/feedback.jsonl` are **ephemeral** in cloud — set `FEEDBACK_ENDPOINT` (free Formspree/Basin form URL) and/or SMTP so feedback reaches you.

## Resume bullets (copy-paste)
- Built offline-first Python SOC lab detecting brute-force, web injection, and phishing with heuristic engines and MITRE ATT&CK mapping
- Integrated hybrid AI explainer (template fallback + LLM API) to coach beginners on triage and remediation
- Added live threat intel (CISA KEV, no API key) with disk caching for offline use and SMTP email alerting for high-severity endpoint events

## Safety
Defensive only. Sample logs are synthetic. Never attack systems you don't own. This tool only *detects* patterns in logs/URLs you give it.
