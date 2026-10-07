"""SentinelLearn — professional Cyberguru header + global tutor popup + interactive SOC."""
import os
import streamlit as st
import streamlit.components.v1 as components

import os as _os
_page_icon = "assets/logo.png" if _os.path.exists("assets/logo.png") else (
    "assets/cyberguru_logo.svg" if _os.path.exists("assets/cyberguru_logo.svg") else "🛡️")
st.set_page_config(page_title="SentinelLearn by Cyberguru", page_icon=_page_icon, layout="wide")

from src.detectors.brute_force import detect_brute_force
from src.detectors.web_attacks import detect_web_attacks
from src.detectors.phishing import score_url
from src.scoring.risk import score_findings
from src.ai.explainer import explain
from src.learn.curriculum import COURSE
from src.learn.resources import RESOURCES
from src.learn.chatbot import answer as tutor_answer
from src.branding import CREATOR_NAME, TOOL_NAME, TAGLINE, BUILDER_LINE

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False

MITRE_LINKS = {
    "brute_force": "https://attack.mitre.org/techniques/T1110/",
    "sqli": "https://attack.mitre.org/techniques/T1190/",
    "xss": "https://attack.mitre.org/techniques/T1189/",
    "path_traversal": "https://attack.mitre.org/techniques/T1083/",
    "phishing": "https://attack.mitre.org/techniques/T1566/002/",
}

for k, v in {"extra_auth": [], "extra_web": [], "extra_urls": [],
             "reviewed": set(), "hist": [("bot", "Namaste! I'm the Cyberguru tutor — ask any cybersecurity question, e.g. 'what is ransomware?' or 'SOC career roadmap?'")],
             "lesson_idx": 0, "last_findings": []}.items():
    st.session_state.setdefault(k, v)

# restore progress wiped by full-page nav reloads (single local profile)
try:
    from src.state.store import load as _load_progress, save as _save_progress
    _saved = _load_progress()
    if _saved:
        st.session_state.hist = [tuple(x) for x in _saved.get("hist", [])][-50:] or st.session_state.hist
        st.session_state.done_lessons = set(_saved.get("done_lessons", []))
        st.session_state.reviewed = set(_saved.get("reviewed", []))
        st.session_state.lesson_idx = int(_saved.get("lesson_idx", 0) or 0)
        st.session_state.last_findings = _saved.get("last_findings", []) or []
        if _saved.get("room_applied"):
            st.session_state["room_applied"] = _saved["room_applied"]
        if isinstance(_saved.get("sim_best"), dict):
            st.session_state["sim_best"] = _saved["sim_best"]
        if _saved.get("user_name"):
            st.session_state["user_name"] = _saved["user_name"]
except Exception:
    pass

# ---------- docked tutor panel (opens from the bottom-right button) ----------
def _tutor_respond(q: str):
    """Queue a reply; streaming happens in-place above the input on rerun."""
    st.session_state.hist.append(("user", q))
    st.session_state["pending_q"] = q
    st.rerun()

def _tutor_stream_here():
    """Stream the pending reply exactly where this is called, then normalize."""
    import html as _h
    from src.learn.chatbot import answer_stream, answer as _ans
    q = st.session_state.pop("pending_q", None)
    if not q:
        return
    box = st.empty()
    box.markdown(f'<div class="cb-bot">{_tutor_icon(22)} <span class="tdots"><span>.</span><span>.</span><span>.</span></span></div>', unsafe_allow_html=True)
    full = ""
    try:
        for chunk in answer_stream(q):
            full += chunk
            box.markdown(f'<div class="cb-bot">{_tutor_icon(22)} {_h.escape(full)}▍</div>', unsafe_allow_html=True)
    except Exception:
        full = ""
    if full.strip():
        st.session_state.hist.append(("bot", full))
    else:
        st.session_state.hist.append(("bot", _ans(q)))
    st.rerun()

_NAV = [
    ("home", "Home", '<path d="M3 10.5L12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M9 21v-6h6v6"/>'),
    ("learn", "Learn", '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>'),
    ("certs", "Certificates", '<circle cx="12" cy="9" r="5"/><path d="M8.5 13.5L7 21l5-2.5L17 21l-1.5-7.5"/>'),
    ("tutor", "AI Tutor", '<rect x="5" y="8" width="14" height="11" rx="3"/><circle cx="9.5" cy="13" r="1" fill="currentColor"/><circle cx="14.5" cy="13" r="1" fill="currentColor"/><line x1="12" y1="8" x2="12" y2="4"/><circle cx="12" cy="3" r="1" fill="currentColor"/>'),
    ("arcade", "Arcade", '<line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/><circle cx="15" cy="11" r="1" fill="currentColor"/><circle cx="17.5" cy="13.5" r="1" fill="currentColor"/><path d="M17.3 5H6.7a4.7 4.7 0 0 0-4.6 5.6l1 5A4 4 0 0 0 7 19l1.7-2.5h6.6L17 19a4 4 0 0 0 3.9-3.4l1-5A4.7 4.7 0 0 0 17.3 5z"/>'),
    ("resources", "Resources", '<circle cx="12" cy="12" r="9"/><line x1="3" y1="12" x2="21" y2="12"/><path d="M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18z"/>'),
    ("analyze", "Analyze", '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.6" y2="16.6"/>'),
    ("sim", "Simulation", '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1" fill="currentColor"/><line x1="12" y1="1" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="1" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="23" y2="12"/>'),
    ("files", "File Check", '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'),
    ("osint", "OSINT", '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1" fill="currentColor"/>'),
    ("about", "About", '<circle cx="12" cy="12" r="9"/><line x1="12" y1="11" x2="12" y2="16"/><circle cx="12" cy="8" r="1" fill="currentColor"/>'),
    ("guide", "Guide", '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 0 1 2.5-2.5A2.5 2.5 0 0 1 14.5 9c0 1.5-2.5 2-2.5 3.5"/><circle cx="12" cy="17" r="1" fill="currentColor"/>'),
    ("account", "Account", '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>'),
]

def _render_navbar(active: str, theme: str = "light") -> None:
    from src.gamify import streak as _streak
    _u = st.session_state.get("user")
    if _u:
        try:
            from src.auth.store import load_progress as _lp
            _ap = _lp(_u["id"]) or {}
            _xp = int(_ap.get("xp", 0) or 0)
            _cur, _ = _streak(_ap.get("days", []) or [])
        except Exception:
            _xp, _cur = 0, 0
        _initial = (_u.get("name", "?") or "?")[:1].upper()
        _right = (f"<span class='nv-stat'>🔥 {_cur}</span>"
                  f"<span class='nv-stat'>◆ {_xp}</span>"
                  f"<a class='nvat' href='{_link('account')}' target='_self'>{_initial}</a>")
    else:
        _right = (f"<a class='navbtn' href='{_link('account')}' target='_self'>Log In</a>"
                  f"<a class='navbtn navbtn-free' href='{_link('account')}' target='_self'>Join FREE</a>")
    links = []
    for key, label, icon in _NAV:
        if key == "account":
            continue  # profile lives behind the avatar, not a tab
        cls = "nl active" if key == active else "nl"
        links.append(
            f'<a class="{cls}" href="{_link(key)}" target="_self">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{icon}</svg><span>{label}</span></a>')
    st.markdown(
        "<nav class='topnav'><div class='nl-wrap'>" + "".join(links) +
        f"<span class='nl-status'>{_right}</span></div></nav>",
        unsafe_allow_html=True)

_NAV_KEYS = [k for k, _, _ in _NAV]
_nav = st.query_params.get("nav", "home")
nav = _nav if _nav in _NAV_KEYS else "home"
_theme = st.query_params.get("theme", "light")
_dark = (_theme == "dark")

def _link(dest: str, theme: str | None = None) -> str:
    """Internal link preserving theme + login session across full reloads."""
    t = theme if theme is not None else _theme
    s = st.session_state.get("session_token", "")
    url = f"?nav={dest}&theme={t}"
    return url + (f"&s={s}" if s else "")

# restore login from URL session token (page switches do full reloads)
try:
    from src.auth.store import check_session as _check_session
    _tok = st.query_params.get("s", "")
    if _tok and not st.session_state.get("user"):
        _u = _check_session(_tok)
        if _u:
            st.session_state.user = _u
            st.session_state.session_token = _tok
    elif not _tok:
        st.session_state.pop("user", None)
        st.session_state.pop("session_token", None)
except Exception:
    pass

# load account progress on fresh sessions + daily streak touch
try:
    from src.auth.store import load_progress as _lp2
    from src.gamify import XP_DAILY, award as _award
    import datetime as _dt
    _u0 = st.session_state.get("user")
    if _u0 and not st.session_state.get("progress_loaded"):
        _ap = _lp2(_u0["id"]) or {}
        if _ap:
            st.session_state.done_lessons = set(_ap.get("done_lessons", []) or [])
            st.session_state.reviewed = set(_ap.get("reviewed", []) or [])
            st.session_state.lesson_idx = int(_ap.get("lesson_idx", 0) or 0)
            if _ap.get("last_findings"):
                st.session_state.last_findings = _ap["last_findings"]
            if isinstance(_ap.get("sim_best"), dict):
                st.session_state.sim_best = _ap["sim_best"]
            if _ap.get("user_name"):
                st.session_state["user_name"] = _ap["user_name"]
        _days = set(_ap.get("days", []) or [])
        _today = _dt.date.today().isoformat()
        if _today not in _days:
            from src.auth.store import save_progress as _sp2
            _days.add(_today)
            _ap["days"] = sorted(_days)
            _award(_ap, XP_DAILY)
            _sp2(_u0["id"], _ap)
            st.toast(f"Daily visit +{XP_DAILY} XP 🔥")
        st.session_state.progress_loaded = True
except Exception:
    pass

