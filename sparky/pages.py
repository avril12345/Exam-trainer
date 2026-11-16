"""All app screens. Each public function is one page in the navigation.

Screens inside a page (e.g. a question in progress) live in ``st.session_state``.
"""
from __future__ import annotations

import random
import re
import time
from html import escape

import streamlit as st

from . import store, ui
from .board import blank_assign, check_board, device_choices, draw_board, model_assign
from .content import (BOARD_SCEN, BOX_NAMES, CARDS, DIAG, MCQ, SLOT_LAB, SLOT_TITLE, SLOTS, SYM,
                      SYMBOLS, bold, fx, slot_cards, slot_pct, strip_tags, sym, sym_plain)
from .formulas import GEN_BY_ID, GENS, is_correct, n3

ss = st.session_state
PAGES: dict = {}  # filled in by streamlit_app.py: name -> st.Page


def go(name: str) -> None:
    st.switch_page(PAGES[name])


def marks(n: int) -> str:
    return ui.plural(n, "mark")


def grade(pc: float) -> str:
    return "Distinction" if pc >= 80 else "Merit" if pc >= 65 else "Pass" if pc >= 50 else "Not yet a pass"


def round_half_up(x: float) -> int:
    return int(x + 0.5)


def back_button(label: str, on_click, key: str) -> None:
    st.button(f"‹ {label}", on_click=on_click, key=key)


# =============================================================================== HOME
def home():
    S = store.S()
    cur, nxt = store.level()
    pct = round((S["xp"] - cur[0]) / (nxt[0] - cur[0]) * 100) if nxt else 100
    acc = round(S["correct"] / S["answered"] * 100) if S["answered"] else 0
    best = "—" if S["mockBest"] is None else f"{S['mockBest']}%"
    to_next = f"{nxt[0] - S['xp']} XP to {nxt[1]}" if nxt else "Top level reached"
    ui.html(f"""<div class="panel">
      <div class="row" style="justify-content:space-between"><h2 style="margin:0">{cur[1]}</h2>{ui.chip(f"{S['xp']} XP")}</div>
      <div class="bar"><i style="width:{pct}%"></i></div><div class="small muted">{to_next}</div>
      <div class="stats"><div class="stat"><b>{S['answered']}</b><span>answered</span></div>
      <div class="stat"><b>{acc}%</b><span>accuracy</span></div><div class="stat"><b>{best}</b><span>best mock T2</span></div></div></div>""")

    with st.container(border=True):
        ui.html(f"""<div class="row" style="justify-content:space-between"><h2 style="margin:0">T2 Installation</h2>{ui.chip('Main focus', 't2')}</div>
        <p class="muted">The T2 paper has the <b>same 20 questions</b> in the same order every year. Only the wording changes.
        Learn each question slot and you know the paper.</p>""")
        c1, c2 = st.columns(2)
        c1.page_link(PAGES["mock"], label="Mock T2 paper", icon=":material/description:", width="stretch")
        c2.page_link(PAGES["t2"], label="T2 paper map", icon=":material/grid_view:", width="stretch")
        st.page_link(PAGES["board"], label="Board Builder (Q7)", icon=":material/electrical_services:", width="stretch")
        weak = sorted(((n, t, slot_pct(n, S["boxes"])) for n, t in SLOTS), key=lambda x: x[2])[:3]
        st.caption("Weakest question slots right now")
        for n, t, p in weak:
            if st.button(f"Q{n} · {t} · {p}% known", key=f"weak_{n}", width="stretch"):
                ss.t2_slot = n
                go("t2")

    st.subheader("Practise")
    c1, c2 = st.columns(2)
    c1.page_link(PAGES["cards"], label="Flashcards", icon=":material/style:", width="stretch")
    c2.page_link(PAGES["quiz"], label="Quick Shift quiz", icon=":material/timer:", width="stretch")
    c1.page_link(PAGES["lab"], label="Formula Lab", icon=":material/calculate:", width="stretch")
    c2.page_link(PAGES["maths"], label="Maths", icon=":material/function:", width="stretch")
    c1.page_link(PAGES["pictures"], label="Diagrams", icon=":material/schema:", width="stretch")
    c2.page_link(PAGES["snap"], label="Symbol Snap", icon=":material/bolt:", width="stretch")

    if S["missed"]:
        with st.container(border=True):
            st.markdown(f"**Review your misses** — {ui.plural(len(S['missed']), 'question')} to go back over")
            if st.button("Review misses", type="primary", key="home_review"):
                start_quiz("review")
                go("quiz")

    with st.container(border=True):
        st.markdown("**Colour code used in calculations**")
        ui.html(f"""<div class="legend"><span>{sym('V')} voltage</span><span>{sym('I')} current</span>
          <span>{sym('R')} {sym('Z')} {sym('XL')} resistance / impedance</span><span>{sym('P')} power</span>
          <span>{sym('f')} {sym('ns')} {sym('tau')} frequency, speed, time</span><span>{sym('pf')} {sym('B')} other</span></div>""")

    with st.expander("Reset my progress"):
        st.write("This clears XP, scores and flashcard boxes on this device. Display settings are kept.")
        if st.checkbox("Yes, I want to start again", key="reset_ok"):
            st.button("Reset progress", on_click=store.reset, key="reset_btn")


