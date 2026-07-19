# 🏔️ Quantum Ascent

**Learn quantum computing by climbing — from your first qubit to solving real
optimization problems with QAOA.**

Built for the [WISER Education Challenge 2026](https://www.thewiser.org/summer-program-2026/wisereducationchallenge)
(see [Instruction_from_WISER.md](Instruction_from_WISER.md) for the brief).

## The idea

Most quantum courses show you slides, then quiz you. Quantum Ascent makes you *do*
the physics, three ways per concept:

1. **🎛️ Play first** — every concept starts as an interactive widget (sliders,
   measurements, live histograms) so your hands build intuition before the math arrives.
2. **⛏️ Fill the gaps** — Jupyter notebooks give you the scaffolding; *you* write the
   quantum code. Instant checkers explain not just *that* you're wrong but *why* —
   and honest shot noise never fails a correct answer (chi-square, not exact-match).
3. **🎨 Make it yours** — the Analogy Studio engineers AI prompts with the precise
   physics baked in, so your favorite AI explains each concept through *your* world
   without pop-science myths.

Progress, XP, and badges track your ascent up six basecamps:
**Qubits → Gates → Entanglement → Hamiltonians → Variational Principle → 🏔️ QAOA Summit.**

## Quick start

**Learner (nothing to install):** visit the [course website](https://quantum-ascent-77617.web.app),
open a basecamp, and hit "Open in Colab".

**Local:**
```bash
pip install -r requirements.txt
jupyter lab notebooks/01_qubits_and_superposition.ipynb   # the course
python tools/serve_local.py                               # the website, at localhost:8000
pytest                                                    # verify everything
```

## Repository structure

- `notebooks/` — interactive course notebooks (gap-fill tasks + instant checkers)
  - `solutions/` — worked solutions (source of truth; student copies are derived)
  - `q2q/` — helper package: checkers, widget embedding, oracle black-boxes
- `website/` — the course platform (Firebase Hosting): ascent map, quizzes,
  XP/badges, widget gallery, Analogy Studio
- `website/widgets/` — self-contained HTML/JS interactives (zero dependencies)
- `tools/` — deterministic scripts (notebook generation, student-copy builder, local server)
- `tests/` — checker unit tests, full notebook execution, widget smoke tests
- `docs/` — target audience, learning objectives, methodology, technologies, AI-use
  disclosure, user guide, future improvements

## Status

🚧 Basecamps 1–2 (The Qubit & Superposition; Gates & Circuits) are live — each with its
interactive widget, gap-fill notebook, quiz, and completion-code handshake. Basecamps 3–6
are being carved out of the mountain — follow the
[ascent map](https://quantum-ascent-77617.web.app/ascent.html).

## License & attribution

Code: [Apache-2.0](LICENSE) · Content: [CC-BY-4.0](LICENSE-CONTENT.md).
Pedagogy inspired by [QWorld's QNickel](https://qworld.net) gap-fill methodology and
[NVIDIA CUDA-Q Academic's](https://github.com/NVIDIA/cuda-q-academic) widget-first
teaching. AI assistance (Claude Code) is used for development and documented in
[`docs/ai_use.md`](docs/ai_use.md); all physics is human-verified against standard
references and executable tests. Full stack: [`docs/technologies.md`](docs/technologies.md).
