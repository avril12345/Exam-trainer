"""Maths tab: worked examples, test questions and key-term practice.

All content comes from ``data/maths.json``:

{
  "topics":    [{"id": "transposition", "name": "Transposition"}],
  "examples":  [{"topic", "title", "problem", "steps": [..], "answer", "tip"?}],
  "questions": [{"topic", "q", "type": "mcq", "o": [..], "a": <index>, "w": "why"}
                {"topic", "q", "type": "number", "a": 12.5, "unit": "m²", "tol": 0.01?, "steps": [..]?, "w"?}],
  "terms":     [{"topic", "term", "def"}]
}
Text may use **bold** for key words and simple HTML (<sup>, <sub>, <b>).
Set "sample": true at the top level while the file still holds placeholder content.
"""
from __future__ import annotations

import json
import random
import re

import streamlit as st

from . import store, ui
from .content import DATA, bold, strip_tags

ss = st.session_state


@st.cache_data
def load_maths(mtime: float) -> dict:
    with open(DATA / "maths.json", encoding="utf-8") as f:
        d = json.load(f)
    for k in ("topics", "examples", "questions", "terms"):
        d.setdefault(k, [])
    return d


def M() -> dict:
    p = DATA / "maths.json"
    return load_maths(p.stat().st_mtime if p.exists() else 0.0)


def _mstate() -> dict:
    S = store.S()
    m = S.setdefault("maths", {})
    m.setdefault("missed", []); m.setdefault("terms", {}); m.setdefault("examples_done", [])
    return m


def topic_name(tid: str) -> str:
    return next((t["name"] for t in M()["topics"] if t["id"] == tid), tid)


def topic_picker(key: str, items: list[dict]) -> str:
    used = [t for t in M()["topics"] if any(i.get("topic") == t["id"] for i in items)]
    if len(used) < 2:
        return "all"
    opts = ["all"] + [t["id"] for t in used]
    return st.selectbox("Topic", opts, format_func=lambda x: "All topics" if x == "all" else topic_name(x), key=key)


# ------------------------------------------------------------------------------ page
def maths_page():
    d = M()
    st.header("Maths")
    if d.get("sample"):
        ui.html('<div class="note"><b>Sample content.</b> This tab will be filled from your maths document.</div>')
    st.caption(f"{len(d['examples'])} worked examples · {len(d['questions'])} test questions · "
               f"{len(d['terms'])} key terms. Answers to 3 decimal places.")
    mode = st.segmented_control("Section", ["examples", "test", "terms"], default="examples", key="maths_mode",
                                format_func={"examples": "Worked examples", "test": "Test questions",
                                             "terms": "Key terms"}.get, label_visibility="collapsed") or "examples"
    {"examples": _examples, "test": _test, "terms": _terms}[mode]()


# ------------------------------------------------------------------------------ worked examples
def _examples():
    d = M(); ms = _mstate()
    ex = d["examples"]
    if not ex:
        st.info("No worked examples yet.")
        return
    cur = ss.get("mx")
    if cur is not None and cur < len(ex):
        return _example(cur)
    st.markdown("Read the problem, **try it yourself on paper**, then reveal the steps one at a time.")
    topic = topic_picker("mx_topic", ex)
    for i, e in enumerate(ex):
        if topic != "all" and e.get("topic") != topic:
            continue
        tick = "✓ " if i in ms["examples_done"] else ""
        st.button(f"{tick}{e['title']}", key=f"mx_{i}", width="stretch", help=topic_name(e.get("topic", "")),
                  on_click=lambda i=i: ss.update(mx=i, mx_shown=0))


def _example(i: int):
    e = M()["examples"][i]; ms = _mstate()
    st.button("‹ All examples", on_click=lambda: ss.update(mx=None), key="mx_back")
    with st.container(border=True):
        ui.html(f'<div class="row">{ui.chip(topic_name(e.get("topic", "")))}</div>')
        st.subheader(e["title"])
        ui.read_aloud(f"mxp_{i}", f'<div class="qtext">{bold(e["problem"])}</div>')
    shown = ss.get("mx_shown", 0)
    steps = e.get("steps", [])
    with st.container(border=True):
        st.markdown("**Working**")
        if shown:
            ui.read_aloud(f"mxs_{i}_{shown}", '<ol class="steps">' + "".join(f"<li>{bold(s)}</li>" for s in steps[:shown]) + "</ol>",
                          label="Read the steps")
        if shown < len(steps):
            st.caption(f"Step {shown} of {len(steps)} shown.")
            c1, c2 = st.columns(2)
            c1.button("Show next step", type="primary", width="stretch", on_click=lambda: ss.update(mx_shown=shown + 1))
            c2.button("Show all steps", width="stretch", on_click=lambda: ss.update(mx_shown=len(steps)))
        else:
            ui.html(ui.feedback("Answer", f"<div>{bold(e['answer'])}</div>"))
            if e.get("tip"):
                ui.html(f'<div class="note"><b>Tip:</b> {bold(e["tip"])}</div>')
            if i not in ms["examples_done"]:
                ms["examples_done"].append(i)
                store.add_xp(3)
    ex = M()["examples"]
    if i + 1 < len(ex):
        st.button("Next example ›", width="stretch", on_click=lambda: ss.update(mx=i + 1, mx_shown=0))


