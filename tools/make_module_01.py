"""Author the Module 01 SOLUTIONS notebook (source of truth).

    python tools/make_module_01.py
    python tools/build_solutions.py 01     # then derive the student version
"""

from nb_common import (
    REPO, analysis, analogy_callout, basecamp_footer, bootstrap_cell,
    briefing, code, exercise, md, task, write_notebook,
)

cells = []

# ----------------------------------------------------------------- header
cells.append(briefing(
    1, "The Qubit & Superposition",
    mission=(
        "Classical bits answer <i>yes</i> or <i>no</i>. Qubits hold something "
        "richer: a pair of <b>amplitudes</b> that only turn into yes/no when "
        "you look. Your mission: build your first quantum states, predict "
        "their measurement statistics <i>before</i> running them, and verify "
        "your predictions on a real quantum simulator.<br><br>"
        "<i>Note: If quantum concepts feel a bit abstract or intimidating at first, "
        "don't worry! We will build and understand these ideas slowly, step-by-step. "
        "Let's take it one step at a time.</i>"
    ),
    objectives=[
        "Describe a qubit state as a 2-amplitude vector and explain why the 'both 0 and 1 at once' slogan is misleading",
        "Use the Born rule to predict measurement probabilities from amplitudes",
        "Build and run your first Qiskit circuit and read measurement counts",
        "Prepare a state with any target measurement probability using a rotation gate",
    ],
    minutes=45,
))
cells.append(bootstrap_cell())

# ----------------------------------------------------------------- 1.1
cells.append(md(r"""## 1.1 From bits to qubits

Let's start with what you already know. A classical bit is like a standard light switch: it is either **0** (off) or **1** (on). There is no middle ground.

A **qubit** (quantum bit) is different. Before you look at it, it isn't set to just 0 or 1. Instead, it is described by two numbers called **amplitudes** (written as $\alpha$ and $\beta$):

$$\ket{\psi} = \alpha \ket{0} + \beta \ket{1}$$

Amplitudes are **not** probabilities themselves — they're a related but different kind of number. Here's the rule that connects them, called the **Born rule**: when you measure the qubit, you get outcome **0** with probability $|\alpha|^2$, and outcome **1** with probability $|\beta|^2$. (The bars mean "size of the number, squared" — for the ordinary positive amplitudes we'll use in this basecamp, that's just the number squared.)

For example, imagine you are **spinning a coin**. While it's spinning, it isn't heads or tails yet — it's some blend of both, described by amplitudes. But when you **slap it down on the table** (in quantum computing, we call this **measurement**), it is forced to land on either heads (0) or tails (1).

> ✍️ **Study Tip:** If these concepts or the mathematical notation feel intimidating at first, don't worry! The best way to grab the concept is to grab a physical pen and write them down on paper together as we go. We will build and understand everything slowly, step-by-step.

> 💡 **Don't panic! Let's break down the rest of the notation:**
> - The vertical bar and angle bracket (like $\ket{\psi}$ or $\ket{0}$) is called **Dirac notation**. It's just a shorthand way of saying *"this is a quantum state."* You can think of it as a wrapper.
> - $\ket{0}$ represents the state where the qubit will definitely measure as **0**.
> - $\ket{1}$ represents the state where the qubit will definitely measure as **1**.

Since a measurement must land on *either* 0 or 1, the two probabilities have to add up to $100\%$ ($1$):
$$|\alpha|^2 + |\beta|^2 = 1.$$

This rule has a name: **normalization**. Every valid qubit state's amplitudes must be sized so this equation holds true — you'll use this constantly from here on, so it's worth remembering the word.

### Why use amplitudes instead of regular probabilities?
If amplitudes just determine probabilities, why not just use normal probabilities?
Unlike regular probabilities (which are always positive numbers), amplitudes can be positive, negative, or even complex numbers. This allows amplitudes to *cancel each other out* (a phenomenon called **interference**). This cancellation is the secret engine behind every quantum speedup you'll meet on this ascent — but for now, we'll keep things simple and only use real, positive amplitudes."""))

