"""Author the Module 02 SOLUTIONS notebook (source of truth).

    python tools/make_module_02.py
    python tools/build_solutions.py 02     # then derive the student version

House pedagogy (see memory: narrative-first authoring style):
story & imagination first -> slow recap -> rename with the formal word ->
plain math -> widget play -> only then the formal tools. Every coding task is
preceded by a fully worked example of the exact same pattern (green check
included), and the task itself is a "change the moves" tweak.
"""

from nb_common import (
    REPO, analysis, analogy_callout, basecamp_footer, bootstrap_cell,
    briefing, code, exercise, md, task, write_notebook,
)

cells = []

# ----------------------------------------------------------------- header
cells.append(briefing(
    2, "Gates & Circuits",
    mission=(
        "In Basecamp 1 you spun a single coin. Now you'll learn the <b>moves</b> "
        "that steer it — and stack those moves into <b>circuits</b>. You'll meet "
        "the bit-flip <b>X</b> and the phase-flip <b>Z</b>, discover that the "
        "<i>order</i> you apply gates in changes the result, see why every "
        "quantum move can be <i>undone</i>, and dodge the #1 beginner trap in "
        "Qiskit: how it numbers qubits.<br><br>"
        "<i>New symbols and a little matrix or two show up here — but every one "
        "is just a tidy name for something you'll first watch happen in the "
        "widget. No memorising. We build it up slowly, one move at a time.</i>"
    ),
    objectives=[
        "Recognise the bit-flip **X** and the phase-flip **Z**, and describe **H** as the 'mixer' — all as simple moves of the arrow",
        "Stack gates into a circuit and predict the result, knowing that **order matters** (gates don't always commute)",
        "Explain why every gate is **reversible** (unitarity) — a quantum computer never quietly loses information",
        "Read Qiskit's qubit ordering correctly and step around the **endianness trap** when interpreting measurement bitstrings",
    ],
    minutes=50,
))
cells.append(bootstrap_cell())

# ----------------------------------------------------------------- 2.1
cells.append(md(r"""## 2.1 Gates are moves you can stack

Quick recap from Basecamp 1. You already met **two gates** without us making a fuss about it:

- the **Hadamard** ($H$) — it set a resting coin *spinning* (tipped $\ket{0}$ down to the fair-coin equator);
- the **rotation** $R_y(\theta)$ — the θ *slider* in gate form, tilting the arrow to any bias you like.

That's the whole idea of a **gate**: a *move* that takes the qubit's arrow from where it is to somewhere new. And just like dance steps, moves can be **stacked** — do one, then the next, then the next. A stack of gates is a **circuit**.

This basecamp is about two brand-new moves and what happens when you combine them. Let's meet them in the playground *before* we name any math."""))

cells.append(exercise(1, (
    "Open the <b>Gate Playground</b> below. It's a single qubit and a row of "
    "gate buttons — click one to drop it on the wire and watch the arrow move. "
    "<br>1️⃣ Click <b>X</b> once (starting from |0⟩). Where does the arrow go? "
    "Read the explanation — this move has a plain-English nickname. "
    "<br>2️⃣ Hit <b>Reset</b>, then click <b>H</b> (fair spin), then click <b>Z</b>. "
    "Did the P(0)/P(1) bars change at all? Look very closely. "
    "<br>3️⃣ Something <i>did</i> change even though the odds didn't — the widget "
    "tells you what. Keep that mystery in mind; it's the seed of Basecamp 3."
)))
cells.append(code('show_widget("gate-playground")'))

cells.append(md(r"""### Naming the two new moves

Time to rename what you just watched with the words the textbooks use.

**The bit-flip $X$.** Clicking $X$ swapped $\ket{0}$ and $\ket{1}$ — a definite 0 became a definite 1. It's the quantum version of the classical NOT gate: it flips the bit. On the Bloch arrow it's a half-turn (180°) that swings the north pole to the south pole.

**The phase-flip $Z$.** This one is sneakier. Clicking $Z$ *did not move the probabilities at all* — a fair coin stayed a fair coin. What it changed was the **phase**: the *sign* hiding on the $\ket{1}$ amplitude. It turns $\ket{1}$ into $-\ket{1}$, leaving $\ket{0}$ alone.

> 🧊 **Why should I care about an invisible sign?** Great question — hold it. A phase you can't see in a single measurement is exactly the ingredient that lets amplitudes *cancel* later (interference). That cancellation is where quantum computers get their edge. Basecamp 3 cashes this in; for now, just notice that $Z$ changes the *state* without changing the *odds*.

*(For the curious — each gate is also a little 2×2 matrix. Feel free to skim; we'll use them properly, not memorise them.)*

$$X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \qquad Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}, \qquad H = \hadamard$$"""))

