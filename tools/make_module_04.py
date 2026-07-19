"""Author the Module 04 SOLUTIONS notebook (source of truth).

    python tools/make_module_04.py
    python tools/build_solutions.py 04     # then derive the student version

House pedagogy (see memory: narrative-first authoring style):
story & imagination first -> slow recap -> rename with the formal word ->
plain math -> widget play -> only then the formal tools. Every coding task is
preceded by a fully worked example of the exact same pattern (green check
included), and the task itself is a "change the moves" tweak.

Basecamp 4 makes the leap from "which outcome?" to "how much?": an observable is
a scoreboard, and its expectation value is the average score — the ENERGY. We
ground it in the +1/-1 scoreboard of Z, visualise the energy as a needle homing
onto an exact ink goal mark (the Born average, straight from Basecamp 1), then
build a two-term ZZ "agreement" cost Hamiltonian that ties directly back to the
Bell pairs of Basecamp 3 and forward to the cost function QAOA will minimise.
"""

from nb_common import (
    REPO, analysis, analogy_callout, basecamp_footer, bootstrap_cell,
    briefing, code, exercise, md, task, write_notebook,
)

cells = []

# ----------------------------------------------------------------- header
cells.append(briefing(
    4, "Hamiltonians & Energy",
    mission=(
        "Until now you've asked one question of a qubit: <b>which face — 0 or "
        "1?</b> This basecamp teaches a richer question: <b>how much?</b> We "
        "attach a <b>number</b> to each outcome — a score — and ask for the "
        "<b>average</b>. That average has a name physicists use constantly: the "
        "<b>expectation value</b>, and when the scoreboard is an <b>energy</b> "
        "scoreboard, it's literally the <b>energy of the state</b>.<br><br>"
        "You'll meet the <b>Z observable</b> (the simplest scoreboard: +1 for 0, "
        "−1 for 1), watch an energy needle settle onto an exact target, and build "
        "your first <b>cost Hamiltonian</b> out of Pauli terms.<br><br>"
        "<i>This is the hinge of the whole course. Everything at the summit — the "
        "variational principle, QAOA, solving a real optimization problem — is "
        "just <b>rolling a state downhill to the lowest energy</b>. First you have "
        "to learn how to read that energy. That's today.</i>"
    ),
    objectives=[
        "Read an **observable** as a scoreboard that assigns a number to each measurement outcome",
        "Compute an **expectation value** $\\langle Z\\rangle = P(0)\\cdot(+1) + P(1)\\cdot(-1)$ — the average score over many shots",
        "Use Qiskit's **SparsePauliOp** and **Statevector.expectation_value** to get a state's energy exactly",
        "Build a two-qubit **cost Hamiltonian** ($ZZ$, the 'agreement' energy) — the seed of every optimization problem ahead",
    ],
    minutes=50,
))
cells.append(bootstrap_cell())

# ----------------------------------------------------------------- 4.1
cells.append(md(r"""## 4.1 From "which face?" to "how much?"

Every measurement so far handed you a bare label: `0` or `1`. Useful, but limited. Let's make it richer by playing a tiny game.

**The game.** Every time you measure a qubit, you get paid:

- measure **0** → you score **+1**
- measure **1** → you score **−1**

Now a single measurement isn't just a face, it's a *payout*. And a whole run of measurements has an **average payout**. That average is the quantity this basecamp is about.

This particular scoreboard — "+1 for outcome 0, −1 for outcome 1" — is so fundamental it has a name you already know from Basecamp 2: the **$Z$ observable**. An **observable** is exactly that: *a rule that attaches a number to each outcome.* $Z$ is the simplest one.

> 🧭 **Mind the sign.** It's tempting to think "outcome 0 scores 0." It doesn't — $Z$ pays **+1** for outcome 0 and **−1** for outcome 1. The scoreboard doesn't care what the bits are *labelled*; it just looks up a payout. Keep that flip straight and the rest is easy."""))

cells.append(exercise(1, (
    "Open the <b>Energy Meter</b> below. The green/amber bar is the qubit's state "
    "in <i>exact</i> Born proportions (green = chance of 0, amber = chance of 1). "
    "The dial underneath runs from <b>−1 to +1</b>, and the black <b>⟨Z⟩ goal</b> "
    "mark sits at the exact average score. "
    "<br>1️⃣ Slide all the way to <b>green (|0⟩)</b>: every shot scores +1, so the "
    "energy pins at <b>+1</b>. Hit <b>Measure ×100</b> and watch the needle sit on "
    "the goal. "
    "<br>2️⃣ Slide to the <b>middle</b> (a fair coin): half +1, half −1 — the "
    "needle wanders but homes in on <b>0</b>. "
    "<br>3️⃣ Slide to <b>75% green</b>: predict the goal <i>before</i> you measure, "
    "then check. (Hint: it's between 0 and +1.)"
)))
cells.append(code('show_widget("energy-meter")'))

