"""Author the Module 05 SOLUTIONS notebook (source of truth).

    python tools/make_module_05.py
    python tools/build_solutions.py 05     # then derive the student version

House pedagogy (see memory: narrative-first authoring style):
story & imagination first -> slow recap -> rename with the formal word ->
plain math -> widget play -> only then the formal tools. Every coding task is
preceded by a fully worked example of the exact same pattern (green check
included), and the task itself is a "change the moves" tweak.

Basecamp 5 turns the energy-reading of Basecamp 4 into a SEARCH. We give the
state a tunable knob (a parameterized RY circuit), read the energy at each
setting to trace an energy landscape, then hand the knob to a classical
optimizer that rolls the state downhill to the ground state. This is the
variational principle — the exact hybrid quantum/classical loop QAOA uses at the
summit. The cost Hamiltonian H = Z + 0.5 X is chosen so its ground state is a
tilted mix (not a basis state), so the search is genuine, not guessable.
"""

from nb_common import (
    REPO, analysis, analogy_callout, basecamp_footer, bootstrap_cell,
    briefing, code, exercise, md, task, write_notebook,
)

cells = []

# ----------------------------------------------------------------- header
cells.append(briefing(
    5, "The Variational Principle",
    mission=(
        "In Basecamp 4 you learned to <b>read</b> a state's energy. Now you'll "
        "learn to <b>lower</b> it — to <i>search</i> for the state that sits at "
        "the very bottom of the energy landscape, the <b>ground state</b>.<br><br>"
        "The trick is beautifully simple: give the state a <b>tuning knob</b> (a "
        "parameterized circuit), read the energy at your current setting, then "
        "nudge the knob to bring the energy down — again and again — until you "
        "hit the valley floor. A <b>classical optimizer</b> does the nudging; the "
        "quantum computer just reports the energy. That back-and-forth is the "
        "<b>variational principle</b>.<br><br>"
        "<i>This is the engine of nearly every near-term quantum algorithm, and "
        "it's the exact loop you'll aim at a real optimization problem at the "
        "summit. Today you build it end to end on one knob.</i>"
    ),
    objectives=[
        "Explain the **variational** idea: don't guess the ground state — build a tunable state and push its energy down",
        "Write a **parameterized ansatz** $RY(\\theta)\\ket{0}$ and a cost function $E(\\theta) = \\langle H\\rangle$",
        "Trace the **energy landscape** and see the ground state sitting at its lowest point",
        "Close the **hybrid loop**: let a classical optimizer tune $\\theta$ down to the ground energy $-\\sqrt{1.25}$",
    ],
    minutes=55,
))
cells.append(bootstrap_cell())

# ----------------------------------------------------------------- 5.1
cells.append(md(r"""## 5.1 Don't guess the state — search for it

You can now measure any state's energy $\langle H\rangle$. So here's the question that runs the rest of quantum computing:

> **Of all the states you could prepare, which one has the *lowest* energy?**

That lowest-energy state has a name — the **ground state** — and its energy is the smallest the Hamiltonian allows. For a *cost* Hamiltonian, where energy encodes the cost of a candidate answer, the ground state literally *is* the solution to your problem. Find the bottom of the valley and you've solved it.

But you can't check infinitely many states one by one. The **variational** idea sidesteps that:

1. Build a state with a **tuning knob** — a parameter $\theta$ you can turn. Call it $\ket{\psi(\theta)}$.
2. **Read its energy** $E(\theta) = \langle\psi(\theta)|H|\psi(\theta)\rangle$ at the current setting.
3. **Nudge $\theta$** in whatever direction lowers the energy.
4. Repeat until you can't go any lower — you've reached the ground state.

Picture a ball let loose on a hilly landscape: it rolls downhill and settles in the lowest valley. The knob $\theta$ is *where along the landscape* you stand; the energy is your *height*. We're going to roll to the bottom.

> 🧭 **This is a partnership.** The quantum computer is the *altimeter* — it tells you your energy at a given $\theta$. A plain **classical optimizer** is the *hiker* — it reads the altitude and decides where to step next. Neither does it alone."""))

