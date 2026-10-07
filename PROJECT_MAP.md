# SentinelLearn — Project Map & Knowledge Base

> Everything lives under: `C:\Users\Iamsi\Documents\Default Project\sentinel-learn\`
> Run from that folder. Tests: 80 passing (`python -m pytest tests -q`).

## 1. Where the tool lives on your PC

| What | Path | Notes |
|---|---|---|
| Web app (everything visual) | `dashboard.py` (~2,700 lines) | All 13 pages, theme, navbar, tutor, games wiring |
| CLI (automation) | `main.py` | `learn / scan / trending / watch / test-email` |
| Python deps | `requirements.txt` | streamlit, plotly, pypdf, Pillow, httpx, pytest… |
| Tool branding | `src/branding.py` | Creator name, tool name, tagline (edit here) |
| Images | `assets/` | `logo.png` (+ crisp `logo_large.png`), `tutor.png`, `home_*.png`, fallback SVGs |
| Sample attack data | `data/sample_auth.log`, `data/sample_web.log`, `data/sample_urls.csv` | Safe fakes for practice |
| Your dev notes | `README.md` | Setup, deploy runbook, resume bullets |

## 2. Config files (the knobs)

| File | Purpose | Committed? |
|---|---|---|
| `.env` (you create from `.env.example`) | SMTP mail, `OPENAI_*`, `OLLAMA_*`, `FEEDBACK_ENDPOINT` | NEVER (gitignored) |
| `.env.example` | Template of every supported variable | Yes |
| `config.yaml` | Detection thresholds, watch interval, KEV URL | Yes |
| `.streamlit/config.toml` | Production: hides tracebacks from users | Yes |
| `.streamlit/secrets.toml.example` | Template for Streamlit Cloud Secrets | Yes (template only) |

## 3. Runtime data (generated while using it — all gitignored)

| File | What it holds | Survives cloud? |
|---|---|---|
| `data/users.db` | Accounts (PBKDF2 hashes), sessions, per-user progress | NO (use Postgres for public) |
| `data/progress.json` | Guest progress cache | NO |
| `data/feedback.jsonl` | Feedback entries (ref, name, contact, texts) | NO (needs endpoint/email) |
| `data/kev_cache.json` | Cached CISA KEV feed for offline use | Rebuilt automatically |

## 4. Every page → its code

| Page (navbar) | Code in `dashboard.py` | Engine behind it |
|---|---|---|
| Home | `if nav == "home"` | Session stats + jump buttons |
| Learn (20 rooms) | `if nav == "learn"` | `src/learn/curriculum.py` (rooms) + `levels.py` (coaching+diagrams) + `depth.py` + `stories.py` + `games.py` + `diagrams.py` |
| Certificates | `if nav == "certs"` | `src/certs/make.py` (PNG + LinkedIn block + resume builder) |
| AI Tutor | `if nav == "tutor"` + popup `tutor_panel()` | `src/learn/chatbot.py` (KB) → `src/ai/local_llm.py` (Ollama) → OpenAI |
| Arcade | `if nav == "arcade"` | `src/learn/arcade.py` (5 JS games) |
| Resources | `if nav == "resources"` | `src/learn/resources.py` |
| Analyze | `if nav == "analyze"` | `detectors/` + `scoring/risk.py` + `scoring/coverage.py` |
| Simulation | `if nav == "sim"` | `src/sim/scenario.py` + `src/sim/library.py` (6 sims) |
| File Check | `if nav == "files"` | `malpdf.py`, `imagecheck.py`, `apkcheck.py` |
| OSINT | `if nav == "osint"` | `src/osint/lookup.py` (DNS/RDAP/GitHub/Gravatar/plate/SMS/photo) |
| Guide | `if nav == "guide"` | Built-in how-to + `src/feedback/store.py` form |
| About | `if nav == "about"` | Stats + scoring explainer |
| Account (avatar only) | `if nav == "account"` | `src/auth/store.py` + `src/gamify.py` (XP/streaks/badges) |

## 5. Key flows (how things connect)

- **Ask a question:** Tutor tab/popup → `answer()` tries Ollama (`local_llm.py`) → falls back to keyword KB (`chatbot.py`) with typo tolerance + suggestions → optional OpenAI enrichment. Streaming renders token-by-token.
- **Login that survives page jumps:** nav links are full reloads, so sessions ride in `?s=TOKEN` (sha256-stored, 30-day expiry). Progress merges account ←→ guest on login/register and saves every run.
- **Room completion:** quiz 5/5 or Mark complete → `done_lessons` + `+100 XP` → certificate PNG unlocks (per-room instantly, final at 20/20).
- **Feedback:** validate → append `feedback.jsonl` → POST `FEEDBACK_ENDPOINT` if set → email owner via SMTP if set.
- **Theme:** `?theme=` param + `body.dark` class; toggle lives inside the hero.

## 6. How to work on it safely

1. `cd sentinel-learn` (always run from here — all relative paths assume it)
2. Change code → `python -m py_compile <file>` → `python -m pytest tests -q` (must stay green)
3. Run UI: `streamlit run dashboard.py` → hard refresh (`Ctrl+Shift+R`) after CSS/JS changes
4. New lesson content needs no code: `curriculum.py` / `levels.py` / `stories.py` / `depth.py` are data
5. Never commit `.env`, `users.db`, `progress.json`, `feedback.jsonl` (already ignored)

## 7. Phase-one deploy checklist

- [ ] `git init` here (or move folder), public GitHub repo, push (check `git status` shows no secrets)
- [ ] share.streamlit.io → main file `dashboard.py` → Deploy
- [ ] Secrets: SMTP_* + FEEDBACK_TO (+ FEEDBACK_ENDPOINT) so feedback survives
- [ ] Accept: no Ollama in cloud (built-in tutor covers), SQLite = single-operator demo
- [ ] Share URL on LinkedIn + README badge; ask pros to use Guide → Feedback
- [ ] Later (phase two): Postgres auth, timed simulations scoring server-side, PWA