# =============================================================================== T2 MAP
def t2_map():
    S = store.S()
    n = ss.get("t2_slot")
    if n:
        return _slot_detail(n)
    st.header("T2 paper map")
    st.markdown("Every T2 paper from 2016 to 2026 follows this order. "
                "Tap a question to see **every version** that has been asked, and practise it.")
    c1, c2 = st.columns(2)
    c1.page_link(PAGES["mock"], label="Sit a mock T2", icon=":material/description:", width="stretch")
    c2.page_link(PAGES["board"], label="Board Builder (Q7)", icon=":material/electrical_services:", width="stretch")
    cols = st.columns(2)
    for k, (num, title) in enumerate(SLOTS):
        p = slot_pct(num, S["boxes"])
        v = len(slot_cards(num))
        with cols[k % 2]:
            st.button(f"Q{num} · {title}  ·  {p}%", key=f"slot_{num}", width="stretch",
                      help=f"{ui.plural(v, 'version')}, {p}% known",
                      on_click=lambda num=num: ss.update(t2_slot=num))
    ui.html('<div class="note">The % goes up as you mark cards <b>Got it</b>. Cards tagged '
            '<span class="chip chk">Check ET101</span> quote the regs. Check those in the ET101 book, '
            'because the model answers do not always agree.</div>')


def _slot_detail(n: int):
    back_button("Paper map", lambda: ss.update(t2_slot=None), "slot_back")
    idx = slot_cards(n)
    ui.html(f'<div class="row">{ui.chip(f"T2 · Q{n}", "t2")}</div>')
    st.header(f"Q{n}: {SLOT_TITLE[n]}")
    st.markdown(f"These are the versions of question {n} that have come up. Learn the **key points** for each one.")
    if st.button(f"Practise these {len(idx)} cards", type="primary", width="stretch", key="slot_go"):
        ss.fc = {"list": random.sample(idx, len(idx)), "i": 0, "flipped": False, "again": [], "slot": n}
        go("cards")
    if n == 7:
        st.page_link(PAGES["board"], label="Open the Board Builder", icon=":material/electrical_services:", width="stretch")
    for gid in SLOT_LAB.get(n, []):
        g = GEN_BY_ID.get(gid)
        if g and st.button(f"Calculation: {g.n}", key=f"slotlab_{gid}", width="stretch"):
            start_lab(gid, "all")
            go("lab")
    for i in idx:
        c = CARDS[i]
        tags = BOX_NAMES[store.box(i)] + (' · <span class="chip chk">Check ET101</span>' if c.get("c") else "")
        ui.html(f'<div class="panel"><div class="row" style="justify-content:space-between;flex-wrap:nowrap;align-items:flex-start">'
                f'<span>{c["q"]}</span>{ui.chip(marks(c.get("m", 1)))}</div><div class="small muted" style="margin-top:6px">{tags}</div></div>')


