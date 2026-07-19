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
| [PennyLane](https://pennylane.ai) | `0.45.0` | Used from Basecamp 5 onward for the variational / gradient-based material, where its autodiff model is the clearest teaching vehicle. |

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

- **pytest** — the whole project is built test-first (see `CLAUDE.md`'s stability-first
  rule). The suite runs checker unit tests, executes every solutions notebook top-to-bottom,
  smoke-tests every widget, and verifies the Python↔JavaScript completion-code parity.
- Run `pytest` from the repo root to reproduce the entire verification pass in one command.

## What we deliberately did **not** use

No React/Vue/Svelte, no bundler, no database, no backend, no analytics, no paid APIs, no
LLM at runtime. Every one of those would add a dependency, a failure mode, or a barrier to
reproduction. The Analogy Studio generates a *prompt* for the learner to paste into whatever
LLM they already use — the course itself never calls a model, so it costs nothing to run and
never breaks when an API changes.
