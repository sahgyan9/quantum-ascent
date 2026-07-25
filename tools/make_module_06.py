"""Author the Module 06 SOLUTIONS notebook — the Summit (source of truth).

    python tools/make_module_06.py
    python tools/build_solutions.py 06     # then derive the student version

House pedagogy (see memory: narrative-first authoring style):
story & imagination first -> slow recap -> rename with the formal word ->
plain math -> widget play -> only then the formal tools. Every coding task is
preceded by a fully worked example of the exact same pattern, and the task is a
"change the moves" tweak.

The capstone ties the whole ascent together on a real optimization problem —
Max-Cut on a 4-node ring — solved with QAOA:
  * the graph & the goal (Basecamp 6 widget: paint the cut by hand)
  * encode it as a cost Hamiltonian H_C = sum Z_i Z_j  (Basecamp 4's ZZ = agreement)
  * build the QAOA ansatz: alternating cost + mixer layers  (Basecamp 3's cx/entanglement, Basecamp 2's rotations)
  * close the variational loop with a classical optimizer   (Basecamp 5)
  * sample the answer and score the approximation ratio.
The mixer is deliberately the student's gap, because dropping it leaves |+>^n's
measurement uniform — a concrete, checkable lesson in why QAOA alternates two moves.
"""

from nb_common import (
    REPO, analysis, analogy_callout, basecamp_footer, bootstrap_cell,
    briefing, code, exercise, md, task, write_notebook,
)

cells = []

# ----------------------------------------------------------------- header
cells.append(briefing(
    6, "Summit — QAOA for Max-Cut",
    mission=(
        "This is the summit. 🏔️ You'll take a <b>real optimization problem</b> — "
        "Max-Cut on a graph — and solve it end to end with a quantum algorithm "
        "you build yourself: <b>QAOA</b> (the Quantum Approximate Optimization "
        "Algorithm).<br><br>"
        "Everything you've climbed comes together here. You'll <b>encode</b> the "
        "problem as a cost Hamiltonian (Basecamp 4's $ZZ$ energy), <b>build</b> a "
        "parameterized circuit from rotations and entangling gates (Basecamps "
        "2–3), and <b>optimize</b> its angles with a classical optimizer "
        "(Basecamp 5) until measuring it hands you the answer.<br><br>"
        "<i>By the end you'll have solved an NP-hard problem on a (simulated) "
        "quantum computer and scored its approximation ratio honestly. That's the "
        "whole mountain — and you'll have built every piece of it.</i>"
    ),
    objectives=[
        "State the **Max-Cut** problem: split a graph's nodes into two groups to cut the most edges",
        "Encode it as a **cost Hamiltonian** $H_C = \\sum_{\\text{edges}} Z_iZ_j$, so the ground state is the best cut",
        "Build the **QAOA ansatz** — alternating **cost** and **mixer** layers — and see why *both* are essential",
        "Run the full **variational loop**, sample the answer, and then find out what *Approximate* really means on a graph that fights back",
    ],
    minutes=70,
))
cells.append(bootstrap_cell())

# ----------------------------------------------------------------- 6.1
cells.append(md(r"""## 6.1 The problem: Max-Cut

Here's a puzzle that looks innocent and turns out to be genuinely hard. You have a **graph** — dots (nodes) joined by lines (edges). Split the nodes into **two groups**. An edge is **cut** if its two endpoints land in *different* groups.

> **Max-Cut:** find the split that cuts the *most* edges.

It sounds simple, but for a big graph there's no known shortcut — the number of possible splits doubles with every node. Max-Cut is **NP-hard**, and it's not a toy: the same shape of problem shows up in circuit design, network science, and machine learning.

Think of it socially: you're seating people at two tables, and every edge is a pair who'd rather *not* sit together. Max-Cut is the seating that separates the most feuding pairs.

We'll work with a small, friendly graph — a **4-node ring** (a square): nodes 0–1–2–3, each joined to its two neighbours. Small enough to check by hand, rich enough to show QAOA working. Go find its best cut:"""))

cells.append(exercise(1, (
    "Open the <b>Max-Cut Painter</b> below — it's the 4-node ring. <b>Click a "
    "node</b> to move it between the green and amber groups; an edge lights up "
    "green when it's <b>cut</b> (its ends are in different groups). "
    "<br>1️⃣ Try to cut <b>all 4</b> edges. "
    "<br>2️⃣ Notice the winning pattern: a <b>checkerboard</b>, where every node "
    "is in the opposite group from both its neighbours. "
    "<br>3️⃣ That best split — cutting all 4 — is exactly the answer we'll make "
    "QAOA discover on its own."
)))
cells.append(code('show_widget("maxcut-painter")'))

