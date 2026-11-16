"""Board Builder (T2 Q7): distribution board drawing, model answer and checks."""
from __future__ import annotations

from html import escape

BAR_COLOURS = {"L1": "#8b5a2b", "L2": "var(--ink)", "L3": "#8a8f98"}


def model_assign(sc: dict) -> list[dict]:
    out, k = [], 0
    for _name, t in sc["loads"]:
        if t == "3":
            out.append({"dev": "TP", "bar": "L123"})
        else:
            dev = "SP" if sc["prot"] == "fuse" else ("RCBO" if t == "1s" else "SP")
            out.append({"dev": dev, "bar": ["L1", "L2", "L3"][k % 3]})
            k += 1
    return out


def blank_assign(sc: dict) -> list[dict]:
    return [{"dev": None, "bar": "L123"} if t == "3"
            else {"dev": "SP" if sc["prot"] == "fuse" else None, "bar": None}
            for _n, t in sc["loads"]]


def device_choices(sc: dict, t: str) -> list[tuple[str, str]]:
    if t == "3":
        return [("TP", "Triple-pole"), ("SP", "Single-pole")]
    if sc["prot"] == "fuse":
        return []
    return [("SP", "MCB"), ("RCBO", "RCBO")]


def check_board(sc: dict, asg: list[dict]) -> list[str]:
    issues = []
    for (n, t), a in zip(sc["loads"], asg):
        if t == "3" and a.get("dev") != "TP":
            issues.append(f"**{n}**: a 3-phase load needs a **triple-pole** device across L1, L2 and L3.")
        if t != "3" and not a.get("bar"):
            issues.append(f"**{n}**: pick which **phase** it is on.")
        if t != "3" and sc["prot"] != "fuse" and not a.get("dev"):
            issues.append(f"**{n}**: pick **MCB** or **RCBO**.")
        if t == "1s" and a.get("dev") and a.get("dev") != "RCBO":
            issues.append(f"**{n}**: socket circuits need RCD protection. Use an **RCBO**.")
    cnt = {"L1": 0, "L2": 0, "L3": 0}
    for a in asg:
        if a.get("bar") in cnt:
            cnt[a["bar"]] += 1
    all_set = all(t == "3" or a.get("bar") for (_n, t), a in zip(sc["loads"], asg))
    if all_set and max(cnt.values()) - min(cnt.values()) > 1:
        issues.append(f"Phases are **not balanced** (L1: {cnt['L1']}, L2: {cnt['L2']}, L3: {cnt['L3']}). "
                      "Spread the single-phase loads out.")
    return issues


def draw_board(sc: dict, asg: list[dict]) -> str:
    n = len(sc["loads"]); cw = 58; W = 120 + n * cw
    y1, y2, y3, yN, yE = 40, 58, 76, 262, 284
    bars = {"L1": y1, "L2": y2, "L3": y3}
    s = [f'<svg class="dg" viewBox="0 0 {W} 300" role="img" aria-label="Distribution board drawing">',
         '<rect x="8" y="30" width="52" height="56" rx="4" class="fs s"/>'
         '<text x="34" y="54" text-anchor="middle" class="t">Main</text>'
         '<text x="34" y="68" text-anchor="middle">switch</text><text x="8" y="22">Supply</text>']
    for k, y in bars.items():
        s.append(f'<path d="M60 {y} H{W - 24}" stroke="{BAR_COLOURS[k]}" stroke-width="4" stroke-linecap="round"/>'
                 f'<text x="{W - 6}" y="{y + 4}" text-anchor="end" class="t">{k}</text>')
    s.append(f'<path d="M60 {yN} H{W - 24}" stroke="#1f6fd1" stroke-width="4" stroke-linecap="round"/>'
             f'<text x="{W - 6}" y="{yN + 4}" text-anchor="end" class="t">N</text>')
    s.append(f'<path d="M60 {yE} H{W - 24}" stroke="#3a9a3a" stroke-width="4" stroke-dasharray="8 5" stroke-linecap="round"/>'
             f'<text x="{W - 6}" y="{yE + 4}" text-anchor="end" class="t">E</text>')
    s.append(f'<path class="s" d="M34 86 V{yN} H60"/>')
    for i, (name, t) in enumerate(sc["loads"]):
        cx = 100 + i * cw; a = asg[i] if i < len(asg) else {}; three = t == "3"
        dev, bar = a.get("dev"), a.get("bar")
        if dev == "TP":
            label = "TP fuse" if sc["prot"] == "fuse" else "TP MCB"
        elif dev == "RCBO":
            label = "RCBO"
        else:
            label = "Fuse" if sc["prot"] == "fuse" else "MCB"
        if dev == "TP":
            for k, y in enumerate((y1, y2, y3)):
                x = cx - 12 + k * 12
                s.append(f'<path class="s" d="M{x} {y} V112"/><circle cx="{x}" cy="{y}" r="3.5" class="fi"/>')
        elif bar in bars:
            y = bars[bar]
            s.append(f'<path d="M{cx} {y} V112" stroke="{BAR_COLOURS[bar]}" stroke-width="2.5"/>'
                     f'<circle cx="{cx}" cy="{y}" r="4" class="fi"/>')
        bad = (three and dev and dev != "TP") or (not three and not bar)
        dash = 'stroke-dasharray="4 3"' if bad else ""
        s.append(f'<rect x="{cx - 21}" y="112" width="42" height="34" rx="4" class="s" fill="var(--panel)" {dash}/>'
                 f'<text x="{cx}" y="133" text-anchor="middle" style="font-size:10.5px" class="t">{label if dev else "?"}</text>')
        s.append(f'<path class="s" d="M{cx} 146 V172"/><path class="s" d="M{cx - 6} 172 h12"/>')
        sub = "3-phase" if three else (bar or "—")
        s.append(f'<text x="{cx}" y="190" text-anchor="middle" class="t" style="font-size:11px">{escape(name)}</text>'
                 f'<text x="{cx}" y="204" text-anchor="middle" style="font-size:10px">{sub}</text>')
        if not three:
            s.append(f'<path d="M{cx + 18} 146 V{yN}" stroke="#1f6fd1" stroke-width="1.5" stroke-dasharray="3 3" fill="none"/>'
                     f'<circle cx="{cx + 18}" cy="{yN}" r="3" fill="#1f6fd1"/>')
    s.append("</svg>")
    return "".join(s)
