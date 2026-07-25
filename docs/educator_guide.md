# Educator Guide — adopting Quantum Ascent

**Time to first class: about 15 minutes.** Nothing to install, no accounts to create, no server
to run, no data leaving your students' browsers.

This guide is deliberately short and deliberately honest about what the platform does *not* do
(see [What this is not](#what-this-is-not)).

---

## 1. The fastest possible adoption (5 minutes)

Send your students one link:

```
https://quantum-ascent-77617.web.app
```

That's it. The site works on a phone, a Chromebook, or a locked-down lab machine. Progress, XP
and badges live in each learner's own browser (`localStorage`) — there is no sign-up, so there
is no roster to manage and no personal data to protect.

## 2. Choosing a track

Every basecamp exists in two equivalent forms. **Pick one, or let students pick.**

| | **Browser track** | **Notebook track** |
|---|---|---|
| Needs | A browser | A Google account (Colab) or local Python |
| Runs | An exact statevector simulator written in JavaScript | Real **Qiskit 2.3.1** + Aer |
| Setup time | 0 s | ~60–90 s for `pip install` on first run |
| Best for | First pass, in-class time, phones, no-install environments | Students who want the industry SDK on their CV |

Both tracks cover the same concepts, set the same tasks, and mint the same completion codes.
**Neither is a lesser version of the other.** If your session is 50 minutes and you cannot
afford a Colab round-trip, use the browser track without hesitation.

## 3. Running it as a course

A six-week shape that works:

| Week | Basecamp | In class | Homework |
|---|---|---|---|
| 0 | **Kit Check** | Run it together, address the radians question | — |
| 1 | 1 · The Qubit | Widget + discussion | Notebook 1 + quiz |
| 2 | 2 · Gates | Widget, then the endianness trap as a live demo | Notebook 2 + quiz |
| 3 | 3 · Entanglement | Two-pane no-signalling demo | Notebook 3 + quiz |
| 4 | 4 · Hamiltonians | Energy Meter | Notebook 4 + quiz |
| 5 | 5 · Variational | Landscape widget | Notebook 5 + quiz |
| 6 | 6 · Summit | QAOA capstone, run as a group | Notebook 6 + post-assessment |

Budget **90 minutes per basecamp** for a genuine beginner, not the ~50 minutes of content the
site quotes. The gap is where the predicting and the being-stuck happen, and that is the part
that teaches.

## 4. Embedding in your LMS (Canvas, Blackboard, Moodle, Google Classroom)

Every widget is a single self-contained HTML file with no external dependencies, so it embeds
anywhere that allows an `<iframe>`:

```html
<!-- One widget, embedded in a Canvas page or a slide deck -->
<iframe src="https://quantum-ascent-77617.web.app/widgets/bloch-sampler/index.html"
        width="900" height="560" style="border:1px solid #e2dfd8;border-radius:10px"
        title="Bloch Sampler — interactive qubit measurement"></iframe>
```

Swap the widget name for any of: `coin-spinner`, `bloch-sampler`, `gate-playground`,
`entanglement-explorer`, `energy-meter`, `qaoa-landscape`, `maxcut-painter`, `circuit-lab`.

To embed a whole basecamp, point the `iframe` at
`https://quantum-ascent-77617.web.app/module.html?id=03`.

### Colab badge for an assignment

```markdown
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sahgyan9/quantum-ascent/blob/main/notebooks/03_entanglement_and_multiqubit.ipynb)
```

## 5. Assessment — what you can actually collect

**The pre/post concept diagnostic** (`/assessment.html`) is the piece designed for you. Ten
questions, taken once before Basecamp 1 and again after the Summit, scored locally, showing
each learner their own delta. Ask students to run the pre-test in the first five minutes of
week 0 — the number is worthless if they take it after they've started.

**Completion codes.** When a learner finishes a notebook's tasks, the notebook prints a code
like `QA-03-1A2B-3C4D`. It is a hash of the basecamp id, so it is *proof the tasks passed*, not
proof of identity — treat it as a completion checkbox, not an exam.

**Progress export.** Any learner can click *Export progress* in the site footer to download a
small JSON file with their XP, badges, quiz scores and assessment deltas. Collecting those
files is the low-tech gradebook: no backend, no privacy exposure, and it works offline.

```jsonc
// quantum-ascent-progress.json — what a student hands in
{ "xp": 740, "badges": ["Superposed", "Entangled"],
  "modules": { "01": { "completed": true, "quizScore": 1, "notebookDone": true } } }
```

## 6. Running it offline / on an air-gapped network

```bash
git clone https://github.com/sahgyan9/quantum-ascent.git
cd quantum-ascent
python tools/serve_local.py       # serves the whole site at localhost:8000
```

The widgets and the browser track have **zero external dependencies** and will work with the
network unplugged. (Two caveats, stated plainly: the site loads Google Fonts and KaTeX from a
CDN — without a network you get system fonts and raw LaTeX, but everything still *functions*.
The notebook track needs the network once, for `pip install`.)

## 7. Licence — you may genuinely fork this

- **Code:** Apache-2.0
- **Content** (notebook prose, quiz questions, widget copy): **CC-BY-4.0**

You may translate it, re-sequence it, drop basecamps, put your institution's name on your fork,
and use it commercially. Attribution is the only requirement. If you translate it, the glossary
(`website/assets/data/glossary.json`) and the quiz bank
(`website/assets/data/quizzes.json`) are plain JSON and are the right places to start.

## 8. The house style, if you write more of it

If you are extending the course, [`pedagogical_style_guide.md`](pedagogical_style_guide.md) is
the specification — including the one rule we would ask you not to break: **wherever a quantum
state is drawn, the visual proportions are exactly the Born-rule probabilities.**

Please also keep the myth discipline. No "0 and 1 at the same time," no "tries all answers at
once." The [Myth Autopsy](https://quantum-ascent-77617.web.app/analogy-studio.html) page exists
to show students what those claims cost.

## What this is not

Said plainly so you can plan around it:

- **No LTI, no gradebook sync.** Progress is per-browser. Clearing site data loses it. The
  JSON export in §5 is the workaround, and it is a real workaround, not a polished one.
- **No identity.** Completion codes prove a task passed, not *who* passed it. Do not use them
  as summative assessment for credit.
- **English only** at present.
- **No quantum hardware.** Everything is simulated — deliberately, so the course costs nothing
  to run and never sits in a queue.

## Questions

Open an issue at [github.com/sahgyan9/quantum-ascent](https://github.com/sahgyan9/quantum-ascent).
If you teach with it, we would genuinely like to hear the pre/post numbers you get.
