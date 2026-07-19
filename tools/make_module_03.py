"""Author the Module 03 SOLUTIONS notebook (source of truth).

    python tools/make_module_03.py
    python tools/build_solutions.py 03     # then derive the student version

House pedagogy (see memory: narrative-first authoring style):
story & imagination first -> slow recap -> rename with the formal word ->
plain math -> widget play -> only then the formal tools. Every coding task is
preceded by a fully worked example of the exact same pattern (green check
included), and the task itself is a "change the moves" tweak. Myth-busting is
explicit: we kill "spooky faster-than-light signalling" the moment it could form.
"""

from nb_common import (
    REPO, analysis, analogy_callout, basecamp_footer, bootstrap_cell,
    briefing, code, exercise, md, task, write_notebook,
)

cells = []

# ----------------------------------------------------------------- header
cells.append(briefing(
    3, "Entanglement",
    mission=(
        "So far every qubit has lived its own life. Now you'll <b>link two of "
        "them</b> so tightly that they stop being two separate coins and become "
        "one shared object — measure one and you instantly know the other. This "
        "is <b>entanglement</b>, the single most famous idea in quantum "
        "computing, and the engine behind almost everything ahead.<br><br>"
        "You'll meet the <b>CNOT</b> gate (the move that does the linking), build "
        "your first <b>Bell pair</b>, and see correlations no pair of ordinary "
        "coins could ever produce.<br><br>"
        "<i>We'll also carefully dismantle the biggest myth here — no, "
        "entanglement does <b>not</b> let you send messages faster than light. "
        "You'll see exactly why, with your own hands.</i>"
    ),
    objectives=[
        "Describe why two qubits need **four** amplitudes ($\\ket{00}, \\ket{01}, \\ket{10}, \\ket{11}$) — the state space grows as $2^n$",
        "Use the **CNOT** gate to link qubits, and build the **Bell pair** $(\\ket{00}+\\ket{11})/\\sqrt{2}$",
        "Explain **entanglement** as a state that *cannot* be split into 'qubit A does this, qubit B does that'",
        "Bust the myth: measuring one entangled qubit reveals — but does **not signal** — its partner (no faster-than-light messaging)",
    ],
    minutes=55,
))
cells.append(bootstrap_cell())

# ----------------------------------------------------------------- 3.1
cells.append(md(r"""## 3.1 Two qubits: the world gets bigger

Everything so far lived on a *single* qubit — one arrow, two amplitudes, one probability split. The moment we add a **second** qubit, something important happens to the bookkeeping.

One qubit had two possible outcomes: $0$ or $1$. **Two** qubits have **four**: $00, 01, 10, 11$. So a two-qubit state needs **four amplitudes**, one for each of those outcomes:

$$\ket{\psi} = a\,\ket{00} + b\,\ket{01} + c\,\ket{10} + d\,\ket{11}$$

(As always, the probabilities are the squares — $|a|^2 + |b|^2 + |c|^2 + |d|^2 = 1$.)

That's the pattern: **$n$ qubits need $2^n$ amplitudes.** Ten qubits already need 1024 numbers; three hundred qubits need more numbers than there are atoms in the visible universe. *That* explosion is where quantum computers get their room to work — and it starts right here, with going from 2 numbers to 4.

> 🧭 **Don't panic about the four terms.** You won't be juggling them by hand. We'll *watch* them in the Explorer first, then let Qiskit track them for us. The point of this section is just one idea: **two qubits share one bigger state.**"""))

cells.append(exercise(1, (
    "Open the <b>Entanglement Explorer</b> below. It shows two qubits — "
    "<b>Qubit A</b> and <b>Qubit B</b> — and lets you measure them together. "
    "<br>1️⃣ Leave the link on <b>Independent</b> and hit <b>Measure ×100</b>. "
    "All four pairs (00, 01, 10, 11) show up, each about 25%. This is two "
    "ordinary, unconnected coins. "
    "<br>2️⃣ Watch the little <b>ink goal marks</b> on each bar — that's the "
    "exact probability the bar climbs toward (the Born rule from Basecamp 1, now "
    "for a pair). "
    "<br>3️⃣ Keep this open; in a moment we'll change the link and something "
    "strange will happen."
)))
cells.append(code('show_widget("entanglement-explorer")'))

