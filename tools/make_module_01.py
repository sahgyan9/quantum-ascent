"""Author the Module 01 SOLUTIONS notebook (source of truth).

    python tools/make_module_01.py
    python tools/build_solutions.py 01     # then derive the student version

House pedagogy (see memory: narrative-first authoring style):
story & imagination first -> slow recap -> rename with the formal word ->
plain math -> widget play -> only then amplitudes/notation. Every coding
task is preceded by a fully worked example of the exact same pattern
(green check included), and the task itself is a "change the numbers" tweak.
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
        "Classical bits answer <i>yes</i> or <i>no</i>. A qubit is more like a "
        "<b>spinning coin</b>: undetermined until you slap it down — and, even "
        "better, <i>you</i> get to choose the coin's bias. Your mission: spin "
        "the coin, bias it to 75/25, then build that exact biased coin as a "
        "real quantum state <b>three different ways</b> — on a widget, on "
        "paper as a vector, and on a quantum circuit whose rotation angle you "
        "compute yourself — predicting the statistics <i>before</i> every "
        "run.<br><br>"
        "<i>Note: If quantum concepts feel a bit abstract or intimidating at first, "
        "don't worry! We will build and understand these ideas slowly, step-by-step. "
        "Let's take it one step at a time.</i>"
    ),
    objectives=[
        "Tell the spinning-coin story of the qubit — undetermined until measured — and say precisely what the pop-science “both 0 and 1 at once” slogan gets wrong",
        "Predict the measurement statistics of fair and biased quantum states before running a single shot (the Born rule)",
        "Write |0⟩, |1⟩, and any superposition as a small vector of two amplitudes",
        "Build and run your first Qiskit circuit and read measurement counts",
        "Steer a qubit to any target probability using the Rᵧ rotation gate",
    ],
    minutes=50,
))
cells.append(bootstrap_cell())

# ----------------------------------------------------------------- 1.1
cells.append(md(r"""## 1.1 From bits to qubits — the spinning coin

Let's start with what you already know. A classical **bit** is like a standard light switch: it is either **0** (off) or **1** (on). Or a coin resting on a table: **0** (heads) or **1** (tails). Or a person: alive (**1**) or dead (**0**). There is no middle ground.

Now, what if I told you a person could be both alive *and* dead at the same time? Or that a coin could be both heads *and* tails at the same time? Sounds bizarre — not possible, right?

Welcome to the world of **quantum**. Bizarre, yes — but not scary. Interesting, and beyond everyday convention.

Meet the **qubit** (quantum bit). Unlike a bit, a qubit **could** be 0, **could** be 1 — or **could** be a combination of both. Notice the word I keep stressing: **could**. It means we are *not sure yet* — the value is **undetermined**. So... how do we ever find out what it is?

Before I answer, let's play a little game. Imagine you walk into your room with a coin in your pocket. You take it out and start **spinning** it on the table. While it spins — right now, this very instant — is it heads or tails? You can't say! It's **undetermined**. So how do you find out? Simple: **slap it down!** The coin is forced to settle on one face — say, heads.

Let's slow down and recapitulate what we just did:

