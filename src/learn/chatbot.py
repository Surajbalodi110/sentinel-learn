"""Offline-first SOC tutor bot. Broad cybersecurity KB + optional LLM upgrade."""
import difflib
import os
import re

KB = [
    (("aaa", "authentication vs authorization", "accounting"),
     "AAA = Authentication (prove WHO you are: password + MFA), Authorization (WHAT you may touch: roles/permissions), Accounting (log WHAT happened: audit trail). Example: MFA login -> teacher folder access -> audit log entry. Full lesson: Learn tab Room 1 + Room 4. Source: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html"),
    (("cia triad", "confidentiality", "integrity", "availability"),
     "CIA Triad = three security promises. Confidentiality: only the right eyes (encryption, MFA). Integrity: data stays unaltered (hashing, signatures). Availability: systems work when needed (backups, redundancy). Every attack breaks one: leaks hit confidentiality, ransomware hits availability. Full lesson: Learn tab Room 1. Source: https://www.cisa.gov/cybersecurity-training-exercises"),
    (("ssh", "rdp", "remote desktop", "port 22", "port 3389"),
     "SSH (port 22) and RDP (port 3389) are remote-admin doors attackers knock on all day — our brute-force lab watches exactly this. Never expose them to the internet; use VPN + MFA. Full lesson: Learn tab Room 2 (ports table). Source: https://attack.mitre.org/techniques/T1021/"),
    (("brute force", "t1110", "failed login", "password guess", "credential stuffing", "password spray"),
     "Brute-force (MITRE T1110): attacker guesses passwords, e.g. 6x 'Failed password for root from 203.0.113.9' = HIGH. Types: brute-force, password-spray, credential-stuffing. Defend: MFA + lockout + throttle + strong passwords. Try: Analyze tab with sample_auth.log. Docs: https://attack.mitre.org/techniques/T1110/"),
    (("sql", "sqli", "injection", "t1190", "union select", "owasp a03"),
     "SQL injection (MITRE T1190): input like `' OR '1'='1` or `UNION SELECT password FROM users` breaks DB queries to steal data. Fix: parameterized queries/ORM, least-privilege DB user, WAF, patch. Try sample_web.log lines 1-2. Docs: https://attack.mitre.org/techniques/T1190/ + https://owasp.org/www-project-top-ten/"),
    (("xss", "cross site", "script", "t1189", "csp"),
     "XSS (MITRE T1189): `<script>alert(document.cookie)</script>` runs in victims' browsers to steal sessions. Types: reflected/stored/DOM. Fix: escape output, Content-Security-Policy header, validate input. Try sample_web.log line 3. Docs: https://attack.mitre.org/techniques/T1189/"),
    (("phish", "url", "link", "t1566", "scam", "smish", "sms", "smishing", "vish", "spear"),
     "Phishing (MITRE T1566.002): fake login links using bare IP, @ trick, many subdomains, free TLD (.tk/.ga), urgency words. Paste any link in Analyze - score >=70 = HIGH. Never click suspicious links; verify sender out-of-band, use MFA + password manager. Docs: https://attack.mitre.org/techniques/T1566/002/"),
    (("traversal", "../", "path", "t1083", "lfi", "directory"),
     "Path traversal (MITRE T1083, CWE-22): `../../etc/passwd` escapes web root to read files. Fix: allowlist + normalize paths, low-priv service user, WAF rule. Docs: https://attack.mitre.org/techniques/T1083/"),
    (("ransomware", "malware", "trojan", "virus", "worm", "backdoor", "rootkit", "rat", "keylogger", "spyware", "adware"),
     "Malware basics: virus (needs host), worm (self-spreads), trojan (fake legit), RAT/backdoor (remote control), ransomware (encrypts for ransom), spyware/keylogger (steals). Defend: patch fast (check KEV), EDR/antivirus, backups offline + tested, least privilege, email filtering. If infected: isolate host, preserve logs, restore from clean backup, reset creds. Source: https://www.cisa.gov/stopransomware"),
    (("ddos", "dos", "denial of service", "botnet", "amplification"),
     "DoS/DDoS floods a service to knock it offline (volumetric, protocol, app-layer; often botnets). Defend: CDN/WAF rate-limiting, anycast, upstream blackholing, capacity planning, runbooks. This lab focuses on login/web/phishing rather than traffic floods. Source: https://www.cisa.gov/"),
    (("firewall", "waf", "ids", "ips", "edr", "xdr", "siem", "soar", "antivirus", "vpn"),
     "Defensive stack: firewall (blocks ports/IPs) -> WAF (blocks web attacks like SQLi/XSS) -> IDS/IPS (detects/blocks network signatures) -> EDR (endpoint behavior) -> SIEM (central logs + correlation, e.g. Splunk/Microsoft Sentinel) -> SOAR (auto-playbooks). VPN encrypts remote access. This tool is a mini-SIEM: it does log detection + triage + alerting. Source: https://www.cisa.gov/"),
    (("mfa", "2fa", "otp", "passkey", "password", "hash", "bcrypt", "password manager"),
     "Passwords: long + unique per site, store in a password manager, enable MFA everywhere (authenticator app or passkey > SMS). Servers store salted hashes (bcrypt/argon2), never plaintext. Lockout + throttle logins - exactly what the brute-force detector watches. Source: https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html"),
    (("encrypt", "tls", "https", "ssl", "certificate", "hashing", "aes", "rsa", "pki"),
     "Encryption: TLS/HTTPS protects data in transit (padlock); AES encrypts stored files; RSA/PKI handles key exchange + certificates. Hashing (SHA-256/bcrypt) verifies integrity. If a login page is http (no S) the phishing scorer adds +10 - never enter passwords on http."),
    (("zero trust", "least privilege", "segmentation", "hardening", "patch", "offline backups", "mfa"),
     "Enterprise hardening: patch KEV bugs first, MFA everywhere, least-privilege accounts, network segmentation, CIS benchmarks, tested offline backups, centralized logging + alerting. Map: Analyze risk score -> Trending KEV -> email alert on HIGH. Source: https://www.cisa.gov/zero-trust-maturity-model"),
    (("mitre", "attack", "framework", "tactic", "technique", "d3fend"),
     "MITRE ATT&CK (https://attack.mitre.org/) maps adversary tactics -> techniques (T1110 brute-force, T1190 exploit, T1566 phishing). D3FEND (https://d3fend.mitre.org/) maps defenses. Every finding here shows its technique ID with a direct link - open Resources tab."),
    (("cert", "cert-in", "india", "report incident", "ncipc", "ciso"),
     "CERT-In (https://www.cert-in.org.in/) is India's national CERT: advisories, vulnerability notes, incident reporting for Indian orgs. Global exploited-bug feed: CISA KEV (https://www.cisa.gov/knownExploitedVulnerabilitiesCatalog). Both in Resources tab with in-tool preview."),
    (("cisa", "kev", "trending", "cve", "cvss", "nvd", "exploit", "zero-day", "zero day"),
     "CISA KEV lists CVEs actively exploited - patch these before anything else. CVSS = severity 0-10; NVD (https://nvd.nist.gov/) has details per CVE. This tool's Trending tab fetches KEV and caches to data/kev_cache.json for offline study."),
    (("pyramid of pain", "pyramid", "ioc", "ioa", "ttp", "threat hunting", "threat hunt", "indicator of compromise"),
     "Pyramid of Pain in 30 seconds: detections ranked by how much changing costs the attacker. Bottom (easy to change): hashes, IPs. Middle: domains, tools. Top (painful): TTPs like T1110 password-guessing. Rule: block IOCs fast with expiry dates, but build durable detections on TTPs. Hunting = starting from a hypothesis ('if ransomware is here, shadow copies die first'), not from alerts. Full lesson: Learn tab Room 9. Source: https://attack.mitre.org/"),
    (("siem", "splunk", "sentinel", "qradar", "spl", "kql", "correlation rule", "what is siem"),
     "SIEM in 30 seconds: Splunk and Microsoft Sentinel gather logs from everywhere, then correlation rules combine weak signals into one strong alert ('5 fails + new-country success = account takeover'). Analysts hunt with query languages: SPL (Splunk) or KQL (Sentinel). This tool is a pocket SIEM — try its threshold slider to feel tuning. Full lesson: Learn tab Room 6. Source: https://www.cisa.gov/cybersecurity-training-exercises"),
    (("soc", "analyst", "triage", "respond", "playbook", "incident response", "nist", "kill chain", "dfir"),
     "SOC loop: 1.Triage (severity) 2.Contain (block IP/domain, isolate host) 3.Eradicate (patch, kill malware) 4.Recover 5.Lessons-learned. Frameworks: NIST IR, Cyber Kill Chain, MITRE ATT&CK. Practice here: Learn -> Analyze -> quiz -> tutor. Resume: 'Built offline-first SOC lab: brute-force/SQLi/XSS/phishing + MITRE mapping + risk scoring + AI coaching + Gmail alerting'. Source: https://www.cisa.gov/cybersecurity-training-exercises"),
    (("career", "job", "resume", "interview", "course", "certification", "security+", "ceh", "soc l1", "roadmap", "beginner", "learn"),
     "Beginner SOC roadmap: 1.Networking + Linux basics 2.OWASP Top 10 3.SIEM triage (this tool!) 4.MITRE ATT&CK 5.Certs: CompTIA Security+ -> TryHackMe SOC L1 -> Blue Team L1. Interview tip: demo this project live - inject a brute-force burst, explain T1110 + MFA fix + risk score. Ask me 'how do I become a SOC analyst?' for steps. Source: https://tryhackme.com/"),
    (("network", "port", "tcp", "udp", "dns", "http", "ip", "subnet", "osi"),
     "Networking for defenders: TCP/UDP ports (22 SSH, 80/443 web, 3389 RDP - brute-forced often), DNS (phishing abuses look-alike domains), HTTP vs HTTPS, IP/subnet basics. Watch auth logs for port-22 guessing - the classic brute-force signal in this lab. Source: https://www.cisa.gov/cybersecurity-training-exercises"),
    (("linux", "windows", "log", "event viewer", "syslog", "auth.log", "powershell"),
     "Logs to know: Linux /var/log/auth.log (SSH brute-force - our sample), web access logs (SQLi/XSS probes), Windows Event Viewer (4625 failed logon). Upload any of them in Analyze tab - detectors are format-tolerant. Source: https://www.cisecurity.org/cis-benchmarks"),
    (("social engineer", "pretext", "bait", "quid pro", "tailgate", "awareness"),
     "Social engineering: phishing, pretexting, baiting, quid-pro-quo, tailgating. Defense: verify out-of-band, security awareness training, MFA (so stolen passwords aren't enough), report buttons. Source: https://attack.mitre.org/techniques/T1566/"),
    (("risk", "score", "critical", "enterprise", "severity", "priority"),
     "Risk score here: HIGH=25, MEDIUM=10, LOW=3, cap 100. >=75 or 3 HIGHs = CRITICAL (isolate now). Sample data = 100/100 CRITICAL - ideal demo. Enterprises prioritize by exploitability (KEV) x exposure x asset value. Source: https://nvd.nist.gov/"),
    (("email", "alert", "gmail", "smtp", "notify", "app password"),
     "Email alerts: Gmail App Password in .env (Google Account -> 2-Step ON -> App passwords -> Mail), then `python main.py test-email`. Watch mode emails every new HIGH. No keys = [DRY-RUN] print - still demoable. Source: https://support.google.com/accounts/answer/185833"),
    (("owasp", "top 10", "a01", "broken access", "api security"),
     "OWASP Top 10 (https://owasp.org/www-project-top-ten/): A01 access control, A02 crypto failures, A03 injection (SQLi/XSS in this lab!). After scanning sample_web.log, read A03 + the Cheat Sheets (https://cheatsheetseries.owasp.org/)."),
    (("osint", "footprint", "recon", "username", "breach", "haveibeenpwned", "whois", "subdomain"),
     "OSINT (passive, in the OSINT tab): domain -> DNS + RDAP registration + crt.sh subdomains; IP -> VirusTotal/AbuseIPDB reports; username -> GitHub profile + manual profile links; email -> Gravatar existence + HaveIBeenPwned link. Rule: only your own or consented targets, never scan or log in. Source: https://attack.mitre.org/tactics/TA0043/"),
    (("digital arrest", "digital-arrest", "cbi", "arrest", "video call", "fake police", "ed raid"),
     "Digital-arrest scam (rampant in India): criminals pose as CBI/police/ED on video call, claim you are in a case, and demand money to 'close' it. TRUTH: no agency arrests over video call or demands UPI payment. WHAT TO DO: hang up, never pay, report on https://cybercrime.gov.in/ or helpline 1930. Source: https://cybercrime.gov.in/"),
    (("otp fraud", "otp", "upi fraud", "upi", "otp share", "sim swap", "kyc fraud", "kyc suspend", "fraud", "asked my", "scammed"),
     "OTP/UPI/KYC fraud: anyone asking for your OTP wants to empty your account — banks NEVER ask for OTP, PIN, or CVV. UPI rule: receiving money needs NO PIN; entering PIN = PAYING. SIM-swap: sudden no-signal + strange SMS = call your operator fast. Lost money? Call 1930 within the golden hours + https://cybercrime.gov.in/. Source: https://www.cert-in.org.in/"),
    (("qr code scam", "scan qr receive", "qr fraud"),
     "QR scam: 'scan this QR to RECEIVE money' is a lie — scanning + PIN always SENDS money. Real receiving needs no QR, no PIN. WHAT TO DO: never scan stranger QRs for incoming payments. Source: https://cybercrime.gov.in/"),
    (("job scam", "parcel scam", "customs fee", "part time task", "telegram task"),
     "Job/parcel scams: 'pay a fee to unlock salary/gift' or 'complete paid tasks on Telegram' always ends with YOU paying. Parcels never need customs fees via UPI links. WHAT TO DO: verify on official sites, never pay upfront, report at https://cybercrime.gov.in/. Source: https://www.cert-in.org.in/"),
    (("vpn", "public wifi", "hotspot safe", "what is vpn"),
     "VPN = encrypted tunnel for your traffic: on public WiFi it stops snoopers reading your data. In 30 seconds: home WiFi (your password) > mobile data > public WiFi + VPN > public WiFi raw. VPN does NOT make you hack-proof — phishing still works. Source: https://www.cisa.gov/cybersecurity-training-exercises"),
    (("hacker", "hacking", "white hat", "black hat", "ethical hack"),
     "Hacker = someone skilled with systems; colour = intent. White-hat (ethical): permission + fixes (this is the career). Black-hat: crimes. Grey-hat: no permission, claims good intent (still risky/illegal). Start white-hat here: Learn tab Rooms 1-20, then TryHackMe SOC paths. Source: https://attack.mitre.org/"),
    (("virus vs malware", "worm vs virus", "what is malware", "trojan horse"),
     "Malware in 30 seconds: virus needs a host file, worm spreads alone, trojan pretends to be legit, ransomware encrypts for money, spyware watches quietly. One rule covers most: patch fast + don't run unknown files + keep offline backups. Full lesson: Learn tab Room 10. Source: https://www.cisa.gov/stopransomware"),
    (("zero day", "zeroday", "0-day", "exploit", "payload", "c2 server", "command and control"),
     "Jargon in 30 seconds: zero-day = bug with no fix yet; exploit = code using the bug; payload = what it delivers (e.g. ransomware); C2 = attacker's remote control channel. Defenders watch KEV for exploited bugs and hunt C2 beacons. Full lesson: Learn tab Rooms 9 + 12. Source: https://www.cisa.gov/knownExploitedVulnerabilitiesCatalog"),
    (("dark web", "tor browser", "deep web"),
     "Layers in 30 seconds: surface web (Google), deep web (your email inbox — login-walled, mostly innocent), dark web (Tor onion sites — Mix of whistleblowing and crime markets). Just visiting is not hacking, but buying/doing crime there is. Investigators use it for intel with permission. Source: https://www.cisa.gov/"),
    (("https", "padlock", "lock icon", "http vs https"),
     "Padlock in 30 seconds: HTTPS encrypts traffic (good), but phishing sites ALSO use it — padlock means private, not honest. Check the DOMAIN spelling + who sent the link. Our Analyze tab flags http logins automatically. Full lesson: Learn tab Room 2. Source: https://owasp.org/www-project-top-ten/"),
    (("ip address", "what is my ip", "static ip", "dynamic ip"),
     "IP in 30 seconds: your device's postal address on a network (home IPs usually change = dynamic). Attackers log IPs from every connection — that is how our brute-force detector spots guessers. Never post yours publicly; it aids targeting. Source: https://www.cisa.gov/cybersecurity-training-exercises"),
    (("firewall vs", "antivirus vs", "vpn vs antivirus", "do i need antivirus"),
     "Trio in 30 seconds: firewall = gatekeeper (which doors open), antivirus/EDR = guard spotting criminals inside, VPN = armored tunnel on hostile networks. You need all three doing different jobs. Full lesson: Learn tab Rooms 2 + 3. Source: https://www.cisa.gov/"),
    (("backup", "3-2-1", "ransomware backup"),
     "3-2-1 rule: 3 copies, 2 different media, 1 offline/offsite. Ransomware-proof ONLY if one copy is offline + you test-restored it. Try restoring one file this week. Full lesson: Learn tab Room 3. Source: https://www.cisa.gov/stopransomware"),
    (("report cybercrime", "report fraud", "report", "1930", "where to complain", "cyber police", "lost money"),
     "India in 30 seconds: fraud happened? 1) Call 1930 FAST (money can sometimes be frozen), 2) file at https://cybercrime.gov.in/, 3) tell your bank. For bugs in systems: https://www.cert-in.org.in/. Save these three links now. Source: https://cybercrime.gov.in/"),
    (("where to start", "beginner roadmap", "fresher", "no experience", "switch to cyber"),
     "Roadmap in 30 seconds: 1) Basics here — Rooms 1-5, 2) Hands-on — Analyze/File Check/OSINT tabs, 3) Guided labs — TryHackMe Pre-Security + SOC Level 1, 4) Cert — CompTIA Security+, 5) Proof — this project on GitHub + interview demo. Skip expensive bootcamps until step 4. Full plan: ask 'SOC career roadmap?'. Source: https://tryhackme.com/"),
    (("spam vs phishing", "is spam phishing", "junk mail"),
     "Difference in 30 seconds: spam = bulk junk selling things (annoying, mostly harmless); phishing = targeted lies stealing logins/money (dangerous). Rule: links + urgency + credentials = treat as phish, verify out-of-band. Full lesson: Learn tab Room 11. Source: https://attack.mitre.org/techniques/T1566/"),
    (("hello", "hi", "namaste", "start", "help", "what can you", "thanks", "thank"),
     "Namaste! I'm your always-on SOC tutor. Ask anything: 'what is ransomware?', 'explain MFA', 'what is CERT-In?', 'SOC career roadmap?', 'how to fix SQLi?'. I answer offline instantly; with OPENAI_API_KEY I go deeper. Resources tab has MITRE/CERT-In/CISA one click away. Start: Learn tab Room 1 + https://tryhackme.com/"),
    (("how to use", "how do i use", "how does this work", "analyze tab", "file check", "risk score",
      "osint tab", "learn tab", "rooms", "test email", "upload", "scan my", "course map", "mark reviewed", "quiz", "lesson"),
     "Using this tool in 30 seconds: ANALYZE tab detects attacks in logs/URLs (tick sample data, Analyze); FILE CHECK scans PDFs/images/APKs; OSINT tab looks up domains, usernames, photos (passive only); LEARN tab runs 20 rooms with quizzes; the TUTOR (me!) answers questions anywhere. Risk score: HIGH=25, MEDIUM=10, LOW=3 - 75+ is CRITICAL. Email alerts need a Gmail App Password, then `python main.py test-email`. Deeper labs: https://tryhackme.com/"),
]