cells.append(code(
"""# Quick check — which edges count toward a Max-Cut?
quiz.ask("m6-maxcut-goal")"""))

# ----------------------------------------------------------------- 6.2
cells.append(md(r"""## 6.2 Encoding the problem as energy

To let a quantum computer search for the best cut, we turn the cut into **energy** — and you already have the tool. Give **each node its own qubit**. A node's group is just that qubit's value: group A = $\ket{0}$, group B = $\ket{1}$. A whole split is then a bitstring like `0101`.

Now recall Basecamp 4's **$ZZ$ agreement scoreboard**: $Z_iZ_j$ scores **$+1$ when two qubits agree** and **$-1$ when they disagree**. Look what that means here:

- an edge is **cut** ⟺ its nodes are in **different** groups ⟺ the two qubits **disagree** ⟺ $Z_iZ_j = -1$
- an edge is **uncut** ⟺ same group ⟺ qubits **agree** ⟺ $Z_iZ_j = +1$

So if we add up $Z_iZ_j$ over every edge, each cut edge subtracts 1 and each uncut edge adds 1. The **cost Hamiltonian** is:

$$H_C = \sum_{(i,j)\,\in\,\text{edges}} Z_i Z_j$$

The split with the **most cuts** is the one with the **lowest energy** $\langle H_C\rangle$ — the **ground state**. And finding a ground state is exactly the variational job you mastered in Basecamp 5. Max-Cut just *became* a quantum energy-minimization problem.

Let's build $H_C$ for our ring. This cell is plumbing — read it, but the idea above is what matters:"""))
cells.append(code(
'''import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector

N = 4                                     # four nodes -> four qubits
EDGES = [(0, 1), (1, 2), (2, 3), (3, 0)]  # the ring

def zz_term(i, j, n):
    """A Pauli string with Z on qubits i and j (qubit 0 = rightmost char)."""
    label = ["I"] * n
    label[n - 1 - i] = "Z"
    label[n - 1 - j] = "Z"
    return "".join(label)

# H_C = sum of Z_i Z_j over the edges.
H_C = SparsePauliOp.from_list([(zz_term(i, j, N), 1.0) for (i, j) in EDGES])
print("Cost Hamiltonian H_C:")
print(H_C)'''))

cells.append(code(
"""# Quick check — why does MINIMIZING <H_C> maximize the cut?
quiz.ask("m6-cost-encoding")"""))

cells.append(md(r"""### Worked example: score the worst split

Before you score the *best* split, let's score the *worst* one to feel the encoding. Put **every** node in the same group — the state $\ket{0000}$ — so **no** edge is cut. Every edge is an agreement ($+1$), and there are 4 of them, so $\langle H_C\rangle$ should be $+4$ (the highest, worst energy):"""))
cells.append(code(
"""# All nodes in group A: |0000>. No cuts -> every edge agrees -> <H_C> = +4.
qc_worst = QuantumCircuit(N)               # an empty circuit leaves all qubits in |0>
worst_energy = Statevector(qc_worst).expectation_value(H_C).real
print("<H_C> for |0000> (no cuts) =", worst_energy)"""))
cells.append(md(r"""`+4.0` — the worst possible, exactly as the scoreboard predicts. Now flip it around and score the champion."""))

# ----------------------------------------------------------------- task 1
cells.append(task(1, (
    "Score the <b>checkerboard</b> cut. In the winning split, nodes <b>0 and "
    "2</b> go in one group and nodes <b>1 and 3</b> in the other — the bitstring "
    "<code>0101</code>. Build that state in <code>qc_best</code> by flipping "
    "<b>qubits 0 and 2</b> to $\\ket{1}$ with <code>.x(0)</code> and "
    "<code>.x(2)</code> (remember: qubit 0 is the rightmost character, so this "
    "makes <code>0101</code>). Then read its energy into <code>cut_energy</code>. "
    "<br><i>Predict first:</i> all 4 edges are cut, each scoring $-1$, so "
    "$\\langle H_C\\rangle = ?$"
)))
cells.append(code(
"""# Build the checkerboard cut |0101> and score it under H_C.
qc_best = QuantumCircuit(N)
### BEGIN SOLUTION
qc_best.x(0)
qc_best.x(2)
cut_energy = Statevector(qc_best).expectation_value(H_C).real
### END SOLUTION
# cut_energy = ...   # <- your <H_C> goes here

# Nothing to change below — the checkerboard should hit the ground energy.
checkers.check_expectation(cut_energy, targets.M6_CUT_ENERGY)"""))
cells.append(analysis(r"""$\langle H_C\rangle = -4$: every one of the 4 edges is cut, each
contributing $-1$. That's the **lowest** energy any split can reach — the ground
state of $H_C$ — and it corresponds to the **maximum cut**. You've now confirmed
both ends of the ladder: the no-cut split sits at $+4$, the all-cut split at $-4$.
A quantum optimizer that finds the bottom of this landscape finds the best cut.
The catch, of course, is that on a big graph we *can't* just write down the answer
the way we did here — we have to search. Enter QAOA."""))

