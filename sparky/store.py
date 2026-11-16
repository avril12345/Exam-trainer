"""Progress, saved in the browser's localStorage.

On the first run of a session the app asks the browser for the saved progress
(one round-trip), then keeps it in ``st.session_state.S``. At the end of every run
the app writes ``S`` back to localStorage if it changed.

Rule for page code: change ``S`` inside button callbacks (``on_click``) or in the
normal flow, and avoid ``st.rerun()`` / ``st.switch_page()`` straight after a change,
because the save happens at the end of the script run.
"""
from __future__ import annotations

import copy
import json
import time

import streamlit as st

from .ui import DEFAULT_SETTINGS

KEY = "sparky_progress_v1"
LEVELS = [(0, "Apprentice"), (150, "Improver"), (400, "Advanced Improver"),
          (800, "Qualified Sparky"), (1500, "Master Electrician")]

DEFAULT_STATE = {
    "xp": 0, "answered": 0, "correct": 0, "bestShift": 0,
    "boxes": {},          # card index (str) -> Leitner box 0-3
    "missed": [],         # MCQ indexes answered wrong
    "mockBest": None, "mockLast": None, "snapBest": 0,
    "prefs": {"qmode": "T2", "qtimed": False, "labp": "T2", "fdeck": "T2", "bbsc": "b"},
    "settings": dict(DEFAULT_SETTINGS),
}

_JS = r"""
export default function({ data, setStateValue }) {
  const KEY = data.key;
  if (typeof data.save === 'string') { try { localStorage.setItem(KEY, data.save); } catch (e) {} }
  if (data.load) {
    let raw = '';
    try { raw = localStorage.getItem(KEY) || ''; } catch (e) { raw = ''; }
    setStateValue('stored', raw);
  }
}
"""
_storage = st.components.v2.component("sparky_storage", js=_JS)


def _merge(saved: dict) -> dict:
    s = copy.deepcopy(DEFAULT_STATE)
    for k, v in saved.items():
        if isinstance(v, dict) and isinstance(s.get(k), dict) and k != "boxes":
            s[k].update(v)
        else:
            s[k] = v
    return s


def load() -> bool:
    """Make sure ``st.session_state.S`` exists. Returns False while still waiting for the browser."""
    ss = st.session_state
    if "S" in ss:
        return True
    res = _storage(key="sparky_storage", data={"key": KEY, "load": True}, default={"stored": None},
                   on_stored_change=lambda: None)
    raw = res.get("stored")
    if raw is None:
        return False
    start(raw)
    ss._storage_mounted = True  # already on the page this run; persist() must not mount it twice
    return True


def start(raw: str = "") -> None:
    """Build the session's progress from the saved JSON (empty string = fresh start)."""
    ss = st.session_state
    try:
        saved = json.loads(raw) if raw else {}
    except (TypeError, ValueError):
        saved = {}
    ss.S = _merge(saved if isinstance(saved, dict) else {})
    ss._saved_json = json.dumps(ss.S, sort_keys=True)
    ss._session_start = time.time()


def persist() -> None:
    """Write progress to the browser if it changed. Call once, at the end of the script."""
    ss = st.session_state
    if "S" not in ss:
        return
    if ss.pop("_storage_mounted", False):
        return  # the next run will save anything that changed in this one
    now = json.dumps(ss.S, sort_keys=True)
    payload = {"key": KEY, "load": False}
    if now != ss.get("_saved_json"):
        payload["save"] = now
        ss._saved_json = now
    _storage(key="sparky_storage", data=payload, default={"stored": None}, on_stored_change=lambda: None)


def S() -> dict:
    return st.session_state.S


def add_xp(n: int) -> None:
    S()["xp"] += n


def level() -> tuple[tuple, tuple | None]:
    xp = S()["xp"]
    cur, nxt = LEVELS[0], None
    for i, lv in enumerate(LEVELS):
        if xp >= lv[0]:
            cur, nxt = lv, (LEVELS[i + 1] if i + 1 < len(LEVELS) else None)
    return cur, nxt


def box(i: int) -> int:
    return S()["boxes"].get(str(i), 0)


def set_box(i: int, b: int) -> None:
    S()["boxes"][str(i)] = b


def reset() -> None:
    settings = S()["settings"]
    st.session_state.S = copy.deepcopy(DEFAULT_STATE)
    st.session_state.S["settings"] = settings