_VOCAB: dict = {}
for _keys, _ in KB:
    for _k in _keys:
        for _tok in re.findall(r"[a-z0-9+]+", _k.lower()):
            if len(_tok) >= 4:
                _VOCAB.setdefault(_tok, _keys[0])

def _suggest(ql: str, words: set, top: int = 3) -> list:
    seen, out = set(), []
    for t in sorted(words, key=len, reverse=True):
        if len(t) < 5:
            continue
        for m in difflib.get_close_matches(t, _VOCAB.keys(), n=2, cutoff=0.82):
            label = _VOCAB[m]
            if label not in seen:
                seen.add(label)
                out.append(label)
        if len(out) >= top:
            break
    return out[:top]

FALLBACK = ("I can help with most defensive-security topics: attacks (brute-force, SQLi, XSS, phishing, malware, ransomware, DDoS), "
            "scams (digital arrest, OTP/UPI/KYC, QR, job/parcel), defenses (MFA, firewall, WAF, EDR, SIEM, VPN, backups), "
            "concepts (CIA, AAA, IP, HTTPS, dark web, zero-day), frameworks (MITRE ATT&CK, OWASP, NIST), "
            "India specifics (CERT-In, 1930, cybercrime.gov.in), trending CVEs (CISA KEV/NVD), SOC careers. "
            "Try: 'what is digital arrest?' or 'is public wifi safe?'. "
            "For official docs open the Resources tab.")