# ----------------------------------------------------------------- spinning coin widget
cells.append(exercise(1, (
    "Try it yourself! Below is the <b>Spinning Coin</b> widget. "
    "<br>1️⃣ The coin is spinning in a 50/50 state. Click <b>Slap! (Measure)</b> to force it to pick 0 (Heads) or 1 (Tails). "
    "<br>2️⃣ Click it 100 times. Notice how the histogram roughly settles into ~50 times Heads and ~50 times Tails."
)))
cells.append(code('show_widget("coin-spinner")'))

# ----------------------------------------------------------------- bloch sampler widget
cells.append(exercise(2, (
    "Below is the <b>Bloch Sampler</b>. The arrow is a qubit state; the "
    "<b>θ slider</b> tilts it between the north pole (|0⟩) and south "
    "pole (|1⟩). "
    "<br>1️⃣ Set θ ≈ 90° and press <b>Measure ×1</b> a few times. Can you "
    "predict each outcome? "
    "<br>2️⃣ Now press <b>Measure ×100</b>. What shape does the histogram "
    "settle into? "
    "<br>3️⃣ Find the θ where outcome 1 appears about a quarter of the time. "
    "Remember that angle — you'll need it in Task 3."
)))
cells.append(code('show_widget("bloch-sampler")'))

# ----------------------------------------------------------------- 1.2
cells.append(md(r"""## 1.2 The math the widget was showing you

> 📐 **Don't worry about the trigonometry!**
> If these formulas look a bit scary, take a deep breath. We are just using basic angles to describe the physical tilt of the arrow in the widget. Let's break it down together.

Any single-qubit state can be represented as an arrow on a sphere. We can write this state using two angles: $\theta$ (the tilt from the top) and $\varphi$ (the twist around the equator, which we can ignore for now):

$$\ket{\psi} = \cos\tfrac{\theta}{2}\,\ket{0} + e^{i\varphi}\sin\tfrac{\theta}{2}\,\ket{1}$$

According to the Born rule, the probability of measuring 0 or 1 is just the square of these coefficients:

$$P(0) = \cos^2\tfrac{\theta}{2}, \qquad P(1) = \sin^2\tfrac{\theta}{2}$$

### Worked Example: The $\theta = 90^\circ$ State
Let's see what happens if we tilt the arrow exactly halfway down to the equator ($\theta = 90^\circ$ or $\pi/2$ radians):
* $\theta/2 = 45^\circ$
* $\cos(45^\circ) = \tfrac{1}{\sqrt{2}}$
* $\sin(45^\circ) = \tfrac{1}{\sqrt{2}}$

Substituting these in, we get the state (often called the $\ket{+}$ state):

$$\ket{+} = \sqrttwo\,\ket{0} + \sqrttwo\,\ket{1}
\;\Rightarrow\;
P(0) = \left(\sqrttwo\right)^2 = \tfrac12,\quad P(1) = \tfrac12.$$

This is a perfect 50/50 coin flip! That is exactly the histogram you watched build up in the widget.
Remember: one single measurement tells you almost nothing (just a 0 or a 1); it is the **statistics over many shots** that reveal the underlying amplitudes. That is how we read quantum data!

### 🐍 Coding connection: Representing states with NumPy
In Python, we represent a qubit's amplitude pair as a **NumPy array**: `np.array([amplitude_0, amplitude_1])`. Run the cell below to see the syntax in action — building the two basic states, reading out a single amplitude, and scaling an array (useful any time you need to normalize a state):"""))

cells.append(code(
"""import numpy as np

state_0 = np.array([1, 0])   # this is |0>: amplitude 1 on "0", amplitude 0 on "1"
state_1 = np.array([0, 1])   # this is |1>
print("state_0 =", state_0)
print("first amplitude of state_0 (index 0):", state_0[0])

# NumPy scales every entry of an array at once — handy for normalizing a state.
# Example: [3, 4] scaled down to a unit-length vector (0.6^2 + 0.8^2 = 1).
example = np.array([3, 4]) / 5
print("example =", example, "-> squares sum to", (example ** 2).sum())"""))

cells.append(md(r"""Notice `example`'s squared entries summed to exactly 1 — that's **normalization** in action, the same rule from §1.1 ($|\alpha|^2+|\beta|^2=1$). Now it's your turn: use the same `np.array(...)` syntax, plus that normalization rule, to build the $\ket{+}$ state yourself in Task 1."""))

