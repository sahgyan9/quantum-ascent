# Use of AI in This Project

The WISER challenge requires that *"any use of generative AI or coding assistants must be
clearly documented,"* and that the team *"be able to explain, verify, and defend all
submitted work."* This document is that disclosure. It is written to be honest about where
AI helped, and — more importantly — to show the **guardrails that keep the physics correct**
regardless of how any line was drafted.

## Short version

AI (Anthropic's Claude, via the Claude Code assistant) was used as a **development and
drafting assistant** throughout: writing website code, scaffolding notebooks, drafting prose,
and building the test infrastructure. **No AI runs at runtime** — the shipped course does not
call any model. Every piece of physics is **human-directed, human-reviewed, and pinned down by
an executable test suite** that anyone can re-run with a single `pytest` command
(currently **88 passing tests**, covering all six basecamps end to end — including the full
QAOA Max-Cut capstone).

## Where AI was used

- **Website & widgets** — HTML/CSS/JavaScript for the course site and the interactive
  widgets (Bloch Sampler, Gate Playground, …) were drafted with AI assistance and then
  reviewed, tested, and refined by hand through live use.
- **Notebook authoring** — AI helped scaffold the solution notebooks and the narrative
  copy, following a human-authored pedagogical style guide (see `CLAUDE.md`).
- **Test infrastructure** — the checkers, the notebook-execution harness, the widget smoke
  tests, and the Python↔JavaScript completion-code parity test were built with AI assistance,
  test-first (the project follows a stability-first rule: tests before features).
- **Documentation** — these `docs/` files and the README were drafted with AI and edited by
  the team.

## Where AI is **not** used

- **Not at runtime.** The course website and notebooks call **no** AI model. The "Analogy
  Studio" *generates a prompt* for the learner to paste into their own LLM; the course itself
  never sends a request anywhere. This means the resource costs nothing to run, works offline,
  and cannot silently break or hallucinate during a lesson.
- **Not as an unchecked authority on physics.** No physics claim is trusted because "the AI
  said so." See the verification layers below.

## How we keep it technically accurate (verify & defend)

The brief's key concern is technical correctness. Our defence is not "we trust the AI" — it
is a stack of independent checks:

1. **Executable tests as ground truth.** Every solution notebook is *executed end-to-end* in
   CI; a wrong gate or a mis-stated amplitude makes a cell fail and blocks the build. The
   quantum checkers use real simulation (Qiskit Aer) and statistical tests, not pattern
   matching.
2. **Cross-implementation checks.** The completion-code hash is implemented twice (Python and
   JavaScript) and a test asserts the two agree — a technique we use precisely *because*
   independent re-derivation catches mistakes a single author (human or AI) would miss.
3. **Human verification against standard references.** The physics is checked against
   established sources (Nielsen & Chuang; Qiskit and PennyLane documentation) — e.g. the
   Born rule $P=|\text{amplitude}|^2$, $H\cdot Z\cdot H = X$, Qiskit's little-endian bit
   ordering, and the QAOA Max-Cut ground energy are all independently confirmed and pinned by
   tests (the capstone's answer is cross-checked against a brute-force maximum cut).
4. **A myth-avoidance style rule.** Our pedagogy explicitly *rejects* common AI/pop-science
   errors (e.g. "a qubit is 0 and 1 at the same time"). The AI was steered away from these,
   and reviewers watched for them, because catching that failure mode is a core design goal.

## Attribution

- Development assistant: **Claude Code** (Anthropic).
- Pedagogical influences (properly attributed, see README): QWorld's QNickel gap-fill
  methodology; NVIDIA CUDA-Q Academic's widget-first teaching.
- All third-party libraries are open-source and used under their published licenses.

The team can explain and defend any part of the submission on request.