cells.append(exercise(1, (
    "Open the <b>Energy Landscape</b> below. The curve is the energy of your "
    "qubit for every angle θ of the knob (cost Hamiltonian <b>H = Z + 0.5·X</b>). "
    "<br>1️⃣ <b>Drag the θ slider</b> and watch the ball ride up and down the "
    "landscape — the green/amber state bar changes with it, just like the Energy "
    "Meter. "
    "<br>2️⃣ <b>Predict</b> where the lowest point is, then park the ball there by "
    "hand. Hard to hit exactly, isn't it? "
    "<br>3️⃣ Now hit <b>Let the optimizer descend</b> and watch a classical "
    "optimizer roll the ball to the <b>ground energy</b> (the ink goal line). "
    "That descent is what you'll code in this basecamp."
)))
cells.append(code('show_widget("qaoa-landscape")'))

cells.append(code(
"""# Quick check — what is the variational strategy for finding the lowest-energy state?
quiz.ask("m5-why-parameter")"""))

# ----------------------------------------------------------------- 5.2
cells.append(md(r"""## 5.2 A one-knob landscape in Qiskit

Let's build that landscape for real. Two ingredients:

**The ansatz (the tunable state).** We reuse the rotation from Basecamp 1: $RY(\theta)\ket{0}$. As $\theta$ turns from $0$ to $2\pi$, this sweeps the qubit through every state on a great circle — plenty of room to search.

**The cost Hamiltonian.** We'll use $H = Z + 0.5\,X$. The $Z$ term is the agreement scoreboard you know; the $X$ term *tilts* the landscape so the lowest-energy state is a **mix**, not a plain $\ket{0}$ or $\ket{1}$. That tilt is what makes this a real search instead of an obvious guess.

Put them together and the energy is a function of the knob:

$$E(\theta) = \langle\psi(\theta)|H|\psi(\theta)\rangle = \cos\theta + 0.5\sin\theta$$

Run the setup (same tools as Basecamp 4):"""))
cells.append(code(
"""# Same energy-reading tools as Basecamp 4.
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector

# The cost Hamiltonian H = Z + 0.5 X, written as a sum of Pauli terms.
H = SparsePauliOp.from_list([("Z", 1.0), ("X", 0.5)])"""))

cells.append(md(r"""### Syntax preview — a cost function you can call

We want a function that takes an angle and returns that state's energy. It's the exact Basecamp 4 pattern (build → observe), just wrapped so we can call it over and over:

```python
def energy(theta):
    qc = QuantumCircuit(1)
    qc.ry(theta, 0)                                    # the ansatz RY(theta)|0>
    return Statevector(qc).expectation_value(H).real   # its energy <H>
```

As before: **no measurement gate** (we read the state directly), and `.real` drops the always-zero imaginary part."""))

cells.append(md(r"""### Worked example: read the energy at three angles

Before writing the reusable function, let's confirm the landscape formula by hand at three angles. Predict each from $E(\theta)=\cos\theta+0.5\sin\theta$, then run:"""))
cells.append(code(
"""# E(0) = cos0 + 0.5 sin0 = +1 ; E(pi/2) = 0 + 0.5 = +0.5 ; E(pi) = -1 + 0 = -1
for theta in [0.0, np.pi / 2, np.pi]:
    qc = QuantumCircuit(1)
    qc.ry(theta, 0)
    e = Statevector(qc).expectation_value(H).real
    print(f"theta = {theta:.3f} rad   E = {e:+.3f}")"""))
cells.append(md(r"""`+1.000`, `+0.500`, `-1.000` — the landscape formula checks out. Starting at $\theta=0$ (the state $\ket{0}$) puts you high on the hillside at $+1$; by $\theta=\pi$ you've dropped to $-1$. But is $\pi$ really the bottom? The $X$ tilt says no — let's find out. First, wrap the pattern into a function."""))