cells.append(md(r"""### Naming it: the expectation value

That "average score" is the **expectation value** of $Z$, written $\langle Z\rangle$. You compute it by weighting each score by how often it happens — the Born probabilities from Basecamp 1:

$$\langle Z\rangle = \underbrace{(+1)}_{\text{score for }0}\cdot P(0) \;+\; \underbrace{(-1)}_{\text{score for }1}\cdot P(1) \;=\; P(0) - P(1)$$

Let's sanity-check it against the widget:

- **$|0\rangle$**: $P(0)=1$, so $\langle Z\rangle = 1 - 0 = +1$. ✅ (all green → +1)
- **$|1\rangle$**: $P(0)=0$, so $\langle Z\rangle = 0 - 1 = -1$. ✅ (all amber → −1)
- **fair coin $|+\rangle$**: $P(0)=P(1)=\tfrac12$, so $\langle Z\rangle = \tfrac12 - \tfrac12 = 0$. ✅

Here's the subtle, beautiful part: **no single measurement ever returns $0$** — each slap is just +1 or −1. Yet the *average* of a fair coin is exactly $0$. The expectation value is a statement about the **long run**, not any one shot. That's the same predict-the-statistics idea you met with the biased coin — we're just reading energy now instead of counting heads.

> 💡 If this feels abstract, grab a pen: write out $\langle Z\rangle = P(0) - P(1)$ and plug in a few probabilities by hand. Three lines of arithmetic and it clicks."""))

cells.append(code(
"""# Quick check — the Z scoreboard: what score does Z give the outcome 0?
quiz.ask("m4-z-scoreboard")"""))
cells.append(code(
"""# Quick check — what is <Z> for a fair 50/50 qubit?
quiz.ask("m4-expectation-average")"""))

# ----------------------------------------------------------------- 4.2
cells.append(md(r"""## 4.2 Reading energy in Qiskit

You could always get $\langle Z\rangle$ by measuring thousands of shots and averaging the scores — that's exactly what the widget did. But Qiskit can also compute it **exactly** from the state vector, with no shot noise at all. Two objects do the work:

- **`SparsePauliOp`** — how we write an observable. `SparsePauliOp("Z")` *is* the Z scoreboard.
- **`Statevector(qc).expectation_value(op)`** — hands back $\langle op\rangle$ for the state your circuit prepares.

Run the setup (same lab as always, plus these two new tools):"""))
cells.append(code(
"""# Our tools, now with the two new energy-reading helpers.
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector"""))

cells.append(md(r"""### Syntax preview — the exact three lines you'll reuse

Here's the whole pattern on the fair coin $|+\rangle$. Read it once; you'll copy this shape in the task.

```python
qc = QuantumCircuit(1)
qc.h(0)                                   # prepare the state |+>
Z = SparsePauliOp("Z")                    # the observable (scoreboard)
energy = Statevector(qc).expectation_value(Z).real   # <Z>, exactly
```

Two things worth noticing: (1) **no measurement gate** — `expectation_value` reads the state directly, so we do *not* call `measure_all()` here. (2) We tack on `.real` because an expectation value of a real observable is a real number, but Qiskit returns it in complex form (`0.0 + 0.0j`); `.real` just drops the always-zero imaginary part."""))

cells.append(md(r"""### Worked example: the energy of $|0\rangle$ and $|+\rangle$

Let's confirm the two values you saw on the dial. Predict each before you run:"""))
cells.append(code(
"""# |0> should score +1 (all green); |+> should score 0 (fair coin).
Z = SparsePauliOp("Z")

qc0 = QuantumCircuit(1)                    # leave it in |0>
print("<Z> for |0> =", Statevector(qc0).expectation_value(Z).real)

qcplus = QuantumCircuit(1)
qcplus.h(0)                               # into |+>
print("<Z> for |+> =", Statevector(qcplus).expectation_value(Z).real)"""))
cells.append(md(r"""`+1.0` and `0.0`, exactly as the scoreboard math predicted. Notice how much sharper this is than sampling — no wobble, because we read the amplitudes directly instead of flipping the coin. Now your turn, on the state that isn't so obvious."""))

