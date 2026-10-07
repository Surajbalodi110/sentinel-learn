"""Arcade: 5 genuinely playable JS games (no quiz radios). Offline, no assets."""

CSS = ("<style>.arc{background:#0B1526;color:#eaf2f8;border-radius:14px;padding:14px;text-align:center;"
       "font-family:sans-serif;user-select:none}.arc button{cursor:pointer}"
       ".ascore{font-size:1.2rem;font-weight:700;color:#00e5cc;margin:6px}"
       ".abtn{background:linear-gradient(90deg,#0e7c6b,#00bfa6);border:none;color:#fff;"
       "border-radius:10px;padding:10px 18px;font-weight:700;margin:4px}"
       ".abtn2{background:#26343f;border:1px solid #2a4358;color:#eaf2f8;border-radius:10px;padding:10px 18px;margin:4px}</style>")

def _wrap(title: str, rules: str, body: str) -> str:
    return (f"{CSS}<div class='arc'><h3 style='margin:4px'>{title}</h3>"
            f"<div style='font-size:.8rem;opacity:.8'>{rules}</div>{body}</div>")


def whack() -> str:
    cells = "".join(f"<button class='cell' id='w{i}'></button>" for i in range(9))
    return _wrap("Whack-a-Phish", "Click ONLY the phish lures. +10 hit, −10 wrong, 30s.",
        f"<div class='ascore' id='ws'>Score: 0 • 30s</div>"
        f"<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:8px;max-width:360px;margin:auto'>{cells}</div>"
        """<script>(function(){var s=0,t=30,iv=null,cur=-1;
var lv=['FREE prize!!!','Urgent: verify','Invoice attached','Hi, lunch?','Meeting notes','Payroll update'];
function tick(){var els=document.querySelectorAll('.cell');els.forEach(function(e,i){e.textContent='';e.style.background='#1b2f47';e.style.border='2px solid #2a4358';e.style.borderRadius='10px';e.style.minHeight='64px';e.style.fontSize='0.72rem';e.style.color='#fff';});
cur=Math.floor(Math.random()*9);var ph=Math.random()<0.55;var el=els[cur];
el.textContent=(ph?'🎣 ':'✉️ ')+lv[Math.floor(Math.random()*lv.length)];el.dataset.ph=ph?'1':'0';
el.style.background=ph?'#5a1f1f':'#1b2f47';}
document.querySelectorAll('.cell').forEach(function(e,i){e.onclick=function(){if(t<=0)return;
if(e.dataset.ph==='1'){s+=10;}else{s-=10;}document.getElementById('ws').textContent='Score: '+s+' • '+t+'s';e.dataset.ph='0';e.style.background='#1b2f47';};});
iv=setInterval(function(){t--;document.getElementById('ws').textContent='Score: '+s+' • '+t+'s';if(t%1===0)tick();if(t<=0){clearInterval(iv);document.getElementById('ws').textContent='DONE! Score: '+s+(s>=80?' — SOC reflexes!':' — try again!');}},1000);tick();})();</script>""")


def ports() -> str:
    return _wrap("Port Panic", "Block exposed-danger ports ONLY (23, 3389, 445, 3306). +25 good, −15 wrong. 30s.",
        """<div class='ascore' id='ps'>Score: 0 • 30s</div><div id='field' style='position:relative;height:300px;background:#101f31;border-radius:10px;overflow:hidden'></div>
<script>(function(){var s=0,t=30;var good={'23':1,'3389':1,'445':1,'3306':1};var all=['443','53','22','80','23','3389','445','3306','8080'];
function spawn(){if(t<=0)return;var f=document.getElementById('field');var d=document.createElement('div');
var p=all[Math.floor(Math.random()*all.length)];d.textContent=':'+p;d.dataset.p=p;
d.style.cssText='position:absolute;left:'+(5+Math.random()*70)+'%;top:-30px;background:#26343f;border:2px solid #00e5cc;color:#fff;border-radius:8px;padding:6px 10px;cursor:pointer;font-weight:700;';
d.onclick=function(){if(t<=0)return;if(good[p]){s+=25;}else{s-=15;}upd();d.remove();};
f.appendChild(d);var y=-30;var fall=setInterval(function(){y+=4;d.style.top=y+'px';if(y>290){clearInterval(fall);d.remove();}},80);}
function upd(){document.getElementById('ps').textContent='Score: '+s+' • '+t+'s';}
var sp=setInterval(function(){if(t>0&&Math.random()<0.7)spawn();},700);
var iv=setInterval(function(){t--;upd();if(t<=0){clearInterval(iv);clearInterval(sp);document.getElementById('ps').textContent='DONE! Score: '+s+(s>=100?' — firewall brain!':' — try again!');}},1000);})();</script>""")


