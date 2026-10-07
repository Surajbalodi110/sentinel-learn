"""Diagram builders: crisp inline SVG, offline, responsive. ASCII only."""

_C = ["#0e7c6b", "#12324a", "#7c3aed", "#b7791f", "#d00000", "#0B1526", "#2a9d8f", "#e76f51"]

def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def triangle(title: str, levels: list) -> str:
    """levels bottom->top: [{label, sub}]. Pyramid SVG."""
    n = len(levels)
    W, top_w, H = 560, 170, 66
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>',
             f'<svg viewBox="0 0 {W} {n * H + 8}" style="width:100%;max-width:640px;height:auto;display:block;margin:auto">']
    for i, lv in enumerate(levels):
        y = (n - 1 - i) * H
        frac0, frac1 = i / n, (i + 1) / n
        w0 = top_w + (W - top_w) * frac0
        w1 = top_w + (W - top_w) * frac1
        x0, x1 = (W - w0) / 2, (W - w1) / 2
        c = _C[i % len(_C)]
        parts.append(f'<polygon points="{x0},{y} {x0 + w0},{y} {x1 + w1},{y + H} {x1},{y + H}" fill="{c}" opacity="0.88" stroke="#fff" stroke-width="2"/>')
        parts.append(f'<text x="{W/2}" y="{y + 27}" text-anchor="middle" fill="#fff" font-size="14" font-weight="bold">{_esc(lv["label"])}</text>')
        if lv.get("sub"):
            parts.append(f'<text x="{W/2}" y="{y + 47}" text-anchor="middle" fill="#ffffffdd" font-size="10.5">{_esc(lv["sub"])}</text>')
    parts.append("</svg>")
    return "".join(parts)

def stack(title: str, rows: list) -> str:
    """rows top->bottom: [{label, sub}]. Layer bars."""
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>']
    for i, r in enumerate(rows):
        c = _C[i % len(_C)]
        parts.append(f'<div style="background:{c};color:#fff;border-radius:10px;padding:9px 14px;margin:6px 0;box-shadow:0 3px 10px rgba(0,0,0,.18)">'
                     f'<b>{_esc(r["label"])}</b><div style="font-size:.8rem;opacity:.9">{_esc(r.get("sub", ""))}</div></div>')
        if i < len(rows) - 1:
            parts.append('<div style="text-align:center;color:#0e7c6b;font-weight:700">&#8595;</div>')
    return "".join(parts)

def pipeline(title: str, steps: list) -> str:
    """Horizontal flow with arrows. steps: [str]."""
    cells = []
    for i, s in enumerate(steps):
        c = _C[i % len(_C)]
        cells.append(f'<div style="flex:1;min-width:110px;background:{c};color:#fff;border-radius:10px;padding:9px 8px;text-align:center;font-size:.78rem"><b>{i+1}</b><br>{_esc(s)}</div>')
        if i < len(steps) - 1:
            cells.append('<div style="align-self:center;color:#0B1526;font-weight:700">&#8594;</div>')
    return (f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>'
            f'<div style="display:flex;gap:6px;flex-wrap:wrap;align-items:stretch">{"".join(cells)}</div>')

def arch(title: str, boxes: list, note: str = "") -> str:
    """Vertical boxes with arrows. boxes: [{label, sub}]."""
    return stack(title, boxes) + (f'<div style="font-size:.8rem;opacity:.8">{_esc(note)}</div>' if note else "")

def arch(title: str, boxes: list, note: str = "") -> str:
    """Vertical boxes with arrows. boxes: [{label, sub}]."""
    return stack(title, boxes) + (f'<div style="font-size:.8rem;opacity:.8">{_esc(note)}</div>' if note else "")