def tutor_panel():
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;
      background:linear-gradient(135deg,#0B1526,#0e7c6b);
      margin:-1rem -1rem 0.8rem -1rem;padding:12px 14px;border-radius:12px 12px 0 0;color:#fff">
      <div>{_tutor_img(34)}</div>
      <div><div style="font-weight:700">Cyberguru Tutor</div>
      <div style="font-size:.72rem;opacity:.85"><span class="dot"></span>online — cybersecurity Q&A</div></div>
    </div>
    """, unsafe_allow_html=True)
    chips = ["What is ransomware?", "Explain MFA", "What is CERT-In?",
             "SOC career roadmap?", "How to fix SQLi?"]
    r1 = st.columns(3)
    for i, ch in enumerate(chips[:3]):
        if r1[i].button(ch, key=f"pp_chip{i}"):
            _tutor_respond(ch)
    r2 = st.columns(2)
    for i, ch in enumerate(chips[3:]):
        if r2[i].button(ch, key=f"pp_chip{i+3}"):
            _tutor_respond(ch)
    import html as _h
    for role, msg in st.session_state.hist[-6:]:
        safe = _h.escape(msg)
        if role == "user":
            st.markdown(f'<div class="cb-user">{safe}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="cb-bot">{_tutor_icon(22)} {safe}</div>', unsafe_allow_html=True)
    st.caption("Full history lives in the AI Tutor tab.")
    _tutor_stream_here()
    with st.form("pp_form", clear_on_submit=True):
        q = st.text_input("Ask anything…", placeholder="e.g. what is zero trust?")
        send = st.form_submit_button("Send ➤", type="primary", use_container_width=True)
    if send and q:
        _tutor_respond(q)

# ---------- sleek hero banner + cool theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
.hero { position: relative; overflow: hidden; background:
  radial-gradient(600px 200px at 85% -20%, #00e5cc33, transparent),
  radial-gradient(500px 220px at 10% 120%, #7c3aed33, transparent),
  linear-gradient(135deg,#0B1526 0%,#12324a 55%,#0b3f3a 100%);
  border: 1px solid #ffffff1f; border-radius: 16px; padding: 16px 20px; color: white;
  margin-bottom: 12px; box-shadow: 0 8px 28px rgba(0,0,0,.3); font-family:'Space Grotesk',sans-serif; }
.hero::before { content:""; position:absolute; inset:0;
  background-image: linear-gradient(#ffffff09 1px, transparent 1px),
  linear-gradient(90deg, #ffffff09 1px, transparent 1px);
  background-size: 28px 28px; mask-image: radial-gradient(ellipse at 30% 20%, black 30%, transparent 75%); }
.hero-inner { position: relative; display: flex; align-items: center; gap: 18px; flex-wrap: wrap; }
.theme-link { margin-left: auto; align-self: center; color: #fff !important; text-decoration: none !important;
  border: 1px solid #ffffff55; border-radius: 999px; padding: 7px 16px; font-size: .8rem; font-weight: 600;
  white-space: nowrap; background: #ffffff14; backdrop-filter: blur(4px); }
.theme-link:hover { background: #ffffff2a; color: #fff !important; }
.hero svg.logo { width: 72px; height: 72px; filter: drop-shadow(0 0 12px #00e5cc88); flex-shrink: 0; }
.hero h1 { margin: 0; font-size: 1.5rem; letter-spacing: .5px;
  background: linear-gradient(90deg,#fff,#7ef9e3); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero h1 span { font-size: 1rem; font-weight: 400; opacity: .75; -webkit-text-fill-color: #9fb3c8; }
.hero p { margin: 4px 0 0; opacity: .85; font-size: .92rem; }
.pill { display:inline-block; background:#ffffff14; border:1px solid #ffffff2e; font-size:.74rem;
  padding:3px 12px; border-radius:999px; margin: 8px 6px 0 0; backdrop-filter: blur(4px); }
.dot { display:inline-block; width:9px; height:9px; border-radius:50%; background:#00e676;
  box-shadow:0 0 10px #00e676; animation: pulse 1.8s infinite; margin-right:6px; }
@keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:.35 } }
.card { background:#fff; border:1px solid #e6e8ec; border-top:3px solid #00bfa6;
  border-radius:14px; padding:14px; margin-bottom:10px; box-shadow: 0 4px 14px rgba(0,0,0,.06); }
.footer { text-align:center; opacity:.75; padding:22px 0 8px; font-size:.85rem; }
/* home card images: identical frames, whole image visible (no crop) */
.home-img { width: 100%; height: 200px; object-fit: contain; object-position: center;
  border-radius: 10px; margin-top: 8px; background: #eef1f6; }
body.dark .home-img { background: #101f31; }
/* helper iframes collapse by default; the pin script sizes arcade frames via inline styles */
div[data-testid="stElementContainer"]:has(iframe[srcdoc]) { min-height: 0; overflow: hidden; margin: 0; padding: 0; }
/* rich sitemap footer */
.sitefooter { background: linear-gradient(135deg,#0B1526 0%,#16324a 60%,#0e4d44 100%);
  border: 1px solid #ffffff1f; border-radius: 16px; color: #c8d3e0;
  padding: 26px 28px 14px 28px; margin-top: 26px; box-shadow: 0 8px 28px rgba(0,0,0,.3); }
.sf-grid { display: grid; grid-template-columns: repeat(4, 1fr) 1.4fr; gap: 18px; }
.sitefooter h4 { color: #fff; margin: 0 0 10px 0; font-size: .95rem; }
.sitefooter a { display: block; color: #9fb3c8 !important; text-decoration: none !important;
  font-size: .83rem; padding: 3px 0; }
.sitefooter a:hover { color: #00e5cc !important; }
.sf-note { display: block; font-size: .78rem; opacity: .75; padding: 3px 0; }
.sf-brand p { font-size: .83rem; }
.sf-bottom { text-align: center; font-size: .78rem; opacity: .7; border-top: 1px solid #ffffff1a;
  margin-top: 16px; padding-top: 12px; }
@media (max-width: 768px) { .sf-grid { grid-template-columns: 1fr 1fr; } }
/* theme switch overlaid inside the hero (right side) */
div[data-testid="stElementContainer"]:has(> #theme-toggle-slot),
div[data-testid="stElementContainer"]:has(> #theme-toggle-slot) + div { height: 0; overflow: visible; }
div[data-testid="stElementContainer"]:has(> #theme-toggle-slot) + div [data-testid="stToggle"] {
  margin-top: -104px !important; position: relative; z-index: 5;
  margin-left: auto; max-width: 150px; }
div[data-testid="stElementContainer"]:has(> #theme-toggle-slot) + div [data-testid="stToggle"] label { color: #fff !important; }
div[data-testid="stElementContainer"]:has(> #theme-toggle-slot) { height: 0; overflow: visible; }
/* THM-style top navbar */
.topnav { background: linear-gradient(135deg,#0B1526 0%,#16324a 60%,#0e4d44 100%);
  border: 1px solid #ffffff1f; border-radius: 16px; margin: 0 0 14px 0;
  box-shadow: 0 8px 28px rgba(0,0,0,.3); }
.nl-wrap { display: flex; align-items: center; gap: 4px; overflow-x: auto; padding: 0 16px; }
.nl { display: flex; align-items: center; gap: 8px; color: #9fb3c8 !important;
  text-decoration: none !important;
  font-weight: 600; font-size: .88rem; padding: 14px 14px; border-bottom: 3px solid transparent; white-space: nowrap; }
.nl svg { width: 20px; height: 20px; }
.nl:hover { color: #ffffff !important; background: #ffffff0d; }
.nl.active { color: #00e5cc !important; border-bottom-color: #00e5cc; }
.nl-status { margin-left: auto; display: flex; align-items: center; gap: 8px; color: #9fb3c8;
  font-size: .78rem; white-space: nowrap; padding-left: 12px; }
.navbtn { color: #eaf2f8 !important; text-decoration: none !important; border: 1px solid #00e5cc;
  border-radius: 8px; padding: 6px 14px !important; font-weight: 700; font-size: .8rem; white-space: nowrap; }
.navbtn-free { background: linear-gradient(90deg,#0e7c6b,#00bfa6) !important; border-color: #00e5cc !important; color: #fff !important; }
.nv-stat { font-weight: 700; color: #eaf2f8; font-size: .82rem; white-space: nowrap; }
.nvat { display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px;
  border-radius: 50%; background: linear-gradient(135deg,#0e7c6b,#00e5cc); color: #0B1526 !important;
  font-weight: 800; text-decoration: none !important; border: 2px solid #00e5cc; }
/* live tutor: typing dots + pulsing avatar button */
.tdots span { display: inline-block; animation: tblink 1.2s infinite; font-weight: 700; }
.tdots span:nth-child(2) { animation-delay: .2s; }
.tdots span:nth-child(3) { animation-delay: .4s; }
@keyframes tblink { 0%, 60%, 100% { opacity: .2; } 30% { opacity: 1; } }
.fab-live { animation: fabPulse 2.6s infinite !important; }
@keyframes fabPulse { 0% { box-shadow: 0 0 0 0 rgba(0,229,204,.55), 0 8px 26px rgba(255,80,50,.45); }
  70% { box-shadow: 0 0 0 16px rgba(0,229,204,0), 0 8px 26px rgba(255,80,50,.45); }
  100% { box-shadow: 0 0 0 0 rgba(0,229,204,0), 0 8px 26px rgba(255,80,50,.45); } }
/* app backdrop + stat tiles */
div[data-testid="stAppViewContainer"] { background:
  radial-gradient(800px 300px at 90% -5%, #00e5cc14, transparent),
  radial-gradient(700px 320px at 5% 0%, #7c3aed12, transparent), #f5f7fa; }
.stat-grid { position:relative; display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-top:14px; }
.stat { background:#ffffff12; border:1px solid #ffffff26; border-radius:12px; padding:10px 12px; backdrop-filter: blur(4px); }
.stat b { font-size:1.25rem; display:block; }
.stat span { font-size:.72rem; opacity:.8; }
.kpi { border-radius:14px; padding:12px 14px; color:#fff; font-weight:700;
  box-shadow: 0 6px 16px rgba(0,0,0,.18); }
/* graphical definition cards */
.def { display: flex; gap: 12px; align-items: flex-start; background: #fff;
  border: 1px solid #e6e8ec; border-left: 6px solid #00bfa6; border-radius: 12px;
  padding: 12px 14px; margin: 8px 0; box-shadow: 0 3px 10px rgba(0,0,0,.05); }
.def .ic { font-size: 1.5rem; line-height: 1.2; }
.def b.t { display: block; font-size: .95rem; }
.def span.d { font-size: .83rem; opacity: .85; }
/* terminal-style code blocks */
div[data-testid="stCodeBlock"] { border-radius: 12px !important; overflow: hidden;
  border: 1px solid #0B1526 !important; box-shadow: 0 6px 18px rgba(0,0,0,.2) !important; }
div[data-testid="stCodeBlock"] pre { background: #0B1526 !important; }
div[data-testid="stCodeBlock"] code { color: #7ef9e3 !important; }
/* friendlier expanders + inputs */
div[data-testid="stExpander"] { border-radius: 12px !important; border: 1px solid #e6e8ec !important; }
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
  border-radius: 10px !important; }
div[data-testid="stMetric"] { background: #fff; border: 1px solid #e6e8ec;
  border-radius: 14px; padding: 10px 14px; box-shadow: 0 3px 10px rgba(0,0,0,.05); }
/* DARK MODE overrides */
body.dark div[data-testid="stAppViewContainer"] { background: #0B1526 !important; }
body.dark .stMarkdown, body.dark p, body.dark li, body.dark span { color: #d7e0ea; }
body.dark h1, body.dark h2, body.dark h3 { color: #ffffff !important; }
body.dark .card, body.dark .def, body.dark div[data-testid="stMetric"] {
  background: #16283d !important; border-color: #2a4358 !important; color: #d7e0ea; }
body.dark div[data-testid="stExpander"] { background: #16283d !important; border-color: #2a4358 !important; }
body.dark div[data-testid="stExpander"] p, body.dark div[data-testid="stExpander"] span { color: #d7e0ea; }
body.dark div[data-testid="stTextInput"] input, body.dark div[data-testid="stTextArea"] textarea {
  background: #101f31 !important; color: #eaf2f8 !important; border-color: #2a4358 !important; }
body.dark div[data-testid="stTable"] td, body.dark div[data-testid="stTable"] th { color: #d7e0ea; }
body.dark .cb-bot { background: #16283d; border-color: #2a4358; color: #d7e0ea; }
body.dark .sec-title { background: linear-gradient(90deg,#7ef9e3,#00e5cc);
  -webkit-background-clip: text; background-clip: text; }
/* dark: buttons, metrics, widgets must stay readable */
body.dark div[data-testid="stButton"] > button[kind="secondary"] {
  background: #16283d !important; color: #eaf2f8 !important; border: 1px solid #2a4358 !important; }
body.dark div[data-testid="stLinkButton"] a {
  background: #16283d !important; color: #7ef9e3 !important; border: 1px solid #2a4358 !important; }
body.dark div[data-testid="stMetric"] label, body.dark div[data-testid="stMetricValue"] > div { color: #eaf2f8 !important; }
body.dark div[data-testid="stMetric"] [data-testid="stMetricDelta"] { color: #9fb3c8 !important; }
body.dark div[data-testid="stWidgetLabel"] *, body.dark div[data-testid="stRadio"] div,
body.dark div[role="radiogroup"] label, body.dark div[data-testid="stCheckbox"] label,
body.dark div[data-testid="stSelectbox"] label, body.dark div[data-testid="stSlider"] label,
body.dark div[data-testid="stFileUploader"] label, body.dark div[data-testid="stTextArea"] label,
body.dark div[data-testid="stTextInput"] label, body.dark div[data-testid="stToggle"] label { color: #d7e0ea !important; }
body.dark div[data-testid="stCaptionContainer"], body.dark .stCaption { color: #9fb3c8 !important; }
body.dark a { color: #7ef9e3 !important; }
body.dark hr { border-color: #2a4358 !important; }
/* keep native light boxes readable: alerts + upload dropzone stay dark-on-light */
body.dark div[data-testid="stAlert"] p, body.dark div[data-testid="stAlert"] span,
body.dark div[data-testid="stAlert"] li, body.dark div[data-testid="stAlert"] div { color: #16202e !important; }
body.dark div[data-testid="stFileUploaderDropzone"] { background: #101f31 !important; border-color: #2a4358 !important; }
/* dark: SVG diagram text (legends, labels) must glow light */
body.dark svg text { fill: #eaf2f8 !important; }
/* dark: dropdown/select menus keep dark-on-light (never inherit page ink) */
body.dark div[data-baseweb="select"] > div { background: #101f31 !important; border-color: #2a4358 !important; }
body.dark div[data-baseweb="select"] div { color: #eaf2f8 !important; }
body.dark div[data-baseweb="menu"] * { color: #16202e !important; }
body.dark div[data-baseweb="menu"] [aria-selected="true"],
body.dark div[data-baseweb="menu"] [aria-selected="true"] * { color: #ffffff !important; }
.sec-title { font-weight:700; font-size:1.05rem; margin: 6px 0 10px;
  background: linear-gradient(90deg,#0B1526,#0e7c6b); -webkit-background-clip:text; background-clip:text; color:transparent; }
/* floating tutor button = the popover trigger after the anchor */
div[data-testid="stElementContainer"]:has(#fab-tutor-anchor) + div[data-testid="stElementContainer"] { height: 0; overflow: visible; }
div[data-testid="stElementContainer"]:has(#fab-tutor-anchor) + div [data-testid="stPopover"] button,
div:has(> #fab-tutor-anchor) + div [data-testid="stPopover"] button {
  position: fixed !important; bottom: 22px !important; right: 22px !important; left: auto !important;
  width: 62px !important; height: 62px !important; border-radius: 50% !important;
  font-size: 28px !important; z-index: 1000 !important; padding: 0 !important;
  background: linear-gradient(135deg,#0B1526,#0e7c6b) !important; border: 2px solid #00e5cc !important; color: #fff !important;
  box-shadow: 0 8px 26px rgba(0,229,204,.35) !important; }
div[data-testid="stElementContainer"]:has(#fab-tutor-anchor) + div [data-testid="stPopover"] button svg:not([width]),
div:has(> #fab-tutor-anchor) + div [data-testid="stPopover"] button svg:not([width]) { display: none !important; }
/* docked chat panel */
div[data-testid="stPopoverBody"] { width: 385px !important; max-width: 92vw !important;
  max-height: 70vh !important; overflow-y: auto !important; border-radius: 16px !important;
  border: 1px solid #e6e8ec !important; box-shadow: 0 16px 48px rgba(0,0,0,.3) !important;
  position: fixed !important; bottom: 96px !important; right: 22px !important;
  top: auto !important; left: auto !important; transform: none !important; z-index: 1001 !important; }
.cb-user { background: linear-gradient(135deg,#0e7c6b,#12324a); color: #fff;
  border-radius: 14px 14px 4px 14px; padding: 9px 12px; margin: 6px 0 6px 32px; font-size: .85rem; }
.cb-bot { background: #eef1f6; color: #16202e; border: 1px solid #dfe3ea;
  border-radius: 14px 14px 14px 4px; padding: 9px 12px; margin: 6px 32px 6px 0; font-size: .85rem; }
.fab-hint { position: fixed; bottom: 94px; right: 22px; z-index: 999; background: #0B1526; color: #fff;
  padding: 10px 14px; border-radius: 12px; font-size: .82rem; max-width: 245px; pointer-events: none;
  box-shadow: 0 8px 24px rgba(0,0,0,.35); border: 1px solid #00e5cc55;
  animation: fabHint 11s forwards; }
@keyframes fabHint { 0%,80% { opacity: 1; transform: translateY(0); } 100% { opacity: 0; transform: translateY(8px); visibility: hidden; } }
/* cool buttons + tabs (one theme: deep navy + teal) */
div[data-testid="stButton"] > button[kind="primary"] {
  background: linear-gradient(90deg,#0e7c6b,#00bfa6) !important; border: none !important;
  border-radius: 12px !important; font-weight: 700 !important; color: #fff !important;
  box-shadow: 0 6px 18px rgba(0,191,166,.4) !important; }
div[data-testid="stButton"] > button[kind="secondary"] { border-radius: 12px !important; font-weight: 600 !important; }
.stTabs [data-baseweb="tab"] { border-radius: 10px !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(90deg,#0B1526,#0e7c6b) !important; color: #fff !important; }
/* responsive */
img { max-width: 100%; height: auto; }
div[data-testid="stTable"], table { overflow-x: auto; }
.stTabs [data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap; }
div[data-testid="stPlotlyChart"] { width: 100%; }
@media (max-width: 768px) {
  div[data-testid="stElementContainer"]:has(> #theme-toggle-slot) + div [data-testid="stToggle"] { margin-top: 0 !important; max-width: none; }
  div[data-testid="stElementContainer"]:has(> #theme-toggle-slot) + div [data-testid="stToggle"] label { color: inherit !important; }
  .hero { padding: 18px; border-radius: 16px; }
  .hero h1 { font-size: 1.35rem !important; }
  .hero svg.logo { width: 52px; height: 52px; }
  .stat-grid { grid-template-columns: 1fr 1fr; }
  .fab-hint { right: 16px; max-width: 200px; font-size: .76rem; }
  .pill { font-size: .66rem; }
  .card { padding: 10px; }
  h1, h2, h3 { overflow-wrap: anywhere; }
  textarea, input { font-size: 16px !important; }
}
</style>
""", unsafe_allow_html=True)