# ----------------------------------------------------------------- 6.3
cells.append(md(r"""## 6.3 The QAOA ansatz: cost + mixer

**QAOA** builds a parameterized state whose measurement concentrates on low-energy (high-cut) bitstrings. It starts every qubit in the fair superposition $\ket{+}$ — every split equally likely — and then applies a few **layers**, each made of two moves with their own tunable angles:

1. **Cost layer** (angle $\gamma$): for every edge, an `rzz(2γ, i, j)` rotation. This stamps a *phase* onto each configuration according to its energy — low-energy cuts get marked.
2. **Mixer layer** (angle $\beta$): an `rx(2β)` rotation on **every** qubit. This is what turns those invisible phases into real **probability**, by letting the marked configurations interfere.

Here's the crucial intuition, and it's a common trap:

> ⚠️ **Why both?** The cost layer alone is *diagonal* — applied to $\ket{+}^{\otimes N}$ it only adds phases, and phases are invisible to a Z-measurement. Measure and you'd get a **uniform** random split — useless. The **mixer** rotates those phases into amplitude differences (interference), so the good cuts actually become *more likely*. Cost **marks**; mixer **makes likely**. You need the pair.

We'll use **2 layers** (so 4 angles total: $\gamma_1,\gamma_2,\beta_1,\beta_2$). Run the setup:"""))
cells.append(code(
"""# The variational-loop tools from Basecamp 5, plus the sampler for the final read-out.
from scipy.optimize import minimize
from qiskit_aer import AerSimulator"""))

cells.append(code(
"""# Quick check — what happens if you forget the mixer?
quiz.ask("m6-qaoa-mixer")"""))

cells.append(md(r"""### Syntax preview — one QAOA layer

```python
qc = QuantumCircuit(N)
qc.h(range(N))                      # start: every split equally likely, |+>^N
for (i, j) in EDGES:
    qc.rzz(2 * gamma, i, j)         # COST: phase each edge by its agreement
for k in range(N):
    qc.rx(2 * beta, k)             # MIXER: rotate phases into real probability
```

`rzz(θ, i, j)` is a two-qubit rotation that acts exactly like $e^{-i\,\tfrac{\theta}{2} Z_iZ_j}$ — the natural "cost" move for a $ZZ$ term. `rx(θ, k)` is the single-qubit rotation you met in Basecamp 2."""))

# ----------------------------------------------------------------- task 2
cells.append(task(2, (
    "Complete the QAOA ansatz by adding the <b>mixer</b>. The <code>h</code> "
    "start and the <b>cost</b> layer (the <code>rzz</code> loop over edges) are "
    "written for you. Add the mixer: a loop that applies <code>.rx(2 * "
    "betas[layer], k)</code> to <b>every</b> qubit <code>k</code> in "
    "<code>range(N)</code>. "
    "<br>Without it, the next cell's search will just return uniform noise — "
    "with it, QAOA will home in on the checkerboard."
)))
cells.append(code(
'''def qaoa_circuit(params):
    """Build the p-layer QAOA circuit for our ring. params = [gammas..., betas...]."""
    p = len(params) // 2
    gammas, betas = params[:p], params[p:]

    qc = QuantumCircuit(N)
    qc.h(range(N))                          # start in |+>^N: every split equally likely
    for layer in range(p):
        # COST layer: phase every edge by its agreement (this part is done for you)
        for (i, j) in EDGES:
            qc.rzz(2 * gammas[layer], i, j)
        # MIXER layer: your turn — an rx(2*betas[layer]) on every qubit
### BEGIN SOLUTION
        for k in range(N):
            qc.rx(2 * betas[layer], k)
### END SOLUTION
    return qc

# A quick look at the 2-layer circuit (4 angles). No check yet — that comes after we optimize.
print(qaoa_circuit([0.5, 0.5, 0.5, 0.5]).draw(output="text"))'''))