# ----------------------------------------------------------------- task 1
cells.append(task(1, (
    "Find the energy of the <b>75/25 biased coin</b> from Basecamp 1 — the state "
    "$RY(\\pi/3)\\,|0\\rangle$, which has $P(0)=\\tfrac34$ and $P(1)=\\tfrac14$. "
    "<br>1️⃣ Build <code>qc_z</code>: a 1-qubit circuit with "
    "<code>.ry(np.pi/3, 0)</code> — <i>no measurement</i>. "
    "<br>2️⃣ Compute its energy into <code>energy_z</code> using the three-line "
    "pattern above with the <code>Z</code> observable. "
    "<br><i>Predict first:</i> $\\langle Z\\rangle = \\tfrac34(+1) + \\tfrac14(-1) "
    "= ?$ — the checker knows the answer."
)))
cells.append(code(
"""# Build the 75/25 state and read its energy under Z.
qc_z = QuantumCircuit(1)
### BEGIN SOLUTION
qc_z.ry(np.pi / 3, 0)
energy_z = Statevector(qc_z).expectation_value(Z).real
### END SOLUTION
# energy_z = ...   # <- your <Z> goes here

# Nothing to change below — we compare your energy to the expected value.
checkers.check_expectation(energy_z, targets.M4_Z75)"""))
cells.append(analysis(r"""$\langle Z\rangle = +0.5$ — exactly $\tfrac34 - \tfrac14$. The
energy landed *between* the two extreme scores because the state is a weighted
blend of the +1 outcome and the −1 outcome. This is the key move of the whole
course in miniature: **a state's energy is just the average of the scoreboard,
weighted by the Born probabilities.** Every algorithm ahead is a search for the
state whose average comes out as low as possible."""))

# ----------------------------------------------------------------- 4.3
cells.append(md(r"""## 4.3 Cost Hamiltonians: scoring a whole configuration

One qubit, one scoreboard. Real problems have *many* qubits and a score that depends on how they relate. The object that holds the full scoreboard for a whole system is the **Hamiltonian** — a sum of Pauli terms, one per rule you want to encode. Its expectation value is the system's **energy**, and when the energy encodes the *cost* of a candidate solution we call it a **cost Hamiltonian**. Minimizing that energy = solving the problem. That's the entire summit in one sentence.

Let's build the simplest interesting one: **$ZZ$**, the two-qubit **agreement** scoreboard.

> 🎯 **The $ZZ$ rule:** score **+1** when the two qubits <b>agree</b> (00 or 11), and **−1** when they <b>disagree</b> (01 or 10).

(Why? $ZZ$ multiplies the two individual Z-scores: $(+1)(+1)=+1$ and $(-1)(-1)=+1$ for agreement; $(+1)(-1)=-1$ for disagreement.) So $\langle ZZ\rangle$ measures, on average, *how aligned the pair is* — and it reaches right back to the Bell pairs you built in Basecamp 3."""))

cells.append(md(r"""### Worked example: the energy of a Bell pair

Remember the Bell pair $\Phi^+ = (|00\rangle + |11\rangle)/\sqrt{2}$ from Basecamp 3? It only ever gives **00 or 11** — the qubits *always agree*. So under the agreement scoreboard its energy should be a perfect **+1**. Let's confirm it, building the observable the same way, just with a two-letter Pauli string:"""))
cells.append(code(
"""# The Bell pair Phi+ always agrees -> its ZZ 'agreement energy' should be +1.
ZZ = SparsePauliOp("ZZ")

qc_bell4 = QuantumCircuit(2)
qc_bell4.h(0)
qc_bell4.cx(0, 1)                          # the Bell recipe from Basecamp 3

print("<ZZ> for the Bell pair =", Statevector(qc_bell4).expectation_value(ZZ).real)"""))
cells.append(md(r"""`+1.0` — perfect agreement, exactly as promised. Each qubit *alone* is still a fair 50/50, but the **pair** is locked into matching, and the agreement scoreboard reads that as maximal energy."""))

cells.append(code(
"""# Quick check — what is <ZZ> for the Bell pair?
quiz.ask("m4-zz-agreement")"""))