# ------------------------------------------------------------------------------ test questions
def _check_number(raw: str, q: dict) -> bool | None:
    txt = re.sub(r"[^0-9.\-eE]", "", (raw or "").replace(",", "."))
    try:
        v = float(txt)
    except ValueError:
        return None
    a = float(q["a"])
    tol = q.get("tol", max(0.0015, abs(a) * 0.005))
    return abs(v - a) <= tol


def _test():
    d = M(); S = store.S(); ms = _mstate()
    qs = d["questions"]
    if not qs:
        st.info("No test questions yet.")
        return
    T = ss.get("mt")
    if T is None:
        st.markdown("**10 questions**, one at a time. You see the working straight after each one.")
        topic = topic_picker("mt_topic", qs)
        pool = [i for i, q in enumerate(qs) if topic == "all" or q.get("topic") == topic]

        def start(p):
            ss.mt = {"items": random.sample(p, min(10, len(p))), "i": 0, "res": [], "picked": None, "tries": 0, "fb": None,
                     "order": {}}

        st.button(f"Start ({min(10, len(pool))} questions)", type="primary", width="stretch", on_click=start, args=(pool,))
        miss = [i for i in ms["missed"] if i < len(qs)]
        if miss:
            st.button(f"Review misses ({len(miss)})", width="stretch", on_click=start, args=(miss,))
        return

    if T["i"] >= len(T["items"]):
        score = sum(T["res"]); total = len(T["items"])
        pc = round(score / total * 100) if total else 0
        ui.html(f'<div class="panel" style="text-align:center"><div class="big">{score}/{total}</div><h2>{pc}%</h2></div>')
        st.button("Try another set", type="primary", width="stretch", on_click=lambda: ss.update(mt=None))
        return

    qi = T["items"][T["i"]]; q = qs[qi]
    states = [("ok" if T["res"][k] else "no") if k < len(T["res"]) else ("now" if k == T["i"] else "")
              for k in range(len(T["items"]))]
    ui.html(ui.dots(states) + f'<div class="small muted">Question {T["i"] + 1} of {len(T["items"])}</div>')
    answered = T["picked"] is not None
    with st.container(border=True):
        ui.html(f'<div class="row">{ui.chip(topic_name(q.get("topic", "")))}</div>')
        ui.read_aloud(f"mtq_{T['i']}", f'<div class="qtext">{bold(q["q"])}</div>')

    def record(ok: bool):
        T["res"].append(ok); T["picked"] = True
        S["answered"] += 1
        if ok:
            S["correct"] += 1; store.add_xp(10)
            ms["missed"] = [x for x in ms["missed"] if x != qi]
        elif qi not in ms["missed"]:
            ms["missed"].append(qi)

    if q.get("type", "mcq") == "mcq":
        order = T["order"].setdefault(str(T["i"]), random.sample(range(len(q["o"])), len(q["o"])))
        if not answered:
            for k, oi in enumerate(order):
                st.button(f"**{'ABCD'[k]}**   {strip_tags(q['o'][oi])}", key=f"mto_{T['i']}_{k}", width="stretch",
                          on_click=lambda oi=oi: (T.update(chosen=oi), record(oi == q["a"])))
        else:
            html = ""
            for k, oi in enumerate(order):
                cls = "right" if oi == q["a"] else "wrong" if oi == T.get("chosen") else "dim"
                html += f'<div class="opt {cls}"><span class="let">{"ABCD"[k]}</span><span>{q["o"][oi]}</span></div>'
            ui.html(html)
            ok = T["res"][-1]
            T["fb"] = ui.feedback("Correct" if ok else "Not quite", f"<div>{bold(q.get('w', ''))}</div>", ok=ok)
    else:
        if not answered:
            with st.form(key=f"mtf_{T['i']}", border=False):
                unit = f" (in {q['unit']})" if q.get("unit") else ""
                val = st.text_input(f"Your answer{unit}", key=f"mta_{T['i']}")
                if st.form_submit_button("Check", type="primary", width="stretch"):
                    ok = _check_number(val, q)
                    if ok is None:
                        T["fb"] = ui.feedback("Type a number first.", ok=False)
                    elif ok or T["tries"] >= 1:
                        record(ok)
                        T["fb"] = ui.feedback("Spot on" if ok else "Answer", f"<div>{q['a']} {q.get('unit', '')}</div>", ok=ok)
                    else:
                        T["tries"] += 1
                        T["fb"] = ui.feedback("Not yet.", "<div>Have one more go.</div>", ok=False)
                    st.rerun()
    if T["fb"]:
        ui.html(T["fb"])
    if answered:
        if q.get("steps"):
            ui.read_aloud(f"mts_{T['i']}", '<ol class="steps">' + "".join(f"<li>{bold(s)}</li>" for s in q["steps"]) + "</ol>",
                          label="Read the working")
        if q.get("type") == "number" and q.get("w"):
            ui.html(f'<div class="note">{bold(q["w"])}</div>')
        last = T["i"] == len(T["items"]) - 1
        st.button("See results" if last else "Next question", type="primary", width="stretch", key=f"mtn_{T['i']}",
                  on_click=lambda: T.update(i=T["i"] + 1, picked=None, tries=0, fb=None))


