# Technologies Used

Quantum Ascent deliberately favours **boring, reproducible, zero-lock-in** technology.
A judge (or an educator adopting the course) should be able to clone the repo, run one
`pip install`, and have every notebook execute and every checker pass — no accounts, no
build step, no paid services. That constraint drove every choice below.

---

## Quantum stack

| Tool | Pinned version | Why |
|---|---|---|
| [Qiskit](https://www.ibm.com/quantum/qiskit) | `2.3.1` | Primary circuit SDK — the industry-standard teaching stack, and the one learners meet again in real research. |
| [Qiskit Aer](https://github.com/Qiskit/qiskit-aer) | `0.17.2` | Local high-performance simulator. Every notebook runs on a laptop; no quantum hardware or cloud queue required. |

**One SDK, on purpose.** We considered teaching PennyLane alongside Qiskit for the
variational material in Basecamps 5–6 and decided against it. A beginner who is still
building their first mental model of a circuit does not benefit from two APIs for the same
idea — they benefit from one API they can predict. Qiskit alone carries the whole course.

**Versions are pinned exactly.** The Colab bootstrap cell installs these same pins, so
the code a student runs in the browser is byte-for-byte the code our test suite executes.
This is what makes "it works on my machine" a guarantee rather than a hope.

## Scientific / numerical

- **NumPy, SciPy** — linear algebra, and the statistical tests (chi-square goodness-of-fit)
  that let our checkers judge *distributions* instead of demanding exact string matches.
- **Matplotlib** + **pylatexenc** — circuit diagrams and plots rendered inside notebooks.

## Course notebooks & tooling

- **Jupyter / nbformat / nbclient** — notebooks are the delivery format; `nbclient` executes
  them end-to-end in CI so a broken notebook can never ship.
- **Google Colab** — the zero-install entry point. Every basecamp has an "Open in Colab"
  button; learners need only a browser and a Google account.
- **Custom generation pipeline** (`tools/`) — solution notebooks are the single source of
  truth; `build_solutions.py` mechanically strips them into student gap-fill copies, so the
  two can never drift apart. LaTeX macros are expanded at build time and tests assert none
  ship unexpanded.

## The browser track's engine

- **`qsim.js`** — a dense **statevector simulator written in plain JavaScript**, no
  dependencies and no build step. It is what lets a learner finish any basecamp without
  installing Python.

  We did not choose this over Qiskit; Qiskit simply cannot run in a browser (its core has
  been compiled Rust since 1.0, and Aer is C++). For the ≤ 5 qubits this course uses, a
  dense statevector is at most 32 complex amplitudes, so exact simulation is a few dozen
  lines — and *exact* is meant literally. `tests/test_qsim.py` runs `qsim.js` under Node
  against Qiskit + Aer over 21 circuits and asserts agreement to **1e-12** on
  probabilities, Pauli expectation values and bitstring ordering.

  The endianness tests matter most: Basecamp 2 teaches Qiskit's little-endian bitstring
  order *deliberately, as a trap*, and a browser track using the opposite convention
  would teach that trap backwards. So the two tracks are pinned to agree, and a drift
  fails the build rather than confusing a learner.

- **Node.js** — test-time only, never shipped. It is how pytest drives the JavaScript.

## Website (the course platform)

- **Vanilla HTML / CSS / JavaScript** — no framework, no bundler, no `node_modules`. The
  entire site is static files that open directly in a browser.
- **Self-contained widgets** — each interactive (Bloch Sampler, Gate Playground, …) is a
  single HTML file with inline JS and **zero external dependencies**, so it runs offline,
  embeds anywhere, and can be audited at a glance.
- **Firebase Hosting** — static CDN hosting for the live site
  ([quantum-ascent-77617.web.app](https://quantum-ascent-77617.web.app)). Nothing dynamic
  runs server-side; progress, XP and badges live in the learner's own browser
  (`localStorage`).
- **Cross-world completion codes** — a hand-rolled 32-bit FNV-1a hash, implemented
  identically in Python (`q2q/progress.py`) and JavaScript (`progress.js`) and cross-checked
  by a test, lets a finished notebook mint a code the website verifies **offline** — no
  server, no accounts.

## Testing & reproducibility

- **pytest** — the whole project is built test-first (stability-first rule: tests, then
  fixes, then features). **302 checks**, covering:
  - every solutions notebook executed top-to-bottom;
  - the browser simulator against Qiskit + Aer, 21 circuits, 1e-12;
  - all twelve browser-track tasks proved solvable, plus the *specific wrong answers* the
    copy promises to diagnose, plus the numbers quoted inside the hints;
  - every numerical claim the capstone makes in prose, recomputed;
  - the myth scanner in both directions — it must catch myths and must **not** fire on
    correct physics;
  - the Python↔JavaScript completion-code parity;
  - site integrity: no dead links, no orphan pages, no stub language, complete navigation;
  - an accessibility floor: every widget must expose an `aria-live` text mirror.
- Run `pytest` from the repo root to reproduce the entire verification pass in one command.
  (Node.js is needed for the JavaScript-side tests; they skip cleanly without it.)

## What we deliberately did **not** use

No React/Vue/Svelte, no bundler, no database, no backend, no analytics, no paid APIs, no
LLM at runtime. Every one of those would add a dependency, a failure mode, or a barrier to
reproduction. The Analogy Studio generates a *prompt* for the learner to paste into whatever
LLM they already use — the course itself never calls a model, so it costs nothing to run and
never breaks when an API changes.