cells.append(exercise(2, (
    "Back to the playground — this time test whether <b>order matters</b>. "
    "<br>1️⃣ <b>Reset</b>, then build <b>H</b> then <b>Z</b>. Note where the arrow "
    "points. "
    "<br>2️⃣ <b>Reset</b>, then build <b>Z</b> then <b>H</b> (same two gates, "
    "swapped). Does the arrow land in the <i>same</i> place? "
    "<br>3️⃣ Predict before you peek — then decide the quick check below."
)))
cells.append(code(
"""# Quick check — does the order of gates matter? (Predict first!)
quiz.ask("m2-order-matters")"""))

cells.append(md(r"""You just discovered that **gates usually don't commute**: $H$ then $Z$ is a *different* circuit from $Z$ then $H$. Order is not a detail — it's part of the recipe. (Sound familiar? "Socks then shoes" and "shoes then socks" use the same two actions and give very different results.)

Keep that in your pocket. Now let's build these circuits for real, in code."""))

# ----------------------------------------------------------------- 2.2
cells.append(md(r"""## 2.2 Building circuits in Qiskit

Same virtual lab as Basecamp 1 — `QuantumCircuit` to build, `AerSimulator` to run. We'll also grab **NumPy** this time, purely so we can talk to gates as little matrices when we want to. Run the setup:"""))
cells.append(code(
"""# Our tools again — the same two as Basecamp 1, plus NumPy for matrices.
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator"""))

cells.append(md(r"""### Worked example: a gate and its undo

Here's a circuit that applies $H$ **twice** to one qubit. Predict it before you run: $H$ sets the coin spinning… so what does a *second* $H$ do? (You saw the answer in the playground — two H's snapped the arrow right back.)

Instead of measuring, we'll check the circuit's **overall action** directly with `check_unitary_equiv`, which compares what your circuit *does* to a target — here, the "do-nothing" identity matrix `np.eye(2)`. A green PASS means the two H's truly cancel:"""))
cells.append(code(
"""# Build H then H on one qubit.
qc_hh = QuantumCircuit(1)
qc_hh.h(0)
qc_hh.h(0)

# Does this circuit do... nothing at all? Compare it to the identity (do-nothing) gate.
checkers.check_unitary_equiv(qc_hh, np.eye(2))"""))

cells.append(md(r"""That green light *is* **unitarity**: every quantum gate is **reversible**. Each move has an undo, so information is never destroyed along the way — a quantum computer only ever *rearranges* amplitudes, never erases them. ($H$ happens to be its own undo; so are $X$ and $Z$.)"""))
cells.append(code(
"""# Quick check — what do two H's in a row do?
quiz.ask("m2-unitary-undo")"""))

# ----------------------------------------------------------------- task 1
cells.append(task(1, (
    "Now stack three moves and discover a hidden identity. Build "
    "<code>qc_flip</code> by applying, in order, <b>H</b>, then <b>Z</b>, then "
    "<b>H</b> to a single qubit — exactly the H-then-Z you played with, capped "
    "by one more H. <br><i>Predict first:</i> Z alone does nothing to the odds… "
    "but sandwiched between two Hadamards? The checker compares your circuit to "
    "a mystery gate — run it and see which famous gate H·Z·H really is."
)))
cells.append(code(
"""# Build H, then Z, then H on one qubit — then discover what single gate it equals.
qc_flip = QuantumCircuit(1)
### BEGIN SOLUTION
qc_flip.h(0)
qc_flip.z(0)
qc_flip.h(0)
### END SOLUTION

# Nothing to change below — we compare your circuit's action to the mystery target.
checkers.check_unitary_equiv(qc_flip, targets.M2_FLIP)"""))
cells.append(analysis(r"""Surprise — **H·Z·H = X**, the bit-flip! A phase-flip, wrapped in
two Hadamards, becomes an honest bit-flip. Here's the intuition: the first $H$
rotates your point of view so that "phase" and "bit value" swap roles; $Z$ does
its phase-flip in that rotated frame; the last $H$ rotates back. What looked
invisible ($Z$ changing only a sign) became fully visible ($X$ flipping 0↔1).
This "sandwich a gate between Hadamards to change what it does" trick shows up
everywhere in quantum computing — and it's your first taste of *why* those
hidden phases are worth caring about."""))