# =============================================================================== MOCK T2
def mock():
    S = store.S()
    MK = ss.get("mock")
    if MK is None:
        st.header("Mock T2 paper")
        st.markdown("**20 questions** in the real exam order, one version of each picked at random. "
                    "Answer on paper, out loud or in the box. Then **tick the key points** you got. The app adds up your marks.")
        best = "—" if S["mockBest"] is None else f"{S['mockBest']}%"
        last = "—" if S["mockLast"] is None else f"{S['mockLast']}%"
        ui.html(f'<div class="stats"><div class="stat"><b>20</b><span>questions</span></div>'
                f'<div class="stat"><b>{best}</b><span>best</span></div><div class="stat"><b>{last}</b><span>last</span></div></div>')
        st.caption("Pass 50 % · Merit 65 % · Distinction 80 %. The real paper is 3 hours. Take breaks between questions if you need to.")
        st.button("Start mock paper", type="primary", width="stretch", on_click=_start_mock, args=(20,))
        st.button("Half paper (10 questions)", width="stretch", on_click=_start_mock, args=(10,))
        return
    if MK["i"] >= len(MK["items"]):
        return _mock_end(MK)

    ci = MK["items"][MK["i"]]
    c = CARDS[ci]
    need = c.get("n") or len(c["a"])
    states = []
    for k, it in enumerate(MK["items"]):
        if k < MK["i"]:
            g = MK["got"][k]
            states.append("ok" if g >= CARDS[it]["m"] else "now" if g > 0 else "no")
        else:
            states.append("now" if k == MK["i"] else "")
    ui.html(ui.dots(states) + f'<div class="small muted">Question {MK["i"] + 1} of {len(MK["items"])}</div>')
    with st.container(border=True):
        ui.html(f'<div class="row">{ui.chip(f"Question {c["s"]}", "t2")}{ui.chip(c["t"])}{ui.chip(marks(c["m"]), "chk")}</div>')
        ui.read_aloud(f"mq_{MK['i']}", f'<div class="qtext">{c["q"]}</div>')
        st.text_area("Your answer (optional — paper or saying it out loud works too)", key=f"mtyped_{MK['i']}",
                     placeholder="Jot key words…", height=110)
    if not MK["revealed"]:
        st.button("Show the key points", type="primary", width="stretch",
                  on_click=lambda: MK.update(revealed=True), key=f"mshow_{MK['i']}")
        return
    with st.container(border=True):
        st.subheader("Tick the points you got")
        st.caption(f"Full marks needs {ui.plural(need, 'point')}.")
        if c.get("fig") in DIAG:
            ui.html(DIAG[c["fig"]]["svg"])
        ticked = sum(bool(st.checkbox(strip_tags(x), key=f"mtick_{MK['i']}_{k}")) for k, x in enumerate(c["a"]))
        if c.get("r"):
            ui.html(f'<div class="ref">Reference: {c["r"]}{" — check in ET101" if c.get("c") else ""}</div>')
        ui.read_aloud(f"ma_{MK['i']}", speak=". ".join(strip_tags(x) for x in c["a"]), label="Read the key points")
        score = round_half_up(c["m"] * min(1, ticked / need))
        st.markdown(f"### Marks: {score} / {c['m']}")
        last = MK["i"] == len(MK["items"]) - 1
        st.button("Finish paper" if last else "Next question", type="primary", width="stretch",
                  on_click=_mock_next, args=(score,), key=f"mnext_{MK['i']}")


def _start_mock(k: int):
    nums = [n for n, _ in SLOTS]
    if k < 20:
        nums = sorted(random.sample(nums, k))
    ss.mock = {"items": [random.choice(slot_cards(n)) for n in nums], "i": 0, "got": [], "revealed": False}


def _mock_next(score: int):
    MK = ss.mock
    ci = MK["items"][MK["i"]]
    c = CARDS[ci]
    MK["got"].append(score)
    store.set_box(ci, min(3, store.box(ci) + 1) if score >= c["m"] else 1)
    store.add_xp(score * 2)
    MK["i"] += 1
    MK["revealed"] = False
    if MK["i"] >= len(MK["items"]):
        S = store.S()
        tot = sum(MK["got"]); mx = sum(CARDS[i]["m"] for i in MK["items"])
        pc = round(tot / mx * 100)
        S["mockLast"] = pc
        if len(MK["items"]) == 20 and (S["mockBest"] is None or pc > S["mockBest"]):
            S["mockBest"] = pc


def _mock_end(MK):
    tot = sum(MK["got"]); mx = sum(CARDS[i]["m"] for i in MK["items"])
    pc = round(tot / mx * 100)
    ui.html(f'<div class="panel" style="text-align:center"><div class="big">{pc}%</div><h2>{grade(pc)}</h2>'
            f'<div class="small muted">{tot} of {mx} marks</div></div>')
    rows = sorted(zip(MK["items"], MK["got"]), key=lambda r: r[1] / CARDS[r[0]]["m"])
    st.subheader("Work on these first")
    for ci, g in rows[:5]:
        c = CARDS[ci]
        if st.button(f"Q{c['s']} · {SLOT_TITLE[c['s']]} — {g}/{c['m']}", key=f"mwork_{ci}", width="stretch"):
            ss.t2_slot = c["s"]
            go("t2")
    with st.expander("All questions"):
        for ci, g in zip(MK["items"], MK["got"]):
            c = CARDS[ci]
            colour = "var(--good)" if g >= c["m"] else "var(--acc)" if g > 0 else "var(--bad)"
            ui.html(f'<div class="row" style="justify-content:space-between;flex-wrap:nowrap"><span class="small">Q{c["s"]} · '
                    f'{SLOT_TITLE[c["s"]]}</span><span class="chip" style="border-color:{colour}">{g}/{c["m"]}</span></div>')
    st.button("New mock", type="primary", width="stretch", on_click=lambda: ss.update(mock=None))


