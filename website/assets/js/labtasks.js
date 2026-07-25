/* Quantum Ascent — the browser track's graded tasks.
   ==================================================

   Twelve tasks, two per basecamp, mirroring the notebook tasks one-for-one.
   Finishing both tasks in a basecamp mints the SAME completion code the
   notebook prints, so the two tracks are genuinely equivalent — a learner who
   never installs Python still lights up the same Ascent map.

   Every task carries:
     - `predict`  a question answered BEFORE running anything. The course asks
                  "predict first" ~20 times and never used to capture it; here
                  the answer is recorded in the Prediction Ledger so the
                  learner ends the course with a calibration report instead of
                  a vague memory of having guessed.
     - `hints`    a three-rung ladder: intuition -> strategy -> near-answer.
                  "Stuck" must have an exit that is not "copy the solution".
     - `check`    a real physics check against the exact state, never a string
                  match on the circuit. Any circuit that produces the required
                  physics passes, because the physics is the learning outcome.
     - `why`      what the checker says when it fails — diagnosing the specific
                  predicted mistake, not just reporting "wrong".

   Task kinds:
     "circuit"  build a circuit that satisfies a physical condition
     "numeric"  answer with a number (tolerance-checked)
     "params"   tune named sliders that drive a generated circuit
*/
"use strict";