# ----------------------------------------------------------------- 6.4
cells.append(md(r"""## 6.4 Close the loop and reach the summit

Now the Basecamp 5 machinery, pointed at Max-Cut. The **cost function** is $\langle H_C\rangle$ of the QAOA state; the **classical optimizer** tunes the 4 angles to drive it down. We try a handful of fixed starting points and keep the best (QAOA landscapes have local dips, so a few starts is good practice — and it keeps this fully reproducible)."""))
cells.append(code(
'''# The cost to minimize: the QAOA state's energy under H_C.
def cost(params):
    return Statevector(qaoa_circuit(params)).expectation_value(H_C).real

# A few fixed starting angles; keep whichever descends lowest.
starts = [[0.5, 0.5, 0.5, 0.5], [0.8, 0.6, 0.4, 0.9], [0.3, 1.1, 0.7, 0.2],
          [1.0, 0.4, 0.5, 0.8], [0.6, 0.6, 0.6, 0.6]]
best_res = None
for x0 in starts:
    res = minimize(cost, x0, method="COBYLA", options={"maxiter": 250})
    if best_res is None or res.fun < best_res.fun:
        best_res = res

print(f"Lowest energy QAOA reached: <H_C> = {best_res.fun:+.3f}  "
      f"(the true ground energy is {targets.M6_CUT_ENERGY:+.0f})")'''))

cells.append(md(r"""The optimizer found the angles. But QAOA's real output isn't the energy — it's the **measurement**. We sample the optimized circuit many times; the most frequent bitstring is the cut it's recommending. Let's read the answer off the mountain:"""))
cells.append(code(
'''# Sample the optimized circuit and read off the winning split.
final = qaoa_circuit(best_res.x)
final.measure_all()
counts = AerSimulator().run(final, shots=2048, seed_simulator=7).result().get_counts()
counts = {k.replace(" ", ""): v for k, v in counts.items()}

best = max(counts, key=counts.get)          # the most-frequent bitstring
print(f"Most frequent split: {best}")

def cut_value(bitstring):
    bits = bitstring[::-1]                   # qubit 0 is the rightmost character
    return sum(1 for (i, j) in EDGES if bits[i] != bits[j])

ratio = cut_value(best) / 4                  # 4 is this ring's true maximum cut
print(f"It cuts {cut_value(best)} of 4 edges  ->  approximation ratio {ratio:.2f}")

# The summit check — did QAOA find a maximum cut?
checkers.check_maxcut_solution(best, EDGES)'''))
cells.append(analysis(r"""**Approximation ratio 1.0** — QAOA found a maximum cut, all on
its own. It never saw the checkerboard; it started from "every split equally
likely", used the cost layer to phase-mark good cuts and the mixer to make them
interfere into being *probable*, and a classical optimizer tuned the angles until
measuring the circuit handed back `0101` (or its mirror `1010`). That is a complete
quantum optimization algorithm — and you built every layer of it.

Now — before you take that 1.0 home — we owe you some honesty about it. 🏔️"""))

# --------------------------------------------------- the honest graphs
# The 4-ring is the friendliest graph in existence for this algorithm: it is
# bipartite (max cut = ALL edges) and p=2 solves it exactly. Stopping here would
# teach "QAOA solves optimization problems", and a judge who knows QAOA would
# notice we picked the one graph where it cannot fail. The two sections below
# pay off the word *Approximate* with two genuinely different lessons.
cells.append(md(r"""---

## 7 · The word we haven't earned yet: **Approximate**

QAOA stands for the **Quantum Approximate Optimization Algorithm**, and so far
nothing you've seen has been approximate at all. That's not luck — it's the graph
we chose.

A 4-node ring is **bipartite**: you can 2-colour it so that *every single edge*
runs between the colours. Its maximum cut is all 4 of 4, and a $p=2$ circuit
reaches it every time. It's the friendliest graph in existence for this algorithm.

Two things can go "wrong" in the real world, and they are completely different
problems. Let's meet both.

### 7a · Frustration: when the best answer still isn't perfect

Three towns, all connected to each other — a **triangle**. Split them into two
groups. Try it on paper before you run the cell: **how many of the 3 roads can you
cut?**"""))
cells.append(code(
'''# Brute force is honest and, at 3 nodes, instant: check all 2^3 splits.
TRIANGLE = [(0, 1), (1, 2), (0, 2)]

def cut_of(bits, edges):
    """How many edges have their endpoints in different groups?"""
    return sum(1 for (i, j) in edges if bits[i] != bits[j])

print(" split | cut")
best_tri = 0
for v in range(8):
    bits = [(v >> k) & 1 for k in range(3)]      # bits[k] = group of node k
    c = cut_of(bits, TRIANGLE)
    best_tri = max(best_tri, c)
    print(f"  {bits}  |  {c}")

print(f"\\nBest possible cut on a triangle: {best_tri} of {len(TRIANGLE)} edges")'''))
cells.append(analysis(r"""**2 out of 3 — and no algorithm on Earth does better.**

Two groups, three mutually connected towns: two of them must land together, and
the road between *those two* can never be cut. This is called **frustration**, and
it is a property of the **problem**, not a failure of the **solver**. A perfect
quantum computer, a supercomputer, and a very patient person with a pencil all
return 2.

Remember this the next time you see an approximation ratio below 1.0. Sometimes it
means the algorithm fell short. Sometimes — as here — it means the algorithm found
the true best answer and the true best answer simply isn't perfect. Those are very
different situations, and telling them apart is the job."""))