# ----------------------------------------------------------------- task 1
cells.append(task(1, (
    "Complete the cost function <code>energy(theta)</code> so it returns the "
    "energy $\\langle H\\rangle$ of the ansatz $RY(\\theta)\\ket{0}$. Follow the "
    "syntax preview exactly: build a 1-qubit circuit, apply "
    "<code>.ry(theta, 0)</code> (<i>no measurement</i>), and return "
    "<code>Statevector(qc).expectation_value(H).real</code>. "
    "<br>The checker calls your function at $\\theta=\\pi/2$, where the energy "
    "should be $+0.5$."
)))
cells.append(code(
'''def energy(theta):
    """Energy <H> of the state RY(theta)|0>, for H = Z + 0.5 X."""
    qc = QuantumCircuit(1)
### BEGIN SOLUTION
    qc.ry(theta, 0)
    return Statevector(qc).expectation_value(H).real
### END SOLUTION

# Nothing to change below — we probe your cost function at theta = pi/2.
checkers.check_expectation(energy(np.pi / 2), targets.M5_E_HALF)'''))
cells.append(analysis(r"""Your `energy(theta)` is the whole quantum half of the
variational loop in three lines: hand it an angle, it prepares that state and
reports its height on the landscape. Everything else — the search — is ordinary
classical code calling this function. That clean split (quantum evaluates, classical
decides) is exactly how real variational algorithms are built."""))

cells.append(md(r"""### See the whole valley

Now that you have `energy(theta)`, sweep the knob all the way around and print the landscape. Watch for where it bottoms out — and notice it is **not** at $\theta=\pi$:"""))
cells.append(code(
"""# Trace the energy landscape in 30-degree steps and mark the lowest so far.
best_e, best_deg = 999, 0
for deg in range(0, 361, 30):
    e = energy(np.deg2rad(deg))
    bar = "#" * int((e + 1.25) / 2.5 * 30)          # a crude text picture of the curve
    print(f"{deg:3d} deg | E = {e:+.3f} | {bar}")
    if e < best_e:
        best_e, best_deg = e, deg
print(f"\\nLowest sampled: E = {best_e:+.3f} near theta = {best_deg} deg "
      f"(the true minimum is between these coarse samples).")"""))
cells.append(md(r"""The valley floor sits somewhere around $200^\circ$–$210^\circ$, **past** $\pi$ ($180^\circ$) — pushed there by the $X$ tilt. Sampling every $30^\circ$ only gets us close; to land *exactly* on the bottom we need something smarter than a coarse sweep. Enter the optimizer."""))

cells.append(code(
"""# Quick check — in the variational loop, who picks the next angle to try?
quiz.ask("m5-who-does-what")"""))

# ----------------------------------------------------------------- 5.3
cells.append(md(r"""## 5.3 Let the computer descend

Instead of eyeballing the table, we hand the knob to a **classical optimizer** — a standard routine that, given a function to minimize, cleverly chooses which inputs to try next so it walks *downhill* with far fewer evaluations than a brute-force sweep. We'll use `COBYLA` from SciPy, a solid, gradient-free choice for these small problems.

The optimizer needs two things: a **function to minimize** (our `energy`) and a **starting point** $\theta_0$. It calls the function, reads the energy, picks a new $\theta$, and repeats until it can't lower the energy any further — the ground state.

> 🧭 **Ignore-the-plumbing note.** We wrap `energy` in a tiny `objective` that also *records* every value it sees into a `history` list. That's just so we can watch the descent and check the final answer — the optimizer itself only cares about the returned number."""))

cells.append(md(r"""### Syntax preview — the optimizer call

```python
from scipy.optimize import minimize

history = []
def objective(params):
    e = energy(params[0])     # params is a list of knobs; we have one
    history.append(e)         # record it so we can see the descent
    return e

result = minimize(objective, x0=[0.6], method="COBYLA")
theta_star = result.x[0]      # the winning angle
```

`minimize` hands your `objective` a *list* of parameters (here just one, `params[0]`), and returns a `result` whose `.x` holds the best angles it found and `.fun` the lowest energy."""))

