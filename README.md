# 🏔️ Quantum Ascent

**Learn quantum computing by climbing — from your first qubit to solving real
optimization problems with QAOA.**

Built for the [WISER Education Challenge 2026](https://www.thewiser.org/summer-program-2026/wisereducationchallenge)
(see [Instruction_from_WISER.md](Instruction_from_WISER.md) for the brief).

## The idea

Most quantum courses show you slides, then quiz you. Quantum Ascent makes you *do*
the physics, and it does it **honestly** — no "0 and 1 at the same time", no
"tries all answers at once", and a capstone that shows you where the algorithm
*fails*.

1. **🎛️ Play first** — every concept starts as an interactive widget (sliders,
   measurements, live histograms) so your hands build intuition before the math arrives.
2. **⛏️ Do the physics — on whichever track suits you.** Both set the same tasks
   and mint the same completion code:
   - **Browser track** — build real circuits by clicking, in the page, with
     **nothing to install and no account**. Runs an exact statevector simulator
     that our test suite checks against Qiskit to twelve decimal places.
   - **Notebook track** — the same tasks in Jupyter/Colab against **real Qiskit**.
   Checkers explain not just *that* you're wrong but *why*, hints escalate over
   three rungs instead of handing you the answer, and honest shot noise never
   fails a correct answer (chi-square, not exact-match).
3. **🔮 Predict, then find out** — every task asks you to commit to a prediction
   before you run anything. Those are recorded, and at the Summit you get a
   **calibration report**: not just what you learned, but how well you can judge
   your own understanding.
4. **🎨 Make it yours, then audit it** — the Analogy Studio engineers AI prompts
   with the precise physics baked in, then lets you paste the AI's answer back
   and scan it for the myths it was told not to use.

Progress, XP, and badges track your ascent up six basecamps:
**Qubits → Gates → Entanglement → Hamiltonians → Variational Principle → 🏔️ QAOA Summit.**

## Quick start

**Learner (nothing to install, no account):** visit the
[course website](https://quantum-ascent-77617.web.app) →
[Kit Check](https://quantum-ascent-77617.web.app/kit-check.html) (10 min, repairs the
maths and Python the course actually leans on) →
[Basecamp 1 in your browser](https://quantum-ascent-77617.web.app/lab.html?id=01).

Want the industry SDK instead? Every basecamp also has a one-click
**Open in Colab** button.

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
- `website/` — the course platform (Firebase Hosting): ascent map, Kit Check,
  browser Lab, quizzes, XP/badges, widget gallery, Analogy Studio, Myth Autopsy,
  pre/post diagnostic
- `website/assets/js/qsim.js` — the exact statevector simulator behind the browser
  track, verified against Qiskit in `tests/test_qsim.py`
- `website/widgets/` — self-contained HTML/JS interactives (zero dependencies)
- `tools/` — deterministic scripts (notebook generation, student-copy builder, local server)
- `tests/` — checker unit tests, full notebook execution, widget smoke tests,
  browser-track/Qiskit parity, and the capstone's numerical claims
- `docs/` — target audience, learning objectives, methodology, technologies, AI-use
  disclosure, pedagogical style guide, educator guide, user guide, future improvements

## Status

🏔️ **All six basecamps are live** — the full ascent from a single qubit to a QAOA Max-Cut
summit. Each one ships an interactive widget, a gap-fill notebook, a quiz, and a
completion-code handshake that lights up the [ascent map](https://quantum-ascent-77617.web.app/ascent.html):

1. **The Qubit & Superposition** — amplitudes, the Born rule, your first circuit
2. **Gates & Circuits** — rotations, unitarity, the endianness trap
3. **Entanglement** — Bell pairs, correlations, and the no-faster-than-light-signalling myth
4. **Hamiltonians & Energy** — observables, expectation values, the ZZ cost Hamiltonian
5. **The Variational Principle** — a parameterized ansatz + a classical optimizer descending an energy landscape
6. **Summit: QAOA for Max-Cut** — encode, build the ansatz, optimize, sample a maximum
   cut, and then meet a **frustrated triangle** (best possible cut still leaves an edge
   uncut) and a **5-cycle** (where $p=1$ genuinely falls short at ratio 0.94) so the word
   *Approximate* actually gets paid off

Plus **Basecamp 0 · Kit Check**, a ten-minute prerequisite repair — radians, the
half-angle, dictionaries, `def … return`, squaring a negative — because what derails
beginners here is never the quantum mechanics.

The full pytest suite (**302 checks**) executes every solutions notebook end to end,
cross-checks the web↔notebook completion codes, verifies the browser simulator against
Qiskit to 1e-12 across 21 circuits, proves all twelve browser tasks are solvable and
every hint's numbers are true, and recomputes every numerical claim the capstone makes
in prose.

```bash
pytest
```

## License & attribution

Code: [Apache-2.0](LICENSE) · Content: [CC-BY-4.0](LICENSE-CONTENT.md).
Pedagogy inspired by [QWorld's QNickel](https://qworld.net) gap-fill methodology and
[NVIDIA CUDA-Q Academic's](https://github.com/NVIDIA/cuda-q-academic) widget-first
teaching. AI assistance (Claude Code) is used for development and documented in
[`docs/ai_use.md`](docs/ai_use.md); all physics is human-verified against standard
references and executable tests. Full stack: [`docs/technologies.md`](docs/technologies.md).
