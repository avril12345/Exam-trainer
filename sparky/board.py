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


PHASE_FILL = {"L1": "#8b5a2b", "L2": "#22262c", "L3": "#8a8f98"}  # brown, black, grey


def draw_board_front(sc: dict, asg: list[dict]) -> str:
    """A front-view picture of the board: enclosure, main switch, devices on the DIN rail,
    phase colours, neutral and earth bars. Updates with the learner's choices."""
    fuse = sc["prot"] == "fuse"
    slots = [96 if t == "3" else 52 for _n, t in sc["loads"]]
    x0 = 24 + 112                      # devices start after the main switch
    W = x0 + sum(slots) + 20
    top, h = 74, 104                   # device row
    s = [f'<svg class="dg" viewBox="0 0 {W} 318" style="min-width:{min(W, 640)}px" role="img" '
         f'aria-label="Front view of the distribution board">',
         f'<rect x="6" y="6" width="{W - 12}" height="306" rx="14" fill="var(--panel)" stroke="var(--ink)" stroke-width="2.5"/>',
         '<text x="20" y="30" class="t" style="font-size:13px">Distribution board — front view</text>',
         f'<text x="{W - 20}" y="30" text-anchor="end" style="font-size:11px">{"Fuses" if fuse else "MCBs / RCBOs"}</text>',
         # DIN rail behind the devices
         f'<rect x="16" y="{top + 42}" width="{W - 32}" height="20" rx="3" fill="#9aa0a6" opacity=".55"/>']

    # main switch (4-pole: L1 L2 L3 N)
    mx = 24
    s.append(f'<rect x="{mx}" y="{top}" width="100" height="{h}" rx="6" fill="#f3f1ec" stroke="var(--ink)" stroke-width="2"/>')
    for k, col in enumerate(["#8b5a2b", "#22262c", "#8a8f98", "#1f6fd1"]):
        s.append(f'<rect x="{mx + 6 + k * 23}" y="{top + 6}" width="19" height="9" rx="2" fill="{col}"/>')
    s.append(f'<rect x="{mx + 14}" y="{top + 36}" width="72" height="30" rx="5" fill="#c0392b"/>'
             f'<text x="{mx + 50}" y="{top + 56}" text-anchor="middle" style="font-size:11px;fill:#fff;font-weight:700">ON</text>'
             f'<text x="{mx + 50}" y="{top + h - 10}" text-anchor="middle" style="font-size:10px;fill:#1d2430">4-pole</text>'
             f'<text x="{mx + 50}" y="{top + h + 20}" text-anchor="middle" class="t" style="font-size:12px">Main switch</text>'
             f'<text x="{mx + 50}" y="{top + h + 35}" text-anchor="middle" style="font-size:10px">L1 L2 L3 N</text>')

    def single(cx: float, dev: str | None, bar: str | None, unset: bool) -> str:
        bw = 34; x = cx - bw / 2
        if unset:
            return (f'<rect x="{x}" y="{top}" width="{bw}" height="{h}" rx="5" fill="none" stroke="var(--muted)" '
                    f'stroke-width="2" stroke-dasharray="5 4"/><text x="{cx}" y="{top + 58}" text-anchor="middle" '
                    f'class="t" style="font-size:20px">?</text>')
        out = [f'<rect x="{x}" y="{top}" width="{bw}" height="{h}" rx="5" fill="#f3f1ec" stroke="var(--ink)" stroke-width="2"/>']
        if bar in PHASE_FILL:
            out.append(f'<rect x="{x + 4}" y="{top + 5}" width="{bw - 8}" height="9" rx="2" fill="{PHASE_FILL[bar]}"/>')
        else:
            out.append(f'<rect x="{x + 4}" y="{top + 5}" width="{bw - 8}" height="9" rx="2" fill="none" '
                       f'stroke="var(--muted)" stroke-dasharray="3 2"/>')
        if fuse:
            out.append(f'<rect x="{x + 7}" y="{top + 24}" width="{bw - 14}" height="54" rx="4" fill="#dcd6c8" stroke="#1d2430"/>'
                       f'<rect x="{cx - 4}" y="{top + 36}" width="8" height="30" rx="2" fill="#b8860b"/>'
                       f'<text x="{cx}" y="{top + h - 8}" text-anchor="middle" style="font-size:9px;fill:#1d2430">FUSE</text>')
        else:
            out.append(f'<rect x="{cx - 7}" y="{top + 38}" width="14" height="26" rx="3" fill="#2b2f36"/>')
            if dev == "RCBO":
                out.append(f'<circle cx="{cx}" cy="{top + 26}" r="6" fill="#f5b700" stroke="#1d2430"/>'
                           f'<text x="{cx}" y="{top + 29.5}" text-anchor="middle" style="font-size:8px;fill:#1d2430;font-weight:700">T</text>')
            label = "RCBO" if dev == "RCBO" else "MCB"
            out.append(f'<text x="{cx}" y="{top + h - 8}" text-anchor="middle" style="font-size:9px;fill:#1d2430;font-weight:700">{label}</text>')
        return "".join(out)

    x = x0
    for i, ((name, t), sw) in enumerate(zip(sc["loads"], slots)):
        a = asg[i] if i < len(asg) else {}
        dev, bar = a.get("dev"), a.get("bar")
        cx = x + sw / 2
        if t == "3":
            if dev == "TP":
                bw = 84; bx = cx - bw / 2
                s.append(f'<rect x="{bx}" y="{top}" width="{bw}" height="{h}" rx="5" fill="#f3f1ec" stroke="var(--ink)" stroke-width="2"/>')
                for k, ph in enumerate(("L1", "L2", "L3")):
                    px = bx + 6 + k * 26
                    s.append(f'<rect x="{px}" y="{top + 5}" width="20" height="9" rx="2" fill="{PHASE_FILL[ph]}"/>'
                             f'<rect x="{px + 3}" y="{top + 38}" width="14" height="26" rx="3" fill="#2b2f36"/>')
                s.append(f'<rect x="{bx + 9}" y="{top + 47}" width="{bw - 18}" height="6" rx="2" fill="#5b6473"/>'
                         f'<text x="{cx}" y="{top + h - 8}" text-anchor="middle" style="font-size:9px;fill:#1d2430;font-weight:700">'
                         f'{"TP FUSE" if fuse else "TP MCB"}</text>')
                sub = "L1 L2 L3"
            elif dev == "SP":
                s.append(single(cx, "SP", None, False))
                s.append(f'<text x="{cx}" y="{top - 6}" text-anchor="middle" style="font-size:10px;fill:var(--bad);font-weight:700">wrong</text>')
                sub = "needs TP"
            else:
                s.append(single(cx, None, None, True))
                sub = "3-phase"
        else:
            unset = (not fuse and not dev)
            s.append(single(cx, dev, bar, unset))
            sub = bar or "pick phase"
        s.append(f'<text x="{cx}" y="{top + h + 20}" text-anchor="middle" class="t" style="font-size:11px">{escape(name)}</text>'
                 f'<text x="{cx}" y="{top + h + 35}" text-anchor="middle" style="font-size:10px">{sub}</text>')
        x += sw

    # neutral and earth bars with one terminal per circuit (+1 for the incoming)
    n_term = len(sc["loads"]) + 1
    for y, label, fill, stroke in ((238, "Neutral bar (N)", "#1f6fd1", "#1f6fd1"), (276, "Earth bar (E)", "#3a9a3a", "#f5b700")):
        bx, bw = 140, n_term * 20 + 20
        dash = 'stroke-dasharray="8 6"' if label.startswith("Earth") else ""
        s.append(f'<text x="24" y="{y + 12}" class="t" style="font-size:12px">{label}</text>'
                 f'<rect x="{bx}" y="{y}" width="{bw}" height="16" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="2.5" {dash}/>')
        for k in range(n_term):
            s.append(f'<circle cx="{bx + 20 + k * 20}" cy="{y + 8}" r="4.5" fill="#d9d4c7" stroke="#1d2430"/>')
    s.append("</svg>")
    return "".join(s)


def draw_board(sc: dict, asg: list[dict]) -> str:
    n = len(sc["loads"]); cw = 58; W = 120 + n * cw
    y1, y2, y3, yN, yE = 40, 58, 76, 262, 284
    bars = {"L1": y1, "L2": y2, "L3": y3}
    s = [f'<svg class="dg" viewBox="0 0 {W} 300" style="min-width:{min(W, 600)}px" role="img" '
         f'aria-label="Distribution board drawing">',
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
