# Phase 4 Sparky Trainer

A revision tool for the Irish SOLAS Electrical Apprenticeship, Phase 4 theory exams (T1 Science and T2 Installation). It is designed for a learner with dyslexia and ADHD: one question per screen, read-aloud on everything, large text controls, a cream or dark background, short sessions and image-led learning.

Open `index.html` in any browser. There is no build step and nothing to install.

## Features

- **T2 paper map**: the T2 paper has the same 20 question slots in the same order every year (2016–2026). Each slot lists every version that has been asked.
- **Mock T2 paper**: 20 questions in exam order. The learner self-marks against the key points, and the app totals the marks and gives a grade (Pass 50 %, Merit 65 %, Distinction 80 %).
- **Board Builder**: interactive practice for T2 Q7 (distribution board drawing), with phase-balance and device checks.
- **Flashcards**: 99 T2 and 10 T1 cards with key-point answers, using Leitner boxes.
- **Quick Shift**: 10 multiple-choice questions per round (69 T2 and 37 T1 in the bank).
- **Formula Lab**: 23 randomised calculation types with colour-coded, step-by-step working.
- **Diagrams**: 19 exam drawings with tap-to-reveal labels.
- **Symbol Snap**: a 60-second game for naming circuit symbols.

Progress is saved in `localStorage`, so it stays on one device.

## Code layout (all in `index.html`)

| Section | What it holds |
|---|---|
| `<style>` | Design tokens (cream/dark themes, quantity colours), all CSS |
| `MCQ` array | Multiple-choice questions `{p, t, q, o[], a, w}` |
| `CARDS` array | Flashcards `{p, s (T2 slot 1–20), m (marks), n (points needed), t, q, a[], r (reference), c (check ET101), fig}` |
| `GENS` array | Formula Lab generators: `make()` returns `{given, ask, ans, unit, steps}` |
| `DIAG` object | SVG diagrams. Labels use `L()`, so they can be hidden in "test me" mode |
| `SYMBOLS` array | IEC-style circuit symbols |
| T2 extras | `SLOTS`, extra T2 generators, `BOARD_SCEN` and `drawBoard()`, extra diagrams |
| Views | Hash-routed screens: `#home #t2 #mock #board #cards #quiz #lab #pictures #snap` |

## Content notes

- The questions and answers are original rewordings based on the topics that recur in past papers. The past papers themselves are not included in this repo (they are © SOLAS).
- Cards tagged **Check ET101** quote the National Rules for Electrical Installations. Some official model answers contradict each other (for example, burial depth for cable in a pipe: 250 mm vs 450 mm), so check these against the ET101 book.