def rings(title: str, rings: list) -> str:
    """Concentric circles left, color legend right: [{label}]. SVG."""
    cx = cy = 145
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>',
             '<svg viewBox="0 0 470 300" style="width:100%;max-width:560px;height:auto;display:block;margin:auto">']
    n = len(rings)
    for i, r in enumerate(rings):
        rad = 132 - i * (108 / max(1, n))
        if rad < 18:
            rad = 18
        c = _C[i % len(_C)]
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="{c}" opacity="0.88" stroke="#fff" stroke-width="2"/>')
    for i, r in enumerate(rings):
        y = 60 + i * 34
        c = _C[i % len(_C)]
        parts.append(f'<circle cx="308" cy="{y - 4}" r="7" fill="{c}" stroke="#fff" stroke-width="1.5"/>')
        parts.append(f'<text x="322" y="{y}" font-size="13" fill="#0B1526">{_esc(r["label"])}</text>')
    parts.append("</svg>")
    return "".join(parts)

def topology(title: str, nodes: list) -> str:
    """nodes: [{label, zone}] horizontal zones with icons. HTML."""
    cells = []
    for i, nd in enumerate(nodes):
        c = _C[i % len(_C)]
        cells.append(f'<div style="flex:1;min-width:100px;background:{c};color:#fff;border-radius:12px;padding:10px 6px;text-align:center;font-size:.75rem">🌐<br><b>{_esc(nd["label"])}</b><br><small>{_esc(nd.get("zone", ""))}</small></div>')
        if i < len(nodes) - 1:
            cells.append('<div style="align-self:center;font-weight:700">🔥</div>')
    return (f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>'
            f'<div style="display:flex;gap:6px;flex-wrap:wrap;align-items:stretch">{"".join(cells)}</div>')

def meters(title: str, meters: list) -> str:
    """meters: [{label, pct}]. Progress-bar gauges."""
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>']
    for i, m in enumerate(meters):
        p = max(0, min(100, int(m.get("pct", 50))))
        c = "#d00000" if p >= 75 else ("#e9c46a" if p >= 40 else "#2a9d8f")
        parts.append(f'<div style="font-size:.8rem;margin-top:6px">{_esc(m["label"])} — {p}%</div>'
                     f'<div style="background:#e6e8ec;border-radius:8px;height:12px"><div style="width:{p}%;background:{c};height:12px;border-radius:8px"></div></div>')
    return "".join(parts)

def flowchart(title: str, steps: list) -> str:
    """steps: [{q, yes, no}] decision chain rendered as cards."""
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>']
    for s in steps:
        parts.append(f'<div class="card" style="border-left:5px solid #7c3aed">❓ <b>{_esc(s["q"])}</b><br>'
                     f'<span style="color:#2a9d8f">✔ { _esc(s.get("yes", ""))}</span> &nbsp; <span style="color:#d00000">✘ {_esc(s.get("no", ""))}</span></div>')
    return "".join(parts)

def logstream(title: str, lines: list) -> str:
    """Fake terminal log lines: [{t, evil}]."""
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>',
             '<div style="background:#0B1526;color:#c8e6c9;border-radius:10px;padding:12px;font-family:monospace;font-size:.75rem">']
    for ln in lines:
        c = "#ff8a80" if ln.get("evil") else "#9ccc9c"
        mark = "🚨" if ln.get("evil") else "·"
        parts.append(f'<div style="color:{c}">{mark} {_esc(ln["t"])}</div>')
    parts.append("</div>")
    return "".join(parts)

def funnel(title: str, stages: list) -> str:
    """stages: [{label, n}]. Wide->narrow bars."""
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>']
    for i, s in enumerate(stages):
        w = 100 - i * (60 / max(1, len(stages)))
        c = _C[i % len(_C)]
        parts.append(f'<div style="width:{w}%;margin:4px auto;background:{c};color:#fff;border-radius:8px;text-align:center;padding:7px;font-size:.78rem">{_esc(s["label"])} ({s.get("n", "")})</div>')
    return "".join(parts)