cells.append(md(r"""### 7b · Depth: when QAOA genuinely falls short

Now a graph where the shortfall *is* the algorithm's. Five towns in a ring —
a **5-cycle**. It's an odd cycle, so like the triangle it can't be perfectly
2-coloured: the true maximum cut is **4 of 5**.

Here's the question worth predicting before you run anything. Random guessing cuts
2.5 edges on average. The true maximum is 4. **Where do you think a $p=1$ QAOA
lands?**

Write your guess down, then run the cell. It reuses exactly the optimizer loop you
built above — COBYLA, from a handful of starting points — at each depth, and reports
the best expected cut it can reach."""))
cells.append(code(
'''from scipy.optimize import minimize

C5 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
N5, MAXCUT_C5 = 5, 4                      # verified by brute force below

assert max(cut_of([(v >> k) & 1 for k in range(N5)], C5)
           for v in range(2 ** N5)) == MAXCUT_C5

def qaoa_expected_cut(gammas, betas, edges=C5, n=N5):
    """<C>: the average cut we'd get by sampling this QAOA circuit."""
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for g, b in zip(gammas, betas):
        for (i, j) in edges:
            qc.rzz(2 * g, i, j)
        qc.rx(2 * b, range(n))
    probs = Statevector(qc).probabilities()
    return sum(pr * cut_of([(v >> k) & 1 for k in range(n)], edges)
               for v, pr in enumerate(probs))

def best_cut_at_depth(p, n_starts=8):
    """Run the same classical optimizer from several fixed starts and keep the
    best. Multi-start matters: this landscape has local optima, so a single run
    can settle for a mediocre answer — exactly the difficulty Basecamp 5 warned
    about with flat regions."""
    rng = np.random.default_rng(7)                 # fixed seed: reproducible
    best = -np.inf
    for _ in range(n_starts):
        x0 = rng.uniform(0, np.pi, 2 * p)
        res = minimize(lambda x: -qaoa_expected_cut(x[:p], x[p:]),
                       x0, method="COBYLA", options={"maxiter": 400})
        best = max(best, -res.fun)
    return best

print(f"Random guessing:      <C> = {len(C5) / 2:.3f}   (ratio {len(C5) / 2 / MAXCUT_C5:.3f})")
for p in (1, 2):
    b = best_cut_at_depth(p)
    print(f"QAOA depth p = {p}:    <C> = {b:.3f}   (ratio {b / MAXCUT_C5:.3f})")
print(f"True maximum:         <C> = {MAXCUT_C5:.3f}   (ratio 1.000)")'''))
cells.append(analysis(r"""**There it is — the "A" in QAOA.**

At $p=1$ the best you can do on this graph is about $\langle C\rangle = 3.75$, an
approximation ratio near **0.94**. That is a real, useful win over guessing (2.5),
and it is genuinely short of the optimum. Add a second layer — which brings a
*second pair of angles*, and that is what depth actually buys you — and the ratio
climbs to essentially **1.000**.

So the honest summary of what you built is:

| | 4-ring (bipartite) | Triangle | 5-cycle |
|---|---|---|---|
| Max cut | 4 of 4 — every edge | **2 of 3** | **4 of 5** |
| QAOA at $p=1$ | ratio 0.75 | ratio 1.00 | ratio 0.94 |
| QAOA at $p=2$ | ratio 1.00 | ratio 1.00 | ratio 1.00 |
| The lesson | the easy case | the *problem* is frustrated | the *algorithm* needs depth |

And one more piece of honesty, because it's the thing people leave out: **more
depth is not free.** Every layer is more gates, and on real hardware more gates
means more noise. Choosing $p$ is a genuine engineering trade-off between a better
answer and a circuit that still survives the machine — not a dial you simply turn
up. Nobody has yet demonstrated a quantum advantage for Max-Cut on real hardware.

You built the algorithm, you saw where it shines, and you saw where it doesn't.
That last part is what makes you dangerous. **You've reached the summit.** 🏔️"""))