var LabTasks = (function () {

  var DEG = Math.PI / 180;
  var near = function (a, b, tol) { return Math.abs(a - b) <= tol; };

  /* Probability of a given bitstring, using Qiskit's label order. */
  function pOf(state, label) {
    var p = QSim.probabilities(state);
    for (var i = 0; i < p.length; i++) if (QSim.label(i, state.n) === label) return p[i];
    return 0;
  }

  /* --------------------------------------------------------------- BC 1 */
  var BC1 = [
    {
      id: "01-1",
      title: "Build a fair coin",
      brief:
        "Your qubit starts at <b>|0⟩</b> — completely determined, a coin lying flat on heads. " +
        "Place <b>one gate</b> that leaves it genuinely undetermined: an exact 50/50 between " +
        "0 and 1.<br><br>Watch the two bars on the right as you do it. When they are exactly " +
        "half and half, you have a spinning coin — <i>not</i> a coin that is somehow both faces " +
        "at once, but one whose face is not yet a fact.",
      builder: { n: 1, lockQubits: true, allowed: ["H", "X", "Z", "RY"] },
      predict: {
        topic: "shot noise",
        q: "Before you place anything — after you build the fair coin and measure it 100 times, how many 0s do you expect?",
        options: ["Exactly 50, every single time", "Around 50 — a bit different each run", "Anything at all: quantum results are pure chaos"],
        answer: 1,
        feedback: [
          "Not quite — 100 flips of a fair coin is almost never exactly 50 heads. The <i>probability</i> is exactly 0.5; the <i>tally</i> wanders.",
          "Exactly right. The probability is exactly 0.5, but 100 samples of it scatter around 50 (typically ±10). That scatter is shot noise, not error.",
          "Not chaos — the distribution is precisely known. It is each individual outcome that is not."
        ]
      },
      hints: [
        "You want to go from 'definitely heads' to 'genuinely undecided'. Which gate in the palette is the one that <i>creates</i> an even split out of a definite state?",
        "The Hadamard gate <b>H</b> takes |0⟩ to an equal mix of |0⟩ and |1⟩. Its amplitudes are both 1/√2 ≈ 0.707, and 0.707² = 0.5 — that is the Born rule giving you the 50%.",
        "Click <b>H</b> in the palette, then click the q0 wire. In Qiskit that single line is <code>qc.h(0)</code>."
      ],
      check: function (c, st) {
        var p0 = QSim.probabilities(st)[0];
        if (near(p0, 0.5, 1e-6)) return { ok: true, msg: "That is a fair coin: P(0) = P(1) = 50%, exactly." };
        if (c.ops.length === 0) return { ok: false, msg: "The circuit is still empty — the qubit is sitting at |0⟩ with P(0) = 100%." };
        return { ok: false, msg: "Not yet — you are at P(0) = " + (100 * p0).toFixed(1) + "%, and a fair coin needs exactly 50.0%." };
      }
    },
    {
      id: "01-2",
      title: "Build a 75/25 qubit",
      brief:
        "Now make a <b>loaded</b> coin: P(0) = 75%, P(1) = 25%.<br><br>" +
        "Use <b>RY(θ)</b>. The rule you need is <b>P(1) = sin²(θ/2)</b> — take the angle, halve " +
        "it, take the sine, square it. Notice the angle slider shows you degrees <i>and</i> " +
        "radians, because Qiskit thinks in radians and most humans think in degrees.",
      builder: { n: 1, lockQubits: true, allowed: ["RY", "H", "X"] },
      predict: {
        topic: "the half-angle rule",
        q: "You need sin²(θ/2) = 0.25, so sin(θ/2) = 0.5. What is θ?",
        options: ["30°", "60°", "120°"],
        answer: 1,
        feedback: [
          "Careful — that is the <i>half</i>-angle. sin(30°) = 0.5, so θ/2 = 30° and θ is twice that.",
          "Yes. sin(θ/2) = 0.5 means θ/2 = 30°, so θ = 60° — which is π/3 radians.",
          "Too far — sin(60°) = 0.866, and 0.866² = 0.75, so 120° would put P(1) at 75%, not 25%."
        ]
      },
      hints: [
        "You are solving for an angle. Start from what you want — P(1) = 0.25 — and work backwards through the squaring and the sine.",
        "sin²(θ/2) = 0.25 → sin(θ/2) = 0.5 → θ/2 = 30° → θ = 60°. The classic slip is stopping at 30°: that is the half-angle, not the angle.",
        "Select <b>RY(θ)</b>, drag the angle slider to <b>60°</b> (the chip beside it will read π/3 rad), then click the q0 wire. In Qiskit: <code>qc.ry(np.pi/3, 0)</code>."
      ],
      check: function (c, st) {
        var p = QSim.probabilities(st), p1 = p[1];
        if (near(p1, 0.25, 0.004)) return { ok: true, msg: "P(0) = 75.0%, P(1) = 25.0%. That is sin²(30°) = 1/4, exactly as designed." };
        if (near(p1, 0.75, 0.02)) return { ok: false, msg: "You have it upside down: P(1) = 75%, not 25%. You are one half-angle too far — try 60°, not 120°." };
        if (near(p1, 0.0670, 0.01)) return { ok: false, msg: "That is θ = 30°, which gives P(1) = sin²(15°) ≈ 6.7%. 30° is the <i>half</i>-angle — double it." };
        return { ok: false, msg: "Not yet — you are at P(1) = " + (100 * p1).toFixed(1) + "%, and you want 25.0%." };
      }
    }
  ];

  /* --------------------------------------------------------------- BC 2 */
  var BC2 = [
    {
      id: "02-1",
      title: "Prove that H·Z·H = X",
      brief:
        "The X gate is the quantum NOT: it turns a definite |0⟩ into a definite |1⟩. " +
        "But it is not fundamental — you can <b>build</b> it.<br><br>" +
        "Using only <b>H</b> and <b>Z</b> (there is no X in this palette), get the qubit from " +
        "|0⟩ to |1⟩ with 100% certainty. Three gates will do it.",
      builder: { n: 1, lockQubits: true, allowed: ["H", "Z", "S", "T"] },
      predict: {
        topic: "phase & interference",
        q: "Z alone leaves P(0) and P(1) completely unchanged. So why can a sandwich of H and Z flip the qubit?",
        options: [
          "Z secretly does change the probabilities, just by a small amount",
          "Z changes the sign of the |1⟩ part — invisible on its own, but H converts that sign into a probability",
          "Three gates in a row always flip a qubit"
        ],
        answer: 1,
        feedback: [
          "No — Z genuinely changes no probability. Run Z alone and watch the bars refuse to move.",
          "Exactly. Phase is real physics that is simply invisible to a measurement <i>right now</i>. H is the gate that converts a phase difference into a probability difference — which is how interference works.",
          "Not in general — try H, H, H and see."
        ]
      },
      hints: [
        "Z does nothing visible to a qubit sitting at |0⟩. So Z cannot go first and cannot go last usefully — something has to put the qubit somewhere Z can act on.",
        "Put the qubit into a superposition first, flip the sign of the |1⟩ half, then fold it back. That is H, then Z, then H.",
        "Place <b>H</b>, then <b>Z</b>, then <b>H</b> again on q0. In Qiskit: <code>qc.h(0); qc.z(0); qc.h(0)</code>."
      ],
      check: function (c, st) {
        var p1 = QSim.probabilities(st)[1];
        if (near(p1, 1, 1e-9)) return { ok: true, msg: "P(1) = 100%. You just built the NOT gate out of a phase flip and two Hadamards — that is interference doing real work." };
        if (c.ops.length === 0) return { ok: false, msg: "Still empty — the qubit is at |0⟩." };
        if (near(p1, 0.5, 0.01)) return { ok: false, msg: "You are at 50/50: the qubit is in superposition but has not been folded back. You need a final H to turn that phase into a certainty." };
        if (near(p1, 0, 1e-9)) return { ok: false, msg: "P(1) is still 0%. If you used H and H with no Z between them, the two Hadamards simply undid each other." };
        return { ok: false, msg: "Not yet — P(1) = " + (100 * p1).toFixed(1) + "%, and you need 100%." };
      }
    },
    {
      id: "02-2",
      title: "The endianness trap",
      brief:
        "Two qubits. Make the register read exactly <b>|10⟩</b> — that is the bitstring " +
        "<code>10</code> with 100% certainty.<br><br>" +
        "Read that bitstring carefully. Qiskit writes the <b>highest-numbered qubit on the " +
        "left</b>, so <code>10</code> means q1 = 1 and q0 = <b>0</b>. Almost everyone flips a " +
        "gate onto the wrong wire the first time. That is the point of this task.",
      builder: { n: 2, lockQubits: true, allowed: ["X", "H", "Z"] },
      predict: {
        topic: "Qiskit endianness",
        q: "To get the bitstring <code>10</code>, which qubit needs the X gate?",
        options: ["q0", "q1"],
        answer: 1,
        feedback: [
          "That is the trap. X on q0 gives you the bitstring <code>01</code>, because q0 is the <i>rightmost</i> character.",
          "Correct — and if that felt backwards, you have just met the single most common Qiskit bug in the wild."
        ]
      },
      hints: [
        "Write the target bitstring out with labels underneath it: the left character belongs to q1, the right character belongs to q0. Which one is the 1?",
        "<code>10</code> means q1 = 1 and q0 = 0. So exactly one X gate is needed, and it goes on the wire that is <i>not</i> q0.",
        "Select <b>X</b> and click the <b>q1</b> wire (the top row). In Qiskit: <code>qc.x(1)</code>."
      ],
      check: function (c, st) {
        if (near(pOf(st, "10"), 1, 1e-9)) return { ok: true, msg: "|10⟩ with certainty. You put the gate on q1 and got the bitstring 10 — you now read Qiskit's ordering correctly." };
        if (near(pOf(st, "01"), 1, 1e-9)) return { ok: false, msg: "You landed on <code>01</code> — the mirror image. You flipped q0, but the 1 in <code>10</code> belongs to q1. This is the endianness trap, and catching it here is exactly the point." };
        if (c.ops.length === 0) return { ok: false, msg: "Still empty — the register reads <code>00</code>." };
        return { ok: false, msg: "Not there yet — P(<code>10</code>) is only " + (100 * pOf(st, "10")).toFixed(1) + "%. You want it at 100%, with no superposition left." };
      }
    }
  ];

  /* --------------------------------------------------------------- BC 3 */
  var BC3 = [
    {
      id: "03-1",
      title: "Make a Bell pair",
      brief:
        "Build the state <b>(|00⟩ + |11⟩)/√2</b>: a 50/50 split between <code>00</code> and " +
        "<code>11</code>, with <code>01</code> and <code>10</code> at exactly zero.<br><br>" +
        "Two gates. When you have it, open the <b>Observables</b> tab: each qubit on its own " +
        "reads P(1) = 50%, yet the pair always agrees. That combination is entanglement.",
      builder: { n: 2, lockQubits: true, allowed: ["H", "X", "Z", "CX", "CZ"] },
      predict: {
        topic: "entanglement",
        q: "Once it is built, you measure q0 alone and get 0. What will q1 give?",
        options: ["0, always", "1, always", "0 or 1, still a coin flip"],
        answer: 0,
        feedback: [
          "Right. The outcomes are perfectly correlated — but notice that neither qubit had a value <i>before</i> the measurement. Correlation, not communication.",
          "That would be the other Bell state, Ψ⁺. This one, Φ⁺, agrees rather than disagrees.",
          "Not once they are entangled — that is exactly what makes this state different from two separate coins."
        ]
      },
      hints: [
        "You need one qubit to become undetermined, and then the second one to copy whatever the first turns out to be. Two different gates, in that order.",
        "H on q0 makes it a fair coin. CNOT with q0 as control and q1 as target then flips q1 exactly when q0 is 1 — so the two always match.",
        "Place <b>H</b> on q0, then select <b>CNOT</b>, click <b>q0</b> (the control), then <b>q1</b> (the target). In Qiskit: <code>qc.h(0); qc.cx(0, 1)</code>."
      ],
      check: function (c, st) {
        var p00 = pOf(st, "00"), p11 = pOf(st, "11"), p01 = pOf(st, "01"), p10 = pOf(st, "10");
        if (near(p00, 0.5, 1e-6) && near(p11, 0.5, 1e-6)) return { ok: true, msg: "A Bell pair. ⟨ZZ⟩ = +1 (they always agree) while each qubit alone is a perfect 50/50 coin — correlated without either one having a value in advance." };
        if (near(p01, 0.5, 1e-6) && near(p10, 0.5, 1e-6)) return { ok: false, msg: "You built Ψ⁺ = (|01⟩+|10⟩)/√2 — entangled, but <i>anti</i>-correlated. Close! Remove the extra flip so the two qubits agree instead of disagree." };
        if (near(p00, 0.25, 0.01)) return { ok: false, msg: "All four outcomes are at 25% — that is two independent coins, not an entangled pair. You have superposed both qubits separately instead of linking them with a CNOT." };
        if (c.ops.length === 0) return { ok: false, msg: "Still empty — the register sits at |00⟩." };
        return { ok: false, msg: "Not yet: P(00) = " + (100 * p00).toFixed(1) + "%, P(11) = " + (100 * p11).toFixed(1) + "%. You want 50% and 50%, with nothing on 01 or 10." };
      }
    },
    {
      id: "03-2",
      title: "The anti-correlated twin",
      brief:
        "Now build <b>Ψ⁺ = (|01⟩ + |10⟩)/√2</b> — the pair that always <i>disagrees</i>.<br><br>" +
        "Start from what you just built and add one more gate. Then check the Observables tab: " +
        "⟨ZZ⟩ should read <b>−1</b> instead of +1. That single sign is the whole difference " +
        "between 'always the same' and 'always opposite'.",
      builder: { n: 2, lockQubits: true, allowed: ["H", "X", "Z", "CX", "CZ"] },
      predict: {
        topic: "no-signalling",
        q: "Alice holds q0 and Bob holds q1, and they walk light-years apart. Alice measures. Can Bob tell — from his own results alone — that she did?",
        options: ["Yes: his qubit jumps to the opposite value the instant she looks", "No: his outcomes stay 50/50 whatever Alice does"],
        answer: 1,
        feedback: [
          "This is the most popular myth in quantum computing. Bob's own histogram is 50/50 before Alice measures and 50/50 after. He learns nothing until he receives her result over an ordinary, slower-than-light channel.",
          "Exactly — and that is why entanglement cannot send a message. The correlation is only visible once the two lists of results are brought together and compared."
        ]
      },
      hints: [
        "You already know how to make the pair that always agrees. Turning 'always agrees' into 'always disagrees' means flipping one of them — before or after the link, either works.",
        "Take H on q0, CNOT from q0 to q1, then flip one wire with X. (Flipping before the CNOT works too — try both and see that they give the same state.)",
        "Place <b>H</b> on q0, <b>CNOT</b> q0→q1, then <b>X</b> on q1. In Qiskit: <code>qc.h(0); qc.cx(0, 1); qc.x(1)</code>."
      ],
      check: function (c, st) {
        var p01 = pOf(st, "01"), p10 = pOf(st, "10");
        var zz = QSim.expectation(st, "ZZ");
        if (near(p01, 0.5, 1e-6) && near(p10, 0.5, 1e-6)) return { ok: true, msg: "Ψ⁺ built: ⟨ZZ⟩ = −1, so the two qubits always disagree — and each one alone is still a fair coin. Nothing here can carry a signal." };
        if (near(zz, 1, 0.01)) return { ok: false, msg: "⟨ZZ⟩ is still +1 — that is the agreeing pair Φ⁺ from the last task. You need one extra flip on one of the wires." };
        if (c.ops.length === 0) return { ok: false, msg: "Still empty — start from the Bell pair you just built." };
        return { ok: false, msg: "Not yet: P(01) = " + (100 * p01).toFixed(1) + "%, P(10) = " + (100 * p10).toFixed(1) + "%. You want 50/50 across those two, and zero on 00 and 11." };
      }
    }
  ];

  /* --------------------------------------------------------------- BC 4 */
  var BC4 = [
    {
      id: "04-1",
      title: "Dial an expectation value",
      brief:
        "⟨Z⟩ is the <b>average</b> of a measurement that only ever returns +1 (for outcome 0) " +
        "or −1 (for outcome 1). So ⟨Z⟩ = P(0) − P(1): it runs from +1 down to −1, and no single " +
        "shot ever lands on the average itself.<br><br>" +
        "Tune <b>RY(θ)</b> until <b>⟨Z⟩ = 0.500</b>. Watch the live readout below the state.",
      builder: { n: 1, lockQubits: true, allowed: ["RY", "H", "X"] },
      objective: {
        label: "⟨Z⟩",
        fn: function (st) { var z = QSim.expectation(st, "Z"); return { value: z, text: z.toFixed(3) }; }
      },
      predict: {
        topic: "expectation values",
        q: "If ⟨Z⟩ = 0.5, what is P(0)?",
        options: ["50%", "75%", "25%"],
        answer: 1,
        feedback: [
          "That would give ⟨Z⟩ = 0.5 − 0.5 = 0, not 0.5.",
          "Right: ⟨Z⟩ = P(0) − P(1) and P(0) + P(1) = 1, so P(0) = (1 + 0.5)/2 = 0.75.",
          "That is the other way round — P(0) = 25% gives ⟨Z⟩ = 0.25 − 0.75 = −0.5."
        ]
      },
      hints: [
        "⟨Z⟩ = P(0) − P(1), and the two probabilities add to 1. Solve those two facts together for P(0).",
        "P(0) = 0.75. And from Basecamp 1 you know P(1) = sin²(θ/2) — so you need sin²(θ/2) = 0.25, an angle you have already found once.",
        "This is the same 60° state as Basecamp 1's loaded coin: <b>RY at 60°</b> on q0. <code>qc.ry(np.pi/3, 0)</code>."
      ],
      check: function (c, st) {
        var z = QSim.expectation(st, "Z");
        if (near(z, 0.5, 0.005)) return { ok: true, msg: "⟨Z⟩ = 0.500. Note that no individual shot ever returns 0.5 — it returns +1 or −1, and only the average lands where you aimed." };
        if (near(z, -0.5, 0.02)) return { ok: false, msg: "You have the sign backwards: ⟨Z⟩ = −0.5 means P(1) = 75%. Rotate the other way (or by less)." };
        return { ok: false, msg: "⟨Z⟩ is currently " + z.toFixed(3) + " — you want +0.500." };
      }
    },
    {
      id: "04-2",
      title: "The cost Hamiltonian's favourite state",
      brief:
        "Max-Cut runs on one observable: <b>⟨ZZ⟩</b>. It reads <b>+1</b> when two qubits agree " +
        "and <b>−1</b> when they disagree — so 'cut this edge' means 'drive ⟨ZZ⟩ to −1'.<br><br>" +
        "Build any two-qubit state with <b>⟨ZZ⟩ = −1</b>. There is more than one right answer, " +
        "and finding a second one is worth your time.",
      builder: { n: 2, lockQubits: true, allowed: ["H", "X", "Z", "CX", "CZ", "RY"] },
      objective: {
        label: "⟨ZZ⟩",
        fn: function (st) { var v = QSim.expectation(st, "ZZ"); return { value: v, text: v.toFixed(3) }; }
      },
      predict: {
        topic: "cost Hamiltonians",
        q: "Which of these gives ⟨ZZ⟩ = −1?",
        options: ["|00⟩", "|01⟩", "Both |00⟩ and |11⟩"],
        answer: 1,
        feedback: [
          "|00⟩ has both qubits agreeing, so ⟨ZZ⟩ = (+1)(+1) = +1.",
          "Yes — the bits disagree, so ⟨ZZ⟩ = (+1)(−1) = −1. In Max-Cut language, that edge is cut.",
          "Both of those have the qubits agreeing, which gives +1 in each case."
        ]
      },
      hints: [
        "⟨ZZ⟩ = −1 means the two qubits <i>never</i> come out the same. What is the simplest state where they always differ?",
        "A single X on one wire gives |01⟩, and the bits disagree in every shot — that is already ⟨ZZ⟩ = −1. The entangled Ψ⁺ from Basecamp 3 also works, which is worth noticing: ⟨ZZ⟩ cannot tell them apart.",
        "Select <b>X</b> and click the q0 wire: <code>qc.x(0)</code>. Then try building Ψ⁺ instead (H, CNOT, X) and watch ⟨ZZ⟩ read −1 for that too."
      ],
      check: function (c, st) {
        var v = QSim.expectation(st, "ZZ");
        if (near(v, -1, 1e-6)) return { ok: true, msg: "⟨ZZ⟩ = −1.000: the two qubits disagree in every single shot. That is one cut edge, and it is the entire building block of the Summit." };
        if (near(v, 1, 0.01)) return { ok: false, msg: "⟨ZZ⟩ = +1 — your qubits always agree. You need them to always differ." };
        if (near(v, 0, 0.05)) return { ok: false, msg: "⟨ZZ⟩ ≈ 0 means they agree half the time — an uncorrelated pair. You need them anti-correlated every time, not on average." };
        return { ok: false, msg: "⟨ZZ⟩ is " + v.toFixed(3) + " — drive it to exactly −1.000." };
      }
    }
  ];

  /* --------------------------------------------------------------- BC 5 */
  var BC5 = [
    {
      id: "05-1",
      title: "Descend to the ground state",
      brief:
        "Here is a real Hamiltonian: <b>H = Z + 0.5·X</b>. Its energy for the state RY(θ)|0⟩ is " +
        "<b>E(θ) = cos θ + 0.5·sin θ</b>.<br><br>" +
        "You are the optimizer. Drag θ until the energy is as low as you can get it — you need " +
        "<b>E ≤ −1.11</b>. Go slowly near the bottom and notice how <i>flat</i> the curve " +
        "becomes: that flatness is exactly what makes an optimizer's job hard.",
      kind: "params",
      params: [{ name: "theta", label: "θ", min: 0, max: 360, step: 1, value: 90, unit: "°" }],
      circuit: function (v) { return { n: 1, ops: [{ g: "RY", q: 0, p: v.theta * DEG }] }; },
      objective: {
        label: "Energy ⟨H⟩",
        fn: function (st) {
          var e = QSim.expectationSum(st, [["Z", 1], ["X", 0.5]]);
          return { value: e, text: e.toFixed(4) };
        }
      },
      predict: {
        topic: "the variational bound",
        q: "The lowest energy any state can have here is −√1.25 ≈ −1.118. Could a cleverer ansatz beat that?",
        options: ["Yes, with enough parameters", "No — never, for any state at all"],
        answer: 1,
        feedback: [
          "No ansatz can. This is the variational theorem: the ground energy is a hard floor set by the Hamiltonian itself, not by your circuit.",
          "Correct. ⟨ψ|H|ψ⟩ ≥ E₀ for every state ψ. A better ansatz gets you closer to the floor; nothing gets you through it."
        ]
      },
      hints: [
        "Both terms matter. cos θ is most negative at 180°, but 0.5·sin θ is <i>positive</i> there — so the true minimum sits a little past 180°.",
        "Minimise cos θ + 0.5 sin θ by setting the derivative to zero: −sin θ + 0.5 cos θ = 0, so tan θ = 0.5. The solution in the right half of the circle is θ = 180° + 26.57°.",
        "Drag θ to about <b>207°</b>. The energy bottoms out at −1.1180, which is −√1.25."
      ],
      check: function (c, st) {
        var e = QSim.expectationSum(st, [["Z", 1], ["X", 0.5]]);
        if (e <= -1.11) return { ok: true, msg: "E = " + e.toFixed(4) + ", against a true ground energy of −1.1180. You just ran a VQE by hand — that is all an optimizer does, only faster." };
        if (e <= -1.0) return { ok: false, msg: "E = " + e.toFixed(4) + " — close. The curve is very flat down here, so keep nudging: the floor is at −1.1180." };
        if (e > 0) return { ok: false, msg: "E = " + e.toFixed(4) + ", which is above zero — you are climbing, not descending. Try angles past 180°." };
        return { ok: false, msg: "E = " + e.toFixed(4) + ". Keep going: you need −1.11 or lower." };
      }
    },
    {
      id: "05-2",
      title: "Name the floor",
      brief:
        "You just found the bottom of one particular curve. The variational theorem says that " +
        "bottom is not an accident of your ansatz — it is the <b>ground-state energy</b> of the " +
        "Hamiltonian, and no state of any kind can go below it.<br><br>" +
        "For <b>H = Z + 0.5·X</b>, that floor is <b>−√(1² + 0.5²)</b>. Work it out and enter it " +
        "below, to three decimal places.",
      kind: "numeric",
      answer: -1.118,
      tol: 0.002,
      placeholder: "e.g. -1.234",
      predict: {
        topic: "non-commuting observables",
        q: "Why is the floor −√(1² + 0.5²) rather than just −1 − 0.5 = −1.5?",
        options: [
          "Because Z and X do not commute — they cannot both be maximally negative at once",
          "Because 0.5 is only counted half the time",
          "It is an approximation; −1.5 is the exact answer"
        ],
        answer: 0,
        feedback: [
          "Exactly. Z and X are incompatible observables, so no state makes both terms simultaneously as negative as possible. The compromise is the vector length, √(1²+0.5²).",
          "Not quite — the coefficient applies always, not sometimes. The real reason is that Z and X cannot be minimised at the same time.",
          "The other way round: −1.118 is exact, and −1.5 is unreachable."
        ]
      },
      hints: [
        "You are being asked for a number you can compute with a calculator: the negative square root of a sum of two squares.",
        "1² = 1 and 0.5² = 0.25, so you want −√1.25.",
        "√1.25 = 1.1180…, so the answer is <b>−1.118</b>."
      ]
    }
  ];

  /* --------------------------------------------------------------- BC 6 */
  var TRIANGLE = [[0, 1], [1, 2], [0, 2]];
  var C5 = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]];

  function cutObjective(edges, n) {
    return {
      label: "Expected cut ⟨C⟩",
      fn: function (st) {
        var p = QSim.probabilities(st), acc = 0;
        for (var i = 0; i < p.length; i++) acc += p[i] * QSim.cutValue(edges, i, n);
        return { value: acc, text: acc.toFixed(3) + " of " + edges.length + " edges" };
      }
    };
  }

  var BC6 = [
    {
      id: "06-1",
      title: "The triangle you cannot cut",
      brief:
        "Three towns, three roads: <b>0–1, 1–2, 0–2</b>. Split them into two groups so that as " +
        "many roads as possible run <i>between</i> the groups.<br><br>" +
        "Each qubit is one town: <b>|0⟩ = group A, |1⟩ = group B</b>. Place <b>X</b> gates to " +
        "assign towns to group B, and watch the cut counter. Get it as high as it will go — " +
        "then notice where it stops.",
      builder: { n: 3, lockQubits: true, allowed: ["X"] },
      objective: cutObjective(TRIANGLE, 3),
      predict: {
        topic: "graph frustration",
        q: "Three roads, two groups. How many roads can you cut at best?",
        options: ["All 3", "2", "1"],
        answer: 1,
        feedback: [
          "It feels like it should be 3 — but try it. With only two groups and three mutually connected towns, two towns must always end up together.",
          "Correct, and this is the key idea of the whole Summit: the <i>best possible</i> answer still leaves an edge uncut. That is a property of the problem, not a failure of the algorithm.",
          "You can do better than 1 — try putting exactly one town on its own."
        ]
      },
      hints: [
        "Try the obvious thing first: put one town in group B and leave two in group A. Count the roads that now run between groups.",
        "Any split of three towns into two groups leaves at least two towns together — and the road between <i>those</i> two can never be cut. So 2 is the ceiling.",
        "Place a single <b>X</b> on any one wire — say q0. Two of the three roads are now cut, and no arrangement does better."
      ],
      check: function (c, st) {
        var p = QSim.probabilities(st), acc = 0;
        for (var i = 0; i < p.length; i++) acc += p[i] * QSim.cutValue(TRIANGLE, i, 3);
        if (near(acc, 2, 1e-6)) return { ok: true, msg: "Two of three roads cut — and that is the true maximum. A triangle is an odd cycle, so one edge always survives. Remember this when QAOA reports a ratio below 1: sometimes the problem, not the algorithm, is the limit." };
        if (acc > 2.0001) return { ok: false, msg: "That reads above 2, which should be impossible for a triangle — please report this." };
        if (near(acc, 0, 1e-6)) return { ok: false, msg: "All three towns are in the same group, so no road is cut. Move one of them across." };
        return { ok: false, msg: "You are cutting " + acc.toFixed(0) + " road" + (acc == 1 ? "" : "s") + ". Two is reachable — try a different split." };
      }
    },
    {
      id: "06-2",
      title: "Summit: run QAOA on a 5-cycle",
      brief:
        "Five towns in a ring: <b>0–1–2–3–4–0</b>. Five roads, and because the ring is odd, the " +
        "best possible cut is <b>4 of 5</b> — again, not all of them.<br><br>" +
        "Below is a real <b>QAOA</b> circuit: Hadamards to consider every split at once, an " +
        "<b>RZZ</b> cost layer that rewards cut edges, and an <b>RX</b> mixer that lets " +
        "solutions move. You are the classical optimizer — tune <b>γ₁</b> and <b>β₁</b> until the " +
        "expected cut reaches <b>3.7 or better</b>.<br><br>" +
        "Then raise <b>depth p</b> to 2. A second layer brings its <i>own</i> pair of angles — " +
        "that is what depth actually buys you — and with four dials the ratio can reach a full " +
        "<b>1.000</b>. Re-tune all four and see.",
      kind: "params",
      params: [
        { name: "gamma1", label: "γ₁ (cost)", min: 0, max: 360, step: 1, value: 60, unit: "°" },
        { name: "beta1", label: "β₁ (mixer)", min: 0, max: 360, step: 1, value: 60, unit: "°" },
        { name: "p", label: "depth p", min: 1, max: 2, step: 1, value: 1, unit: "" },
        { name: "gamma2", label: "γ₂ (cost)", min: 0, max: 360, step: 1, value: 30, unit: "°",
          showIf: function (v) { return v.p >= 2; } },
        { name: "beta2", label: "β₂ (mixer)", min: 0, max: 360, step: 1, value: 165, unit: "°",
          showIf: function (v) { return v.p >= 2; } }
      ],
      /* Each layer carries its own (gamma, beta). Sharing one pair across both
         layers looks tidier but caps the ratio at 0.962 on this graph, which
         would make the "depth reaches the optimum" lesson a lie. Independent
         angles are also what real QAOA does. */
      circuit: function (v) {
        var ops = [], q;
        var g = [v.gamma1, v.gamma2], b = [v.beta1, v.beta2];
        for (q = 0; q < 5; q++) ops.push({ g: "H", q: q });
        for (var layer = 0; layer < v.p; layer++) {
          for (var e = 0; e < C5.length; e++)
            ops.push({ g: "RZZ", q: C5[e][0], t: C5[e][1], p: 2 * g[layer] * DEG });
          for (q = 0; q < 5; q++) ops.push({ g: "RX", q: q, p: 2 * b[layer] * DEG });
        }
        return { n: 5, ops: ops };
      },
      objective: cutObjective(C5, 5),
      predict: {
        topic: "approximation & depth",
        q: "A random guess cuts 2.5 edges on average, and the true maximum is 4. What do you expect the best p=1 QAOA to reach?",
        options: ["Exactly 4 — it finds the optimum", "Somewhere between: better than random, short of perfect", "Below 2.5 — QAOA needs deeper circuits to beat guessing"],
        answer: 1,
        feedback: [
          "Not at p = 1. One layer is not enough on this graph — which is precisely why the 'A' in QAOA stands for Approximate.",
          "Exactly right. The best p = 1 result is about 3.75 out of 4 — a real gain over guessing, and a real shortfall from optimal. Depth is what closes the gap.",
          "One layer already beats random guessing comfortably. The question is by how much, not whether."
        ]
      },
      hints: [
        "Move γ₁ first with β₁ held still, and watch the cut readout rise and fall — you are hand-drawing a slice through the energy landscape. Then do the same with β₁. Most of the range is bad; a narrow band is good.",
        "Good p = 1 angles for this ring live near <b>γ₁ ≈ 67°, β₁ ≈ 113°</b> — and, by symmetry, near γ₁ ≈ 113°, β₁ ≈ 67° too. That gets you ⟨C⟩ ≈ 3.75, which is ratio 0.937 and <i>not</i> the optimum.",
        "For the full 1.000, set <b>p = 2</b> and use <b>γ₁ = 105°, β₁ = 148°, γ₂ = 32°, β₂ = 165°</b>. Four dials instead of two is exactly what the extra layer bought you."
      ],
      check: function (c, st) {
        var p = QSim.probabilities(st), acc = 0;
        for (var i = 0; i < p.length; i++) acc += p[i] * QSim.cutValue(C5, i, 5);
        var ratio = acc / 4;
        if (acc >= 3.99) return {
          ok: true,
          msg: "⟨C⟩ = " + acc.toFixed(3) + " — approximation ratio " + ratio.toFixed(3) + ". You reached the " +
               "true optimum, and you did it by adding depth rather than by searching harder. Note what that " +
               "cost: twice the circuit, twice the parameters. On a real device, depth costs noise — which is " +
               "why choosing p is a genuine engineering decision and not just 'turn it up'. 🏔️"
        };
        if (acc >= 3.7) return {
          ok: true,
          msg: "⟨C⟩ = " + acc.toFixed(3) + " of a maximum 4 — approximation ratio " + ratio.toFixed(3) +
               ". You beat random guessing (2.5) by a wide margin without ever enumerating all 32 splits, " +
               "and you fell short of perfect. Both halves of that sentence are the lesson. " +
               "Now set <b>p = 2</b>, tune all four angles, and see the ratio reach 1.000."
        };
        if (acc <= 2.5) return { ok: false, msg: "⟨C⟩ = " + acc.toFixed(3) + ", which is no better than guessing at random (2.5). Sweep γ₁ across its full range — most of it is bad, and a narrow band is good." };
        return { ok: false, msg: "⟨C⟩ = " + acc.toFixed(3) + " (ratio " + ratio.toFixed(3) + "). Better than random — keep tuning, you need 3.7." };
      }
    }
  ];

  var BY_MODULE = { "01": BC1, "02": BC2, "03": BC3, "04": BC4, "05": BC5, "06": BC6 };

  return {
    forModule: function (id) { return BY_MODULE[id] || []; },
    all: BY_MODULE,
    graphs: { triangle: TRIANGLE, c5: C5 }
  };
})();

if (typeof module !== "undefined" && module.exports) module.exports = LabTasks;