# ----------------------------------------------------------------- task 2
cells.append(task(2, (
    "Now build the <b>opposite</b> pair and read its agreement energy. Recall the "
    "<b>anti-correlated</b> Bell pair $\\Psi^+$ from Basecamp 3: the Bell recipe "
    "plus one extra flip, so the qubits <i>always disagree</i>. "
    "<br>1️⃣ Build <code>qc_zz</code>: <code>.h(0)</code>, <code>.cx(0, 1)</code>, "
    "then <code>.x(1)</code> — <i>no measurement</i>. "
    "<br>2️⃣ Compute <code>energy_zz</code> = $\\langle ZZ\\rangle$ with the "
    "<code>ZZ</code> observable. "
    "<br><i>Predict first:</i> if they <b>always disagree</b>, every shot scores "
    "−1 — so the energy should be…?"
)))
cells.append(code(
"""# The anti-correlated pair: Bell recipe, then flip qubit 1 so they disagree.
qc_zz = QuantumCircuit(2)
### BEGIN SOLUTION
qc_zz.h(0)
qc_zz.cx(0, 1)
qc_zz.x(1)
energy_zz = Statevector(qc_zz).expectation_value(ZZ).real
### END SOLUTION
# energy_zz = ...   # <- your <ZZ> goes here

# Nothing to change below — we compare your energy to the expected value.
checkers.check_expectation(energy_zz, targets.M4_ZZ_ANTI)"""))
cells.append(analysis(r"""$\langle ZZ\rangle = -1$: perfect *disagreement*. By flipping a
single qubit you slid the pair from the highest agreement energy (+1) to the
lowest (−1), without touching the entanglement. Picture those two values, +1 and
−1, as the top and bottom of an energy landscape. Everything from here on is
about **finding the state that sits at the bottom** — and if your cost Hamiltonian
is built so the bottom encodes the answer to a real problem, then rolling downhill
*is* solving it. That's Max-Cut at the summit, and you now have the tool that
reads the height."""))

# ----------------------------------------------------------------- analogy
cells.append(analogy_callout(
    "observables, expectation values and cost Hamiltonians",
    (
        "I'm learning quantum computing. Explain what an OBSERVABLE, an "
        "EXPECTATION VALUE, and a COST HAMILTONIAN are, using an analogy from MY "
        "background: [YOUR HOBBY/FIELD HERE].\n\n"
        "Ground rules — your analogy MUST respect these facts:\n"
        "1) An observable is a rule that assigns a NUMBER (a score) to each "
        "possible measurement outcome. The Z observable scores outcome 0 as +1 "
        "and outcome 1 as -1.\n"
        "2) The expectation value <Z> is the AVERAGE score over many measurements, "
        "weighted by the Born probabilities: <Z> = (+1)*P(0) + (-1)*P(1). A single "
        "measurement is only ever +1 or -1; the average can be anything in "
        "between (e.g. 0 for a fair coin).\n"
        "3) A cost Hamiltonian is a sum of such scoreboards that assigns an ENERGY "
        "(a total cost) to each configuration of qubits. Solving an optimization "
        "problem means finding the configuration with the LOWEST energy.\n"
        "4) Do NOT say a qubit 'has' a definite value before measurement, and do "
        "NOT say it is '0 and 1 at the same time'. Talk in terms of probabilities "
        "and averages.\n\n"
        "End by telling me where the analogy breaks down."
    ),
))

# ----------------------------------------------------------------- claim code
cells.append(md(r"""## 🎓 Log your climb — claim your completion code

You learned to read a state's **energy**: you computed $\langle Z\rangle = +0.5$ for
the biased coin, and $\langle ZZ\rangle = -1$ for the anti-correlated pair. Let's
bank it! Run the cell below — it re-checks your **Task 1** (`qc_z`) and **Task 2**
(`qc_zz`) right here in this kernel and, if they pass, prints your personal
**completion code**.

Copy that code into the **“Log your notebook”** box on the
[Basecamp 4 page](https://quantum-ascent-77617.web.app/module.html?id=04#claim)
to light up this camp on your Ascent map and bank your climber XP. 🏔️"""))
cells.append(code("progress.claim_basecamp_4(qc_z, qc_zz)"))

# ----------------------------------------------------------------- footer
cells.append(basecamp_footer(
    4,
    summary=(
        "You made the leap from *which outcome* to *how much*. You read an "
        "**observable** as a scoreboard, computed **expectation values** "
        "$\\langle Z\\rangle$ and $\\langle ZZ\\rangle$ exactly with "
        "**SparsePauliOp** and **Statevector**, and built a two-qubit **cost "
        "Hamiltonian** whose energy runs from +1 (agree) to −1 (disagree). You can "
        "now measure the 'height' of any state — the last thing you need before "
        "learning to roll downhill."
    ),
    quiz_url="https://quantum-ascent-77617.web.app/module.html?id=04#quiz",
    next_label="Basecamp 5: The Variational Principle — tune a circuit's angles to descend the energy landscape to its lowest point",
    solutions_relpath="solutions/04_hamiltonians_and_expectation_solutions.ipynb",
))

write_notebook(
    cells,
    REPO / "notebooks" / "solutions" / "04_hamiltonians_and_expectation_solutions.ipynb",
)
