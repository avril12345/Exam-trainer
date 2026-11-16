# Phase 4 Sparky Trainer

A revision app for the Irish SOLAS Electrical Apprenticeship, Phase 4 theory exams (T1 Science, T2 Installation and Maths). It is built for a learner with dyslexia and ADHD: one question per screen, read-aloud on everything, adjustable text, tinted backgrounds, short sessions and picture-led learning.

## Run it

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Put it online (free)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Create app** → pick this repo, branch `main`, file `streamlit_app.py`.
3. Share the link. It works on a phone.

Progress is saved in the browser (localStorage), so it stays on the device he uses. There's no login.

## Features

- **T2 paper map**: the T2 paper has the same 20 question slots every year (2016–2026). Each slot lists every version that has been asked.
- **Mock T2 paper**: 20 questions in exam order. Self-mark against the key points; the app totals the marks and gives a grade (Pass 50 %, Merit 65 %, Distinction 80 %).
- **Board Builder**: interactive practice for T2 Q7 (distribution board drawing), with phase-balance and device checks. Shows a front-view picture of the board and the exam wiring drawing. 4 past-paper versions plus 5 sample questions in the same style (labelled "Sample question").
- **Flashcards**: 99 T2 and 10 T1 cards with key-point answers, using Leitner boxes.
- **Quick Shift quiz**: 10 multiple-choice questions per round (69 T2 and 37 T1 in the bank). Optional 2-minute clock.
- **Formula Lab**: 23 randomised calculation types with colour-coded, step-by-step working.
- **Maths**: worked examples (one step at a time), test questions (multiple choice or type the number) and key terms (flip cards and a match game).
- **Diagrams**: 19 exam drawings with tap-to-reveal labels.
- **Symbol Snap**: a 60-second game for naming circuit symbols. Shows the score, right/wrong and accuracy when time runs out or when Stop is pressed.
- **Block Drop**: one block at a time falls down the screen showing a circuit symbol or a short exam question. Tap one of 4 answers (or press 1–4 / A–D) before it lands. Questions take 15–25 seconds to fall, symbols 8 seconds. 3 lives, a speed bonus and a gentle speed-up (or "Steady pace"). Decks: T2, T1, Mixed or Symbols only. Optional read-aloud holds each block until it has been read. Missed questions go to the review list.

## Dyslexia-friendly design

- **Display** menu on every page: font (Lexend, Atkinson Hyperlegible, Verdana), text size, line/letter spacing, background tint (cream, soft blue, soft green, peach, grey), read-aloud speed, and a reading ruler that follows the mouse.
- **Read aloud** on every question, answer and explanation. Each word is highlighted as it is spoken.
- Short lines (max ~65 characters), left-aligned, no italics, key words in bold colour.
- Big buttons (52 px+), one question per screen, progress dots, a break reminder every 15 minutes.
- Light and dark themes (dark: ⋮ menu → Settings).

## Code layout

| Path | What it holds |
|---|---|
| `streamlit_app.py` | Entry point: navigation, loading saved progress, Display menu |
| `sparky/pages.py` | All screens (Home, T2 map, Mock, Board, Flashcards, Quiz, Formula Lab, Diagrams, Snap) |
| `sparky/maths.py` | The Maths tab |
| `sparky/ui.py` | Dyslexia CSS and browser components (read-aloud, diagram reveal, Snap game, clock, ruler) |
| `sparky/store.py` | Progress state and saving to the browser |
| `sparky/formulas.py` | Formula Lab generators |
| `sparky/board.py` | Board Builder drawing and checks |
| `sparky/content.py` | Loads the JSON content |
| `data/*.json` | Questions, flashcards, diagrams, symbols, paper map, maths content |
| `legacy/index.html` | The original single-file web app (kept for reference) |

### Adding maths content

Edit `data/maths.json`. The format is described at the top of `sparky/maths.py`. Remove `"sample": true` once the real content is in.

## Content notes

- The questions and answers are original rewordings based on the topics that recur in past papers. The past papers themselves are not included in this repo (they are © SOLAS).
- Cards tagged **Check ET101** quote the National Rules for Electrical Installations. Some official model answers contradict each other (for example, burial depth for cable in a pipe: 250 mm vs 450 mm), so check these against the ET101 book.