def kanban(title: str, cols: list) -> str:
    """cols: [{label, cards[]}]. Board columns."""
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div><div style="display:flex;gap:8px;flex-wrap:wrap">']
    for i, col in enumerate(cols):
        c = _C[i % len(_C)]
        cards = "".join(f'<div style="background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:6px;margin:5px 0;font-size:.75rem">🎫 {_esc(x)}</div>' for x in col.get("cards", []))
        parts.append(f'<div style="flex:1;min-width:130px;background:#f1f3f6;border-radius:10px;padding:8px"><b style="color:{c}">{_esc(col["label"])}</b>{cards}</div>')
    parts.append("</div>")
    return "".join(parts)

def wheel(title: str, steps: list) -> str:
    """Circular cycle: steps arranged around. SVG numbered dots."""
    import math
    cx = cy, R = 150, 105
    cx = cy = 150
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)} (cycle repeats)</div>',
             '<svg viewBox="0 0 300 300" style="width:100%;max-width:360px;height:auto;display:block;margin:auto">']
    n = len(steps)
    pts = []
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#0e7c6b" stroke-width="2" stroke-dasharray="5,4" marker-end="none"/>')
    for i, (x, y) in enumerate(pts):
        c = _C[i % len(_C)]
        parts.append(f'<circle cx="{x}" cy="{y}" r="17" fill="{c}" stroke="#fff" stroke-width="2"/><text x="{x}" y="{y+5}" text-anchor="middle" fill="#fff" font-size="13" font-weight="bold">{i+1}</text>')
    parts.append("</svg><ol style='font-size:.82rem'>" + "".join(f"<li>{_esc(s)}</li>" for s in steps) + "</ol>")
    return "".join(parts)

def branches(title: str, root: str, arms: list) -> str:
    """arms: [{label, sub}]. Root splits into branches."""
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>',
             f'<div style="text-align:center;background:#0B1526;color:#fff;border-radius:10px;padding:8px;margin-bottom:4px">📥 {_esc(root)}</div><div style="display:flex;gap:8px;flex-wrap:wrap">']
    for i, a in enumerate(arms):
        c = _C[i % len(_C)]
        parts.append(f'<div style="flex:1;min-width:120px;background:{c};color:#fff;border-radius:10px;padding:9px;font-size:.78rem"><b>{_esc(a["label"])}</b><br><small>{_esc(a.get("sub", ""))}</small></div>')
    parts.append("</div>")
    return "".join(parts)

def emailmock(title: str, lines: list) -> str:
    """Annotated fake email. lines: [{t, flag}]; flag=True highlights red."""
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)} — spot the red flags</div>',
             '<div style="border:1px solid #e0e0e0;border-radius:12px;padding:12px;background:#fff;font-size:.82rem">']
    for ln in lines:
        if ln.get("flag"):
            parts.append(f'<div style="background:#ffe1e1;border-left:4px solid #d00000;padding:6px;margin:5px 0">🚩 {_esc(ln["t"])}<br><small>{_esc(ln.get("why", ""))}</small></div>')
        else:
            parts.append(f'<div style="padding:4px 6px">{_esc(ln["t"])}</div>')
    parts.append("</div>")
    return "".join(parts)

def heatmap(title: str, rows: list, cols: list, cells: dict) -> str:
    """cells: {(r,c): level 0-3}. Matrix table."""
    shades = ["#e3f5e9", "#fff7d6", "#ffeed9", "#ffc9c9"]
    h = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div><table style="border-collapse:collapse;font-size:.78rem"><tr><th></th>']
    h += "".join(f"<th style='padding:6px'>{_esc(c)}</th>" for c in cols)
    h += "</tr>"
    for r in rows:
        h.append("<tr>")
        h.append(f"<th style='padding:6px;text-align:left'>{_esc(r)}</th>")
        for c in cols:
            v = cells.get((r, c), 0)
            h.append(f"<td style='background:{shades[v]};padding:8px;border:1px solid #fff;text-align:center'>{['LOW','MED','HIGH','FIX NOW'][v]}</td>")
        h.append("</tr>")
    h.append("</table>")
    return "".join(h)

