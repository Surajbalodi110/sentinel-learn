"""Game specs per lesson: spot / order / match. Rendered in Task 2b."""

GAMES = {
"sec-fund": {"type": "match", "title": "Match the promise", "pairs": {
  "Encrypted customer DB": "Confidentiality", "Signed software update": "Integrity", "Dual power + backups": "Availability"}},
"net-sec": {"type": "spot", "mode": "evil", "prompt": "One of these servers invites ransomware. Which?",
 "items": [{"label": "Web: 443 open, patched, WAF on", "evil": False, "why": "Needed, encrypted, guarded — fine."},
  {"label": "RDP 3389 open to the whole internet", "evil": True, "why": "Global password-guessing + top ransomware vector."},
  {"label": "SSH reachable only via company VPN", "evil": False, "why": "Admin path with encryption + access control."}]},
"endpoint": {"type": "spot", "mode": "evil", "prompt": "Which host is already in trouble?",
 "items": [{"label": "Patched laptop, EDR green, backups tested", "evil": False, "why": " textbook healthy."},
  {"label": "Server 2008, SMBv1 on, no EDR, 'backups someday'", "evil": True, "why": "Wormable + blind + unrecoverable."},
  {"label": "Phone with updates on, MFA everywhere", "evil": False, "why": "Boring and safe."}]},
"iam": {"type": "spot", "mode": "evil", "prompt": "Three access requests land. Deny which?",
 "items": [{"label": "Dev needs staging read for 2 days, manager approved", "evil": False, "why": "Scoped, approved, expring — fine."},
  {"label": "'CEO' (new Gmail) demands permanent prod admin tonight", "evil": True, "why": "Unverified identity + excessive + urgent = classic fraud."},
  {"label": "Analyst requests SIEM read for their team role", "evil": False, "why": "Matches RBAC — approve."}]},
"monitoring": {"type": "spot", "mode": "evil", "prompt": "One log line screams attack. Which?",
 "items": [{"label": "Accepted password for alice from office IP", "evil": False, "why": "Normal success."},
  {"label": "6x Failed password for root from 203.0.113.9", "evil": True, "why": "Brute-force pattern T1110."},
  {"label": "Backup job completed on db-01", "evil": False, "why": "Routine."}]},
"siem": {"type": "order", "title": "Put the pipeline in order", "steps": ["Ingest logs", "Normalize fields", "Correlate signals", "Alert + ticket"]},
"soc-ops": {"type": "order", "title": "Triage in the right order", "steps": ["Validate TP/FP", "Scope blast radius", "Set severity", "Contain or escalate"]},
"ir": {"type": "order", "title": "Respond in the right order", "steps": ["Isolate host", "Remove persistence", "Restore clean", "Learn + fix root cause"]},
"threat-det": {"type": "match", "title": "Detection layer match", "pairs": {
  "Block 203.0.113.9": "IOC (expires fast)", "Flag powershell -enc from Word": "IOA (behavior)", "Alert any password-spray pattern": "TTP (durable)"}},
"malware": {"type": "spot", "mode": "evil", "prompt": "One file must never be opened. Which?",
 "items": [{"label": "report.pdf from known vendor, expected", "evil": False, "why": "Expected + proper extension."},
  {"label": "invoice.pdf.exe from unknown sender", "evil": True, "why": "Double extension trojan carrier."},
  {"label": "team photo.png from colleague", "evil": False, "why": "Ordinary image."}]},
"phish-email": {"type": "spot", "mode": "evil", "prompt": "One mail is a phish. Which?",
 "items": [{"label": "Bank app alert: open the app yourself to check", "evil": False, "why": "No link, directs to official app."},
  {"label": "'Suspended! verify at 192.0.2.9.verify-login.tk'", "evil": True, "why": "Urgency + bare IP + look-alike domain."},
  {"label": "Colleague shares meeting notes link (company domain)", "evil": False, "why": "Known sender, real domain."}]},
"vuln-mgmt": {"type": "spot", "mode": "evil", "prompt": "Patch windows are scarce. Which vuln FIRST?",
 "items": [{"label": "CVSS 4.2 on isolated test VM", "evil": False, "why": "Low impact, no exposure."},
  {"label": "KEV-listed bug on internet web server", "evil": True, "why": "Exploited now + reachable = emergency."},
  {"label": "CVSS 7.5 on internal printer", "evil": False, "why": "Matters, but after the KEV fire."}]},
"ti": {"type": "match", "title": "Match actor to motive", "pairs": {
  "Ransomware gang": "Money", "APT group": "Espionage", "Hacktivist crew": "Message", "Rogue employee": "Grudge or gain"}},
"net-det": {"type": "spot", "mode": "evil", "prompt": "One flow is malware talking. Which?",
 "items": [{"label": "Laptop streaming video, bursty MBs", "evil": False, "why": "Human pattern: bursty, big."},
  {"label": "Server POSTs 500 bytes hourly to unknown IP", "evil": True, "why": "Beaconing: regular, small, strange host."},
  {"label": "Nightly backup to known storage", "evil": False, "why": "Scheduled, known destination."}]},
"appsec": {"type": "spot", "mode": "evil", "prompt": "One input is an attack. Which?",
 "items": [{"label": "Search box: 'blue shoes size 9'", "evil": False, "why": "Plain text, no metacharacters."},
  {"label": "Login: admin' OR '1'='1", "evil": True, "why": "SQLi breaking the query."},
  {"label": "Comment: 'Great article, thanks!'", "evil": False, "why": "No code, no tricks."}]},
"cloud": {"type": "spot", "mode": "evil", "prompt": "One config leaks. Which?",
 "items": [{"label": "Bucket private, MFA root, logging on", "evil": False, "why": "Locked down properly."},
  {"label": "Bucket 'backups' public + indexed", "evil": True, "why": "World-readable data."},
  {"label": "SSH via VPN only, tight groups", "evil": False, "why": "No open admin doors."}]},
"hardening": {"type": "spot", "mode": "good", "prompt": "One server is hardened. Which?",
 "items": [{"label": "Telnet open, admin/admin, all ports answer", "evil": True, "why": "Every bad default at once."},
  {"label": "SSH keys only, default-deny firewall, CIS baseline", "evil": False, "why": "Minimal + locked + verified."},
  {"label": "RDP public 'for convenience', SMBv1 on", "evil": True, "why": "Convenience for attackers too."}]},
"forensics": {"type": "order", "title": "Capture in volatility order", "steps": ["RAM capture", "Disk image", "Logs + artifacts"]},
"automation": {"type": "spot", "mode": "good", "prompt": "One automation is safe to run. Which?",
 "items": [{"label": "Auto-delete mailboxes on any alert", "evil": True, "why": "Destructive + untested FP rate."},
  {"label": "Enrich IOC + draft ticket, human approves blocks", "evil": False, "why": "Machine gathers, human decides."},
  {"label": "Auto-block whole internet on first FP", "evil": True, "why": "Self-inflicted outage."}]},
"frameworks": {"type": "match", "title": "Match map to question", "pairs": {
  "ATT&CK": "HOW do they act?", "Kill Chain": "WHERE to break it?", "NIST CSF": "Is the program complete?", "CIS": "WHAT first?"}},
}