# =============================================================================== BOARD BUILDER
def board():
    S = store.S()
    st.header("Board Builder — T2 Q7")
    st.markdown("Choose the **protective device** and **busbar** for each load. "
                "The drawing updates as you go. This is what you draw in the exam.")
    ids = [s["id"] for s in BOARD_SCEN]
    by_id = {s["id"]: s for s in BOARD_SCEN}
    cur = S["prefs"].get("bbsc", "b")
    sid = st.selectbox("Which version of the question?", ids, index=ids.index(cur) if cur in ids else 1,
                       format_func=lambda i: f"{by_id[i]['name']} ({by_id[i]['papers']})", key="bb_sel")
    S["prefs"]["bbsc"] = sid
    sc = by_id[sid]
    blank = blank_assign(sc)

    def wkey(i, f):
        return f"bb_{sid}_{i}_{f}"

    asg = []
    for i, b in enumerate(blank):
        a = dict(b)
        for f in ("dev", "bar"):
            if wkey(i, f) in ss and ss[wkey(i, f)] is not None:
                a[f] = ss[wkey(i, f)]
        asg.append(a)

    with st.container(border=True):
        ui.html(f'<div style="overflow-x:auto">{draw_board(sc, asg)}</div>')

    for i, (name, t) in enumerate(sc["loads"]):
        with st.container(border=True):
            kind = "3-phase" if t == "3" else "single-phase" + (" socket" if t == "1s" else "")
            ui.html(f'<div class="row" style="justify-content:space-between"><b>{escape(name)}</b>{ui.chip(kind)}</div>')
            devs = device_choices(sc, t)
            if devs:
                labels = dict(devs)
                st.segmented_control("Device", [k for k, _ in devs], format_func=labels.get, key=wkey(i, "dev"),
                                     label_visibility="collapsed")
            if t != "3":
                st.segmented_control("Phase", ["L1", "L2", "L3"], key=wkey(i, "bar"), label_visibility="collapsed")

    msg = ss.get("bb_msg")
    if msg and msg[0] == sid:
        ui.html(msg[1])

    def do_check():
        issues = check_board(sc, asg)
        if not issues:
            store.add_xp(20)
            ss.bb_msg = (sid, ui.feedback("Board passes", "<div>Balanced phases, right devices. Now draw it on paper from memory.</div>"))
        else:
            body = "".join(f"<div>• {bold(x)}</div>" for x in issues)
            ss.bb_msg = (sid, ui.feedback("Not yet", body, ok=False))

    def do_model():
        for i, a in enumerate(model_assign(sc)):
            if device_choices(sc, sc["loads"][i][1]):
                ss[wkey(i, "dev")] = a["dev"]
            if sc["loads"][i][1] != "3":
                ss[wkey(i, "bar")] = a["bar"]
        ss.bb_msg = (sid, ui.feedback("Model answer", "<div>3-phase loads on triple-pole devices, single-phase loads "
                                                      "rotated L1 → L2 → L3, sockets on RCBOs.</div>"))

    c1, c2 = st.columns(2)
    c1.button("Check my board", type="primary", width="stretch", on_click=do_check)
    c2.button("Show model answer", width="stretch", on_click=do_model)
    ui.html('<div class="note"><b>Exam tips:</b> draw the main switch and the L1, L2, L3, N and E bars. '
            'Use triple-pole devices for 3-phase loads. Spread single-phase loads evenly across the phases. '
            'Put sockets on RCBOs. Label every circuit.</div>')