def merge(title: str, ins: list, out: str) -> str:
    """Many feeds into one diamond into action."""
    cells = "".join(f'<div style="flex:1;min-width:100px;background:#12324a;color:#fff;border-radius:10px;padding:8px;text-align:center;font-size:.75rem">📡<br>{_esc(x)}</div>' for x in ins)
    return (f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div><div style="display:flex;gap:6px;flex-wrap:wrap">{cells}</div>'
            f'<div style="text-align:center;font-size:1.4rem">⬇️</div>'
            f'<div style="text-align:center;background:#7c3aed;color:#fff;border-radius:10px;padding:8px">🔷 Correlate + score</div>'
            f'<div style="text-align:center;font-size:1.4rem">⬇️</div>'
            f'<div style="text-align:center;background:#2a9d8f;color:#fff;border-radius:10px;padding:8px">✅ {_esc(out)}</div>')

def packet(title: str, fields: list) -> str:
    """fields: [{label, evil}]. Layered packet bars."""
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>']
    for f in fields:
        bg = "#d00000" if f.get("evil") else "#12324a"
        mark = " 🚨 EVIL" if f.get("evil") else ""
        parts.append(f'<div style="background:{bg};color:#fff;border-radius:8px;padding:8px;margin:5px 0;font-family:monospace;font-size:.78rem">{_esc(f["label"])}{mark}<br><small>{_esc(f.get("sub", ""))}</small></div>')
    return "".join(parts)