def memory() -> str:
    pairs = [["Brute-force", "T1110"], ["SQL injection", "T1190"], ["XSS", "T1189"],
             ["Phishing link", "T1566.002"], ["Path traversal", "T1083"], ["Remote services", "T1021"]]
    import json
    deck = []
    for i, p in enumerate(pairs):
        deck.append({"t": p[0], "k": i})
        deck.append({"t": p[1], "k": i})
    return _wrap("MITRE Memory", "Flip pairs: attack ↔ technique ID. Fewest moves wins.",
        """<div class='ascore' id='ms'>Moves: 0 • Pairs: 0/6</div><div id='board' style='display:grid;grid-template-columns:repeat(4,1fr);gap:8px;max-width:420px;margin:auto'></div>
<script>(function(){var deck=""" + json.dumps(deck) + """;
deck.sort(function(){return Math.random()-0.5;});var b=document.getElementById('board');var first=null,lock=false,moves=0,found=0;
deck.forEach(function(c){var d=document.createElement('button');d.textContent='?';d.dataset.k=c.k;d.dataset.t=c.t;
d.style.cssText='min-height:64px;border-radius:10px;background:#26343f;color:#fff;border:2px solid #2a4358;font-weight:700;font-size:.72rem;';
d.onclick=function(){if(lock||d.dataset.done||d===first){return;}d.textContent=d.dataset.t;d.style.background='#0e7c6b';
if(!first){first=d;return;}moves++;lock=true;var a=first;first=null;
if(a.dataset.k===d.dataset.k){setTimeout(function(){a.dataset.done='1';d.dataset.done='1';a.style.visibility='hidden';d.style.visibility='hidden';found++;lock=false;upd();if(found===6)document.getElementById('ms').textContent='CLEARED in '+moves+' moves! '+(moves<=10?'— elite memory!':'— nice!');},400);}
else{setTimeout(function(){a.textContent='?';d.textContent='?';a.style.background='#26343f';d.style.background='#26343f';lock=false;upd();},700);}};
b.appendChild(d);});
function upd(){document.getElementById('ms').textContent='Moves: '+moves+' • Pairs: '+found+'/6';}})();</script>""")


def sprint() -> str:
    urls = [["http://192.0.2.9.verify-login.tk/inbox", 1], ["https://accounts.google.com/signin", 0],
            ["http://paypal-secure.ga@login.evil.com/", 1], ["https://example.com/blog/security", 0],
            ["https://bit.ly/FreePrizeWinner2024", 1], ["https://www.cert-in.org.in/", 0],
            ["http://10.0.0.5/bank/update", 1], ["https://github.com/", 0]]
    import json
    return _wrap("Phish-or-Legit Sprint", "Call each URL in 45s. +10, streak bonus every 5.",
        """<div class='ascore' id='ss'>Score: 0 • Streak: 0 • 45s</div>
<div id='url' style='background:#fff;color:#0B1526;border-radius:10px;padding:16px;margin:10px auto;max-width:420px;font-weight:700;word-break:break-all'></div>
<div><button class='abtn' id='bp'>🎣 PHISH</button><button class='abtn2' id='bl'>✅ LEGIT</button></div>
<script>(function(){var urls=""" + json.dumps(urls) + """;var s=0,streak=0,t=45,idx=-1;
function next(){idx=Math.floor(Math.random()*urls.length);document.getElementById('url').textContent=urls[idx][0];}
function upd(){document.getElementById('ss').textContent='Score: '+s+' • Streak: '+streak+' • '+t+'s';}
function go(v){if(t<=0)return;if(urls[idx][1]===v){s+=10;streak++;if(streak%5===0)s+=10;}else{s-=10;streak=0;}upd();next();}
document.getElementById('bp').onclick=function(){go(1);};document.getElementById('bl').onclick=function(){go(0);};
next();var iv=setInterval(function(){t--;upd();if(t<=0){clearInterval(iv);document.getElementById('ss').textContent='DONE! Score: '+s+(s>=80?' — human firewall!':' — try again!');}},1000);})();</script>""")


def patch() -> str:
    return _wrap("Patch Rush", "Click KEV (+25) and Critical (+15) first. Lows waste a click (−10). 30s.",
        """<div class='ascore' id='qs'>Score: 0 • 30s</div><div id='qlist' style='max-width:420px;margin:auto;text-align:left'></div>
<script>(function(){var s=0,t=30,n=0;var pool=[['KEV RCE, internet-facing','kev'],['KEV privesc, servers','kev'],['CVSS 9.8 internet','crit'],['CVSS 8.1 app','crit'],['CVSS 5.4 internal','low'],['CVSS 3.1 test VM','low']];
function spawn(){if(t<=0||n>=14)return;n++;var q=document.getElementById('qlist');var v=pool[Math.floor(Math.random()*pool.length)];
var d=document.createElement('button');d.textContent=(v[1]==='kev'?'🔥 KEV: ':v[1]==='crit'?'🟠 ':'🟢 ')+v[0];d.dataset.k=v[1];
d.style.cssText='display:block;width:100%;text-align:left;margin:5px 0;padding:9px;border-radius:10px;border:1px solid #2a4358;background:'+(v[1]==='kev'?'#5a1f1f':v[1]==='crit'?'#4a3413':'#1b2f47')+';color:#fff;';
d.onclick=function(){if(t<=0)return;if(v[1]==='kev')s+=25;else if(v[1]==='crit')s+=15;else s-=10;
document.getElementById('qs').textContent='Score: '+s+' • '+t+'s';d.remove();};q.appendChild(d);}
function upd(){document.getElementById('qs').textContent='Score: '+s+' • '+t+'s';}
var sp=setInterval(function(){spawn();},1600);spawn();
var iv=setInterval(function(){t--;upd();if(t<=0){clearInterval(iv);clearInterval(sp);document.getElementById('qs').textContent='DONE! Score: '+s+(s>=100?' — patch royalty!':' — try again!');}},1000);})();</script>""")

GAMES = [
    ("whack", "Whack-a-Phish", "Reflex clicking: smash lures, spare legit mail."),
    ("ports", "Port Panic", "Falling packets: block only dangerous exposures."),
    ("memory", "MITRE Memory", "Flip-match attacks to technique IDs."),
    ("sprint", "Phish-or-Legit Sprint", "45 seconds of URL verdicts."),
    ("patch", "Patch Rush", "Triage the vuln queue like a pro."),
]

def get(game_id: str) -> str:
    return {"whack": whack, "ports": ports, "memory": memory,
            "sprint": sprint, "patch": patch}[game_id]()
