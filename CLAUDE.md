# CLAUDE.md

Single-file web app: everything lives in `index.html` (HTML, CSS and vanilla JS, with no build or dependencies apart from Google Fonts). See README.md for how the code is laid out.

## Who it's for
A 27-year-old electrical apprentice with dyslexia and some ADHD, studying for the Irish SOLAS Phase 4 exams. T2 (Installation) is his priority.

## Rules when editing
- Keep the tone adult and trade-like. Nothing childish (no cartoons, confetti or emoji).
- Dyslexia-friendly: Lexend body font, short sentences, one question per screen, bold the key word in questions, read-aloud available on all text, big tap targets (≥ 44 px).
- Image-led: prefer diagrams (inline SVG using the `dg` classes and the `L()` label helper) over text.
- Calculations go to 3 decimal places (the exam asks for this). Keep quantity colours consistent (`SYM` map: V blue, I red, R/Z orange, P green, f/time purple, other teal).
- Regulation facts that come from ET101 get `c:1` (the "Check ET101" tag) unless verified against the book.
- Progress uses `localStorage` behind the `store` helper (try/catch). The app must still work without it.
- Test in a narrow (390 px) viewport.