cells.append(md(r"""### When two qubits are really just two separate stories

The Independent link you just played with has a special property: it **factors**. "Qubit A is a fair coin" *and*, separately, "Qubit B is a fair coin." You can tell each qubit's story on its own, and stapling them together describes the whole. A state like that is called a **product state** — it's genuinely two objects that happen to sit next to each other.

Most two-qubit states are like this. But not all of them. Let's go find one that *isn't*."""))

cells.append(exercise(2, (
    "Back in the Explorer, switch the link to <b>Correlated (a Bell pair)</b> and "
    "hit <b>Measure ×100</b>. <br>1️⃣ Two of the bars — <b>01</b> and <b>10</b> — "
    "stay flat at zero. Only <b>00</b> and <b>11</b> ever appear. "
    "<br>2️⃣ Look at the <b>“How often the two coins agreed”</b> readout: 100%. "
    "The coins <i>always</i> land on the same face. "
    "<br>3️⃣ Yet each coin <i>alone</i> is still a fair 50/50 — cover one and the "
    "other is pure chance. It's the <b>link</b> that's certain, not either coin. "
    "Sit with how odd that is, then answer the quick check."
)))
cells.append(code(
"""# Quick check — with the Correlated (Bell) link, which outcomes appear?
quiz.ask("m3-bell-outcomes")"""))

cells.append(md(r"""### Naming it: entanglement

That correlated state is famous enough to have a name — the **Bell state** $\Phi^+$:

$$\ket{\Phi^+} = \frac{\ket{00} + \ket{11}}{\sqrt{2}}$$

Read it out loud: "an equal mix of *both zero* and *both one* — and nothing else." There's no $\ket{01}$ term and no $\ket{10}$ term, so a mismatch is simply impossible.

Here's the crucial part. Try to split $\ket{\Phi^+}$ into "Qubit A is doing ___ *and* Qubit B is doing ___." **You can't.** No description of A by itself, combined with any description of B by itself, ever reproduces this state. The only honest description is of the **pair, as one object**.

That un-splittability *is* the definition:

> 🔗 **Entanglement:** a state of two (or more) qubits that **cannot** be written as one qubit's state *and* another's. The qubits no longer have separate identities — only the whole does.

A product state = two stories. An entangled state = **one story you can't tear in half.**"""))

# ----------------------------------------------------------------- 3.2
cells.append(md(r"""## 3.2 Building a Bell pair in Qiskit

How do you actually *link* two qubits? With one new gate: the **CNOT** (controlled-NOT), written `cx` in Qiskit.

CNOT is a two-qubit move with a **control** and a **target**:

> 🎯 **CNOT rule:** look at the control qubit. If it's $\ket{1}$, flip the target. If it's $\ket{0}$, do nothing.

On its own that's just a conditional bit-flip — very classical. The magic appears when the control is in *superposition*: then "flip / don't flip" happens for both possibilities at once, and the two qubits get braided together.

Same lab as before — `QuantumCircuit`, `AerSimulator`, and NumPy. Run the setup:"""))
cells.append(code(
"""# Our familiar tools.
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator"""))

cells.append(md(r"""### Worked example: CNOT as a plain conditional flip

Let's watch the CNOT rule with **no** superposition first, so it's totally concrete. We'll force the control (qubit 0) to $\ket{1}$ with an $X$, then apply `cx(0, 1)` — control 0, target 1. Since the control is 1, the target should flip. Predict the bitstring before you run (remember Basecamp 2: **qubit 0 is the rightmost character**):"""))
cells.append(code(
"""# Control = qubit 0, target = qubit 1. Force the control to 1, then CNOT.
qc_cnot = QuantumCircuit(2)
qc_cnot.x(0)          # control becomes |1>
qc_cnot.cx(0, 1)      # control is 1 -> flip the target (qubit 1)
qc_cnot.measure_all()

# Both qubits should now read 1 -> '11' every shot.
counts_cnot = checkers.run_and_tally(qc_cnot, shots=200)
checkers.check_counts_close(counts_cnot, {"11": 1.0})"""))
cells.append(md(r"""Control was $1$, so the target flipped — both qubits ended up $1$, giving `'11'`. A CNOT with a *definite* control is nothing exotic. Now let's make the control a **spin** instead."""))