# ------------------------------------------------------------------------------ key terms
def _terms():
    d = M(); ms = _mstate()
    terms = d["terms"]
    if not terms:
        st.info("No key terms yet.")
        return
    K = ss.get("mk")
    if K is None:
        st.markdown("**Flip cards:** see the term, say what it means, then check.  \n"
                    "**Match:** read the meaning and pick the right term.")
        topic = topic_picker("mk_topic", terms)
        pool = [i for i, t in enumerate(terms) if topic == "all" or t.get("topic") == topic]
        known = sum(1 for i in pool if ms["terms"].get(str(i), 0) >= 2)
        st.caption(f"{known} of {len(pool)} terms known")

        def start(kind):
            order = sorted(random.sample(pool, len(pool)), key=lambda i: ms["terms"].get(str(i), 0))[:10]
            ss.mk = {"kind": kind, "list": order, "i": 0, "flipped": False, "again": [], "picked": None, "res": []}

        c1, c2 = st.columns(2)
        c1.button("Flip cards", type="primary", width="stretch", on_click=start, args=("flip",))
        c2.button("Match game", width="stretch", on_click=start, args=("match",), disabled=len(terms) < 4,
                  help="Needs at least 4 terms" if len(terms) < 4 else None)
        with st.expander("See all terms"):
            for i in pool:
                t = terms[i]
                st.markdown(f"**{t['term']}** — {strip_tags(t['def'])}")
        return

    if K["i"] >= len(K["list"]) and K["again"]:
        K["list"] += K["again"]; K["again"] = []
    if K["i"] >= len(K["list"]):
        extra = f"<div>{sum(K['res'])} of {len(K['res'])} right</div>" if K["kind"] == "match" else ""
        ui.html(f'<div class="panel" style="text-align:center"><div class="big">Done</div>{extra}</div>')
        st.button("Back", type="primary", width="stretch", on_click=lambda: ss.update(mk=None))
        return

    ti = K["list"][K["i"]]; t = terms[ti]
    c1, c2 = st.columns([3, 1], vertical_alignment="center")
    c1.caption(f"Term {K['i'] + 1} of {len(K['list'])}")
    c2.button("End", width="stretch", on_click=lambda: ss.update(mk=None), key="mk_end")

    if K["kind"] == "flip":
        with st.container(border=True):
            ui.read_aloud(f"mkt_{K['i']}", f'<div class="qtext" style="font-size:1.6rem"><b>{t["term"]}</b></div>')
            if K["flipped"]:
                ui.read_aloud(f"mkd_{K['i']}", f"<p>{bold(t['def'])}</p>", label="Read the meaning")
        if not K["flipped"]:
            st.button("Show meaning", type="primary", width="stretch", on_click=lambda: K.update(flipped=True), key=f"mkf_{K['i']}")
            return

        def rate(r):
            b = ms["terms"].get(str(ti), 0)
            if r == 0:
                ms["terms"][str(ti)] = 0; K["again"].append(ti)
            else:
                ms["terms"][str(ti)] = min(3, b + 1); store.add_xp(3)
            K["i"] += 1; K["flipped"] = False

        a, g = st.columns(2)
        a.button("Again", width="stretch", on_click=rate, args=(0,), key=f"mkr0_{K['i']}", icon=":material/replay:")
        g.button("Got it", type="primary", width="stretch", on_click=rate, args=(1,), key=f"mkr1_{K['i']}", icon=":material/check:")
        return

    # match game: meaning shown, pick the term
    opts_key = f"mkopts_{K['i']}"
    if opts_key not in K:
        others = random.sample([i for i in range(len(terms)) if i != ti], min(3, len(terms) - 1))
        K[opts_key] = random.sample([ti] + others, len(others) + 1)
    with st.container(border=True):
        st.caption("Which term means this?")
        ui.read_aloud(f"mkm_{K['i']}", f'<div class="qtext">{bold(t["def"])}</div>')
    if K["picked"] is None:
        def pick(i):
            ok = i == ti
            K["picked"] = i; K["res"].append(ok)
            b = ms["terms"].get(str(ti), 0)
            ms["terms"][str(ti)] = min(3, b + 1) if ok else 0
            if ok:
                store.add_xp(3)
        for n, i in enumerate(K[opts_key]):
            st.button(strip_tags(terms[i]["term"]), key=f"mkp_{K['i']}_{n}", width="stretch", on_click=pick, args=(i,))
        return
    html = ""
    for i in K[opts_key]:
        cls = "right" if i == ti else "wrong" if i == K["picked"] else "dim"
        html += f'<div class="opt {cls}"><span>{terms[i]["term"]}</span></div>'
    ui.html(html)
    st.button("Next", type="primary", width="stretch", key=f"mkn_{K['i']}",
              on_click=lambda: K.update(i=K["i"] + 1, picked=None))