# ----------------------------------------------------------------- task 1
cells.append(task(1, (
    "Build the |+⟩ state as a NumPy array of its two amplitudes: equal "
    "weight on |0⟩ and |1⟩, both amplitudes real and positive, "
    "properly normalized (their squares must sum to 1 — see §1.1). "
    "The checker forgives global phase but not normalization."
)))
cells.append(code(
"""plus = None  # Initialize
# Build the |+> state as an array of its two amplitudes [amp_0, amp_1].
# Both amplitudes are equal, real, and positive — and the array must be
# normalized: (amp_0)^2 + (amp_1)^2 must equal 1.
# Hint: assign your array to the variable 'plus'
### BEGIN SOLUTION
plus = np.array([1, 1]) / np.sqrt(2)
### END SOLUTION

checkers.check_statevector(plus, targets.M1_TASK1)"""))
cells.append(analysis(r"""Why $\tfrac{1}{\sqrt{2}}$ and not $\tfrac12$?
Normalization lives on the *squares*: we need
$|\alpha|^2 + |\beta|^2 = \tfrac12 + \tfrac12 = 1$.
If you had written $[\tfrac12, \tfrac12]$, the squares would sum to
$\tfrac14 + \tfrac14 = \tfrac12$ — only "half a qubit" of probability, which
physics forbids and the checker rejects. Every valid qubit state lives on the
unit circle of amplitude space."""))

# ----------------------------------------------------------------- 1.3
cells.append(md(r"""## 1.3 Your first quantum circuit

In real quantum hardware, we can't directly type amplitude arrays. Instead, we start every qubit in the default state $\ket{0}$ and apply **quantum gates** (which act like operations that rotate the dials). 

The **Hadamard gate** ($H$) is the ultimate superposition-maker. It takes a qubit starting at $\ket{0}$ and sets its dials to a perfect 50/50 split ($\ket{+}$):

$$H = \hadamard{}, \qquad H\ket{0} = \ket{+}.$$

Let's build this circuit in Qiskit. A quantum circuit is read from left to right: prepare the qubits, apply the transformations (gates), and finally, measure the outcomes."""))
cells.append(code(
"""from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

qc = QuantumCircuit(1)      # one qubit, starts in |0>
qc.h(0)                     # Hadamard on qubit 0
qc.measure_all()            # read it out
qc.draw(output="mpl")"""))

# ----------------------------------------------------------------- task 2
cells.append(task(2, (
    "Run the circuit above for <b>1024 shots</b> on the <code>AerSimulator</code> "
    "and collect the counts dictionary. <i>Before you run it</i>: write down "
    "how many '0's you expect. Then let the checker judge your statistics — "
    "it uses a chi-square test, so honest shot noise passes but a wrong "
    "circuit fails."
)))
cells.append(code(
"""counts = None  # Initialize
# Run the simulation and assign the counts dictionary to `counts`
### BEGIN SOLUTION
counts = AerSimulator().run(qc, shots=1024).result().get_counts()
### END SOLUTION

print(counts)
checkers.check_counts_close(counts, {"0": 0.5, "1": 0.5})"""))
cells.append(analysis(r"""You did **not** get exactly 512/512 — and that's the
point. Each shot is an independent Born-rule sample, so the counts fluctuate
like 1024 coin flips (standard deviation $\approx \sqrt{1024 \cdot \tfrac12 \cdot \tfrac12} = 16$).
This is why every quantum result you'll ever report is *statistics over
shots*, and why the checker asks "is this consistent with 50/50?" rather than
"is this exactly 50/50?". Run the cell again — you'll get slightly different
counts, same verdict."""))

# ----------------------------------------------------------------- 1.4
cells.append(md(r"""## 1.4 Steering the amplitudes: the $R_y$ gate

The Hadamard gate only gives a 50/50 split. What if we want to dial in any specific probability? 

We do this by rotating the qubit state by a chosen angle using the $R_y(\theta)$ gate. This is the programmatic version of the $\theta$ slider you used in the first exercise:

$$R_y(\theta)\ket{0} = \cos\tfrac{\theta}{2}\,\ket{0} + \sin\tfrac{\theta}{2}\,\ket{1}$$

If you want a target probability of getting a 1 (i.e. $P(1)$), you just solve the equation:
$$\sin^2\tfrac{\theta}{2} = P(1)$$

This concept — *choosing an angle to get a specific distribution* — is extremely powerful! Later on the Summit, we will see how variational algorithms tune these rotation angles until the measurement statistics output the solution to a hard computational problem.

One more tool before Task 3: instead of running many shots to *estimate* probabilities, Qiskit can compute a circuit's exact amplitude pair directly — this is called the circuit's **statevector**. Task 3 checks your statevector exactly, rather than counting shots."""))

