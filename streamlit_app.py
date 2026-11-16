"""Phase 4 Sparky Trainer — Streamlit app.

Run locally:  streamlit run streamlit_app.py
"""
from __future__ import annotations

import time

import streamlit as st

from sparky import pages, store, ui

st.set_page_config(page_title="Phase 4 Trainer", page_icon="⚡", layout="centered",
                   initial_sidebar_state="collapsed")
ss = st.session_state

# ---- navigation (set up first, so a direct link like /quiz survives the loading run)
P = {
    "home": st.Page(pages.home, title="Home", icon=":material/home:", url_path="home", default=True),
    "t2": st.Page(pages.t2_map, title="T2 Map", icon=":material/grid_view:", url_path="t2"),
    "mock": st.Page(pages.mock, title="Mock T2", icon=":material/description:", url_path="mock"),
    "board": st.Page(pages.board, title="Board Builder", icon=":material/electrical_services:", url_path="board"),
    "cards": st.Page(pages.cards, title="Flashcards", icon=":material/style:", url_path="cards"),
    "quiz": st.Page(pages.quiz, title="Quiz", icon=":material/timer:", url_path="quiz"),
    "lab": st.Page(pages.lab, title="Formula Lab", icon=":material/calculate:", url_path="lab"),
    "maths": st.Page(pages.maths, title="Maths", icon=":material/function:", url_path="maths"),
    "pictures": st.Page(pages.pictures, title="Diagrams", icon=":material/schema:", url_path="diagrams"),
    "snap": st.Page(pages.snap, title="Symbol Snap", icon=":material/bolt:", url_path="snap"),
}
pages.PAGES.update(P)
pg = st.navigation(list(P.values()), position="top")


# ---- load saved progress from the browser (first run of a session waits for it)
if not store.load():
    ui.inject_css(ui.DEFAULT_SETTINGS)
    st.header("Phase 4 Trainer")
    st.write("Loading your progress…")
    st.button("Start without saved progress", on_click=store.start)
    st.stop()

S = store.S()
ui.inject_css(S["settings"])

# ---- top bar: name, level, display settings
def _set(field: str, key: str):
    if ss.get(key) is not None:  # a segmented control can be clicked off
        S["settings"][field] = ss[key]


cur, _nxt = store.level()
c1, c2 = st.columns([3, 2], vertical_alignment="center")
c1.markdown(f"**⚡ Phase 4 Trainer**  \n:gray[{cur[1]} · {S['xp']} XP]")
with c2.popover("Aa  Display", width="stretch"):
    cfg = S["settings"]
    st.selectbox("Font", list(ui.FONTS), index=list(ui.FONTS).index(cfg["font"]) if cfg["font"] in ui.FONTS else 0,
                 key="set_font", on_change=_set, args=("font", "set_font"))
    st.slider("Text size", 15, 28, int(cfg["size"]), key="set_size", on_change=_set, args=("size", "set_size"))
    st.segmented_control("Spacing", list(ui.SPACING), default=cfg["spacing"], key="set_spacing",
                         on_change=_set, args=("spacing", "set_spacing"))
    if ui.is_dark():
        st.caption("Background colours work in light mode.")
    else:
        st.selectbox("Background colour", list(ui.TINTS),
                     index=list(ui.TINTS).index(cfg["tint"]) if cfg["tint"] in ui.TINTS else 0,
                     key="set_tint", on_change=_set, args=("tint", "set_tint"))
    st.select_slider("Read-aloud speed", [0.7, 0.8, 0.9, 1.0, 1.1, 1.2], value=cfg["rate"], key="set_rate",
                     format_func=lambda v: {0.7: "Slow", 0.9: "Normal", 1.2: "Fast"}.get(v, str(v)),
                     on_change=_set, args=("rate", "set_rate"))
    st.toggle("Reading ruler (follows the mouse)", value=cfg["ruler"], key="set_ruler",
              on_change=_set, args=("ruler", "set_ruler"))
    st.caption("Dark mode: open the **⋮** menu (top right) → **Settings** → theme.")

# ---- break reminder every 15 minutes
now = time.time()
ss.setdefault("_last_break", now)
if now - ss._last_break > 15 * 60:
    st.toast("15 minutes done. Stand up, stretch, grab a drink. Take a 2-minute break.", icon=":material/self_improvement:")
    ss._last_break = now

pg.run()

ui.reading_ruler(S["settings"]["ruler"])
store.persist()