# =============================================================================== FLASHCARDS
def cards():
    S = store.S()
    FC = ss.get("fc")
    if FC is None:
        st.header("Flashcards")
        st.markdown("Read the question. **Say your answer out loud.** Then flip. "
                    "Answers are key points — the words examiners look for.")
        deck = st.segmented_control("Deck", ["T2", "T1", "all"], default=S["prefs"]["fdeck"], key="fdeck",
                                    format_func={"T2": "T2 written", "T1": "T1 explain", "all": "All"}.get,
                                    label_visibility="collapsed") or "T2"
        S["prefs"]["fdeck"] = deck
        pool = [i for i, c in enumerate(CARDS) if deck == "all" or c["p"] == deck]
        cnt = [sum(1 for i in pool if store.box(i) == b) for b in range(4)]
        ui.html('<div class="boxes">' + "".join(f"<span><b>{cnt[b]}</b>{BOX_NAMES[b]}</span>" for b in range(4)) + "</div>")

        def start():
            order = sorted(random.sample(pool, len(pool)), key=store.box)
            ss.fc = {"list": order[:10], "i": 0, "flipped": False, "again": [], "slot": None}

        st.button("Start 10 cards", type="primary", width="stretch", on_click=start)
        if deck == "T2":
            st.page_link(PAGES["t2"], label="Pick by question number (paper map)", icon=":material/grid_view:", width="stretch")
        ui.html('<div class="note">Cards marked <span class="chip chk">Check ET101</span> come from the regs. '
                'Past-paper answers sometimes disagree, so check those against the ET101 book.</div>')
        return

    if FC["i"] >= len(FC["list"]) and FC["again"]:
        FC["list"] += FC["again"]
        FC["again"] = []
    if FC["i"] >= len(FC["list"]):
        ui.html('<div class="panel" style="text-align:center"><div class="big">Done</div><h2>Deck finished</h2>'
                '<p class="muted" style="margin:0 auto">Cards you marked “Again” came back round until you had them.</p></div>')

        def back():
            slot = FC.get("slot")
            ss.fc = None
            if slot:
                ss.t2_slot = slot

        if FC.get("slot"):
            if st.button("Back to the paper map", type="primary", width="stretch"):
                back(); go("t2")
        else:
            st.button("Back", type="primary", width="stretch", on_click=back)
        return

    ci = FC["list"][FC["i"]]
    c = CARDS[ci]
    c1, c2 = st.columns([3, 1], vertical_alignment="center")
    c1.caption(f"Card {FC['i'] + 1} of {len(FC['list'])}")
    c2.button("End", width="stretch", on_click=lambda: ss.update(fc=None), key="fc_end")
    with st.container(border=True):
        tags = ui.chip(c["p"] + (f" · Q{c['s']}" if c.get("s") else ""), c["p"].lower())
        if c.get("m"):
            tags += ui.chip(marks(c["m"]))
        tags += ui.chip(c["t"]) + (ui.chip("Check ET101", "chk") if c.get("c") else "")
        ui.html(f'<div class="row">{tags}</div>')
        ui.read_aloud(f"fq_{ci}_{FC['i']}", f'<div class="qtext">{c["q"]}</div>')
        if FC["flipped"]:
            if c.get("fig") in DIAG:
                ui.html(DIAG[c["fig"]]["svg"])
            extra = ""
            if c.get("n") and c["n"] < len(c["a"]):
                extra += f'<div class="ref">Any {c["n"]} of these for full marks.</div>'
            if c.get("r"):
                extra += f'<div class="ref">Reference: {c["r"]}</div>'
            ui.read_aloud(f"fa_{ci}_{FC['i']}", '<ul class="keypoints">' + "".join(f"<li>{x}</li>" for x in c["a"]) + "</ul>" + extra,
                          label="Read the answer")
    if not FC["flipped"]:
        st.button("Show answer", type="primary", width="stretch", on_click=lambda: FC.update(flipped=True), key=f"flip_{FC['i']}")
        return

    def rate(r: int):
        b = store.box(ci)
        if r == 0:
            store.set_box(ci, 1); FC["again"].append(ci)
        elif r == 1:
            store.set_box(ci, max(1, min(2, b)))
        else:
            store.set_box(ci, min(3, b + 1)); store.add_xp(5)
        FC["i"] += 1
        FC["flipped"] = False

    st.caption("How did you do?")
    a, b, g = st.columns(3)
    a.button("Again", width="stretch", on_click=rate, args=(0,), key=f"r0_{FC['i']}", icon=":material/replay:")
    b.button("Nearly", width="stretch", on_click=rate, args=(1,), key=f"r1_{FC['i']}", icon=":material/trending_up:")
    g.button("Got it", type="primary", width="stretch", on_click=rate, args=(2,), key=f"r2_{FC['i']}", icon=":material/check:")


# =============================================================================== QUICK SHIFT QUIZ
def start_quiz(mode: str):
    S = store.S()
    if mode == "review":
        pool = [i for i in S["missed"] if 0 <= i < len(MCQ)]
    else:
        pool = [i for i, q in enumerate(MCQ) if mode == "mix" or q["p"] == mode]
    items = [(i, random.sample(range(len(MCQ[i]["o"])), len(MCQ[i]["o"]))) for i in random.sample(pool, min(10, len(pool)))]
    timed = mode != "review" and S["prefs"].get("qtimed", False)
    ss.quiz = {"items": items, "i": 0, "res": [], "mode": mode, "timed": timed,
               "deadline": time.time() + 120 if timed else None, "streak": 0, "picked": None, "timeout": False}