def gates(title: str, gates: list) -> str:
    """gates: [{label, check}]. Vertical checkpoints."""
    parts = [f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>']
    for i, g in enumerate(gates):
        icon = "✅" if g.get("check") else "🚫"
        parts.append(f'<div class="card" style="text-align:center">{icon} <b>{_esc(g["label"])}</b><br><small>{_esc(g.get("sub", ""))}</small></div>')
        if i < len(gates) - 1:
            parts.append('<div style="text-align:center">⬇️</div>')
    return "".join(parts)

def splitbar(title: str, left: str, right: str, pct: int) -> str:
    """Two-sided responsibility bar."""
    return (f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>'
            f'<div style="display:flex;border-radius:10px;overflow:hidden;color:#fff;font-size:.78rem">'
            f'<div style="width:{pct}%;background:#7c3aed;padding:10px;text-align:center">{_esc(left)} {pct}%</div>'
            f'<div style="width:{100-pct}%;background:#0e7c6b;padding:10px;text-align:center">{_esc(right)} {100-pct}%</div></div>')

def beforeafter(title: str, before: list, after: list) -> str:
    """Two-column comparison."""
    b = "".join(f"<li>{_esc(x)}</li>" for x in before)
    a = "".join(f"<li>{_esc(x)}</li>" for x in after)
    return (f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>'
            f'<div style="display:flex;gap:8px;flex-wrap:wrap"><div class="card" style="flex:1;min-width:150px;border-top:3px solid #d00000"><b>❌ Before</b><ul>{b}</ul></div>'
            f'<div class="card" style="flex:1;min-width:150px;border-top:3px solid #2a9d8f"><b>✅ After</b><ul>{a}</ul></div></div>')

def timeline(title: str, events: list) -> str:
    """events: [{t, label}]. Horizontal time axis."""
    dots = []
    for i, e in enumerate(events):
        c = _C[i % len(_C)]
        dots.append(f'<div style="flex:1;min-width:90px;text-align:center;font-size:.72rem"><div style="background:{c};color:#fff;border-radius:50%;width:30px;height:30px;line-height:30px;margin:auto">{i+1}</div><b>{_esc(e["t"])}</b><br>{_esc(e["label"])}</div>')
    return (f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>'
            f'<div style="display:flex;gap:4px;align-items:flex-start">{"".join(dots)}</div>')

def loop(title: str, steps: list, gate: str) -> str:
    """Cycle with approval diamond."""
    cells = []
    for i, s in enumerate(steps):
        cells.append(f'<div style="flex:1;min-width:100px;background:#12324a;color:#fff;border-radius:10px;padding:8px;text-align:center;font-size:.75rem">{i+1}. {_esc(s)}</div>')
    return (f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div><div style="display:flex;gap:6px;flex-wrap:wrap">{"".join(cells)}</div>'
            f'<div style="text-align:center;margin:8px 0"><span style="background:#fff;border:3px solid #e9c46a;border-radius:12px;padding:8px 14px;display:inline-block">🔷 Human gate: {_esc(gate)}</span></div>'
            f'<div style="text-align:center">🔁 repeats every alert</div>')

def mindmap(title: str, center: str, arms: list) -> str:
    """arms: [{label, sub}]. Center with branches."""
    cells = "".join(f'<div style="flex:1;min-width:120px;background:#f1f3f6;border:2px solid #0e7c6b;border-radius:10px;padding:8px;font-size:.75rem"><b>{_esc(a["label"])}</b><br><small>{_esc(a.get("sub", ""))}</small></div>' for a in arms)
    return (f'<div style="font-weight:700;margin:4px 0">{_esc(title)}</div>'
            f'<div style="text-align:center;background:linear-gradient(135deg,#0B1526,#0e7c6b);color:#fff;border-radius:12px;padding:10px;margin-bottom:8px"><b>{_esc(center)}</b></div>'
            f'<div style="display:flex;gap:8px;flex-wrap:wrap">{"".join(cells)}</div>')

def render(spec: dict) -> str:
    k = spec.get("kind", "pipeline")
    if k == "triangle":
        return triangle(spec.get("title", ""), spec.get("levels", []))
    if k == "stack":
        return stack(spec.get("title", ""), spec.get("rows", []))
    if k == "arch":
        return arch(spec.get("title", ""), spec.get("boxes", []), spec.get("note", ""))
    if k == "rings":
        return rings(spec.get("title", ""), spec.get("rings", []))
    if k == "topology":
        return topology(spec.get("title", ""), spec.get("nodes", []))
    if k == "meters":
        return meters(spec.get("title", ""), spec.get("meters", []))
    if k == "flowchart":
        return flowchart(spec.get("title", ""), spec.get("steps", []))
    if k == "logstream":
        return logstream(spec.get("title", ""), spec.get("lines", []))
    if k == "funnel":
        return funnel(spec.get("title", ""), spec.get("stages", []))
    if k == "kanban":
        return kanban(spec.get("title", ""), spec.get("cols", []))
    if k == "wheel":
        return wheel(spec.get("title", ""), spec.get("steps", []))
    if k == "branches":
        return branches(spec.get("title", ""), spec.get("root", ""), spec.get("arms", []))
    if k == "emailmock":
        return emailmock(spec.get("title", ""), spec.get("lines", []))
    if k == "heatmap":
        return heatmap(spec.get("title", ""), spec.get("rows", []), spec.get("cols", []), spec.get("cells", {}))
    if k == "merge":
        return merge(spec.get("title", ""), spec.get("ins", []), spec.get("out", ""))
    if k == "packet":
        return packet(spec.get("title", ""), spec.get("fields", []))
    if k == "gates":
        return gates(spec.get("title", ""), spec.get("gates", []))
    if k == "splitbar":
        return splitbar(spec.get("title", ""), spec.get("left", ""), spec.get("right", ""), int(spec.get("pct", 50)))
    if k == "beforeafter":
        return beforeafter(spec.get("title", ""), spec.get("before", []), spec.get("after", []))
    if k == "timeline":
        return timeline(spec.get("title", ""), spec.get("events", []))
    if k == "loop":
        return loop(spec.get("title", ""), spec.get("steps", []), spec.get("gate", ""))
    if k == "mindmap":
        return mindmap(spec.get("title", ""), spec.get("center", ""), spec.get("arms", []))
    return pipeline(spec.get("title", ""), spec.get("steps", []))