# ----------------------------------------------------------------- task 3
cells.append(task(3, (
    "Prepare the state with P(1) = 1/4 (the one you hunted for with "
    "the slider in Exercise 2). Create a 1-qubit circuit, apply "
    "<code>qc3.ry(theta, 0)</code> with the right angle, and check the exact "
    "statevector. <br><i>Paper first:</i> solve "
    "sin²(θ/2) = 1/4, then code it."
)))
cells.append(code(
"""qc3 = QuantumCircuit(1)
### BEGIN SOLUTION
theta = np.pi / 3           # sin^2(theta/2) = 1/4  =>  theta/2 = pi/6
qc3.ry(theta, 0)
### END SOLUTION

checkers.check_statevector(qc3, targets.M1_TASK3)"""))
cells.append(analysis(r"""Let's break down the math step-by-step to see how we got that angle:
1. We want the probability of getting a 1 to be $1/4$, so:
   $$P(1) = \sin^2\tfrac{\theta}{2} = \tfrac14$$
2. Taking the square root of both sides gives:
   $$\sin\tfrac{\theta}{2} = \tfrac12$$
3. What angle has a sine of $1/2$? That is $30^\circ$ (or $\pi/6$ radians):
   $$\tfrac{\theta}{2} = \tfrac{\pi}{6}$$
4. Multiplying by 2 gives our rotation angle $\theta$:
   $$\theta = \tfrac{\pi}{3} \approx 1.047 \text{ radians (or } 60^\circ \text{)}$$
   (This is the ≈ 60° angle you found using the slider in Exercise 2!)

When we plug this back into our state formula, we get:
$$\cos\tfrac{\pi}{6}\ket{0} + \sin\tfrac{\pi}{6}\ket{1} = \tfrac{\sqrt3}{2}\ket{0} + \tfrac12\ket{1}$$

And indeed, the squares of these amplitudes are:
* $P(0) = \left(\tfrac{\sqrt3}{2}\right)^2 = \tfrac34$
* $P(1) = \left(\tfrac12\right)^2 = \tfrac14$

Amplitudes $\rightarrow$ squares $\rightarrow$ probabilities. Once this chain feels automatic, you're officially thinking in quantum!"""))

# ----------------------------------------------------------------- analogy
cells.append(analogy_callout(
    "superposition and measurement",
    (
        "I'm learning quantum computing. Explain superposition and measurement "
        "using an analogy from MY background: [YOUR HOBBY/FIELD HERE].\n\n"
        "Ground rules — your analogy MUST respect these facts:\n"
        "1) A qubit state is two amplitudes (α, β), complex numbers with "
        "|α|²+|β|²=1. It is NOT 'both 0 and 1 at once'.\n"
        "2) Measurement gives outcome 0 with probability |α|² and 1 with "
        "probability |β|² (Born rule), and the state then collapses to that "
        "outcome.\n"
        "3) Amplitudes can be negative/complex and can cancel (interference); "
        "probabilities cannot.\n"
        "4) One measurement reveals almost nothing; statistics over many "
        "shots reveal the amplitudes.\n\n"
        "End by telling me where the analogy breaks down."
    ),
))

# ----------------------------------------------------------------- footer
cells.append(basecamp_footer(
    1,
    summary=(
        "You can now write a qubit as amplitudes, predict its statistics "
        "with the Born rule, and steer it with $H$ and $R_y$ in Qiskit — "
        "prediction before simulation, every time."
    ),
    quiz_url="https://quantum-ascent-77617.web.app/module.html?id=01#quiz",
    next_label="Basecamp 2: Gates & Circuits — where rotations compose and phases start to matter",
    solutions_relpath="solutions/01_qubits_and_superposition_solutions.ipynb",
))

write_notebook(
    cells,
    REPO / "notebooks" / "solutions" / "01_qubits_and_superposition_solutions.ipynb",
)