def quiz():
    S = store.S()
    Q = ss.get("quiz")
    if Q is None:
        st.header("Quick Shift")
        st.markdown("**10 questions**, one at a time. You get the explanation straight after each one.")
        mode = st.segmented_control("Paper", ["T2", "T1", "mix"], default=S["prefs"]["qmode"], key="qmode",
                                    format_func={"T2": "T2 Installation", "T1": "T1 Science", "mix": "Mixed"}.get) or "T2"
        S["prefs"]["qmode"] = mode
        timed = st.segmented_control("Mode", ["Relaxed", "Inspector (2 min clock)"],
                                     default="Inspector (2 min clock)" if S["prefs"]["qtimed"] else "Relaxed",
                                     key="qtimed") or "Relaxed"
        S["prefs"]["qtimed"] = timed != "Relaxed"
        st.button("Start shift", type="primary", width="stretch", on_click=start_quiz, args=(mode,))
        t2 = sum(q["p"] == "T2" for q in MCQ)
        st.caption(f"{t2} T2 and {len(MCQ) - t2} T1 questions in the bank. Wrong answers go to your review list.")
        if S["missed"]:
            st.button(f"Review misses ({len(S['missed'])})", width="stretch", on_click=start_quiz, args=("review",))
        return

    if Q["timed"] and not Q["timeout"] and time.time() >= Q["deadline"]:
        Q["timeout"] = True
    if Q["i"] >= len(Q["items"]) or Q["timeout"]:
        return _quiz_end(Q)

    qi, order = Q["items"][Q["i"]]
    q = MCQ[qi]
    states = [("ok" if Q["res"][k] else "no") if k < len(Q["res"]) else ("now" if k == Q["i"] else "")
              for k in range(len(Q["items"]))]
    c1, c2 = st.columns([3, 1], vertical_alignment="center")
    with c1:
        ui.html(ui.dots(states))
    with c2:
        if Q["timed"]:
            # The clock ticks in the browser; when it hits zero it triggers a rerun,
            # and the deadline check above ends the shift.
            ui.countdown("qclock", Q["deadline"])
        else:
            st.caption(f"{Q['i'] + 1} / {len(Q['items'])}")

    with st.container(border=True):
        tags = ui.paper_chip(q["p"]) + ui.chip(q["t"]) + (ui.chip(f"{Q['streak']} in a row", "chk") if Q["streak"] >= 3 else "")
        ui.html(f'<div class="row">{tags}</div>')
        spoken = strip_tags(q["q"]) + ". " + ". ".join(f"{'ABCD'[k]}. {strip_tags(q['o'][oi])}" for k, oi in enumerate(order))
        ui.read_aloud(f"q_{Q['i']}", f'<div class="qtext">{bold(q["q"])}</div>', speak=spoken)

    if Q["picked"] is None:
        for k, oi in enumerate(order):
            st.button(f"**{'ABCD'[k]}**   {strip_tags(q['o'][oi])}", key=f"opt_{Q['i']}_{k}", width="stretch",
                      on_click=_answer, args=(oi,))
        return

    ok = Q["picked"] == q["a"]
    opts = ""
    for k, oi in enumerate(order):
        cls = "right" if oi == q["a"] else "wrong" if oi == Q["picked"] else "dim"
        opts += f'<div class="opt {cls}"><span class="let">{"ABCD"[k]}</span><span>{q["o"][oi]}</span></div>'
    ui.html(opts)
    ui.read_aloud(f"w_{Q['i']}", ui.feedback("Correct" if ok else "Not quite", f'<div>{q["w"]}</div>', ok=ok),
                  label="Read the explanation")
    last = Q["i"] == len(Q["items"]) - 1
    st.button("See results" if last else "Next question", type="primary", width="stretch", key=f"next_{Q['i']}",
              on_click=lambda: Q.update(i=Q["i"] + 1, picked=None))


def _answer(oi: int):
    S = store.S()
    Q = ss.quiz
    if Q["timed"] and time.time() >= Q["deadline"]:
        Q["timeout"] = True
        return
    qi, _ = Q["items"][Q["i"]]
    q = MCQ[qi]
    ok = oi == q["a"]
    Q["picked"] = oi
    Q["res"].append(ok)
    S["answered"] += 1
    if ok:
        S["correct"] += 1
        Q["streak"] += 1
        store.add_xp(10 + (5 if Q["streak"] >= 3 else 0))
        S["missed"] = [x for x in S["missed"] if x != qi]
    else:
        Q["streak"] = 0
        if qi not in S["missed"]:
            S["missed"].append(qi)


def _quiz_end(Q):
    S = store.S()
    score = sum(Q["res"]); total = len(Q["items"])
    if Q["mode"] != "review" and total == 10 and score > S["bestShift"]:
        S["bestShift"] = score
    msg = ("Distinction territory. Nice work." if score >= 8 else "Solid shift. Merit level." if score >= 6.5
           else "A pass. Have a go at the review list." if score >= 5 else "Tough shift. Do the review list, then try again.")
    out = '<div class="chip chk">Time ran out</div>' if Q["timeout"] else ""
    ui.html(f'<div class="panel" style="text-align:center"><div class="big">{score}/{total}</div><h2>{msg}</h2>'
            f'<div class="small muted">Exam grades: Pass 50 % · Merit 65 % · Distinction 80 %</div>{out}</div>')
    with st.expander("This shift", expanded=True):
        for k, (qi, _) in enumerate(Q["items"]):
            if k >= len(Q["res"]):
                mark, col = "–", "var(--line)"
            else:
                mark, col = ("✓", "var(--good)") if Q["res"][k] else ("✗", "var(--bad)")
            ui.html(f'<div class="row" style="flex-wrap:nowrap;align-items:flex-start;margin:4px 0">'
                    f'<span class="chip" style="border-color:{col}">{mark}</span><span class="small">{bold(MCQ[qi]["q"])}</span></div>')
    c1, c2 = st.columns(2)
    c1.button("Another shift", type="primary", width="stretch", on_click=start_quiz, args=(Q["mode"],))
    if S["missed"]:
        c2.button(f"Review misses ({len(S['missed'])})", width="stretch", on_click=start_quiz, args=("review",))
    st.button("Back to setup", width="stretch", on_click=lambda: ss.update(quiz=None))