# ----------------------------------------------------------------- 2.3
cells.append(md(r"""## 2.3 Two qubits, and the trap that catches everyone

Real circuits have more than one qubit. The moment you add a second, Qiskit springs a famous surprise on newcomers — so let's walk into it on purpose, with eyes open.

Make a **2-qubit** circuit. The qubits are numbered **qubit 0** and **qubit 1**. When you measure, Qiskit hands back a little string like `'10'` — and here's the trap:

> ⚠️ **Qiskit writes qubit 0 on the *right*.** The string is read **right-to-left**: the rightmost character is qubit 0, the next one left is qubit 1, and so on. (Computer scientists call this *little-endian* — the "littlest" qubit sits at the right end, exactly like the ones digit sits at the right end of the number 42.)

So a result of `'10'` means **qubit 1 = 1, qubit 0 = 0**. Let's prove it: we'll flip **qubit 1** and watch which character lights up."""))
cells.append(code(
"""# Worked example: a 2-qubit circuit. Flip qubit 1, then measure everything.
qc_demo = QuantumCircuit(2)
qc_demo.x(1)                 # flip qubit 1 only
qc_demo.measure_all()

# Run it and read the bitstring. Predict first: which character turns into a 1?
counts_demo = checkers.run_and_tally(qc_demo, shots=200)

# Qubit 1 is the LEFT character, so flipping it should give '10' every time.
checkers.check_counts_close(counts_demo, {"10": 1.0})"""))
cells.append(md(r"""See it? We touched qubit **1** and the **left** character became `1` → `'10'`. Now you predict the mirror image before you build it:"""))
cells.append(code(
"""# Quick check — flip qubit 0 instead. Which bitstring? (Predict, then build it below.)
quiz.ask("m2-endianness")"""))

# ----------------------------------------------------------------- task 2
cells.append(task(2, (
    "Build <code>qc_endian</code>: a <b>2-qubit</b> circuit that flips <b>only "
    "qubit 0</b> and then measures. The measurement is already wired for you — "
    "you just add the one flip. <br><i>Predict first:</i> qubit 0 is the "
    "<b>rightmost</b> character, so which bitstring should show up on every "
    "shot? Get it right and you've beaten the trap that catches almost every "
    "beginner."
)))
cells.append(code(
"""# A 2-qubit circuit. Flip ONLY qubit 0 — predict the bitstring before you run!
qc_endian = QuantumCircuit(2)
### BEGIN SOLUTION
qc_endian.x(0)
### END SOLUTION

# Nothing to change below — the measurement, then 512 shots checked against '01'.
qc_endian.measure_all()
counts = checkers.run_and_tally(qc_endian, shots=512)
checkers.check_counts_close(counts, {"01": 1.0})"""))
cells.append(analysis(r"""Flipping qubit **0** lit up the **right** character → `'01'`,
the mirror image of the worked example. That's the whole trap: **Qiskit reads
right-to-left.** Whenever a result looks backwards, you now know the culprit —
count the qubits from the right. Two habits save you every time: read bitstrings
right-to-left, and when in doubt, flip one known qubit (like we just did) to see
where it lands."""))

# ----------------------------------------------------------------- analogy
cells.append(analogy_callout(
    "quantum gates, circuit order, and reversibility",
    (
        "I'm learning quantum computing. Explain quantum gates and circuits "
        "using an analogy from MY background: [YOUR HOBBY/FIELD HERE].\n\n"
        "Ground rules — your analogy MUST respect these facts:\n"
        "1) A gate is a reversible move applied to a qubit's state; a circuit "
        "is a sequence of such moves read left to right.\n"
        "2) X is the bit-flip (|0⟩↔|1⟩). Z is the phase-flip: it multiplies "
        "|1⟩ by -1, changing the state but NOT the measurement probabilities.\n"
        "3) Gates generally do NOT commute — the order matters (H then Z differs "
        "from Z then H).\n"
        "4) Every gate is unitary, i.e. reversible: applying it has an undo, so "
        "no information is lost (H·H returns you to the start).\n\n"
        "End by telling me where the analogy breaks down."
    ),
))

# ----------------------------------------------------------------- claim code
cells.append(md(r"""## 🎓 Log your climb — claim your completion code

You stacked gates into circuits, discovered that **H·Z·H = X**, and stepped
around Qiskit's endianness trap. Let's bank it! Run the cell below: it re-checks
your **Task 1** (`qc_flip`) and **Task 2** (`qc_endian`) right here in this
kernel and — if they pass — prints a personal **completion code**.

Copy that code into the **“Log your notebook”** box on the
[Basecamp 2 page](https://quantum-ascent-77617.web.app/module.html?id=02#claim)
to light up this camp on your Ascent map and bank your climber XP. 🏔️"""))
cells.append(code("progress.claim_basecamp_2(qc_flip, qc_endian)"))

# ----------------------------------------------------------------- footer
cells.append(basecamp_footer(
    2,
    summary=(
        "You turned single gates into circuits: you met the bit-flip $X$ and "
        "the phase-flip $Z$, proved that order matters, saw that every gate is "
        "reversible, discovered the H·Z·H = X sandwich, and learned to read "
        "Qiskit's bitstrings right-to-left. You now speak the grammar of "
        "quantum circuits."
    ),
    quiz_url="https://quantum-ascent-77617.web.app/module.html?id=02#quiz",
    next_label="Basecamp 3: Entanglement — where two qubits share a single, spooky fate",
    solutions_relpath="solutions/02_gates_and_circuits_solutions.ipynb",
))

write_notebook(
    cells,
    REPO / "notebooks" / "solutions" / "02_gates_and_circuits_solutions.ipynb",
)