def _asset(*names: str) -> str | None:
    """Absolute asset path that works regardless of Streamlit's working directory."""
    import os
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    for n in names:
        p = os.path.join(base, n)
        if os.path.exists(p):
            return p
    return None

def _logo_img(size: int = 72) -> str:
    """Real logo first (assets/logo.png), else built-in SVG shield."""
    import base64
    p = _asset("logo.png", "logo.jpg", "logo.jpeg")
    if p:
        with open(p, "rb") as fh:
            raw = fh.read()
        mime = "image/png" if raw[:8] == bytes([137, 80, 78, 71, 13, 10, 26, 10]) else "image/jpeg"
        b64 = base64.b64encode(raw).decode()
        return (f'<img src="data:{mime};base64,{b64}" width="{size}" height="{size}" '
                f'style="border-radius:14px;object-fit:cover;flex-shrink:0;'
                f'filter:drop-shadow(0 0 12px #00e5cc88)">')
    return _logo_svg()

def _page_icon() -> str:
    return _asset("logo.png", "logo.jpg", "logo.jpeg", "cyberguru_logo.svg") or "🛡️"

def _logo_svg() -> str:
    p = _asset("cyberguru_logo.svg")
    try:
        with open(p or "", encoding="utf-8") as f:
            svg = f.read()
        return svg.replace("<svg ", '<svg class="logo" width="72" height="72" ', 1)
    except Exception:
        return "🛡️"

def _home_art(name: str) -> str:
    """Home card illustration: assets/<name>.png (or .jpg) if you provide it, else nothing."""
    import base64
    p = _asset(f"{name}.png", f"{name}.jpg", f"{name}.jpeg")
    if not p:
        return ""
    with open(p, "rb") as fh:
        raw = fh.read()
    mime = "image/png" if raw[:8] == bytes([137, 80, 78, 71, 13, 10, 26, 10]) else "image/jpeg"
    return (f'<img class="home-img" src="data:{mime};base64,{base64.b64encode(raw).decode()}" >')

def _art_learn() -> str:
    return '''<svg viewBox="0 0 200 120" style="width:100%;height:auto;border-radius:10px">
<rect width="200" height="120" rx="10" fill="#e8f4f8"/>
<circle cx="168" cy="24" r="12" fill="#ffd66e"/>
<rect x="20" y="88" width="90" height="8" rx="3" fill="#8a5a3b"/>
<rect x="28" y="60" width="18" height="28" rx="2" fill="#0e7c6b"/>
<rect x="48" y="60" width="18" height="28" rx="2" fill="#12a48f"/>
<line x1="57" y1="66" x2="57" y2="82" stroke="#fff" stroke-width="2"/>
<polygon points="120,40 160,40 140,30" fill="#1f2937"/>
<rect x="132" y="40" width="16" height="10" fill="#1f2937"/>
<rect x="118" y="50" width="12" height="38" fill="#374151"/>
<rect x="150" y="98" width="34" height="6" rx="3" fill="#9aa7b5"/>
<rect x="60" y="92" width="20" height="14" rx="2" fill="#b5651d"/>
<path d="M70 92 q-8,-16 -2,-26 M70 92 q2,-14 10,-20 M70 92 q10,-10 16,-8" stroke="#2a9d8f" stroke-width="3" fill="none"/>
</svg>'''

def _art_analyze() -> str:
    return '''<svg viewBox="0 0 200 120" style="width:100%;height:auto;border-radius:10px">
<rect width="200" height="120" rx="10" fill="#101c2e"/>
<rect x="18" y="26" width="64" height="44" rx="4" fill="#1b2f47" stroke="#00e5cc" stroke-width="1.5"/>
<rect x="26" y="60" width="10" height="22" fill="#00e5cc"/><rect x="40" y="48" width="10" height="34" fill="#7c3aed"/><rect x="54" y="66" width="10" height="16" fill="#e9c46a"/>
<rect x="92" y="26" width="64" height="44" rx="4" fill="#1b2f47" stroke="#00e5cc" stroke-width="1.5"/>
<polyline points="98,60 112,48 122,54 136,36 150,42" stroke="#ff6b6b" stroke-width="2.5" fill="none"/>
<polygon points="168,44 182,68 154,68" fill="#eab308"/>
<text x="168" y="63" text-anchor="middle" font-size="12" font-weight="bold" fill="#0B1526">!</text>
<rect x="40" y="76" width="20" height="4" fill="#33475c"/><rect x="116" y="76" width="20" height="4" fill="#33475c"/>
<circle cx="100" cy="98" r="9" fill="#d00000"/>
<path d="M91,112 q9,-12 18,0 l0,-6 h-18 z" fill="#d00000"/>
</svg>'''

def _art_ask() -> str:
    return '''<svg viewBox="0 0 200 120" style="width:100%;height:auto;border-radius:10px">
<rect width="200" height="120" rx="10" fill="#eef2ff"/>
<rect x="18" y="18" width="110" height="44" rx="12" fill="#fff" stroke="#c7d2e8" stroke-width="2"/>
<polygon points="40,62 34,76 52,62" fill="#fff"/>
<text x="73" y="45" text-anchor="middle" font-size="26" font-weight="bold" fill="#0e7c6b">?</text>
<rect x="120" y="66" width="62" height="30" rx="10" fill="#0e7c6b"/>
<polygon points="160,96 166,106 154,96" fill="#0e7c6b"/>
<text x="151" y="86" text-anchor="middle" font-size="15" font-weight="bold" fill="#fff">✓</text>
<circle cx="60" cy="98" r="13" fill="#f2c49b"/>
<path d="M47,96 q13,-14 26,0 l0,-8 q-13,-10 -26,0 z" fill="#5a3a26"/>
<rect x="51" y="93" width="7" height="6" rx="3" fill="none" stroke="#1f2937" stroke-width="1.6"/>
<rect x="62" y="93" width="7" height="6" rx="3" fill="none" stroke="#1f2937" stroke-width="1.6"/>
<path d="M55,106 q5,4 10,0" stroke="#7c4a12" stroke-width="1.6" fill="none"/>
</svg>'''

def _tutor_icon(size: int = 30) -> str:
    return _tutor_img(size)

def _tutor_mime_and_b64(path: str):
    import base64
    with open(path, "rb") as fh:
        raw = fh.read()
    if raw[:8] == bytes([137, 80, 78, 71, 13, 10, 26, 10]):
        return "image/png", base64.b64encode(raw).decode()
    return "image/jpeg", base64.b64encode(raw).decode()

def _tutor_img(size: int = 30) -> str:
    """Real photo first (assets/tutor.png), else built-in SVG avatar."""
    p = _asset("tutor.png", "tutor.jpg", "tutor.jpeg")
    if p:
        mime, b64 = _tutor_mime_and_b64(p)
        return (f'<img src="data:{mime};base64,{b64}" width="{size}" height="{size}" '
                f'style="border-radius:50%;vertical-align:-6px;object-fit:cover">')
    try:
        q = _asset("tutor_teacher.svg")
        with open(q or "", encoding="utf-8") as fh:
            svg = fh.read()
        return svg.replace("<svg ",
            f'<svg width="{size}" height="{size}" style="vertical-align:-6px" ', 1)
    except Exception:
        return "🎓"

def _tutor_avatar_uri() -> str:
    """Data URI for the FAB button: real photo preferred, SVG fallback."""
    import urllib.parse
    p = _asset("tutor.png", "tutor.jpg", "tutor.jpeg")
    if p:
        mime, b64 = _tutor_mime_and_b64(p)
        return f"data:{mime};base64," + b64
    with open(_asset("tutor_teacher.svg") or "", encoding="utf-8") as fh:
        return "data:image/svg+xml," + urllib.parse.quote(fh.read())
_next_theme = "light" if _dark else "dark"
_next_label = "🌙 Dark" if _dark else "☀️ Light"
st.markdown(f"""
<div class="hero"><div class="hero-inner">
  {_logo_img()}
  <div style="flex:1;min-width:220px">
    <h1>{TOOL_NAME} <span>by {CREATOR_NAME}</span></h1>
    <p>{TAGLINE}</p>
  </div>
  <a class="theme-link" href="{_link(nav, _next_theme)}" target="_self">{_next_label}</a>
  <a class="theme-link" href="{_link('guide')}" target="_self">📖 Guide</a>
</div>
""", unsafe_allow_html=True)
components.html(
    "<script>try{window.parent.document.body.classList.toggle('dark',__DARK__);}catch(e){}</script>".replace(
        "__DARK__", "true" if _dark else "false"),
    height=0)
_render_navbar(nav)

def _need_login() -> bool:
    """Lock card for members-only material. Returns True when page must stop."""
    if st.session_state.get("user"):
        return False
    st.markdown("<div class='card' style='border-top:3px solid #e9c46a'><b>🔒 Members only.</b> "
                "Browse freely — but rooms, simulations, games and certificates need a free account, "
                "so your progress is saved to YOU.</div>", unsafe_allow_html=True)
    if st.button("🔑 Log in before accessing this module", type="primary"):
        st.query_params["nav"] = "account"
        st.rerun()
    return True

def _snap() -> dict:
    return {
        "hist": [list(x) for x in st.session_state.get("hist", [])][-50:],
        "done_lessons": sorted(st.session_state.get("done_lessons", set())),
        "reviewed": sorted(st.session_state.get("reviewed", set())),
        "lesson_idx": st.session_state.get("lesson_idx", 0),
        "last_findings": st.session_state.get("last_findings", []),
        "room_applied": st.session_state.get("room_applied", ""),
        "sim_best": st.session_state.get("sim_best", 0),
        "user_name": st.session_state.get("user_name", ""),
    }

def _give_xp(n: int) -> int:
    """Award XP to the logged-in account (persists immediately). Returns new total."""
    _u = st.session_state.get("user")
    if not _u:
        return 0
    from src.auth.store import load_progress as _lp, save_progress as _sp
    from src.gamify import award as _aw
    p = _lp(_u["id"]) or {}
    base = _snap()
    base["xp"] = p.get("xp", 0)
    base["days"] = p.get("days", [])
    base["feedback_given"] = p.get("feedback_given", False)
    _aw(base, n)
    _sp(_u["id"], base)
    return int(base["xp"])

def _apply_account_progress(uid: int) -> None:
    from src.auth.store import load_progress as _lp
    p = _lp(uid)
    if not p:
        st.session_state.progress_loaded = True
        return
    st.session_state.done_lessons = set(p.get("done_lessons", []) or [])
    st.session_state.reviewed = set(p.get("reviewed", []) or [])
    st.session_state.lesson_idx = int(p.get("lesson_idx", 0) or 0)
    if p.get("last_findings"):
        st.session_state.last_findings = p["last_findings"]
    if isinstance(p.get("sim_best"), dict):
        st.session_state.sim_best = p["sim_best"]
    if p.get("user_name"):
        st.session_state["user_name"] = p["user_name"]
    if p.get("hist"):
        st.session_state.hist = [tuple(x) for x in p["hist"]]
    st.session_state.progress_loaded = True