# =============================================================================== FORMULA LAB
def start_lab(gid: str | None, pf: str):
    ss.lab = {"id": gid, "pf": pf, "count": 0, "right": 0, "cur": None}
    _next_problem()


def _next_problem():
    L = ss.lab
    pool = [g for g in GENS if L["pf"] == "all" or g.p == L["pf"]]
    g = GEN_BY_ID[L["id"]] if L["id"] else random.choice(pool)
    L["cur"] = {"g": g.id, "p": g.make(), "tries": 0, "done": False, "shown": 0, "fb": None}
    L["n"] = L.get("n", 0) + 1


def lab():
    S = store.S()
    L = ss.get("lab")
    if L is None:
        st.header("Formula Lab")
        st.markdown("New numbers every time. **Try it first**, then reveal the steps one at a time.")
        pf = st.segmented_control("Paper", ["T2", "T1", "all"], default=S["prefs"]["labp"], key="labp",
                                  format_func={"T2": "T2 calcs", "T1": "T1 calcs", "all": "All"}.get,
                                  label_visibility="collapsed") or "T2"
        S["prefs"]["labp"] = pf
        st.button(f"Random mix ({'all' if pf == 'all' else pf})", type="primary", width="stretch",
                  on_click=start_lab, args=(None, pf))
        gens = [g for g in GENS if pf == "all" or g.p == pf]
        for topic in dict.fromkeys(g.t for g in gens):
            st.subheader(topic)
            for g in gens:
                if g.t == topic:
                    st.button(f"{g.n}  ›", key=f"gen_{g.id}", width="stretch", on_click=start_lab, args=(g.id, "all"))
        return

    cur = L["cur"]; g = GEN_BY_ID[cur["g"]]; p = cur["p"]
    c1, c2 = st.columns([2, 1], vertical_alignment="center")
    c1.button("‹ All formulas", on_click=lambda: ss.update(lab=None), key="lab_back")
    c2.caption(f"{L['right']}/{L['count']} right" + ("" if L["id"] else " · mix"))

    with st.container(border=True):
        ui.html(f'<div class="row">{ui.paper_chip(g.p)}{ui.chip(g.t)}</div><div class="qtext">{p["ask"]}</div>')
        given = "".join(f'<div class="gv {SYM.get(k, [k, "k"])[1]}"><small>given</small>{sym(k)} = <b>{v}</b> {u}</div>'
                        for k, v, u in p["given"])
        ui.html(f'<div class="given">{given}</div>')
        spoken = p["ask"] + ". Given: " + ", ".join(f"{sym_plain(k)} equals {v} {u}" for k, v, u in p["given"])
        ui.read_aloud(f"lab_{L['n']}", speak=spoken)

    with st.container(border=True):
        with st.form(key=f"labf_{L['n']}", border=False, enter_to_submit=True):
            unit = f" (in {p['unit']})" if p["unit"] else ""
            val = st.text_input(f"Your answer{unit} — 3 decimal places", placeholder="e.g. 4.205", key=f"ans_{L['n']}")
            sub = st.form_submit_button("Next problem" if cur["done"] else "Check", type="primary", width="stretch")
        if sub:
            if cur["done"]:
                _next_problem()  # progress was already counted when the answer was checked
                st.rerun()
            _check_lab(val)
            st.rerun()  # redraw so the feedback and button label match the new state
        if not cur["done"] and cur["shown"] < len(p["steps"]):
            st.button("Show next step", width="stretch", on_click=lambda: cur.update(shown=cur["shown"] + 1), key=f"hint_{L['n']}")
        if cur["fb"]:
            ui.html(cur["fb"])

    with st.container(border=True):
        st.subheader("Working")
        shown = len(p["steps"]) if cur["done"] else cur["shown"]
        if shown:
            ui.html('<ol class="steps">' + "".join(f"<li>{fx(s)}</li>" for s in p["steps"][:shown]) + "</ol>")
        if shown < len(p["steps"]):
            st.caption("Steps are hidden. Tap **Show next step** if you get stuck.")