# ----------------------------------------------------------------- task 2
cells.append(task(2, (
    "Close the loop: call the optimizer to find the ground state. The "
    "<code>objective</code> wrapper (which records the <code>history</code>) is "
    "written for you — you just add the one line that runs the search. "
    "<br>Call <code>minimize(objective, x0=[0.6], method=\"COBYLA\")</code> and "
    "store it in <code>result</code>. "
    "<br><i>Predict first:</i> the coarse sweep bottomed out near $-1.1$ — the "
    "optimizer should settle onto the exact ground energy $-\\sqrt{1.25}\\approx "
    "-1.118$."
)))
cells.append(code(
'''from scipy.optimize import minimize

history = []
def objective(params):
    e = energy(params[0])      # evaluate the energy at the optimizer's current angle
    history.append(e)          # (plumbing) record it so we can watch the descent
    return e

### BEGIN SOLUTION
result = minimize(objective, x0=[0.6], method="COBYLA")
### END SOLUTION
# result = ...   # <- call minimize(...) here

theta_star = result.x[0]
print(f"Optimizer finished in {len(history)} energy evaluations.")
print(f"Ground energy found: {result.fun:+.4f}  at theta* = {theta_star:.4f} rad "
      f"({np.rad2deg(theta_star):.1f} deg)")

# Nothing to change below — did the descent reach the true ground energy?
checkers.check_optimum(history, targets.M5_GROUND)'''))
cells.append(analysis(r"""The optimizer rolled downhill to $E \approx -1.118$ — the exact
ground energy $-\sqrt{1.25}$ — landing near $\theta^\star \approx 206^\circ$, well
past $\pi$, precisely where the $X$ tilt hid the valley floor. Notice it needed only
a couple of dozen energy evaluations, not a fine sweep of the whole circle. You just
ran a complete **variational algorithm**: a parameterized quantum state, a cost
function, and a classical optimizer closing the loop. This is the template for VQE,
QAOA, and most near-term quantum computing — and at the summit you'll point this exact
machinery at a real optimization problem."""))

cells.append(code(
"""# Quick check — the optimizer stalls at E = -1.118. What have you found?
quiz.ask("m5-ground-state")"""))

# ----------------------------------------------------------------- analogy
cells.append(analogy_callout(
    "the variational principle (parameterized states + a classical optimizer)",
    (
        "I'm learning quantum computing. Explain the VARIATIONAL PRINCIPLE using "
        "an analogy from MY background: [YOUR HOBBY/FIELD HERE].\n\n"
        "Ground rules — your analogy MUST respect these facts:\n"
        "1) We build a quantum state that depends on tunable knobs (parameters), "
        "called a parameterized circuit or ansatz.\n"
        "2) A cost Hamiltonian assigns an ENERGY to each state; the goal is to "
        "find the state with the LOWEST energy (the ground state).\n"
        "3) It is a HYBRID loop: the quantum computer only EVALUATES the energy at "
        "the current knob settings; a CLASSICAL optimizer reads that energy and "
        "decides how to adjust the knobs to lower it. Repeat until you reach the "
        "bottom.\n"
        "4) Do NOT claim the quantum computer 'tries all states at once' or "
        "'instantly finds the minimum'. It is an iterative downhill search, one "
        "energy evaluation at a time.\n\n"
        "End by telling me where the analogy breaks down."
    ),
))

# ----------------------------------------------------------------- claim code
cells.append(md(r"""## 🎓 Log your climb — claim your completion code

You built a full variational loop: a tunable state, a cost function `energy(theta)`,
and a classical optimizer that descended to the ground energy $-\sqrt{1.25}$. Let's
bank it! Run the cell below — it re-checks your **Task 1** (`energy`) and **Task 2**
(`theta_star`) right here in this kernel and, if they pass, prints your personal
**completion code**.

Copy that code into the **“Log your notebook”** box on the
[Basecamp 5 page](https://quantum-ascent-77617.web.app/module.html?id=05#claim)
to light up this camp on your Ascent map and claim the **🏅 Ground State** badge. 🏔️"""))
cells.append(code("progress.claim_basecamp_5(energy, theta_star)"))

# ----------------------------------------------------------------- footer
cells.append(basecamp_footer(
    5,
    summary=(
        "You turned energy-*reading* into energy-*minimizing*. You wrote a "
        "parameterized ansatz $RY(\\theta)\\ket{0}$, built a cost function "
        "$E(\\theta)=\\langle H\\rangle$, traced the landscape, and closed the "
        "hybrid loop — a classical optimizer descended to the ground energy "
        "$-\\sqrt{1.25}$ that no single angle could beat. That's the variational "
        "principle, the beating heart of near-term quantum algorithms, running "
        "end to end in your own notebook."
    ),
    quiz_url="https://quantum-ascent-77617.web.app/module.html?id=05#quiz",
    next_label=("Basecamp 6 — the Summit: QAOA for Max-Cut. Point this exact "
                "variational machinery at a real graph problem and solve it end to end"),
    solutions_relpath="solutions/05_variational_principle_solutions.ipynb",
))

write_notebook(
    cells,
    REPO / "notebooks" / "solutions" / "05_variational_principle_solutions.ipynb",
)
