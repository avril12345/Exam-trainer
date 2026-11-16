"""Study content loaded from the JSON files in ``data/``.

The JSON was extracted from the original single-file app (``legacy/index.html``).
Edit the JSON to add or fix questions.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def _load(name: str):
    with open(DATA / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


MCQ: list[dict] = _load("mcq")            # {p, t, q, o[], a, w}
CARDS: list[dict] = _load("cards")        # {p, s, m, n, t, q, a[], r, c, fig}
SLOTS: list[list] = _load("slots")        # [[1, 'Motor couplings & bearings'], ...]
SLOT_TITLE = {n: t for n, t in SLOTS}
SLOT_LAB: dict[int, list[str]] = {int(k): v for k, v in _load("slot_lab").items()}
# Note: in the original app two generators shared the id "flux", so Q17 linked to the T1
# flux-density one. The T1 generator is now "fluxB", so "flux" here means luminous flux (T2).
BOARD_SCEN: list[dict] = _load("board_scen")
SYM: dict[str, list[str]] = _load("sym")  # key -> [html label, colour class]
DIAG: dict[str, dict] = _load("diag")     # key -> {n, t, svg}
SYMBOLS: list[dict] = _load("symbols")    # {n, s}

BOX_NAMES = ["New", "Learning", "Nearly", "Known"]


def slot_cards(s: int) -> list[int]:
    return [i for i, c in enumerate(CARDS) if c.get("s") == s]


def slot_pct(s: int, boxes: dict) -> int:
    idx = slot_cards(s)
    if not idx:
        return 0
    return round(sum(min(3, boxes.get(str(i), 0)) for i in idx) / (len(idx) * 3) * 100)


def bold(s: str) -> str:
    """Turn **word** into <b>word</b> (key words in questions)."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def strip_tags(s: str) -> str:
    """Plain text for button labels and speech: X<sub>L</sub> -> XL."""
    s = re.sub(r"<br\s*/?>", " ", s)
    return re.sub(r"<[^>]+>", "", s).replace("**", "")


def sym(k: str) -> str:
    label, cls = SYM.get(k, [k, "k"])
    return f'<span class="q {cls}">{label}</span>'


def fx(s: str) -> str:
    """Replace {key} markers in Formula Lab steps with colour-coded symbols."""
    return re.sub(r"\{(\w+)\}", lambda m: sym(m.group(1)), s)


@lru_cache(maxsize=None)
def sym_plain(k: str) -> str:
    return re.sub(r"<[^>]+>", "", SYM.get(k, [k])[0])