1. We **spun** the coin → while spinning, its face is **undetermined**. (This blend of possibilities is what quantum physicists call a **superposition** — yes, the word from this module's title. You already understand it!)
2. We **slapped** it → the coin was forced to pick exactly one face.

In the quantum world this is *exactly* what happens with a qubit. Only instead of "slapping", we use a fancier, widely used word: **measurement**. Slap = measure. Same idea, better suit."""))

# ----------------------------------------------------------------- coin widget, fair round
cells.append(exercise(1, (
    "Don't take my word for it — play! Below is the <b>Spinning Coin</b> widget. "
    "<br>1️⃣ The coin is spinning: undetermined. Click <b>Slap! (Measure)</b> and force it to pick 0 (Heads) or 1 (Tails). Spin and slap a few times — can you ever predict the outcome? "
    "<br>2️⃣ Before you click <b>Slap ×100</b>, make a prediction: what should the histogram look like after 100 slaps? <i>Now</i> click, and check yourself. "
    "<br><i>(Leave the P(Heads) slider at 50% for now — we'll come back to it in a moment.)</i>"
)))
cells.append(code('show_widget("coin-spinner")'))

cells.append(md(r"""### Let's write it down mathematically

Our coin is **fair** (unbiased): heads and tails are equally likely. And at the end of the day, quantum is math — so let's capture what the widget just showed you, using nothing more than percentages:

$$P(\text{heads}) = 50\% = \tfrac12, \qquad P(\text{tails}) = 50\% = \tfrac12$$

(Read $P(\text{heads})$ as *"the probability of heads"*.) One more small observation — the two probabilities **add up to 1**:

$$\tfrac12 + \tfrac12 = 1$$

Of course they do: when you slap the coin, it *must* land on one of the two faces. Keep this little "everything adds up to 1" rule in your pocket — it will follow us all the way to the summit.

> ✍️ **Study tip:** If the math ever feels intimidating, the best way to grab it is to grab a physical pen and write it down on paper as we go. Seriously — it works.

### Now let's bend the rules: a biased coin

Say you take your coin to a workshop and shave one side cleverly, so that heads now comes up **75%** of the time. The math becomes:

$$P(\text{heads}) = 75\% = \tfrac34, \qquad P(\text{tails}) = 25\% = \tfrac14, \qquad \tfrac34 + \tfrac14 = 1$$

Still adds up to 1 — the slapped coin still *must* land on some face. The only thing that changed is **how the certainty is shared** between the two faces.

And in the widget, the **P(Heads) slider** lets you do exactly this. No workshop needed."""))

cells.append(exercise(2, (
    "Back to the widget — this time, own the bias. "
    "<br>1️⃣ Drag <b>P(Heads)</b> to 75%. "
    "<br>2️⃣ <b>Predict first</b>: after 100 slaps, roughly how many heads? Write your guess down! "
    "<br>3️⃣ Click <b>Slap ×100</b> and compare the bars with the green prediction lines. How close was your guess? "
    "<br>4️⃣ One more experiment: find the slider settings where the coin stops being quantum and behaves exactly like a <i>classical bit</i>. (Hint: there are two of them.)"
)))
cells.append(code('show_widget("coin-spinner")'))

cells.append(md(r"""**New tool unlocked: 🧠 quick checks.** Every now and then I'll pause and ask you a small question — run the cell, click the answer you believe, and you get instant feedback. Wrong guesses cost nothing (no grades here!) and each one comes with its own hint, so click until the box turns green. Committing to an answer *before* seeing the result is where the learning happens. Try your first one:"""))
cells.append(code(
"""# Quick check — click the answer you believe. (Predict first, then peek!)
quiz.ask("m1-biased-prediction")"""))

cells.append(md(r"""Did you find the classical-bit settings? At $P(\text{heads}) = 100\%$ or $0\%$ there is no uncertainty left — every slap gives the same face. A bit is just a coin with all of its certainty piled on one side!

### From coins to qubits

Here's the punchline of this whole section: a **qubit is like a coin whose bias *you* get to choose** — any split you like, not just 50/50. A large part of quantum computing is the art of setting up these biases cleverly and then slapping (sorry — *measuring*) at the right moment.

But how do we *picture* "any split you like" for a qubit? For that, physicists use a beautiful picture called the **Bloch sphere**. Let's meet it."""))

# ----------------------------------------------------------------- 1.2
cells.append(md(r"""## 1.2 The Bloch sphere — a globe for your qubit

Picture a globe. At the **north pole** lives *"definitely 0"*. At the **south pole** lives *"definitely 1"*. A qubit state is an **arrow** from the center of the globe to a point on its surface:

- Arrow pointing straight **up** (north pole) → every measurement gives **0**. No uncertainty — a classical bit!
- Arrow pointing straight **down** (south pole) → every measurement gives **1**. Also classical!
- Arrow **tilted** anywhere in between → *undetermined*, with a bias set by the tilt.

The tilt angle has a name: $\theta$ (the Greek letter *theta*). Tilt a little away from the north pole → mostly 0 with a pinch of 1. Tilt all the way to the **equator** → the fair coin, 50/50. Tilt past the equator → mostly 1.

Play with it below — the θ slider is your new bias dial."""))

cells.append(exercise(3, (
    "Below is the <b>Bloch Sampler</b>. The arrow is a qubit state; the "
    "<b>θ slider</b> tilts it between the north pole (|0⟩) and the south pole (|1⟩). "
    "<br>1️⃣ Set θ ≈ 90° (the equator) and press <b>Measure ×1</b> a few times. Can you predict each single outcome? (Be honest — nobody can! Single outcomes are truly random; only the <i>statistics</i> are predictable.) "
    "<br>2️⃣ Now press <b>Measure ×100</b>. What shape does the histogram settle into? Where have you seen it before? "
    "<br>3️⃣ Hunt for the θ where outcome 1 appears about a <b>quarter</b> of the time — our 75/25 biased coin, reborn as a qubit! Remember that angle: you'll meet it again in Task 2."
)))
cells.append(code('show_widget("bloch-sampler")'))

cells.append(md(r"""### The math the widget was showing you

> 📐 **Don't worry about the trigonometry!**
> If the formulas below look scary, take a deep breath. We are only describing the *tilt of an arrow* with basic angles — and we'll sanity-check every formula against things you have already seen with your own eyes.

The θ slider controls the two probabilities like this:

$$P(0) = \cos^2\tfrac{\theta}{2}, \qquad P(1) = \sin^2\tfrac{\theta}{2}$$

Let's sanity-check it on paper (pen out!):

* **North pole**, $\theta = 0°$: $\cos(0°) = 1$, $\sin(0°) = 0$, so $P(0) = 1$ and $P(1) = 0$. Always 0 — just like the widget. ✔
* **Equator**, $\theta = 90°$: $\theta/2 = 45°$, and $\cos(45°) = \sin(45°) = \sqrttwo$, so $P(0) = P(1) = \tfrac12$ — the fair coin you watched settle into a 50/50 histogram. ✔ This fair-coin state is famous enough to own a name: $\ket{+}$ (*"the plus state"*). Remember it — it shows up everywhere in quantum computing.

And notice something lovely: $\cos^2 + \sin^2 = 1$ *always* (you may remember this identity from school). Our "everything adds up to 1" rule isn't an extra requirement — it's built right into the geometry of the sphere.

### The last layer: amplitudes

Time for one honest confession, and then you know everything this module needs. A qubit doesn't directly store the *probabilities* — it stores two related numbers called **amplitudes**, and the probabilities are their **squares**:

$$\underbrace{\cos\tfrac{\theta}{2}}_{\text{amplitude of } 0} \qquad \underbrace{\sin\tfrac{\theta}{2}}_{\text{amplitude of } 1} \qquad\Longrightarrow\qquad P(0) = \left(\cos\tfrac{\theta}{2}\right)^{\!2}, \quad P(1) = \left(\sin\tfrac{\theta}{2}\right)^{\!2}$$

This *"square the amplitude to get the probability"* rule is famous enough to have a name — the **Born rule**. And *"the squares of all amplitudes add up to 1"* also has a name — **normalization**. Two new words, but notice: both describe things you have already seen and checked yourself.

Physicists write a general qubit state like this (deep breath — decoding table right below):

$$\ket{\psi} = \alpha\,\ket{0} + \beta\,\ket{1}$$

> 💡 **Don't panic! Let's decode the notation piece by piece:**
> - The bar-and-bracket wrapper (as in $\ket{\psi}$ or $\ket{0}$) is called **Dirac notation**. It's just shorthand for *"this is a quantum state"* — a label wrapper, nothing more.
> - $\ket{0}$ is the state that always measures **0** (the north pole); $\ket{1}$ always measures **1** (the south pole).
> - $\alpha$ and $\beta$ (*alpha* and *beta*) are the two amplitudes — for our tilted arrow, $\alpha = \cos\tfrac{\theta}{2}$ and $\beta = \sin\tfrac{\theta}{2}$.
> - Born rule: $P(0) = |\alpha|^2$ and $P(1) = |\beta|^2$. Normalization: $|\alpha|^2 + |\beta|^2 = 1$. (The bars mean "size of the number" — for the ordinary positive amplitudes we use in this basecamp, $|\alpha|^2$ is simply $\alpha^2$.)

### Seeing states as vectors

There's one more way to write the very same thing — as a little column of the two amplitudes, top row for 0, bottom row for 1. This is called a **vector**:

$$\ket{0} = \myvector{1 \\ 0}, \qquad \ket{1} = \myvector{0 \\ 1}, \qquad \ket{\psi} = \alpha\,\ket{0} + \beta\,\ket{1} = \myvector{\alpha \\ \beta}$$

Read $\ket{0} = \myvector{1 \\ 0}$ out loud: *all* of the amplitude ($1$) sits on outcome 0, and *none* ($0$) sits on outcome 1 — definitely 0, the north pole. If you have never met vectors before, don't sweat it: for us a vector is just a tidy list of the two amplitudes.

And our 75/25 biased coin? Its probabilities are $\tfrac34$ and $\tfrac14$, so its amplitudes are the **square roots** of those: $\sqrt{\tfrac34} = \tfrac{\sqrt3}{2} \approx 0.866$ and $\sqrt{\tfrac14} = \tfrac12$. As a vector:

$$|\text{biased coin}\rangle = \myvector{\sqrt3/2 \\ 1/2}$$

Hold on to that little vector — at the end of this basecamp, you will build it on a real quantum circuit.

And now you can decode the fancy word in this module's title precisely. A **superposition** is any state whose two amplitudes are *both* nonzero — a tilted arrow, a spinning coin. **Not** *"0 and 1 at the same time"* (the coin is not showing two faces at once!) — rather, ***undetermined*, with a definite recipe of amplitudes** that fixes the statistics you'll see when you measure.

### Why amplitudes and not just probabilities?

Fair question! If amplitudes only exist to be squared, why bother with them at all? Because unlike probabilities (which are always positive), amplitudes can be **negative** — or even complex numbers. Two amplitudes can therefore *cancel each other out*, a phenomenon called **interference**. That cancellation is the secret engine behind every quantum speedup you'll meet on this ascent. For now we'll keep our amplitudes real and positive — but remember where the magic lives.

One last takeaway before we start coding: a single slap tells you almost nothing (just one 0 or one 1). It is the **statistics over many shots** that reveal the amplitudes. That is how we read quantum data!"""))

cells.append(code(
"""# Quick check — amplitudes or probabilities? This trap catches everyone once.
quiz.ask("m1-amplitude-vector")"""))

# ----------------------------------------------------------------- 1.3
cells.append(md(r"""## 1.3 Your first quantum circuit

Time to get hands-on! So far we've written qubits down on paper. But a real quantum computer doesn't take vectors as input: every qubit is born at the north pole ($\ket{0}$), and we move it around with **quantum gates** — operations that tilt and turn the arrow.

The most famous gate of all is the **Hadamard gate** ($H$): it tilts the arrow from the north pole straight down to the **equator**. In coin language: $H$ takes a coin lying flat and *sets it spinning*, perfectly fair, 50/50 — it turns $\ket{0}$ into the $\ket{+}$ state you met in §1.2.

*(For the curious: $H$ can also be written as a small matrix, $H = \hadamard$. Feel free to ignore it for now — we'll play with gate matrices properly in Basecamp 2.)*

To build circuits we'll use **Qiskit** — a free Python library that acts as our virtual quantum lab. Never seen it before? Perfect — we'll meet it **one small piece at a time**, one tiny cell per idea. Run each cell as you go, top to bottom, and watch your circuit grow step by step.

### Step 1 — import the toolbox

Like any Python library, we import the pieces we need first. Just two: `QuantumCircuit` for *building* circuits, and `AerSimulator` for *running* them (we'll use that one a little later)."""))
cells.append(code(
"""# Let's import the necessary tools first — just run me!
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator"""))

cells.append(md(r"""### Step 2 — create a circuit (gather your coin)

A **quantum circuit** is the recipe we hand to the quantum computer: which qubits to prepare, which gates to apply, and when to measure. It is read **left to right**, like sheet music.

Creating one takes a single line. The number in the parentheses is simply *how many qubits we want* — and every one of them is born fresh at the north pole, $\ket{0}$:"""))
cells.append(code(
"""# Let's create our circuit — the 1 means "give me 1 qubit" (one coin, lying flat at |0>).
qc = QuantumCircuit(1)

# Let's draw it — one lonely qubit wire, waiting for instructions.
qc.draw(output="mpl")"""))

cells.append(md(r"""### Step 3 — apply the Hadamard gate (start the spin)

Gates are applied one line at a time. `qc.h(0)` means "*apply the $H$ gate to qubit number 0*".

Wait — why 0 and not 1? Python counts from **zero**, so our first (and only) qubit is qubit number **0**. Run the cell and compare the drawing with the one above — your circuit just grew an $H$ box:"""))
cells.append(code(
"""# Let's apply the Hadamard gate to qubit 0 — the way you would start the coin spinning.
qc.h(0)

# Let's draw it again — an H box has appeared on the wire.
qc.draw(output="mpl")"""))

cells.append(md(r"""### Step 4 — add the measurement (the slap!)

One thing is still missing: the slap. `measure_all()` measures **every** qubit in the circuit and writes each answer down.

Written down *where*? A slapped coin shows a plain, ordinary 0 or 1 — that's a **classical bit**, exactly the light-switch kind from §1.1. So measuring automatically adds a classical bit to the circuit to hold the result. In the drawing you'll see it as the **double-line wire** at the bottom, and the little dial symbol is the measurement itself:"""))
cells.append(code(
"""# Let's add the measurement — the slap! The result lands in a classical bit.
qc.measure_all()

# Let's admire the finished circuit: prepare, spin, slap — read left to right.
qc.draw(output="mpl")"""))

cells.append(md(r"""☝️ **A tiny gotcha before you move on:** Steps 2–4 all add onto the *same* circuit `qc`. If you accidentally run Step 3 twice, the drawing will show **two** $H$ boxes. No harm done — just re-run from Step 2 (it hands you a brand-new circuit) down to here, and the drawing will look right again."""))

cells.append(code(
"""# Quick check — can you read your own circuit drawing?
quiz.ask("m1-double-wire")"""))

cells.append(md(r"""### Worked example: running a circuit on the simulator

Your circuit is built — but it hasn't *run* yet. Before we run *our* circuit, let's learn the running-a-circuit syntax on the most boring circuit imaginable: **no gates at all**. The coin is never spun — it just lies there showing 0. So — predict it before you run it! — every single shot must come out `0`.

Read each comment, then the line below it. Task 1 will ask you to do this for the *spinning* coin:"""))
cells.append(code(
"""# Let's build the most boring circuit imaginable: a qubit we never touch.
qc_boring = QuantumCircuit(1)
qc_boring.measure_all()

# Let's create the simulator — our virtual lab bench.
sim = AerSimulator()

# Let's run the circuit 100 times (each repetition is called a "shot").
job = sim.run(qc_boring, shots=100)

# Let's collect the finished results...
result = job.result()

# ...and tally them into a dictionary: {outcome: how many times it appeared}.
counts_boring = result.get_counts()
print(counts_boring)

# Bonus: this is what the course's green light looks like when statistics check out.
checkers.check_counts_close(counts_boring, {"0": 1.0})"""))

# ----------------------------------------------------------------- task 1
cells.append(task(1, (
    "Now build the spinning-coin circuit <b>yourself</b> — the same three "
    "moves you just watched: create a one-qubit circuit, apply the Hadamard "
    "gate, and add the measurement. Everything below the steps is plumbing "
    "you don't need to touch: it runs your circuit for <b>1024 shots</b> and "
    "checks the statistics. <br><i>Before you run it:</i> predict — out of "
    "1024 slaps of a fair coin, roughly how many '0's do you expect? Exactly "
    "that number, or just close? (The checker uses a chi-square test, so "
    "honest shot noise passes but a wrong circuit fails.)"
)))
cells.append(code(
"""# Let's initialize your circuit — one qubit, fresh at |0> (gather your coin).
### BEGIN SOLUTION
qc_spin = QuantumCircuit(1)
### END SOLUTION
### STUDENT SAFETY: qc_spin = None  # remove None and define your circuit

# Let's apply the Hadamard gate — start the coin spinning.
### BEGIN SOLUTION
qc_spin.h(0)
### END SOLUTION

# Let's add the measurement — the slap!
### BEGIN SOLUTION
qc_spin.measure_all()
### END SOLUTION

# Nothing to change below — press Run: 1024 shots, tallied and checked.
counts = checkers.run_and_tally(qc_spin, shots=1024)
checkers.check_counts_close(counts, {"0": 0.5, "1": 0.5})"""))
cells.append(analysis(r"""You did **not** get exactly 512/512 — and that's the
point. Each shot is an independent Born-rule sample, so the counts fluctuate
like 1024 honest coin flips (standard deviation $\approx \sqrt{1024 \cdot \tfrac12 \cdot \tfrac12} = 16$).
This is why every quantum result you'll ever report is *statistics over
shots*, and why the checker asks "is this consistent with 50/50?" rather than
"is this exactly 50/50?". Run the cell again — you'll get slightly different
counts, same verdict."""))

# ----------------------------------------------------------------- 1.4
cells.append(md(r"""## 1.4 Steering the amplitudes: the $R_y$ gate

The Hadamard gate always lands on the equator — always the fair coin. But you biased a coin to 75/25 with a *slider* in §1.1. Where's the slider for a circuit?

Meet the $R_y(\theta)$ gate: *"rotate the arrow by angle $\theta$"*. It is literally the θ slider from the Bloch Sampler, in gate form:

$$R_y(\theta)\ket{0} = \cos\tfrac{\theta}{2}\,\ket{0} + \sin\tfrac{\theta}{2}\,\ket{1}$$

Want a specific probability of measuring 1? Just solve $\sin^2\tfrac{\theta}{2} = P(1)$ for $\theta$, and rotate by that. *Choosing an angle to get a chosen distribution* — hold on to this idea: later, near the Summit, we'll watch variational algorithms tune rotation angles automatically until the statistics spit out the answer to a hard problem.

One more tool first. Instead of estimating probabilities from thousands of shots, Qiskit can compute a circuit's exact amplitude pair directly — this is called the circuit's **statevector**. The checkers below use it, so you get an exact verdict with no shot noise.

### Worked example: $R_y$ at the equator

Everything below is complete — nothing to fill in. Run it: we rotate by $\theta = \pi/2$ (that's 90°, remember the equator?), and the checker confirms we've rebuilt our old friend $\ket{+}$, this time with a gate. This green light is also what success looks like in Task 2:"""))
cells.append(code(
"""# Let's import NumPy — we only need it for the number pi.
import numpy as np

# Let's create a fresh one-qubit circuit — a new coin in your hand.
qc_fair = QuantumCircuit(1)

# Let's choose the fair-coin angle: 90 degrees. (Qiskit angles are in radians.)
theta_fair = np.pi / 2

# Let's apply the rotation — the arrow tilts down to the equator.
qc_fair.ry(theta_fair, 0)

# Let's check the exact state: |+> again — a green PASS is expected here.
checkers.check_statevector(qc_fair, targets.M1_PLUS)"""))

# ----------------------------------------------------------------- task 2
cells.append(task(2, (
    "The grand finale: prepare our 75/25 biased-coin state <b>on a circuit</b> "
    "— the little vector (√3/2, 1/2) from §1.2, and the same state you hunted "
    "with the θ slider in Exercise 3. Start from the worked example and "
    "change one number: the angle. <br><i>Paper first:</i> solve "
    "sin²(θ/2) = 1/4 for θ (hint: which angle has a sine of 1/2?), then "
    "write it in radians."
)))
cells.append(code(
"""# Let's create a fresh one-qubit circuit — a new coin in your hand.
qc3 = QuantumCircuit(1)

# Let's choose the rotation angle so that P(1) becomes 1/4.
# The line below currently holds the FAIR-coin angle (pi/2) — change it!
theta = np.pi / 2
### BEGIN SOLUTION
theta = np.pi / 3               # sin^2(theta/2) = 1/4  =>  theta/2 = pi/6
### END SOLUTION

# Nothing to change below — we apply your rotation and check the exact state.
qc3.ry(theta, 0)
checkers.check_statevector(qc3, targets.M1_TASK2)"""))
cells.append(analysis(r"""Let's break down the math step-by-step to see how we got that angle:
1. We want the probability of getting a 1 to be $1/4$, so:
   $$P(1) = \sin^2\tfrac{\theta}{2} = \tfrac14$$
2. Taking the square root of both sides gives:
   $$\sin\tfrac{\theta}{2} = \tfrac12$$
3. What angle has a sine of $1/2$? That is $30^\circ$ (or $\pi/6$ radians):
   $$\tfrac{\theta}{2} = \tfrac{\pi}{6}$$
4. Multiplying by 2 gives our rotation angle $\theta$:
   $$\theta = \tfrac{\pi}{3} \approx 1.047 \text{ radians (or } 60^\circ \text{)}$$
   (This is the ≈ 60° angle you found with the slider in Exercise 3!)

Plugging it back into the $R_y$ formula, the circuit prepares:
$$\cos\tfrac{\pi}{6}\ket{0} + \sin\tfrac{\pi}{6}\ket{1} = \tfrac{\sqrt3}{2}\ket{0} + \tfrac12\ket{1} = \myvector{\sqrt3/2 \\ 1/2}$$

— *exactly* the little vector from §1.2. One coin, three costumes: a slider position, a vector of amplitudes, and now a circuit. And in every costume: amplitudes $\rightarrow$ squares $\rightarrow$ probabilities. Once that chain feels automatic, you're officially thinking in quantum."""))

# ----------------------------------------------------------------- analogy
cells.append(analogy_callout(
    "superposition and measurement",
    (
        "I'm learning quantum computing. Explain superposition and measurement "
        "using an analogy from MY background: [YOUR HOBBY/FIELD HERE].\n\n"
        "Ground rules — your analogy MUST respect these facts:\n"
        "1) A qubit state is two amplitudes (α, β), complex numbers with "
        "|α|²+|β|²=1. It is NOT 'both 0 and 1 at once' — it is undetermined "
        "until measured, like a spinning coin before it is slapped down.\n"
        "2) Measurement gives outcome 0 with probability |α|² and 1 with "
        "probability |β|² (Born rule), and the state then collapses to that "
        "outcome — the slap that forces one face.\n"
        "3) Amplitudes can be negative/complex and can cancel (interference); "
        "probabilities cannot.\n"
        "4) One measurement reveals almost nothing; statistics over many "
        "shots reveal the amplitudes.\n\n"
        "End by telling me where the analogy breaks down."
    ),
))

# ----------------------------------------------------------------- claim code
cells.append(md(r"""## 🎓 Log your climb — claim your completion code

You built the 75/25 biased coin three ways and verified each one. Now let's make
it count on the mountain! Run the cell below: it re-checks your **Task 1** and
**Task 2** circuits right here in this kernel and — if they pass — prints a
personal **completion code**.

Copy that code into the **“Log your notebook”** box on the
[Basecamp 1 page](https://quantum-ascent-77617.web.app/module.html?id=01#claim)
to light up this camp on your Ascent map and bank your climber XP. Finishing the
notebook is the one thing the website can't verify for you — so it's the one
thing you get to prove. 🏔️"""))
cells.append(code("progress.claim_basecamp_1(qc_spin, qc3)"))

# ----------------------------------------------------------------- footer
cells.append(basecamp_footer(
    1,
    summary=(
        "You began with a spinning coin and ended by steering a real quantum "
        "state: you built the same 75/25 biased coin as a slider setting, a "
        "vector of amplitudes, and an $R_y$ circuit you aimed yourself — "
        "predicting the statistics before every run. Prediction before "
        "simulation, every time: that's the mountaineer's discipline."
    ),
    quiz_url="https://quantum-ascent-77617.web.app/module.html?id=01#quiz",
    next_label="Basecamp 2: Gates & Circuits — where rotations compose and phases start to matter",
    solutions_relpath="solutions/01_qubits_and_superposition_solutions.ipynb",
))

write_notebook(
    cells,
    REPO / "notebooks" / "solutions" / "01_qubits_and_superposition_solutions.ipynb",
)
