"""Passive OSINT helpers. Public APIs only, no keys, no scanning. Offline-safe."""
import hashlib
import re

DOMAIN_RE = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.[a-z]{2,})+$", re.IGNORECASE)
IP_RE = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
USER_RE = re.compile(r"^[a-zA-Z0-9_.-]{2,39}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def clean_domain(s: str) -> str:
    s = (s or "").strip().lower().split("://")[-1].split("/")[0].split(":")[0]
    return s[:-1] if s.endswith(".") else s

def is_domain(s: str) -> bool:
    return bool(DOMAIN_RE.match(clean_domain(s)))

def is_ip(s: str) -> bool:
    if not IP_RE.match((s or "").strip()):
        return False
    return all(0 <= int(p) <= 255 for p in s.strip().split("."))

def vt_link(ioc: str) -> str:
    return f"https://www.virustotal.com/gui/search/{ioc}"

def abuse_link(ip: str) -> str:
    return f"https://www.abuseipdb.com/check/{ip}"

def _get_json(url: str, timeout: int = 12, headers: dict | None = None):
    import httpx
    r = httpx.get(url, timeout=timeout, follow_redirects=True,
                  headers=headers or {"User-Agent": "SentinelLearn-OSINT/1.0 (defensive lab)"})
    r.raise_for_status()
    return r.json()

def dns_lookup(domain: str) -> dict:
    """A / MX / TXT via Google DNS-over-HTTPS (no key)."""
    import httpx
    out: dict = {}
    for qtype in ("A", "MX", "TXT", "NS"):
        try:
            j = _get_json(f"https://dns.google/resolve?name={domain}&type={qtype}")
            out[qtype] = [a.get("data", "") for a in j.get("Answer", [])][:8]
        except Exception as e:
            out[qtype] = [f"lookup failed: {type(e).__name__}"]
    return out

def rdap_domain(domain: str) -> dict:
    """Registration data via RDAP redirector (no key)."""
    try:
        j = _get_json(f"https://rdap.org/domain/{domain}")
        return {"ok": True, "registrar": str((j.get("entities") or [{}])[0].get("vcardArray", ""))[:0] or "see events below",
                "events": [{e.get("eventAction"): e.get("eventDate")} for e in j.get("events", [])][:6],
                "nameservers": [n.get("ldhName") for n in j.get("nameservers", [])][:6],
                "status": (j.get("status") or [])[:6]}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: offline or RDAP blocked?"}

def crtsh_subdomains(domain: str, limit: int = 20) -> dict:
    """Certificate-transparency subdomains (no key). Often slow — short timeout."""
    import httpx
    try:
        j = _get_json(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=15)
        subs = sorted({x.get("name_value", "").split("\n")[0].strip().lower() for x in j if x.get("name_value")})
        subs = [s for s in subs if s.endswith(domain.lower())][:limit]
        return {"ok": True, "count": len(subs), "subdomains": subs}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: crt.sh slow/blocked, retry online"}

def github_user(username: str) -> dict:
    """Public GitHub profile (no key, generous limit)."""
    try:
        j = _get_json(f"https://api.github.com/users/{username}")
        return {"ok": True, "login": j.get("login"), "name": j.get("name"),
                "created": (j.get("created_at") or "")[:10], "repos": j.get("public_repos"),
                "followers": j.get("followers"), "bio": (j.get("bio") or "")[:160],
                "url": j.get("html_url")}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: user missing or offline"}

def gravatar_exists(email: str) -> dict:
    """Does this email have a public Gravatar? (MD5 + d=404, no key)."""
    import httpx
    h = hashlib.md5(email.strip().lower().encode()).hexdigest()
    try:
        r = httpx.get(f"https://www.gravatar.com/avatar/{h}?d=404", timeout=10,
                      headers={"User-Agent": "SentinelLearn-OSINT/1.0"})
        return {"ok": True, "exists": r.status_code == 200, "hash": h[:12] + "..."}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: offline?"}

PROFILE_LINKS = ["https://github.com/{}", "https://x.com/{}", "https://www.linkedin.com/in/{}",
                 "https://instagram.com/{}", "https://medium.com/@{}"]

# ---------- India vehicle plate decode (format only — owner identity needs VAHAN login) ----------
IN_STATES = {"AN": "Andaman Nicobar", "AP": "Andhra Pradesh", "AR": "Arunachal Pradesh",
    "AS": "Assam", "BR": "Bihar", "CH": "Chandigarh", "CT": "Chhattisgarh", "DN": "Dadra Nagar Haveli+Daman Diu",
    "DL": "Delhi", "GA": "Goa", "GJ": "Gujarat", "HP": "Himachal Pradesh", "HR": "Haryana",
    "JH": "Jharkhand", "JK": "Jammu Kashmir", "KA": "Karnataka", "KL": "Kerala", "LA": "Ladakh",
    "LD": "Lakshadweep", "MH": "Maharashtra", "ML": "Meghalaya", "MN": "Manipur", "MP": "Madhya Pradesh",
    "MZ": "Mizoram", "NL": "Nagaland", "OD": "Odisha", "PB": "Punjab", "PY": "Puducherry",
    "RJ": "Rajasthan", "SK": "Sikkim", "TN": "Tamil Nadu", "TR": "Tripura", "TS": "Telangana",
    "UK": "Uttarakhand", "UP": "Uttar Pradesh", "WB": "West Bengal"}
_PLATE_RE = re.compile(r"^([A-Z]{2})\s*(\d{1,2})\s*([A-Z]{1,3})\s*(\d{3,4})$")

def parse_plate(s: str) -> dict:
    """Decode Indian plate format: state + RTO code. No owner data (needs VAHAN login)."""
    p = re.sub(r"[^A-Z0-9]", "", (s or "").upper())
    m = re.match(r"^([A-Z]{2})(\d{1,2})([A-Z]{1,3})(\d{3,4})$", p)
    if not m:
        return {"ok": False, "error": "Not Indian private format (e.g. DL 8C A1234). BH/Bharat series also unsupported."}
    st_, rto, series, num = m.groups()
    state = IN_STATES.get(st_)
    if not state:
        return {"ok": False, "error": f"Unknown state code '{st_}'"}
    return {"ok": True, "state": state, "state_code": st_, "rto": rto,
            "note": "Owner name/address needs VAHAN login or mParivahan (owner-only/authorized use)."}

# ---------- India phone / smishing triage (no owner identity without Truecaller key) ----------
_NUM_RE = re.compile(r"^(\+91|91|0)?([6-9]\d{9})$")

def classify_number(s: str) -> dict:
    n = (s or "").replace(" ", "").replace("-", "")
    if re.match(r"^\+?140\d{7,9}$", n):
        return {"ok": True, "kind": "telemarketing series (140)", "note": "Promo calls/SMS come from 140; banks never ask OTP from these."}
    if n.startswith("1800") or n.startswith("1860"):
        return {"ok": True, "kind": "toll-free helpline", "note": "Verify the number from the official site before calling back."}
    m = _NUM_RE.match(n)
    if m:
        return {"ok": True, "kind": "valid Indian mobile", "normalized": "+91" + m.group(2),
                "note": "Owner name needs Truecaller key/police request. Check spam reports via links below."}
    return {"ok": False, "error": "Not an Indian mobile (expect 10 digits starting 6-9, optional +91)."}

SMISH_PATTERNS = [
    ("otp/share/verify immediately", 20), ("kyc", 20), ("blocked/suspend/deactivat", 20),
    ("prize/winner/lottery/congratulations", 20), ("electricity/power bill.*(due|disconnect|pay)", 20),
    ("bank.*(update/hold/last date)", 15), ("apk|download.*app|install.*apk", 25),
    ("parcel/customs.*(fee/hold/penalty)", 15), ("job.*(fee/deposit/earn.*lakh)", 15),
    ("upi.*(collect/cashback/refund)", 15), ("http", 10),
]

def smishing_score(text: str) -> dict:
    t = (text or "").lower()
    reasons, score = [], 0
    for pat, pts in SMISH_PATTERNS:
        keys = pat.split("/")
        if any(k in t for k in keys if len(k) > 2):
            reasons.append(f"smishing lure: {pat.split('/')[0]}")
            score += pts
    if re.search(r"(bit\.ly|tinyurl|t\.co|cutt\.ly|\.tk|\.xyz)", t):
        reasons.append("shortened/suspicious link — paste it in Analyze tab URL box")
        score += 15
    score = min(100, score)
    level = "HIGH" if score >= 60 else ("MEDIUM" if score >= 25 else "LOW")
    if not reasons:
        reasons = ["no classic smishing lures"]
    reasons.append("report spam SMS to 1909 / cybercrime.gov.in; never share OTP")
    return {"score": score, "level": level, "reasons": reasons}
