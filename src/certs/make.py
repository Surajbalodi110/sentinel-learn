"""Certificates (PNG) + skill maps for resume/LinkedIn. Offline, Pillow only."""

import hashlib
from datetime import date

SKILLS = {
 "sec-fund": ["CIA triad", "AAA model", "Defense-in-depth", "Security controls"],
 "net-sec": ["TCP/IP & ports", "DNS security", "Firewalls", "Segmentation"],
 "endpoint": ["EDR concepts", "Patch prioritization (KEV)", "Hardening basics"],
 "iam": ["MFA design", "RBAC", "Privileged access", "Access reviews"],
 "monitoring": ["Log analysis", "Windows/Linux event IDs", "Threshold tuning"],
 "siem": ["SPL", "KQL", "Correlation rules", "Alert tuning"],
 "soc-ops": ["Alert triage", "Severity vs priority", "Escalation writing"],
 "ir": ["NIST IR phases", "Containment", "Lessons-learned"],
 "threat-det": ["IOCs/IOAs/TTPs", "Pyramid of Pain", "Threat hunting"],
 "malware": ["Malware types", "Sandboxing", "Ransomware response"],
 "phish-email": ["Phishing analysis", "SPF/DKIM/DMARC", "BEC defense"],
 "vuln-mgmt": ["CVE/CVSS", "Risk-based patching", "Nessus/OpenVAS concepts"],
 "ti": ["Threat intel cycle", "ATT&CK mapping", "OSINT"],
 "net-det": ["IDS/IPS", "Wireshark filters", "DNS analysis"],
 "appsec": ["OWASP Top 10", "Injection/XSS fixes", "Access control"],
 "cloud": ["Cloud IAM", "Security groups", "CSPM basics"],
 "hardening": ["CIS benchmarks", "Default-deny", "Drift control"],
 "forensics": ["Evidence handling", "Timeline analysis", "Artifact knowledge"],
 "automation": ["Python for SOC", "SOAR playbooks", "Approval gates"],
 "frameworks": ["MITRE ATT&CK", "NIST CSF", "CIS Controls", "Kill Chain"],
}

NAVY, TEAL, GOLD, WHITE = (11, 21, 38), (0, 191, 166), (233, 196, 106), (234, 242, 248)

ROOM_TITLES = {
 "sec-fund": "Security Fundamentals", "net-sec": "Network Security",
 "endpoint": "Endpoint Security", "iam": "Identity & Access Security",
 "monitoring": "Security Monitoring", "siem": "SIEM", "soc-ops": "SOC Operations",
 "ir": "Incident Response", "threat-det": "Threat Detection",
 "malware": "Malware Defense", "phish-email": "Phishing & Email Security",
 "vuln-mgmt": "Vulnerability Management", "ti": "Threat Intelligence",
 "net-det": "Network Detection", "appsec": "Application Security",
 "cloud": "Cloud Security", "hardening": "Security Hardening",
 "forensics": "Digital Forensics", "automation": "Security Automation",
 "frameworks": "Security Frameworks",
}

SIM_TITLES = {"night-shift": "Night Shift", "ransomware-3am": "Ransomware at 3 AM",
 "insider-exfil": "The Quiet Leaver", "supply-chain": "Poisoned Update",
 "bec-wire": "The $47,000 Email", "ddos-smokescreen": "Noise + Knife"}


def build_resume(name: str, done_ids: list, sim_best: dict) -> str:
    skills = sorted({s for rid in done_ids for s in SKILLS.get(rid, [])})
    sims = [f"{SIM_TITLES.get(k, k)} (best {v})" for k, v in sorted(sim_best.items()) if v]
    L = [f"# {name.strip() or 'Your Name'} — Aspiring SOC Analyst",
         "",
         "## Summary",
         f"Hands-on defensive security training via SentinelLearn SOC Lab: {len(done_ids)}/20 course rooms, "
         f"{len(sims)} live incident simulations" + (", AI-tutored throughout." if done_ids else "."),
         "",
         "## Skills",
         ", ".join(skills) if skills else "Complete rooms to grow this list.",
         "",
         "## Hands-on labs (SentinelLearn)",
         "- Log triage: brute-force (T1110), SQLi/XSS/traversal (T1190/T1189/T1083), phishing URLs (T1566)",
         "- Static file triage: PDF/JS flags, image EXIF, APK permissions; passive OSINT (DNS, RDAP, cert logs)",
         "- Risk scoring (0–100), Gmail alerting, CISA KEV trending",
         "",
         "## Simulations cleared"]
    L += [f"- {s}" for s in sims] or ["- Run your first simulation in the Simulation tab."]
    L += ["",
          "## Coursework",
          f"SentinelLearn SOC Lab by Cyberguru — {len(done_ids)}/20 rooms "
          "(Security Fundamentals → Frameworks), each with labs, games, war stories, quizzes.",
          "",
          "## Tools", "Python, Streamlit, Ollama (local LLM), MITRE ATT&CK, Splunk SPL, KQL, Wireshark, Nmap basics."]
    return "\n".join(L)