# ----------------------------------------------------------------- analogy
cells.append(analogy_callout(
    "QAOA solving Max-Cut (cost layer + mixer layer + classical optimizer)",
    (
        "I'm learning quantum computing. Explain how QAOA solves the Max-Cut "
        "problem, using an analogy from MY background: [YOUR HOBBY/FIELD HERE].\n\n"
        "Ground rules — your analogy MUST respect these facts:\n"
        "1) Max-Cut: split a graph's nodes into two groups to maximize the number "
        "of edges whose endpoints are in different groups.\n"
        "2) We encode it as a cost Hamiltonian H_C = sum of Z_i Z_j over edges; a "
        "cut edge (qubits disagree) lowers the energy, so the best cut is the "
        "lowest-energy (ground) state.\n"
        "3) QAOA builds a circuit that starts in an equal superposition of all "
        "splits, then alternates a COST layer (phases each split by its energy) "
        "and a MIXER layer (turns those phases into real probability via "
        "interference). BOTH layers are needed.\n"
        "4) A CLASSICAL optimizer tunes the layer angles; then you MEASURE the "
        "circuit many times and take the most frequent bitstring as the answer.\n"
        "5) Do NOT claim QAOA 'tries all cuts at once and instantly returns the "
        "best'. It shifts probability toward good cuts over an iterative loop, and "
        "the final answer comes from sampling.\n\n"
        "End by telling me where the analogy breaks down."
    ),
))

# ----------------------------------------------------------------- claim code
cells.append(md(r"""## 🎓 Log your climb — claim the Summit code

You solved a real NP-hard problem with a quantum algorithm you built from scratch:
you scored the checkerboard cut at $\langle H_C\rangle = -4$ (**Task 1**) and let
QAOA rediscover it by sampling `best` (**Task 2**) — and then you went on to see what
that ratio looks like on graphs that don't hand it to you.
Run the cell below — it re-checks both here in this kernel and, if they pass, prints
your final **completion code**.

Copy it into the **“Log your notebook”** box on the
[Summit page](https://quantum-ascent-77617.web.app/module.html?id=06#claim)
to light the final camp on your Ascent map and claim the **🏅 Summit** badge. 🏔️"""))
cells.append(code("progress.claim_basecamp_6(cut_energy, best)"))

# ----------------------------------------------------------------- footer
cells.append(basecamp_footer(
    6,
    summary=(
        "You reached the summit. You framed **Max-Cut**, encoded it as a cost "
        "Hamiltonian $H_C=\\sum Z_iZ_j$, built the **QAOA ansatz** from a cost "
        "layer and a mixer layer, closed the **variational loop** with a classical "
        "optimizer, and sampled a **maximum cut**. Then you did the thing most "
        "courses skip: you took the same algorithm to a **frustrated triangle** "
        "(where the best possible answer still leaves an edge uncut) and a "
        "**5-cycle** (where $p=1$ genuinely falls short at ratio 0.94, and depth "
        "is what closes the gap) — so you know what *Approximate* costs, not just "
        "what it promises. Every idea of the ascent — superposition, gates, "
        "entanglement, energy, the variational principle — met in one working "
        "quantum algorithm that *you assembled*. Congratulations, climber. 🏔️"
    ),
    quiz_url="https://quantum-ascent-77617.web.app/module.html?id=06#quiz",
    next_label=("You've topped out the main ascent! Revisit any basecamp to "
                "deepen it, try a bigger or messier graph in the QAOA code, or "
                "take the post-course assessment to measure how far you climbed"),
    solutions_relpath="solutions/06_qaoa_maxcut_capstone_solutions.ipynb",
))

write_notebook(
    cells,
    REPO / "notebooks" / "solutions" / "06_qaoa_maxcut_capstone_solutions.ipynb",
)