def render_game(spec: dict, lid: str) -> None:
    import random
    import streamlit as st
    st.write("**" + spec.get("title", spec.get("prompt", "Game")) + "**")
    if spec.get("prompt") and spec.get("title"):
        st.write(spec["prompt"])
    elif spec.get("prompt"):
        st.write(spec["prompt"])
    sk, bk = f"streak{lid}", f"best{lid}"
    st.session_state.setdefault(sk, 0)
    st.session_state.setdefault(bk, 0)
    t = spec["type"]
    if t == "spot":
        mode = spec.get("mode", "evil")
        for i, it in enumerate(spec["items"]):
            if st.button(("☠️ " if mode == "evil" else "🛡️ ") + it["label"], key=f"gs{lid}{i}"):
                good = (it["evil"] and mode == "evil") or ((not it["evil"]) and mode == "good")
                if good:
                    st.session_state[sk] += 1
                    st.session_state[bk] = max(st.session_state[bk], st.session_state[sk])
                    st.success(f"Correct! {it['why']}")
                else:
                    st.session_state[sk] = 0
                    st.error(f"Miss. {it['why']}")
                st.rerun()
        st.caption(f"Streak: {st.session_state[sk]} • Best: {st.session_state[bk]}")
    elif t == "order":
        steps = spec["steps"]
        rnd = random.Random(lid)
        order = list(range(len(steps)))
        rnd.shuffle(order)
        letters = "ABCDEFGH"
        for pos, si in enumerate(order):
            st.write(f"{letters[pos]}. {steps[si]}")
        ans = st.text_input("Type the correct order (e.g. BDAC):", key=f"go{lid}", max_chars=len(steps))
        if ans and len(ans.strip()) == len(steps):
            want = "".join(letters[order.index(i)] for i in range(len(steps)))
            if ans.strip().upper() == want:
                st.success("Perfect order! " + " → ".join(steps))
                st.balloons()
            else:
                st.error("Not quite — think cause before effect, then retry.")
    elif t == "match":
        pairs = spec["pairs"]
        rnd = random.Random(lid + "m")
        defs = list(pairs.values())
        rnd.shuffle(defs)
        picks = {}
        for i, term in enumerate(pairs.keys()):
            picks[term] = st.radio(term, defs, key=f"gm{lid}{i}", index=None)
        if st.button("Check matches", key=f"gmgo{lid}"):
            wrong = [t for t, d in picks.items() if pairs[t] != d]
            if not wrong:
                st.success("All matched!")
                st.balloons()
            else:
                st.error(f"{len(wrong)} off — reconsider: {', '.join(wrong)}")
