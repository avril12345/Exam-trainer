# CLAUDE.md

Streamlit app (`streamlit_app.py` + `sparky/` package). Content lives in `data/*.json`. See README.md for the layout. The original single-file version is in `legacy/index.html`, kept for reference only.

Run: `.venv/Scripts/streamlit run streamlit_app.py` (venv made with `uv venv` + `uv pip install -r requirements.txt`). Deploys to Streamlit Community Cloud.

## Who it's for
A 27-year-old electrical apprentice with dyslexia and some ADHD, studying for the Irish SOLAS Phase 4 exams. T2 (Installation) is his priority; Maths is also covered.

## Rules when editing
- Keep the tone adult and trade-like. Nothing childish (no cartoons or emoji in content).
- Celebrations (asked for by the owner): short wire-colour confetti (`ui.cheer`) for a right answer or a finished set, and an electric-arc "buzz" (`ui.buzz`) each time the level bar passes another 10 %. Both skip for reduced motion; confetti can be turned off in Display.
- Feedback is encouraging: a mistake is "not yet" and goes to the review list. Use soft terracotta (`--bad`), not alarm red.
- Dyslexia-friendly: Lexend body font, short sentences, one question per screen, bold the key word in questions (`**word**`), read-aloud on all text (`ui.read_aloud`), big tap targets (≥ 44 px), no italics.
- Image-led: prefer diagrams (inline SVG using the `dg` classes) over text.
- Calculations go to 3 decimal places (the exam asks for this). Keep quantity colours consistent (`SYM` map: V blue, I red, R/Z orange, P green, f/time purple, other teal).
- Regulation facts that come from ET101 get `"c": 1` (the "Check ET101" tag) unless verified against the book.
- Progress lives in `st.session_state.S` and is saved to browser localStorage by `store.persist()` at the end of each run. The app must still work if storage is unavailable.
- Browser components use `st.components.v2` (inline, no iframe), so the global CSS in `ui.inject_css` applies to them.
- Test in a narrow (390 px) viewport.