cells.append(md(r"""### The recipe for entanglement

Put the control qubit into a fair superposition with $H$ **first**, *then* CNOT:

$$\ket{0}\ket{0} \;\xrightarrow{\;H\text{ on qubit }0\;}\; \frac{\ket{0}+\ket{1}}{\sqrt{2}}\ket{0} \;\xrightarrow{\;\text{CNOT}\;}\; \frac{\ket{00}+\ket{11}}{\sqrt{2}}$$

Watch what CNOT does to the two pieces of the superposition: the $\ket{0}$-control part leaves the target alone (stays $\ket{00}$), while the $\ket{1}$-control part flips the target (becomes $\ket{11}$). The "flip / don't flip" got tied to the control's coin-flip — and that knot is the entanglement. Two gates, $H$ then CNOT, is the entire Bell-pair recipe. Your turn to build it."""))

# ----------------------------------------------------------------- task 1
cells.append(task(1, (
    "Build the Bell pair <code>qc_bell</code>. Starting from a fresh 2-qubit "
    "circuit, apply <b>H to qubit 0</b>, then <b>CNOT with control 0, target "
    "1</b> (<code>.cx(0, 1)</code>). <br><i>Don't measure it</i> — this time we "
    "check the actual <b>state vector</b> to confirm it's exactly "
    "$(\\ket{00}+\\ket{11})/\\sqrt{2}$: two amplitudes of $1/\\sqrt{2}$ on "
    "$\\ket{00}$ and $\\ket{11}$, and zero on the mismatched outcomes."
)))
cells.append(code(
"""# Build the Bell pair: H on qubit 0, then CNOT (control 0 -> target 1).
qc_bell = QuantumCircuit(2)
### BEGIN SOLUTION
qc_bell.h(0)
qc_bell.cx(0, 1)
### END SOLUTION

# Nothing to change below — we compare your state to the Phi+ Bell target.
checkers.check_statevector(qc_bell, targets.M3_BELL)"""))
cells.append(analysis(r"""You just built genuine entanglement in two lines. The state
$(\ket{00}+\ket{11})/\sqrt{2}$ has equal amplitude on "both 0" and "both 1", and
**exactly zero** on the mismatched $\ket{01}$ and $\ket{10}$ — which is why the
Explorer's 01 and 10 bars stayed flat. Notice the checker forgives global phase
but nothing else: your two amplitudes have to be the same, and the cross terms
have to vanish. If they do, the qubits are locked together."""))
cells.append(code(
"""# Quick check — you measure qubit A of a Bell pair and get 0. What is qubit B?
quiz.ask("m3-measure-partner")"""))

# ----------------------------------------------------------------- 3.3
cells.append(md(r"""## 3.3 Correlation, the other Bell pair, and a myth to bury

The Bell pair $\Phi^+$ makes the qubits **agree**. With a tiny tweak we can make them do the opposite — **always disagree**. Take the Bell recipe and flip one qubit at the end with an $X$: now the only outcomes are $\ket{01}$ and $\ket{10}$. Same entanglement, mirror-image correlation (this is the Explorer's **Anti-correlated** link, the Bell state $\Psi^+$).

Before you build it, let's name the elephant in the room."""))

cells.append(md(r"""> 🚫 **Myth:** "Entangled qubits communicate instantly, so you can send messages faster than light."
>
> ✅ **Reality:** You cannot. Look *only* at Qubit A across many Bell pairs and you see a boring, perfectly random 50/50 stream of 0s and 1s — measuring B does nothing you could ever detect on A. The correlation is real, but it only *appears* when someone later lays the two lists of results **side by side and compares them**. Comparing lists needs an ordinary (slower-than-light) message. So entanglement gives you shared randomness that's *linked*, never a telephone. No signal travels; nothing arrives sooner than light."""))
cells.append(md(r"""Why does the "spooky action" story feel so tempting, then? Because measuring A really does pin down B's value. But "learning something about B" isn't "sending something to B." Opening one of two envelopes that were sealed together tells you what's in the other instantly, too — no magic, and definitely no message. Entanglement is stranger than sealed envelopes (the correlations can beat *any* pre-arranged classical scheme — that's the deep part, for a later climb), yet it still refuses to carry a signal."""))
cells.append(code(
"""# Quick check — which state is genuinely entangled (can't be split in two)?
quiz.ask("m3-entangled-or-not")"""))