def cred_id(name: str, scope: str) -> str:
    h = hashlib.sha256(f"{name.strip().lower()}|{scope}".encode()).hexdigest()[:10].upper()
    return f"CG-{h[:5]}-{h[5:]}"


def _font(size: int):
    from PIL import ImageFont
    import os
    for p in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _bg_image(W: int, H: int):
    """Hero-style backdrop: navy→teal gradient + subtle grid. Pure Pillow."""
    from PIL import Image, ImageDraw
    top, bottom = (11, 21, 38), (14, 77, 68)
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        f = y / max(1, H - 1)
        row = (int(top[0] + (bottom[0] - top[0]) * f),
               int(top[1] + (bottom[1] - top[1]) * f),
               int(top[2] + (bottom[2] - top[2]) * f))
        for x in range(W):
            px[x, y] = row
    d = ImageDraw.Draw(img)
    for x in range(0, W, 28):
        d.line([(x, 0), (x, H)], fill=(24, 40, 60))
    for y in range(0, H, 28):
        d.line([(0, y), (W, y)], fill=(24, 40, 60))
    return img


def _logo_file():
    """Crisp source preferred: assets/logo_large.* beats the web-sized logo."""
    import os
    cands = ["assets/logo_large.png", "assets/logo_large.jpg",
             "assets/logo.png", "assets/logo.jpg"]
    here = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets"))
    for f in cands:
        if os.path.exists(f):
            return f
        p = os.path.join(here, os.path.basename(f))
        if os.path.exists(p):
            return p
    return None


def build(name: str, title: str, subtitle: str, scope: str) -> bytes:
    """Render a 1200x850 certificate PNG on the hero-style backdrop. Returns bytes."""
    from PIL import Image, ImageDraw
    import io
    W, H = 1200, 850
    img = _bg_image(W, H)
    d = ImageDraw.Draw(img)
    d.rectangle([24, 24, W - 24, H - 24], outline=TEAL, width=4)
    d.rectangle([40, 40, W - 40, H - 40], outline=GOLD, width=2)
    logo = _logo_file()
    if logo:
        try:
            from PIL import Image as I
            lg = I.open(logo).convert("RGBA")
            lg.thumbnail((300, 200), I.LANCZOS)
            img.paste(lg, ((W - lg.width) // 2, 56), lg)
        except Exception:
            pass
    cx = W // 2
    d.text((cx, 300), "CYBERGURU  •  SENTINELLEARN", font=_font(26), fill=TEAL, anchor="mm")
    d.text((cx, 370), "Certificate of Completion", font=_font(58), fill=WHITE, anchor="mm")
    d.line([(cx - 180, 420), (cx + 180, 420)], fill=GOLD, width=2)
    d.text((cx, 458), "Proudly presented to", font=_font(24), fill=GOLD, anchor="mm")
    d.text((cx, 524), name.strip()[:40] or "Learner", font=_font(60), fill=WHITE, anchor="mm")
    d.text((cx, 606), title, font=_font(34), fill=TEAL, anchor="mm")
    d.text((cx, 648), subtitle, font=_font(23), fill=GOLD, anchor="mm")
    cid = cred_id(name, scope)
    d.text((cx, 704), f"Credential ID: {cid}", font=_font(24), fill=WHITE, anchor="mm")
    d.text((cx, 734), f"Issued {date.today().isoformat()}",
           font=_font(19), fill=(150, 170, 190), anchor="mm")
    d.line([(180, 776), (430, 776)], fill=GOLD, width=1)
    d.line([(770, 776), (1020, 776)], fill=GOLD, width=1)
    d.text((305, 796), "Cyberguru, Creator", font=_font(22), fill=WHITE, anchor="mm")
    d.text((895, 796), "SentinelLearn SOC Lab", font=_font(22), fill=WHITE, anchor="mm")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