def _check_lab(raw: str):
    S = store.S(); L = ss.lab; cur = L["cur"]; p = cur["p"]
    txt = re.sub(r"[^0-9.\-eE]", "", (raw or "").replace(",", "."))
    try:
        v = float(txt)
    except ValueError:
        cur["fb"] = ui.feedback("Type a number first.", ok=False)
        return
    cur["tries"] += 1
    ok = is_correct(v, p["ans"])
    if ok or cur["tries"] >= 2:
        cur["done"] = True
        L["count"] += 1
        S["answered"] += 1
        if ok:
            L["right"] += 1; S["correct"] += 1; store.add_xp(15)
        tail = "" if ok else " — check the working below."
        cur["fb"] = ui.feedback("Spot on" if ok else "Answer", f"<div>{n3(p['ans'])} {p['unit']}{tail}</div>", ok=ok)
    else:
        cur["fb"] = ui.feedback("Not yet.", "<div>Have one more go, or show a step.</div>", ok=False)


# =============================================================================== DIAGRAMS
def pictures():
    k = ss.get("diag")
    if k in DIAG:
        d = DIAG[k]
        back_button("All diagrams", lambda: ss.update(diag=None), "dg_back")
        ui.html(f'<div class="row">{ui.chip(d["t"])}</div>')
        st.header(d["n"])
        ui.diagram_reveal(f"dg_{k}", d["svg"])
        return
    st.header("Diagrams")
    st.markdown("These are the drawings the papers ask for. **T2 first.** "
                "Open one, hide the labels, and name each part before you tap it.")
    ents = sorted(DIAG.items(), key=lambda kv: 0 if kv[1]["t"].startswith("T2") else 1)
    cols = st.columns(2)
    for n, (key, d) in enumerate(ents):
        with cols[n % 2]:
            with st.container(border=True):
                ui.html(d["svg"])
                st.button(d["n"], key=f"dgo_{key}", width="stretch", help=d["t"],
                          on_click=lambda key=key: ss.update(diag=key))
                st.caption(d["t"])
    st.page_link(PAGES["snap"], label="Play Symbol Snap", icon=":material/bolt:", width="stretch")


# =============================================================================== SYMBOL SNAP
def snap():
    S = store.S()
    SN = ss.setdefault("snap", {"phase": "intro", "round": 0, "score": 0, "best_before": 0})

    def start():
        SN.update(phase="play", round=SN["round"] + 1, best_before=S["snapBest"])

    if SN["phase"] == "play":
        def done():
            res = ss.get(f"snap_{SN['round']}") or {}
            val = res.get("done") if hasattr(res, "get") else None
            if not val:
                return
            SN["score"] = int(val.get("score", 0))
            store.add_xp(2 * SN["score"])
            if SN["score"] > S["snapBest"]:
                S["snapBest"] = SN["score"]
            SN["phase"] = "done"

        st.caption("Tap the right name. Wrong answers cost 3 seconds.")
        ui._snap(key=f"snap_{SN['round']}", data={"round": SN["round"], "symbols": SYMBOLS, "seconds": 60},
                 on_done_change=done)
        st.button("Stop", on_click=lambda: SN.update(phase="intro"))
        return

    if SN["phase"] == "done":
        nb = SN["score"] > SN["best_before"]
        ui.html(f'<div class="panel" style="text-align:center"><div class="big">{SN["score"]}</div>'
                f'<h2>{"New best score" if nb else "Time up"}</h2><div class="small muted">Best: {S["snapBest"]}</div></div>')
        c1, c2 = st.columns(2)
        c1.button("Play again", type="primary", width="stretch", on_click=start)
        c2.page_link(PAGES["pictures"], label="Diagrams", icon=":material/schema:", width="stretch")
        return

    if SN["phase"] == "learn":
        back_button("Back", lambda: SN.update(phase="intro"), "snap_learn_back")
        cols = st.columns(2)
        for n, s in enumerate(SYMBOLS):
            with cols[n % 2]:
                ui.html(f'<div class="panel"><div class="symbox">{s["s"]}</div><b>{s["n"]}</b></div>')
        return

    st.header("Symbol Snap")
    st.markdown("**60 seconds.** A symbol appears — tap its name. Wrong answers cost 3 seconds.")
    ui.html(f'<div class="symbox">{SYMBOLS[6]["s"]}</div>')
    st.caption(f"Best score: **{S['snapBest']}**")
    st.button("Start", type="primary", width="stretch", on_click=start)
    st.button("Learn the symbols first", width="stretch", on_click=lambda: SN.update(phase="learn"))


# =============================================================================== MATHS
def maths():
    from .maths import maths_page
    maths_page()