def _merge_local_progress(uid: int) -> None:
    """First register: fold this browser's guest progress into the new account."""
    from src.auth.store import load_progress as _lp, save_progress as _sp
    if _lp(uid):
        _apply_account_progress(uid)
        return
    _sp(uid, _snap())

def gauge(score):
    if not HAS_PLOTLY:
        st.progress(score / 100)
        return
    color = "#d00000" if score >= 75 else ("#e76f51" if score >= 40 else ("#e9c46a" if score >= 15 else "#2a9d8f"))
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score,
        title={"text": "Risk"}, gauge={"axis": {"range": [0, 100]},
        "bar": {"color": color}, "steps": [{"range": [0, 15], "color": "#e3f5e9"},
        {"range": [15, 40], "color": "#fff7d6"}, {"range": [40, 75], "color": "#ffeed9"},
        {"range": [75, 100], "color": "#ffe1e1"}]}))
    fig.update_layout(height=220, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

def _lines(up, sample, extra):
    if up is not None:
        return up.getvalue().decode(errors="ignore").splitlines()
    if sample:
        with open(sample, errors="ignore") as f:
            return f.read().splitlines()
    return [] + extra

# ---------- ANALYZE ----------
if nav == "home":
    st.subheader("Welcome to your SOC training ground")
    st.write("New here? Follow the path below — 15 minutes from zero to your first caught attack.")
    s1, s2, s3 = st.columns(3)
    with s1:
        with st.container(border=True):
            st.markdown(_home_art('home_learn'), unsafe_allow_html=True)
            st.markdown("### Learn")
            st.write("Start Room 1: CIA triad in plain English.")
            if st.button("Start learning", key="home_learn", use_container_width=True):
                st.query_params["nav"] = "learn"
                st.rerun()
    with s2:
        with st.container(border=True):
            st.markdown(_home_art('home_analyze'), unsafe_allow_html=True)
            st.markdown("### Analyze")
            st.write("Catch a live brute-force in sample logs.")
            if st.button("Catch an attack", key="home_analyze", use_container_width=True):
                st.query_params["nav"] = "analyze"
                st.rerun()
    with s3:
        with st.container(border=True):
            st.markdown(_home_art('home_ask'), unsafe_allow_html=True)
            st.markdown("### Ask")
            st.write("Stuck? The tutor answers anything.")
            if st.button("Meet the tutor", key="home_tutor", use_container_width=True):
                st.query_params["nav"] = "tutor"
                st.rerun()
    st.divider()
    done = st.session_state.get("done_lessons", set())
    m1, m2, m3 = st.columns(3)
    m1.metric("Rooms completed", f"{len(done)}/20")
    m2.metric("Detection engines", "8")
    m3.metric("MITRE techniques", "8+")
    if done:
        st.progress(len(done) / 20, text="Your course progress")
        if st.button("▶ Continue where you left off"):
            from src.learn.curriculum import COURSE
            ids = [l["id"] for l in COURSE]
            nxt = next((i for i, x in enumerate(ids) if x not in done), 0)
            st.session_state.lesson_idx = nxt
            st.query_params["nav"] = "learn"
            st.rerun()
    st.divider()
    st.subheader("Explore the lab")
    st.markdown("""
- **📚 Learn** — 20 rooms: CIA to frameworks, with diagrams, games, war stories, quizzes
- **🤖 AI Tutor** — instant answers, offline built-in or local open model
- **🌐 Resources** — MITRE, CERT-In, CISA, OWASP, NVD with in-tool preview
- **🔍 Analyze** — brute-force, SQLi/XSS, phishing URLs, risk gauge, simulator
- **📁 File Check** — suspicious PDFs, image metadata, APK triage
- **🔎 OSINT** — passive domain, username, email, photo, plate + smishing checks
""")

if nav == "analyze":
    left, main = st.columns([1, 2.2])
    with left:
        st.subheader("Controls")
        use_samples = st.checkbox("Use sample attacks", value=True)
        threshold = st.slider("Brute-force threshold", 2, 10, 5)
        auth_file = st.file_uploader("Auth log", type=["log", "txt"], key="auth")
        web_file = st.file_uploader("Web log", type=["log", "txt"], key="web")
        urls_text = st.text_area("URLs (one per line)",
            "https://accounts.google.com/signin\nhttp://192.168.1.100.verify-login.tk/secure/update")
        with st.expander("🎮 Attack simulator (live)"):
            n = st.slider("Failed logins from attacker", 1, 12, 6)
            if st.button("💥 Inject brute-force burst"):
                st.session_state.extra_auth += [
                    f"Oct 7 12:00:0{i} lab sshd[1]: Failed password for root from 203.0.113.99 port 5000{i} ssh2"
                    for i in range(n)]
                st.toast(f"Injected {n} fails from 203.0.113.99")
            if st.button("💉 Inject SQLi"):
                st.session_state.extra_web.append('9.9.9.9 - - [07/Oct/2026] "GET /?id=1 UNION SELECT password FROM users HTTP/1.1" 200 1')
            if st.button("📜 Inject XSS"):
                st.session_state.extra_web.append('9.9.9.9 - - [07/Oct/2026] "GET /?q=<script>alert(1)</script> HTTP/1.1" 200 1')
            if st.button("Clear injected"):
                st.session_state.extra_auth, st.session_state.extra_web = [], []
        run = st.button("🛡️ Analyze now", type="primary", use_container_width=True)
    with main:
        if run:
            auth_lines = _lines(auth_file, "data/sample_auth.log" if use_samples else None, st.session_state.extra_auth)
            web_lines = _lines(web_file, "data/sample_web.log" if use_samples else None, st.session_state.extra_web)
            findings = detect_brute_force(auth_lines, threshold=threshold) + detect_web_attacks(web_lines)
            urls = [x.strip() for x in urls_text.splitlines() if x.strip()] + st.session_state.extra_urls
            for u in urls:
                s = score_url(u)
                if s["level"] in ("HIGH", "MEDIUM"):
                    findings.append({"type": "phishing", "severity": s["level"], **s,
                                     "title": f"Phishing {s['level']} ({s['score']}): {u}"})
            st.session_state.last_findings = findings
            st.session_state.reviewed = set()
        findings = st.session_state.last_findings
        if not findings and not run:
            st.info("👈 Hit Analyze now. Try simulator: inject burst → re-analyze → watch risk jump.")
        elif not findings:
            st.success("Clean at this threshold.")
            st.caption("Checked: brute-force (T1110), web probes (T1190/T1189/T1083), phishing URLs. "
                       "Not checked: malware behavior, C2, lateral movement, exfil — clean ≠ proven safe.")
        else:
            risk = score_findings(findings)
            k1, k2 = st.columns([1, 1.4])
            with k1:
                gauge(risk["score"])
            with k2:
                st.metric("Level", risk["level"])
                st.caption(risk["action"])
                n_high = sum(1 for f in findings if f.get("severity") == "HIGH")
                n_med = sum(1 for f in findings if f.get("severity") == "MEDIUM")
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:6px">
                  <div class="kpi" style="background:linear-gradient(135deg,#d00000,#ff6b6b)">{n_high}<br><small>HIGH</small></div>
                  <div class="kpi" style="background:linear-gradient(135deg,#b7791f,#e9c46a)">{n_med}<br><small>MEDIUM</small></div>
                  <div class="kpi" style="background:linear-gradient(135deg,#0B1526,#0e7c6b)">{len(findings)}<br><small>TOTAL</small></div>
                </div>
                """, unsafe_allow_html=True)
            from src.scoring.coverage import scan_summary, CHECKED, NOT_CHECKED
            st.caption(scan_summary(len(auth_lines), len(web_lines), len(urls), threshold))
            with st.expander("🔍 What this scan did and did NOT check"):
                st.write("**Checked:**")
                for c in CHECKED:
                    st.write("- " + c)
                st.write("**NOT checked (out of scope for this lab):**")
                for c in NOT_CHECKED:
                    st.write("- " + c)
                st.warning("A clean result means no matching patterns — not proof of safety.")
            if HAS_PLOTLY:
                import plotly.express as px
                sev = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
                typ: dict = {}
                for f in findings:
                    sev[str(f.get("severity", "LOW")).upper()] = sev.get(str(f.get("severity")).upper(), 0) + 1
                    typ[f.get("type", "?")] = typ.get(f.get("type", "?"), 0) + 1
                g1, g2 = st.columns(2)
                with g1:
                    st.plotly_chart(px.pie(names=list(sev.keys()), values=list(sev.values()),
                        title="By severity", color_discrete_sequence=["#d00000", "#e9c46a", "#2a9d8f"]),
                        use_container_width=True)
                with g2:
                    st.plotly_chart(px.bar(x=list(typ.keys()), y=list(typ.values()),
                        title="By type", labels={"x": "type", "y": "count"}),
                        use_container_width=True)
            st.subheader("Triage findings")
            f1, f2, f3 = st.columns(3)
            with f1:
                st.caption("Severity")
                sev_f = [s for s in ("HIGH", "MEDIUM", "LOW")
                         if st.checkbox(s, value=True, key="fsev" + s)]
            _types = sorted({f.get("type", "?") for f in findings})
            with f2:
                st.caption("Type")
                type_f = [t for t in _types if st.checkbox(t, value=True, key="ftyp" + t)]
            q = f3.text_input("Search (IP, keyword)", "")
            shown = [f for f in findings if f.get("severity") in sev_f and f.get("type") in type_f
                     and (not q or q.lower() in (f.get("title", "") + str(f.get("evidence", ""))).lower())]
            done = len([t for t in [f["title"] for f in findings] if t in st.session_state.reviewed])
            st.progress(done / max(1, len(findings)), text=f"Triaged {done}/{len(findings)}")
            for f in shown:
                key = f["title"]
                mark = "✅" if key in st.session_state.reviewed else ("🔴" if f.get("severity") == "HIGH" else "🟡")
                with st.expander(f"{mark} [{f.get('severity')}] {f.get('title')}"):
                    st.code(str(f.get("evidence", f.get("url", "")))[:600])
                    if f.get("reasons"):
                        st.write("Why flagged: " + "; ".join(f["reasons"]))
                    if mitre := MITRE_LINKS.get(f.get("type", "")):
                        st.link_button("Open MITRE technique ↗", mitre)
                    st.text("AI coach:")
                    st.write(explain(f))
                    if st.button("Mark reviewed", key="rv" + key):
                        st.session_state.reviewed.add(key)
                        st.rerun()
            with st.expander("📈 Trending exploited bugs (CISA KEV)"):
                try:
                    from src.intel.trending import fetch_trending
                    items, mode = fetch_trending(top=8)
                    st.caption(f"mode={mode}")
                    st.table(items)
                except Exception as e:
                    st.warning(str(e))

# ---------- FILE CHECK (PDF / image / APK — no logs needed) ----------
if nav == "sim":
    from src.sim.scenario import TICKS as _NS_TICKS, ACTIONS, score_action, grade
    from src.sim.library import SIMS as _LIB
    from src.detectors.brute_force import detect_brute_force as _bf
    from src.detectors.web_attacks import detect_web_attacks as _wa
    from src.detectors.phishing import score_url as _su
    _SIMS = {"night-shift": {"title": "Night Shift",
             "briefing": "Friday 23:40. You are the L1 on duty. Evidence drips in tick by tick — triage like it matters, because here it scores you.",
             "ticks": _NS_TICKS}}
    for _s in _LIB:
        _SIMS[_s["id"]] = _s
    for k, v in {"sim_id": "", "sim_step": 0, "sim_score": 0, "sim_log": [], "sim_t0": 0.0,
                 "sim_done": False, "sim_best": {}, "sim_started": False}.items():
        st.session_state.setdefault(k, v)
    if isinstance(st.session_state.sim_best, int):
        st.session_state.sim_best = {}
    st.subheader("🎯 SOC simulations — pick your shift")
    if _need_login():
        st.stop()
    if not st.session_state.sim_id or st.session_state.sim_id not in _SIMS:
        st.session_state.sim_id = ""
        st.caption("Six scenarios, one action per tick. Correct +20, wrong −10, freezing −15.")
        _ids = list(_SIMS.keys())
        for _r in range(0, len(_ids), 3):
            _cols = st.columns(3)
            for _j, _sid in enumerate(_ids[_r:_r + 3]):
                _sm = _SIMS[_sid]
                _best = st.session_state.sim_best.get(_sid)
                with _cols[_j]:
                    with st.container(border=True):
                        st.markdown(f"**{_sm['title']}**")
                        st.caption(f"{len(_sm['ticks'])} ticks" + (f" • best {_best}" if _best else ""))
                        st.write(_sm["briefing"][:110] + "…")
                        if st.button("Select", key="simsel" + _sid, use_container_width=True):
                            st.session_state.sim_id = _sid
                            st.session_state.sim_started = False
                            st.session_state.sim_done = False
                            st.rerun()
        st.stop()
    SIM = _SIMS[st.session_state.sim_id]
    TICKS = SIM["ticks"]
    _mybest = st.session_state.sim_best.get(st.session_state.sim_id)
    if _mybest:
        st.caption(f"🏆 Personal best on this sim: {_mybest}")
    if st.button("‹ All simulations", key="simback"):
        st.session_state.sim_id = ""
        st.session_state.sim_started = False
        st.session_state.sim_done = False
        st.rerun()
    st.subheader(f"🎯 {SIM['title']}")
    st.caption(f"{len(TICKS)} ticks, one action each. Correct +20, wrong −10, freezing −15.")
    if not st.session_state.sim_started and not st.session_state.sim_done:
        st.markdown(f"<div class='card'><b>Briefing:</b> {SIM['briefing']}</div>",
                    unsafe_allow_html=True)
        if st.button("▶ Start shift", type="primary"):
            import time
            st.session_state.sim_step = 0
            st.session_state.sim_score = 0
            st.session_state.sim_log = []
            st.session_state.sim_t0 = time.time()
            st.session_state.sim_done = False
            st.session_state.sim_started = True
            st.rerun()
    elif not st.session_state.sim_done:
        i = st.session_state.sim_step
        tick = TICKS[i]
        import time
        el = int(time.time() - (st.session_state.sim_t0 or time.time()))
        st.markdown(f"<div class='card'><b>{tick['title']}</b> ⏱ {el // 60:02d}:{el % 60:02d} • "
                    f"Score {st.session_state.sim_score} • Tick {i + 1}/{len(TICKS)}</div>",
                    unsafe_allow_html=True)
        st.write(tick["brief"])
        ev = tick["auth"] + tick["web"] + tick["urls"]
        if ev:
            st.code("\n".join(ev))
        else:
            st.caption("No new raw logs this tick — decide on context.")
        acc_auth = [l for t in TICKS[:i + 1] for l in t["auth"]]
        acc_web = [l for t in TICKS[:i + 1] for l in t["web"]]
        _f = _bf(acc_auth, threshold=5) + _wa(acc_web)
        for u in [x for t in TICKS[:i + 1] for x in t["urls"]]:
            _s = _su(u)
            if _s["level"] in ("HIGH", "MEDIUM"):
                _f.append({"type": "phishing", "severity": _s["level"], **_s, "title": f"Phishing {_s['level']}"})
        _h = sum(1 for f in _f if f.get("severity") == "HIGH")
        st.caption(f"Console so far: {len(_f)} findings ({_h} HIGH). Your detectors see it — do you act?")
        act = st.radio("Your action:", ACTIONS, key=f"simact{st.session_state.sim_id}{i}", index=None)
        if st.button("Commit action", type="primary", key=f"simgo{st.session_state.sim_id}{i}"):
            if act is None:
                st.warning("Pick an action first — freezing also scores (−15).")
            else:
                pts = score_action(tick, act)
                st.session_state.sim_score += pts
                st.session_state.sim_log.append({"tick": tick["title"], "you": act,
                                                 "pts": pts, "why": tick["why"]})
                if i + 1 >= len(TICKS):
                    st.session_state.sim_done = True
                    _b = st.session_state.sim_best
                    _first = st.session_state.sim_id not in _b
                    _b[st.session_state.sim_id] = max(_b.get(st.session_state.sim_id, -999),
                                                      st.session_state.sim_score)
                    if _first:
                        from src.gamify import XP_SIM_CLEAR
                        _give_xp(XP_SIM_CLEAR)
                        st.toast(f"Simulation cleared! +{XP_SIM_CLEAR} XP")
                else:
                    st.session_state.sim_step = i + 1
                st.rerun()
    else:
        import time
        el = int(time.time() - (st.session_state.sim_t0 or time.time()))
        total = 20 * len(TICKS)
        sc = st.session_state.sim_score
        st.markdown(f"<div class='card'><h3>Debrief — {grade(sc, total)}</h3>"
                    f"<p>Score {sc}/{total} • Time {el // 60:02d}:{el % 60:02d} • "
                    f"Best {st.session_state.sim_best.get(st.session_state.sim_id, sc)}</p></div>", unsafe_allow_html=True)
        for e in st.session_state.sim_log:
            icon = "✅" if e["pts"] > 0 else "❌"
            with st.expander(f"{icon} {e['tick']} — you: {e['you']} ({e['pts']:+d})"):
                st.write(e["why"])
        _rooms = sorted({r for e in st.session_state.sim_log for t in TICKS
                         if t["title"] == e["tick"] for r in t.get("rooms", [])})
        if _rooms:
            st.caption("📖 Replay armed with:")
            for rid in _rooms:
                st.link_button(f"Room: {rid} ↗", f"{_link('learn')}&room={rid}")
        if st.button("🔁 Run it back", use_container_width=True):
            st.session_state.sim_step = 0
            st.session_state.sim_score = 0
            st.session_state.sim_log = []
            st.session_state.sim_done = False
            st.session_state.sim_started = True
            import time
            st.session_state.sim_t0 = time.time()
            st.rerun()

if nav == "files":
    st.subheader("File Check — for non-log files")
    st.caption("Static triage only: nothing is opened, played, or installed. For a final verdict use VirusTotal.")
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        pdf = st.file_uploader("PDF document", type=["pdf"], key="pdf")
        if st.button("Scan PDF", use_container_width=True):
            if pdf is None:
                st.warning("Upload a PDF first.")
            else:
                from src.detectors.malpdf import analyze_pdf
                r = analyze_pdf(pdf.getvalue(), pdf.name)
                st.session_state["file_result"] = r
                st.rerun()
    with fcol2:
        img = st.file_uploader("Image", type=["png", "jpg", "jpeg", "gif", "webp", "bmp"], key="img")
        if st.button("Scan image", use_container_width=True):
            if img is None:
                st.warning("Upload an image first.")
            else:
                from src.detectors.imagecheck import analyze_image
                r = analyze_image(img.getvalue(), img.name)
                st.session_state["file_result"] = r
                st.rerun()
    with fcol3:
        apk = st.file_uploader("APK file", type=["apk", "zip"], key="apk")
        if st.button("Scan APK", use_container_width=True):
            if apk is None:
                st.warning("Upload an APK first.")
            else:
                from src.detectors.apkcheck import analyze_apk
                r = analyze_apk(apk.getvalue(), apk.name)
                st.session_state["file_result"] = r
                st.rerun()
    r = st.session_state.get("file_result")
    if r:
        color = {"HIGH": "#d00000", "MEDIUM": "#b7791f", "LOW": "#2a9d8f"}[r["level"]]
        st.markdown(f"""<div class="card" style="border-top:3px solid {color}">
          <h3 style="margin:0">{r['file']} — {r['level']} ({r['score']}/100)</h3>
          <small>{r['meta']}</small></div>""", unsafe_allow_html=True)
        st.progress(r["score"] / 100)
        for x in r["reasons"]:
            st.write("- " + x)
        if st.button("Ask Tutor about this result"):
            st.session_state.hist.append(("user", f"Explain this {r['kind']} result: {r['level']} {r['score']}/100"))
            st.session_state.hist.append(("bot", tutor_answer(
                f"file scan {r['kind']} {r['level']} score {r['score']}: " + "; ".join(r["reasons"][:4]))))
            st.toast("Answer added to AI Tutor tab")

# ---------- OSINT (passive only: your assets or consented targets) ----------
if nav == "osint":
    st.subheader("OSINT — passive lookups, no scanning")
    st.caption("Rules: investigate only your own / consented assets. This tab queries public records (DNS, registration, cert logs) — it never port-scans or logs in anywhere.")
    o1, o2, o3 = st.columns(3)
    with o1:
        st.markdown('<div class="sec-title">🌐 Domain / IP</div>', unsafe_allow_html=True)
        ioc = st.text_input("domain or IP", placeholder="example.com", key="osint_ioc")
        if st.button("Look up", use_container_width=True):
            from src.osint.lookup import (clean_domain, is_domain, is_ip, dns_lookup,
                                          rdap_domain, crtsh_subdomains, vt_link, abuse_link)
            d = clean_domain(ioc)
            if is_domain(d):
                with st.spinner("DNS + registration + cert logs…"):
                    st.write("**DNS**", dns_lookup(d))
                    r = rdap_domain(d)
                    st.write("**Registration (RDAP)**", r)
                    c = crtsh_subdomains(d)
                    st.write("**Subdomains (cert transparency)**",
                             c.get("subdomains", c.get("error")))
                    st.link_button("VirusTotal report ↗", vt_link(d))
            elif is_ip(ioc.strip()):
                st.link_button("VirusTotal report ↗", vt_link(ioc.strip()))
                st.link_button("AbuseIPDB report ↗", abuse_link(ioc.strip()))
                st.caption("IP lookups open in reputation DBs (their free tier shows history).")
            else:
                st.error("Enter a valid domain (example.com) or IPv4.")
    with o2:
        st.markdown('<div class="sec-title">👤 Username</div>', unsafe_allow_html=True)
        uname = st.text_input("username", placeholder="octocat", key="osint_user")
        if st.button("Footprint", use_container_width=True):
            from src.osint.lookup import USER_RE, github_user, PROFILE_LINKS
            if not USER_RE.match(uname or ""):
                st.error("2-39 chars: letters, numbers, _ . -")
            else:
                g = github_user(uname)
                st.write("**GitHub**", g if g.get("ok") else g.get("error"))
                st.caption("Also check manually (opens profile or 404):")
                for t in PROFILE_LINKS:
                    st.link_button(t.format("x").split("/")[2] + f" @{uname} ↗", t.format(uname))
    with o3:
        st.markdown('<div class="sec-title">✉️ Email</div>', unsafe_allow_html=True)
        email = st.text_input("email", placeholder="you@example.com", key="osint_email")
        if st.button("Check", use_container_width=True):
            from src.osint.lookup import EMAIL_RE, gravatar_exists
            if not EMAIL_RE.match(email or ""):
                st.error("That doesn't look like an email.")
            else:
                g = gravatar_exists(email)
                if g.get("ok"):
                    if g["exists"]:
                        st.success("Has a public Gravatar profile.")
                    else:
                        st.info("No public Gravatar — smaller footprint.")
                else:
                    st.warning(g.get("error"))
                st.link_button("HaveIBeenPwned breach check ↗", "https://haveibeenpwned.com/")
                st.caption("HIBP needs a free API key for automation — use their site directly.")
    st.divider()
    st.markdown('<div class="sec-title">🚗 Vehicle plate — format decode (owner needs VAHAN)</div>', unsafe_allow_html=True)
    st.caption("Owner name/address is NOT public data — it needs VAHAN login (vahan.parivahan.gov.in) or the mParivahan app. This decodes state/RTO from the plate format.")
    vplate = st.text_input("Plate number", placeholder="DL 8C A1234", key="osint_plate")
    if st.button("Decode plate", use_container_width=True):
        from src.osint.lookup import parse_plate
        p = parse_plate(vplate)
        if p.get("ok"):
            st.success(f"{p['state_code']} = {p['state']} • RTO code {p['rto']}")
            st.caption(p["note"])
            st.link_button("VAHAN portal ↗", "https://vahan.parivahan.gov.in/nrservices/faces/user/citizen/citizenlogin.xhtml")
        else:
            st.error(p.get("error"))
    st.divider()
    st.markdown('<div class="sec-title">📲 Smishing SMS + caller check</div>', unsafe_allow_html=True)
    st.caption("Paste the SMS text and sender number. Owner identity needs Truecaller/police channels — but lures + fake sender series are detectable offline.")
    snum = st.text_input("Sender number / ID (e.g. +919876543210 or VM-HDFCBK)", key="osint_num")
    stext = st.text_area("SMS text", placeholder="Your KYC is suspended, verify immediately…", key="osint_sms")
    if st.button("Analyze SMS", use_container_width=True):
        from src.osint.lookup import classify_number, smishing_score
        c = classify_number(snum)
        st.write("**Number:**", c.get("kind", c.get("error")), "—", c.get("note", ""))
        s = smishing_score(stext)
        color = {"HIGH": "#d00000", "MEDIUM": "#b7791f", "LOW": "#2a9d8f"}[s["level"]]
        st.markdown(f"<b style='color:{color}'>{s['level']} ({s['score']}/100)</b>", unsafe_allow_html=True)
        for x in s["reasons"]:
            st.write("- " + x)
        st.link_button("Truecaller search ↗", "https://www.truecaller.com/")
        st.link_button("Report: cybercrime.gov.in ↗", "https://cybercrime.gov.in/")

    st.divider()
    st.markdown('<div class="sec-title">🖼️ Photo lookup — place clues, not face ID</div>', unsafe_allow_html=True)
    st.caption("Only your own / consented photos. This tool cannot identify private people — for reverse-image search, upload the photo on the engines below (they open in a new tab).")
    ph1, ph2 = st.columns([1, 1.4])
    with ph1:
        photo = st.file_uploader("Upload photo", type=["png", "jpg", "jpeg", "webp"], key="osint_photo")
        if photo and st.button("Inspect photo", use_container_width=True):
            from src.detectors.imagecheck import extract_gps
            _pb = photo.getvalue()
            st.session_state["photo_bytes"] = _pb
            st.session_state["photo_gps"] = extract_gps(_pb)
            st.session_state["photo_done"] = True
    with ph2:
        if st.session_state.get("photo_done"):
            gps = st.session_state.get("photo_gps")
            if gps:
                st.success(f"GPS embedded: {gps['lat']}, {gps['lon']}")
                st.link_button("View on Google Maps ↗",
                    f"https://www.google.com/maps?q={gps['lat']},{gps['lon']}")
                st.link_button("View on OpenStreetMap ↗",
                    f"https://www.openstreetmap.org/?mlat={gps['lat']}&mlon={gps['lon']}#map=15/{gps['lat']}/{gps['lon']}")
            else:
                st.info("No GPS embedded (most uploads strip it). Use reverse-image engines → or AI describe ↓.")
            if st.button("🤖 Describe with AI (needs API key)"):
                from src.ai.vision import describe_image
                _pb = st.session_state.get("photo_bytes")
                if not _pb:
                    st.warning("Upload and inspect a photo first.")
                else:
                    with st.spinner("Asking vision model…"):
                        d = describe_image(_pb)
                if d:
                    st.write(d)
                else:
                    st.warning("Set OPENAI_API_KEY (vision model) or photo too large. Offline fallback: EXIF + engines.")
        st.caption("Reverse-image engines (upload the photo there):")
        st.link_button("Google Lens ↗", "https://lens.google.com/")
        st.link_button("TinEye ↗", "https://tineye.com/")
        st.link_button("Bing Visual ↗", "https://www.bing.com/visualsearch")
        st.link_button("Yandex Images ↗", "https://yandex.com/images/")

# ---------- LEARN: 20-lesson interactive course ----------
if nav == "certs":
    if _need_login():
        st.stop()
    from src.learn.curriculum import COURSE as _CCOURSE
    from src.certs.make import build as _cert, cred_id as _cid, SKILLS as _SK, build_resume as _resume
    st.session_state.setdefault("done_lessons", set())
    done = st.session_state.done_lessons
    st.subheader("🎓 Certificates & resume")
    st.progress(len(done) / 20, text=f"Completed {len(done)}/20")
    _name = st.text_input("Certificate name (as on LinkedIn)", value=st.session_state.get("user_name", ""))
    if _name != st.session_state.get("user_name", ""):
        st.session_state["user_name"] = _name
    _who = (_name.strip() or "Learner")
    st.caption("Room certificates unlock as you complete rooms. For a sharper logo, save the original large file as assets/logo_large.png.")
    _ids = [l["id"] for l in _CCOURSE]
    for _r in range(0, len(_CCOURSE), 4):
        _cc = st.columns(4)
        for _j, _les in enumerate(_CCOURSE[_r:_r + 4]):
            _lid = _les["id"]
            with _cc[_j]:
                if _lid in done:
                    _png = _cert(_who, _les["title"], _les["area"], f"room:{_lid}")
                    st.download_button(f"🏅 {_les['area'].split('. ', 1)[-1]}", _png,
                                       file_name=f"cert-{_lid}.png", mime="image/png",
                                       key="cert" + _lid)
                else:
                    st.caption(f"🔒 {_les['area'].split('. ', 1)[-1]}")
    st.divider()
    if len(done) == len(_CCOURSE):
        st.success("All 20 rooms complete — claim your graduation certificate!")
        _full = _cert(_who, "Complete SOC Analyst Program",
                      "All 20 rooms • labs, games, simulations-ready", "program:complete")
        st.download_button("🎓 Download final certificate (PNG)", _full,
                           file_name="sentinellearn-certificate.png", mime="image/png")
        _cidv = _cid(_who, "program:complete")
        st.code(f"LinkedIn > Me > Add profile section > Licenses & certifications:\n"
                f"Name: Complete SOC Analyst Program (SentinelLearn)\n"
                f"Issuer: Cyberguru\n"
                f"Credential ID: {_cidv}\n"
                f"Skills: {', '.join(sorted({s for rid in done for s in _SK.get(rid, [])})[:12])}…",
                language="text")
    else:
        st.info(f"Final certificate unlocks at 20/20 (now {len(done)}).")
    st.divider()
    st.markdown("**📄 Resume builder** — generated from YOUR actual progress:")
    _rm = _resume(_who, [i for i in _ids if i in done], st.session_state.get("sim_best", {}))
    st.code(_rm, language="markdown")
    st.download_button("⬇ Download resume markdown", _rm.encode(),
                       file_name="soc-resume.md", mime="text/markdown")

if nav == "learn":
    st.session_state.setdefault("done_lessons", set())
    done = st.session_state.done_lessons
    st.subheader("🎓 Defensive classes — 20 lessons, visual + quiz each")
    st.progress(len(done) / len(COURSE), text=f"Completed {len(done)}/{len(COURSE)}")
    with st.expander("🗺️ Course map (click a lesson to jump)"):
        for r in range(0, len(COURSE), 4):
            cols = st.columns(4)
            for j, les in enumerate(COURSE[r:r + 4]):
                mark = "✅" if les["id"] in done else f"{r + j + 1}."
                if cols[j].button(f"{mark} {les['area'].split('. ', 1)[-1]}", key="jump" + les["id"]):
                    st.session_state.lesson_idx = r + j
                    st.rerun()
    idx = st.session_state.lesson_idx
    if _need_login():
        st.stop()
    _rq = st.query_params.get("room", "")
    if _rq and st.session_state.get("room_applied") != _rq:
        _ids = [l["id"] for l in COURSE]
        if _rq in _ids:
            idx = _ids.index(_rq)
            st.session_state.lesson_idx = idx
        st.session_state["room_applied"] = _rq
    l = COURSE[idx]
    tick = "✅ " if l["id"] in done else ""
    st.markdown(f"<div class='card'><small>🧩 Room {idx + 1}/20 • {l['area']}</small><h3 style='margin:4px 0'>{tick}{l['title']}</h3><p>{l['overview']}</p></div>", unsafe_allow_html=True)
    from src.learn.diagrams import render as render_diagram
    from src.learn.levels import LEVELS as LV
    lv = LV.get(l["id"], {})
    if lv.get("diagram"):
        st.markdown(render_diagram(lv["diagram"]), unsafe_allow_html=True)
    st.markdown("### Task 1 — 📖 Learn (basic → advanced)")
    with st.expander("🟢 Level 1 — Basics: what is it, why it matters", expanded=True):
        st.write(lv.get("beginner", ""))
        if lv.get("img_b"):
            st.markdown(render_diagram(lv["img_b"]), unsafe_allow_html=True)
    with st.expander("🟡 Level 2 — Intermediate: how it works"):
        st.write(lv.get("intermediate", ""))
        if lv.get("img_i"):
            st.markdown(render_diagram(lv["img_i"]), unsafe_allow_html=True)
    with st.expander("🔴 Level 3 — Advanced: enterprise reality"):
        st.write(lv.get("advanced", ""))
        if lv.get("img_a"):
            st.markdown(render_diagram(lv["img_a"]), unsafe_allow_html=True)
    with st.expander("📌 Key points (revision)"):
        for p in l["points"]:
            st.write("- " + p)
    st.markdown("### Task 2 — 🎮 Lab (interactive)")
    v = l["visual"]
    if v["kind"] == "picker":
        choice = st.radio(v["label"], list(v["options"].keys()), key="vis" + l["id"], index=None)
        if choice is not None:
            st.info(v["options"][choice])
    elif v["kind"] == "table":
        f = st.text_input(v.get("search", "Filter"), key="visf" + l["id"])
        rows = [r for r in v["rows"] if not f or f.lower() in " ".join(r).lower()]
        st.dataframe(rows, use_container_width=True)
        if not rows:
            st.warning("No rows match — clear the filter.")
    elif v["kind"] == "stepper":
        sk = "step" + l["id"]
        st.session_state.setdefault(sk, 0)
        s = st.session_state[sk]
        st.markdown(f"<div class='card'><h3>Phase {s + 1}/{len(v['steps'])}</h3><p>{v['steps'][s]}</p></div>", unsafe_allow_html=True)
        st.progress((s + 1) / len(v["steps"]))
        b1, b2 = st.columns(2)
        if b1.button("⬅ Prev phase", key="sp" + l["id"], disabled=(s == 0)):
            st.session_state[sk] = s - 1
            st.rerun()
        if b2.button("Next phase ➡", key="sn" + l["id"], disabled=(s == len(v["steps"]) - 1)):
            st.session_state[sk] = s + 1
            st.rerun()
    elif v["kind"] == "scenario":
        st.write("**" + v["q"] + "**")
        pick = st.radio("Your call:", v["options"], key="vsc" + l["id"])
        if st.button("Lock in answer", key="vsb" + l["id"]):
            if v["options"].index(pick) == v["answer"]:
                st.success("Correct. " + v["why"])
            else:
                st.error("Not quite. " + v["why"])
    elif v["kind"] == "checklist":
        checked = [st.checkbox(x, key="vcl" + l["id"] + str(i)) for i, x in enumerate(v["items"])]
        st.progress(sum(checked) / len(checked), text=f"{sum(checked)}/{len(checked)} hardened")
    elif v["kind"] == "code":
        st.caption(v.get("lang", "Example"))
        st.code(v["code"])
        st.info(v.get("note", ""))
    from src.learn.stories import STORIES as ST
    from src.learn.games import GAMES as GM, render_game as _rg
    stt = ST.get(l["id"], {})
    if stt:
        st.markdown("### Task 3 — 📰 War story + analyst day")
        st.markdown(f"<div class='card' style='border-top:3px solid #7c3aed'><b>📰 What really happened:</b> {stt['story']}</div>", unsafe_allow_html=True)
        st.caption("👩‍💻 A day doing this: " + stt["day"])
    gm = GM.get(l["id"])
    if gm:
        st.markdown("### Task 4 — 🎮 Play it")
        _rg(gm, l["id"])
    from src.learn.depth import DEPTH as DP
    dp = DP.get(l["id"], {})
    st.markdown("### Task 5 — 📚 Go deeper")
    for para in dp.get("deep_dive", []):
        st.write(para)
    with st.expander("⚠️ Mistakes that cause incidents"):
        for m in dp.get("mistakes", []):
            st.write("- " + m)
    if dp.get("commands"):
        with st.expander("⌨️ Commands & tools to try"):
            for c in dp["commands"]:
                st.code(c)
    with st.expander("💼 Interview prep"):
        for it in dp.get("interview", []):
            st.write("**Q: " + it["q"] + "**")
            st.write("A: " + it["a"])
    st.markdown("### Task 6 — ✅ Checkpoint")
    st.write(l["try_it"])
    for link in l.get("links", []):
        st.link_button("Open reference ↗", link)
    tq = l["task_q"]
    tans = st.radio("Checkpoint: " + tq["q"], tq["opts"], key="tq" + l["id"], index=None)
    if tans is not None:
        if tq["opts"].index(tans) == tq["a"]:
            st.success("Checkpoint cleared. " + tq["why"])
        else:
            st.error("Try again. " + tq["why"])
    st.divider()
    st.subheader(f"Task 7 — 📝 Final quiz: {l['title']} (5 questions)")
    correct = 0
    total = len(l["quiz"])
    for i, q in enumerate(l["quiz"]):
        ans = st.radio(f"{i + 1}. {q['q']}", q["opts"], key=f"cq{l['id']}{i}", index=None)
        with st.expander(f"💡 Hint for Q{i + 1}"):
            st.write(q.get("hint") or "Re-read Task 1 levels above — the answer is defined there.")
        if ans is not None:
            if q["opts"].index(ans) == q["a"]:
                st.success("Correct. " + q["why"])
                correct += 1
            else:
                st.error("Not quite. " + q["why"])
    st.progress(correct / total, text=f"Quiz: {correct}/{total}")
    c1, c2, c3 = st.columns(3)
    if c1.button("⬅ Prev lesson", disabled=(idx == 0)):
        st.session_state.lesson_idx = idx - 1
        st.rerun()
    if c2.button("Mark complete ★"):
        if l["id"] not in done:
            from src.gamify import XP_ROOM
            _give_xp(XP_ROOM)
            st.toast(f"Lesson complete! +{XP_ROOM} XP")
        done.add(l["id"])
        st.rerun()
    if l["id"] in done:
        from src.certs.make import build as _roomcert
        _who2 = (st.session_state.get("user_name", "") or st.session_state.get("user", {}).get("name", "") or "Learner")
        _png2 = _roomcert(_who2, l["title"], l["area"], f"room:{l['id']}")
        st.download_button("🏅 Download your room certificate", _png2,
                           file_name=f"cert-{l['id']}.png", mime="image/png",
                           key="roomcert" + l["id"])
    if c3.button("Next lesson ➡", disabled=(idx == len(COURSE) - 1)):
        st.session_state.lesson_idx = idx + 1
        st.rerun()
    if correct == total and total > 0 and l["id"] not in done:
        done.add(l["id"])
        from src.gamify import XP_ROOM
        _give_xp(XP_ROOM)
        st.balloons()
        st.success(f"🎉 {total}/{total} — lesson auto-completed! +{XP_ROOM} XP")

# ---------- TUTOR TAB: dedicated console with resource-backed answers ----------
def _related(text: str):
    """Top-2 official resources + best Learn room for a tutor answer."""
    import re
    toks = {w for w in re.findall(r"[a-z0-9+]+", text.lower()) if len(w) > 3}
    scored = []
    for r in RESOURCES:
        name_toks = {w for w in re.findall(r"[a-z0-9+]+", (r["name"] + " " + r["desc"]).lower()) if len(w) > 3}
        hit = len(toks & name_toks)
        if hit:
            scored.append((hit, r))
    scored.sort(key=lambda x: -x[0])
    from src.learn.curriculum import COURSE
    best_room, best_n = None, 0
    for les in COURSE:
        rt = {w for w in re.findall(r"[a-z0-9+]+", (les["area"] + " " + les["title"]).lower()) if len(w) > 3}
        n = len(toks & rt)
        if n > best_n:
            best_room, best_n = les, n
    return [r for _, r in scored[:2]], best_room

if nav == "tutor":
    st.markdown(f"""
<div class="hero" style="padding:14px 18px"><div class="hero-inner">
  {_tutor_img(40)}
  <div style="flex:1;min-width:200px">
    <div style="font-size:1.3rem;font-weight:700">Cyberguru Tutor</div>
    <p>Ask anything — every answer ships with sources to go deeper.</p>
  </div>
</div>
""", unsafe_allow_html=True)
    try:
        from src.ai.local_llm import status as _st, default_model as _dm
        _s = _st()
        if _s["ok"]:
            st.success(f"Local AI active ({_dm()}) — free, private, offline.")
        else:
            with st.expander("⬆️ Upgrade to a real AI (free, 5 min, optional)"):
                st.write("Built-in answers work now. For full open-model answers: 1) Install Ollama from https://ollama.com/ 2) run `ollama pull llama3.1` 3) restart this app. Low-RAM PC? Use `ollama pull phi3` (smaller). No keys, no cloud, works offline.")
    except Exception:
        pass
    chips = ["What is ransomware?", "Explain MFA", "What is CERT-In?", "SOC career roadmap?"]
    c1 = st.columns(2)
    for i, ch in enumerate(chips[:2]):
        if c1[i].button(ch, key=f"ch{i}", use_container_width=True):
            _tutor_respond(ch)
    c2 = st.columns(2)
    for i, ch in enumerate(chips[2:]):
        if c2[i].button(ch, key=f"ch{i+2}", use_container_width=True):
            _tutor_respond(ch)
    st.markdown("### 💬 Conversation")
    import html as _hh
    for role, msg in st.session_state.hist:
        safe = _hh.escape(msg)
        if role == "user":
            st.markdown(f'<div class="cb-user">{safe}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="cb-bot">{_tutor_img(22)} {safe}</div>', unsafe_allow_html=True)
            res, room = _related(msg)
            if res or room:
                st.caption("📚 Go deeper:")
                for r in res:
                    st.link_button(f"{r['name']} ↗", r["url"])
                if room:
                    st.link_button(f"📖 Related room: {room['title']} ↗",
                        f"{_link('learn')}&room={room['id']}")
    _tutor_stream_here()
    with st.form("tutor_page_form", clear_on_submit=True):
        _pq = st.text_input("Ask anything…", placeholder="e.g. what is zero trust? how do firewalls work?")
        _send = st.form_submit_button("Send ➤", type="primary", use_container_width=True)
    if _send and _pq:
        _tutor_respond(_pq)
    if st.button("🧹 Clear conversation"):
        st.session_state.hist = []
        st.rerun()

# ---------- RESOURCES ----------
if nav == "arcade":
    from src.learn.arcade import GAMES as _AG, get as _agame
    st.subheader("🕹️ Arcade — reflexes of an analyst")
    st.caption("Real games, real timers. High score beat? Screenshot it for the resume.")
    if _need_login():
        st.stop()
    st.session_state.setdefault("arcade_gid", "")
    gid = st.session_state.arcade_gid
    _valid = [g[0] for g in _AG]
    if gid and gid not in _valid:
        st.session_state.arcade_gid = ""
        gid = ""
    if not gid:
        _ids = [g[0] for g in _AG]
        for _r in range(0, len(_AG), 2):
            _cols = st.columns(2)
            for _j, (g, t, d) in enumerate(_AG[_r:_r + 2]):
                with _cols[_j]:
                    with st.container(border=True):
                        st.markdown(f"**{t}**")
                        st.caption(d)
                        if st.button("▶ Play", key="arcplay" + g, use_container_width=True):
                            st.session_state.arcade_gid = g
                            st.rerun()
    else:
        if st.button("‹ All games", key="arcback"):
            st.session_state.arcade_gid = ""
            st.rerun()
        st.markdown('<span id="arcade-frame"></span>', unsafe_allow_html=True)
        components.html(_agame(gid), height=560, scrolling=False)

if nav == "resources":
    st.subheader("Official docs — search + preview inside tool")
    sq = st.text_input("Search resources", "")
    cats = ["All"] + sorted({r["cat"] for r in RESOURCES})
    cat = st.radio("Category", cats, horizontal=True, key="res_cat")
    for r in [x for x in RESOURCES if (cat == "All" or x["cat"] == cat)
              and (not sq or sq.lower() in (x["name"] + x["desc"]).lower())]:
        st.markdown(f"<div class='card'><b>{r['name']}</b> <small>• {r['cat']}</small><br>{r['desc']}</div>",
                    unsafe_allow_html=True)
        b1, b2 = st.columns([1, 4])
        b1.link_button("Open ↗", r["url"])
        if b2.toggle(f"Preview {r['name']}", key="pv" + r["url"]):
            try:
                components.iframe(r["url"], height=480)
            except Exception:
                st.info("Blocked embedding — use Open.")

if nav == "guide":
    st.subheader("📖 User guide — how to use this tool")
    st.caption("Five minutes here saves an hour of clicking around.")
    with st.expander("🚀 Start here (first 15 minutes)", expanded=True):
        st.write("1. **Home** — follow the 3-step path: Learn → Analyze → Ask.")
        st.write("2. **Learn Room 1** — CIA triad, then its quiz. Green checkmarks track you.")
        st.write("3. **Analyze** — tick sample data, Analyze, meet your first HIGH finding.")
        st.write("4. **Simulation** — run Night Shift when quizzes feel easy.")
        st.write("5. **Certificates** — Learn tab bottom; final unlocks at 20/20.")
    with st.expander("🔍 Analyze, File Check, OSINT"):
        st.write("- **Analyze**: logs/URLs in → risk gauge + triage. Simulator injects attacks live. 'Clean' means no matching patterns, never proven-safe.")
        st.write("- **File Check**: upload PDF/image/APK for static triage. Nothing executes.")
        st.write("- **OSINT**: passive lookups only (DNS, GitHub, Gravatar, photo GPS, plate format, SMS lures). Your assets or consented targets.")
    with st.expander("🎓 Learn, Arcade, Simulation, Tutor"):
        st.write("- **Learn**: 20 rooms × 7 tasks. Quizzes need 5/5; hints hide behind 💡 buttons.")
        st.write("- **Arcade**: 5 reflex games with timers. Scores are for fun (screenshot them!).")
        st.write("- **Simulation**: 6 incidents, one action per tick. Wrong calls cost points — including the FP traps.")
        st.write("- **Tutor**: built-in answers offline; install Ollama for full local AI. Every full-page answer lists deeper resources.")
    with st.expander("❓ FAQ"):
        st.write("**Dark mode resets?** It's in the URL — use in-app links (they carry it); typed URLs default to light.")
        st.write("**Progress lost?** Saved locally in the browser session + data/progress.json on your machine.")
        st.write("**Local AI slow?** First answer loads the model (30–90s CPU); later ones stream faster. Try `phi3` on low RAM.")
        st.write("**Is my upload sent anywhere?** No — files are analyzed in memory, in your browser session.")
    st.divider()
    st.subheader("💬 Feedback — shape what we build next")
    st.caption("Reviewed by the maintainer. Fields marked * are required.")
    _fn = st.text_input("Your name *", key="fb_name", placeholder="e.g. Priya Sharma")
    _fc = st.text_input("Contact (email / phone / LinkedIn)", key="fb_contact", placeholder="How do we reach you?")
    _fr = st.slider("Overall rating", 1, 5, 5, key="fb_rating")
    _fl = st.text_area("What would you LOVE to have in this tool? *", key="fb_love", placeholder="e.g. Hindi tutor mode, more simulations…")
    _fi = st.text_area("What could be BETTER? *", key="fb_improve", placeholder="e.g. confusing page, slow tutor, missing topic…")
    if st.button("Send feedback", type="primary", use_container_width=True):
        from src.feedback.store import submit as _fbsubmit
        import os as _os
        _e, _errs, _ch = _fbsubmit(_fn, _fc, _fr, _fl, _fi)
        if _errs:
            for _x in _errs:
                st.error(_x)
        else:
            st.success(f"Thanks {_e['name']}! Received as **{_e['ref']}** via {', '.join(_ch)}.")
            if st.session_state.get("user"):
                from src.gamify import XP_FEEDBACK
                _give_xp(XP_FEEDBACK)
                try:
                    from src.auth.store import load_progress as _lpf, save_progress as _spf
                    _fp = _lpf(st.session_state.user["id"]) or {}
                    _fp["feedback_given"] = True
                    _spf(st.session_state.user["id"], _fp)
                except Exception:
                    pass
                st.toast(f"Feedback bonus +{XP_FEEDBACK} XP")
            _via = []
            if _os.getenv("FEEDBACK_ENDPOINT"):
                _via.append("shared review board")
            if _os.getenv("SMTP_HOST"):
                _via.append("owner email")
            st.caption("Stored in the project feedback log" + (f" and forwarded to {', '.join(_via)}." if _via else
                       " (owner-only file for now — email/endpoint forwarding activates when the maintainer configures it)."))

if nav == "account":
    from src.auth.store import register as _reg, verify as _login, new_session as _nsess, end_session as _endsess
    from src.auth.store import load_progress as _lprog
    from src.gamify import rank_for, streak as _stk, earned as _earn, BADGES as _BG
    _u = st.session_state.get("user")
    if _u:
        _p = _lprog(_u["id"]) or {}
        _xp = int(_p.get("xp", 0) or 0)
        _cur, _long = _stk(_p.get("days", []) or [])
        _rank = rank_for(_xp)
        _done = _p.get("done_lessons", []) or []
        _bests = _p.get("sim_best", {}) or {}
        _initial = (_u.get("name", "?") or "?")[:1].upper()
        st.markdown(f"""
<div class="hero" style="padding:16px 20px"><div class="hero-inner">
  <div class="nvat" style="width:56px;height:56px;font-size:1.4rem">{_initial}</div>
  <div style="flex:1;min-width:200px">
    <h1 style="font-size:1.4rem">{_u['name']}</h1>
    <p>{_u['email']} • 🏅 {_rank} • 🔥 {_cur}-day streak (best {_long}) • ◆ {_xp} XP</p>
  </div>
</div>
""", unsafe_allow_html=True)
        _nxt = next((b for b, _ in [(5000, ''), (2500, ''), (1200, ''), (600, ''), (200, '')] if _xp < b), None)
        if _nxt:
            st.progress(min(1.0, _xp / _nxt), text=f"{_nxt - _xp} XP to next rank")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rooms", f"{len(_done)}/20")
        m2.metric("Streak", f"{_cur}🔥")
        m3.metric("XP", f"{_xp}")
        m4.metric("Sims cleared", f"{len(_bests)}")
        st.markdown("### 🏅 Badges")
        _got = set(_earn(_p))
        _bl = {b[0]: (b[1], b[2]) for b in _BG}
        for _r in range(0, len(_BG), 4):
            _cols = st.columns(4)
            for _j, _bid in enumerate([b[0] for b in _BG][_r:_r + 4]):
                _t, _d = _bl[_bid]
                with _cols[_j]:
                    if _bid in _got:
                        st.markdown(f"<div class='card' style='text-align:center;border-top:3px solid #e9c46a'>🏅<br><b>{_t}</b><br><small>{_d}</small></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='card' style='text-align:center;opacity:.45'>🔒<br><b>{_t}</b><br><small>{_d}</small></div>", unsafe_allow_html=True)
        st.markdown("### ⚙️ Menu")
        _m1, _m2 = st.columns(2)
        with _m1:
            if st.button("📚 My progress", use_container_width=True):
                st.query_params["nav"] = "learn"
                st.rerun()
            if st.button("🎓 Certificates", use_container_width=True):
                st.query_params["nav"] = "learn"
                st.rerun()
            if st.button("🌐 Resources", use_container_width=True):
                st.query_params["nav"] = "resources"
                st.rerun()
        with _m2:
            if st.button("💬 Give feedback", use_container_width=True):
                st.query_params["nav"] = "guide"
                st.rerun()
            if st.button("Log out", use_container_width=True):
                _endsess(st.session_state.get("session_token", ""))
                for _k in ("user", "session_token", "progress_loaded", "room_applied"):
                    st.session_state.pop(_k, None)
                st.query_params.clear()
                st.query_params["nav"] = "home"
                st.rerun()
    else:
        st.markdown("## Join free. Learn cyber defense by doing.")
        st.caption("Rooms, simulations, certificates and saved progress — free forever for learners.")
        _left, _right = st.columns([1, 1])
        with _left:
            st.markdown("<div class='card'>✅ <b>20 course rooms</b> — CIA to frameworks, quizzes included<br>"
                        "✅ <b>6 live simulations</b> — triage under pressure<br>"
                        "✅ <b>Certificates + resume builder</b> for LinkedIn<br>"
                        "✅ <b>Progress saved</b> across devices (per account)</div>", unsafe_allow_html=True)
            st.caption("Passwords are salted + hashed (PBKDF2). Browse freely — members-only material is marked 🔒.")
        with _right:
            _mode = st.radio("Choose:", ["Join FREE", "Log in"], horizontal=True, key="acc_mode")
            _em = st.text_input("Email Address", key="acc_email", placeholder="Example@example.com")
            _pw = st.text_input("Password", type="password", key="acc_pw",
                                placeholder="8+ characters" if _mode != "Log in" else "Your password")
            if _mode != "Log in":
                _nm = st.text_input("Display name", key="acc_name", placeholder="e.g. Cyberguru")
                if st.button("Continue", type="primary", use_container_width=True):
                    _nu, _err = _reg(_nm, _em, _pw)
                    if _err:
                        st.error(_err)
                    else:
                        _tok = _nsess(_nu["id"])
                        st.session_state.user, st.session_state.session_token = _nu, _tok
                        _merge_local_progress(_nu["id"])
                        st.query_params["s"] = _tok
                        st.toast(f"Welcome, {_nu['name']}!")
                        st.rerun()
                st.caption("Already have an account? Pick **Log in** above.")
            else:
                if st.button("Log in", type="primary", use_container_width=True):
                    _nu, _err = _login(_em, _pw)
                    if _err:
                        st.error(_err)
                    else:
                        _tok = _nsess(_nu["id"])
                        st.session_state.user, st.session_state.session_token = _nu, _tok
                        _apply_account_progress(_nu["id"])
                        st.query_params["s"] = _tok
                        st.toast(f"Welcome back, {_nu['name']}!")
                        st.rerun()
                st.caption("New here? Pick **Join FREE** above.")

if nav == "about":
    st.subheader("About SentinelLearn")
    st.write(f"{TOOL_NAME} by **{CREATOR_NAME}** — {TAGLINE}. A defensive, beginner-first SOC lab: detect real attack patterns in logs, files, and URLs, learn why they matter across 20 rooms, and get AI coaching throughout.")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Detection engines", "8", "logs + files + OSINT")
    a2.metric("MITRE techniques", "8+", "mapped per finding")
    a3.metric("Tutor topics", "60+", "offline + local AI")
    a4.metric("Risk scale", "100", "points, explained")
    with st.expander("What each section does", expanded=True):
        st.write("- **Analyze**: brute-force, SQLi/XSS/traversal + phishing URLs, risk gauge, attack simulator, triage filters")
        st.write("- **File Check**: suspicious-PDF, image-metadata, and APK static triage — nothing executes")
        st.write("- **OSINT**: passive domain/IP/username/email/photo lookups + plate + smishing checks (consented targets only)")
        st.write("- **Learn**: 20 rooms, 5 tasks each — levels, diagrams, labs, games, war stories, quizzes")
        st.write("- **AI Tutor**: built-in answers offline, local open model (Ollama) when installed")
        st.write("- **Resources**: MITRE ATT&CK, CERT-In, CISA, OWASP, NVD with in-tool preview")
    with st.expander("How scoring works"):
        st.write("HIGH=25, MEDIUM=10, LOW=3, capped at 100. 75+ (or 3 HIGHs) is CRITICAL. Scores are triage aids, not verdicts — confirm before acting.")
        st.markdown("""
<div class="def"><div class="ic">🔴</div><div><b class="t">HIGH — 25 pts</b><span class="d">Actively dangerous pattern (brute-force, injection). Triage today.</span></div></div>
<div class="def"><div class="ic">🟡</div><div><b class="t">MEDIUM — 10 pts</b><span class="d">Suspicious, needs review this week (traversal, odd link).</span></div></div>
<div class="def"><div class="ic">🟢</div><div><b class="t">LOW — 3 pts</b><span class="d">Weak signal or hygiene note. Monitor.</span></div></div>
""", unsafe_allow_html=True)
    st.caption(f"Created by {CREATOR_NAME} • {BUILDER_LINE} • Defensive learning only: synthetic sample data. For real incidents contact your SOC / CERT-In.")

# ---------- footer + floating tutor button (bottom-right, every page) ----------
st.markdown(f"""
<div class="sitefooter">
  <div class="sf-grid">
    <div><h4>Learn</h4>
      <a href="{_link('learn')}" target="_self">20 course rooms</a>
      <a href="{_link('analyze')}" target="_self">Analyze lab</a>
      <a href="{_link('files')}" target="_self">File check</a>
      <a href="{_link('osint')}" target="_self">OSINT lab</a>
      <a href="{_link('tutor')}" target="_self">AI tutor</a>
      <a href="{_link('arcade')}" target="_self">Arcade games</a>
    </div>
    <div><h4>Resources</h4>
      <a href="https://attack.mitre.org/" target="_blank">MITRE ATT&amp;CK</a>
      <a href="https://www.cert-in.org.in/" target="_blank">CERT-In</a>
      <a href="https://www.cisa.gov/knownExploitedVulnerabilitiesCatalog" target="_blank">CISA KEV</a>
      <a href="https://owasp.org/www-project-top-ten/" target="_blank">OWASP Top 10</a>
      <a href="https://nvd.nist.gov/" target="_blank">NVD</a>
    </div>
    <div><h4>Safety</h4>
      <a href="https://cybercrime.gov.in/" target="_blank">Report cybercrime</a>
      <a href="https://haveibeenpwned.com/" target="_blank">HaveIBeenPwned</a>
      <a href="{_link('about')}" target="_self">How scoring works</a>
      <a href="{_link('about')}" target="_self">About this tool</a>
    </div>
    <div><h4>Project</h4>
      <a href="{_link('about')}" target="_self">About</a>
      <a href="{_link('guide')}" target="_self">User guide + feedback</a>
      <a href="{_link('resources')}" target="_self">All resources</a>
      <span class="sf-note">Created by <b>{CREATOR_NAME}</b></span>
      <span class="sf-note">{BUILDER_LINE}</span>
    </div>
    <div class="sf-brand">
      <div style="font-weight:700;font-size:1.05rem">🛡️ {TOOL_NAME} <span style="font-weight:400;font-size:.8rem;opacity:.7">by {CREATOR_NAME}</span></div>
      <p>A beginner-first, defensive SOC lab: detect real attack patterns, learn across 20 rooms, and get AI coaching throughout.</p>
      <p class="sf-note">Defensive learning only — synthetic sample data. For real incidents contact your SOC / CERT-In.</p>
    </div>
  </div>
  <div class="sf-bottom">Created by <b>{CREATOR_NAME}</b> • {BUILDER_LINE}</div>
</div>
<div class="fab-hint">👋 <b>Questions on cybersecurity?</b><br>Tap your tutor below — ask anything!</div>
""", unsafe_allow_html=True)

st.markdown('<span id="fab-tutor-anchor"></span>', unsafe_allow_html=True)
with st.popover("💬", help="Ask any cybersecurity question"):
    tutor_panel()

# JS pin: position the REAL popover trigger button fixed bottom-right.
# (CSS selectors alone can't reliably reach Streamlit's nested button.)
components.html("""
<script>
(function() {
  function pin() {
    try {
      var doc = window.parent.document;
      var btns = doc.querySelectorAll('[data-testid="stPopover"] button');
      var btn = null;
      for (var i = 0; i < btns.length; i++) {
        if (btns[i].textContent.indexOf('\\uD83D\\uDCAC') !== -1) { btn = btns[i]; break; }
      }
      if (!btn && btns.length) btn = btns[btns.length - 1];
      if (btn) {
        var s = btn.style;
        s.position = 'fixed'; s.bottom = '22px'; s.right = '22px';
        s.left = 'auto'; s.top = 'auto'; s.width = '62px'; s.height = '62px';
        s.borderRadius = '50%'; s.fontSize = '28px'; s.zIndex = '1000';
        s.padding = '0'; s.margin = '0'; s.overflow = 'hidden';
        s.background = 'linear-gradient(135deg,#0B1526,#0e7c6b)';
        s.border = '2px solid #00e5cc'; s.color = '#fff';
        s.boxShadow = '0 8px 26px rgba(0,229,204,.35)';
        btn.title = 'Ask anything about cybersecurity!';
        btn.setAttribute('aria-label', 'Open Cyberguru Tutor');
        btn.classList.add('fab-live');
        btn.innerHTML = '<img src="__AVATAR__" width="46" height="46" style="border-radius:50%;object-fit:cover;display:block;margin:auto">';
        var cont = btn.closest('[data-testid="stElementContainer"]');
        if (cont) { cont.style.height = '0px'; cont.style.overflow = 'visible'; }
        return true;
      }
    } catch (e) { return false; }
    return false;
  }
  var tries = 0;
  var iv = setInterval(function () { tries++; if (pin() || tries > 60) clearInterval(iv); }, 250);
  // size helper iframes directly: games get a tall frame, pin/theme helpers collapse
  function sizeFrames() {
    try {
      var doc = window.parent.document;
      var fr = doc.querySelectorAll('iframe[srcdoc]');
      for (var i = 0; i < fr.length; i++) {
        var sd = fr[i].getAttribute('srcdoc') || '';
        var game = (sd.indexOf('arcade-game') !== -1) || (sd.indexOf('ascore') !== -1);
        var c = fr[i].closest('[data-testid="stElementContainer"]');
        if (game) {
          if (c) { c.style.height = 'auto'; c.style.minHeight = '560px'; c.style.overflow = 'visible'; c.style.margin = ''; c.style.padding = ''; }
          fr[i].style.height = '560px'; fr[i].style.minHeight = '560px';
          fr[i].style.display = 'block'; fr[i].style.border = '0'; fr[i].style.width = '100%';
        } else {
          if (c) { c.style.height = '0px'; c.style.minHeight = '0px'; c.style.overflow = 'hidden'; c.style.margin = '0'; c.style.padding = '0'; }
          fr[i].style.height = '0px'; fr[i].style.minHeight = '0px'; fr[i].style.border = '0';
        }
      }
    } catch (e) {}
  }
  setInterval(sizeFrames, 1000);
  // dock any open popover panel bottom-right above the button
  function dock(panel) {
    var s = panel.style;
    s.position = 'fixed'; s.bottom = '96px'; s.right = '22px';
    s.top = 'auto'; s.left = 'auto'; s.transform = 'none';
    s.width = '385px'; s.maxWidth = '92vw'; s.maxHeight = '70vh';
    s.overflowY = 'auto'; s.zIndex = '1001';
    s.borderRadius = '16px';
    s.boxShadow = '0 16px 48px rgba(0,0,0,.3)';
  }
  function isTutorPanel(el) {
    try {
      var t = el.textContent || "";
      return t.indexOf("Cyberguru Tutor") !== -1 && t.indexOf("Ask anything") !== -1;
    } catch (e) { return false; }
  }
  function sweep(root) {
    try {
      var doc = window.parent.document;
      var scope = root || doc;
      var found = [];
      if (scope.querySelectorAll) {
        var q = scope.querySelectorAll('[data-testid="stPopoverBody"]');
        for (var i = 0; i < q.length; i++) found.push(q[i]);
      }
      for (var k = 0; k < found.length; k++) {
        if (isTutorPanel(found[k])) dock(found[k]);
      }
      fixSelects(doc);
    } catch (e) {}
  }
  // force readable select text in dark mode (menus portal outside widgets, CSS can't pin them)
  function fixSelects(doc) {
    try {
      if (!doc.body.classList.contains('dark')) return;
      var boxes = doc.querySelectorAll('[data-testid="stSelectbox"]');
      for (var i = 0; i < boxes.length; i++) {
        var inner = boxes[i].querySelectorAll('div');
        for (var j = 0; j < inner.length; j++) {
          if (!inner[j].querySelector('[role="listbox"]')) inner[j].style.color = '#eaf2f8';
        }
      }
      var opts = doc.querySelectorAll('[role="listbox"] [role="option"], [data-baseweb="menu"] [role="option"], [data-baseweb="menu"] li');
      for (var k = 0; k < opts.length; k++) {
        if (opts[k].getAttribute('aria-selected') === 'true') {
          opts[k].style.color = '#ffffff';
        } else {
          opts[k].style.color = '#16202e';
          opts[k].style.background = '';
        }
      }
      var lists = doc.querySelectorAll('[role="listbox"]');
      for (var m = 0; m < lists.length; m++) lists[m].style.background = '#ffffff';
    } catch (e) {}
  }
  try {
    var obs = new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) {
        var nodes = muts[i].addedNodes;
        for (var j = 0; j < nodes.length; j++) {
          if (nodes[j].nodeType === 1) sweep(nodes[j]);
        }
      }
    });
    obs.observe(window.parent.document.body, { childList: true, subtree: true });
    setTimeout(function () { try { fixSelects(window.parent.document); } catch (e) {} }, 1200);
  } catch (e) {}
})();
</script>
""".replace("__AVATAR__", _tutor_avatar_uri()), height=0)

# persist progress (chat, rooms, triage, findings) across full-page nav reloads
try:
    _snap_state = _snap()
    _save_progress(_snap_state)
    _u = st.session_state.get("user")
    if _u:
        from src.auth.store import load_progress as _lpw, save_progress as _sp
        _keep = _lpw(_u["id"]) or {}
        for _k in ("xp", "days", "feedback_given"):
            if _k in _keep and _k not in _snap_state:
                _snap_state[_k] = _keep[_k]
        _sp(_u["id"], _snap_state)
except Exception:
    pass