def offline_answer(q: str) -> str:
    ql = q.lower()
    words = set(re.findall(r"[a-z0-9+]+", ql))
    best, best_hits = None, 0
    for keys, ans in KB:
        hits = sum(1 for k in keys if k in ql and (len(k) > 4 or k in words))
        if hits > best_hits:
            best, best_hits = ans, hits
    if best:
        return best
    # fuzzy pass: typos like ransomeware/fishing/brutforce
    fbest, fscore = None, 0.0
    for keys, ans in KB:
        for k in keys:
            for tok in re.findall(r"[a-z0-9+]+", k):
                if len(tok) < 5:
                    continue
                for w in words:
                    if len(w) < 5 or w == tok:
                        continue
                    r = difflib.SequenceMatcher(None, w, tok).ratio()
                    if r > fscore:
                        fbest, fscore = ans, r
    if fbest and fscore >= 0.82:
        return fbest + "\n\n(guessed your topic from spelling — ask again if I missed.)"
    sug = _suggest(ql, words)
    if sug:
        return (FALLBACK + f"\n\nClosest matches for you: {', '.join(sug)}. "
                f"Try asking 'what is {sug[0]}?'")
    return FALLBACK

LAST_ENGINE = "built-in"

def answer_stream(q: str):
    """Yield live chunks from local AI, or nothing when unavailable (caller uses answer())."""
    global LAST_ENGINE
    try:
        from src.ai.local_llm import stream as _s, default_model as _dm
        started = False
        for chunk in _s(q):
            if not started:
                LAST_ENGINE = "local-ai:" + _dm()
                started = True
            yield chunk
    except Exception:
        return

def answer(q: str) -> str:
    global LAST_ENGINE
    try:
        from src.ai.local_llm import ask as _llm, default_model as _dm
        llm = _llm(q)
        if llm:
            LAST_ENGINE = "local-ai:" + _dm()
            return llm
    except Exception:
        pass
    LAST_ENGINE = "built-in"
    base = offline_answer(q)
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        return base if base == FALLBACK else base + "\n\n(tip: ask a follow-up like 'show example' or 'how to fix?')"
    try:
        import httpx
        b = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        m = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        r = httpx.post(f"{b}/chat/completions", timeout=25,
            headers={"Authorization": f"Bearer {key}"},
            json={"model": m, "messages": [
                {"role": "system", "content": "Friendly beginner SOC tutor. Under 150 words, plain English, defensive only. End with one official link (MITRE/CERT-In/CISA/OWASP/NVD)."},
                {"role": "user", "content": q + f"\nOffline context: {base}"}],
             "max_tokens": 300})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return base