# ----------------------------------------------------------------- task 2
cells.append(task(2, (
    "Build <code>qc_anti</code>, the <b>anti-correlated</b> pair. Start exactly "
    "like the Bell pair — <b>H on qubit 0</b>, then <b>CNOT (0 → 1)</b> — then add "
    "<b>one</b> more move: an <b>X on qubit 1</b> to flip it. The measurement is "
    "already wired for you. <br><i>Predict first:</i> flipping one half of a "
    "'they always agree' pair should make them 'always disagree' — so only "
    "<b>'01'</b> and <b>'10'</b> should ever appear, about half each."
)))
cells.append(code(
"""# The anti-correlated pair: Bell recipe, then flip qubit 1 so they disagree.
qc_anti = QuantumCircuit(2)
### BEGIN SOLUTION
qc_anti.h(0)
qc_anti.cx(0, 1)
qc_anti.x(1)
### END SOLUTION

# Nothing to change below — measure, then check the outcomes are 01 / 10 only.
qc_anti.measure_all()
counts_anti = checkers.run_and_tally(qc_anti, shots=512)
checkers.check_counts_close(counts_anti, {"01": 0.5, "10": 0.5})"""))
cells.append(analysis(r"""Perfect anti-correlation: only `'01'` and `'10'`, so the two
qubits land on opposite faces every single time — yet each one alone is still a
fair 50/50. By flipping just one qubit you turned "always agree" into "always
disagree" without breaking the entanglement. $\Phi^+$ and $\Psi^+$ are two of the
four **Bell states**, the fundamental alphabet of two-qubit entanglement — and
they're the raw material for teleportation, superdense coding, and error
correction further up the mountain."""))

# ----------------------------------------------------------------- analogy
cells.append(analogy_callout(
    "entanglement and Bell pairs (without the faster-than-light myth)",
    (
        "I'm learning quantum computing. Explain quantum entanglement using an "
        "analogy from MY background: [YOUR HOBBY/FIELD HERE].\n\n"
        "Ground rules — your analogy MUST respect these facts:\n"
        "1) Two entangled qubits share ONE joint state that cannot be described "
        "as 'qubit A does X and qubit B does Y' separately.\n"
        "2) The Bell pair (|00>+|11>)/sqrt(2) always gives matching results (00 "
        "or 11), each 50%; each qubit measured alone is a fair 50/50.\n"
        "3) Measuring one qubit reveals its partner's value but does NOT send any "
        "signal — you can't communicate faster than light. The correlation is "
        "only visible when the two result lists are later compared.\n"
        "4) Do NOT say the qubits 'communicate' or 'influence each other faster "
        "than light'. Avoid 'spooky action' as a literal mechanism.\n\n"
        "End by telling me where the analogy breaks down."
    ),
))

# ----------------------------------------------------------------- claim code
cells.append(md(r"""## 🎓 Log your climb — claim your completion code

You built real entanglement: a Bell pair whose qubits always agree, and its
anti-correlated twin whose qubits always disagree. Let's bank it! Run the cell
below — it re-checks your **Task 1** (`qc_bell`) and **Task 2** (`qc_anti`) right
here in this kernel and, if they pass, prints your personal **completion code**.

Copy that code into the **“Log your notebook”** box on the
[Basecamp 3 page](https://quantum-ascent-77617.web.app/module.html?id=03#claim)
to light up this camp on your Ascent map and claim the **🏅 Entangled** badge. 🏔️"""))
cells.append(code("progress.claim_basecamp_3(qc_bell, qc_anti)"))

# ----------------------------------------------------------------- footer
cells.append(basecamp_footer(
    3,
    summary=(
        "You linked two qubits into one shared state. You met the **CNOT** gate, "
        "built the Bell pair $(\\ket{00}+\\ket{11})/\\sqrt{2}$, saw that "
        "entanglement is a state you *cannot* split in two, made an "
        "anti-correlated pair with a single extra flip, and buried the "
        "faster-than-light myth for good. This is the beating heart of quantum "
        "computing — and you just built it yourself."
    ),
    quiz_url="https://quantum-ascent-77617.web.app/module.html?id=03#quiz",
    next_label="Basecamp 4: Hamiltonians & Energy — how a quantum computer measures the 'cost' of a state",
    solutions_relpath="solutions/03_entanglement_and_multiqubit_solutions.ipynb",
))

write_notebook(
    cells,
    REPO / "notebooks" / "solutions" / "03_entanglement_and_multiqubit_solutions.ipynb",
)
