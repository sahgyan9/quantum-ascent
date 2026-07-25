/* Quantum Ascent — QSim: an exact statevector simulator in plain JavaScript.
   =========================================================================

   WHY THIS EXISTS
   ---------------
   The course's biggest drop-off was the Colab round-trip: five context switches
   and a 60–90 second `pip install` *before* the learner sees anything rewarding.
   Qiskit cannot run in a browser — since 1.0 its core is compiled Rust, and Aer
   is C++ — so "just run Qiskit in WASM" is not available to us.

   But we do not need Qiskit to be *correct*. For the <= 5 qubits this course
   ever uses, a dense statevector is at most 32 complex numbers, and exact
   simulation is a few dozen lines. So the browser track runs real, exact
   quantum mechanics — not an animation of it, and not an approximation.

   CONTRACTS THIS FILE PROMISES (all pinned by tests/test_qsim.py, which runs
   this exact file under Node and compares against Qiskit + Aer):

   1. EXACTNESS. Amplitudes are computed, never faked. A student who gets a
      number here gets the same number Qiskit gives, to 1e-12.

   2. QISKIT ENDIANNESS. Qubit 0 is the LEAST significant bit, and bitstrings
      print as q[n-1]...q[1]q[0]. This is the single most notorious beginner
      trap in Qiskit, and Basecamp 2 teaches it deliberately. A browser track
      that quietly used the opposite convention would teach the trap backwards,
      so we match Qiskit exactly — including in the bitstring key order of
      sample() counts.

   3. NO DEPENDENCIES. Pure ES5-compatible JS, no imports, no build step. Works
      from a file:// URL with the network unplugged.

   State representation: { n, re: Float64Array(2^n), im: Float64Array(2^n) }.
   Complex amplitudes are kept even though the course keeps every amplitude
   real and non-negative — because RZ, S, T and RZZ genuinely need phase, and a
   simulator that silently dropped it would be a lie we'd have to explain later.
*/
"use strict";

var QSim = (function () {

  /* ------------------------------------------------------------------ state */

  /** |00…0>, the state every circuit starts in. */
  function zeroState(n) {
    var size = 1 << n;
    var st = { n: n, re: new Float64Array(size), im: new Float64Array(size) };
    st.re[0] = 1;
    return st;
  }

  function cloneState(st) {
    return { n: st.n, re: Float64Array.from(st.re), im: Float64Array.from(st.im) };
  }

  /* ------------------------------------------------------------------ gates */

  /* A single-qubit gate is [a, b, c, d] with each entry [re, im]:
         | a  b |
         | c  d |
     Applying it to qubit q pairs up every basis state that differs only in
     bit q, and mixes that pair. Bit q is (1 << q) because qubit 0 is the low
     bit (contract 2). */
  function applyGate1(st, q, m) {
    var size = 1 << st.n, bit = 1 << q;
    var a = m[0], b = m[1], c = m[2], d = m[3];
    for (var i = 0; i < size; i++) {
      if (i & bit) continue;               // visit each pair once, from its 0-side
      var j = i | bit;
      var x0r = st.re[i], x0i = st.im[i];
      var x1r = st.re[j], x1i = st.im[j];
      st.re[i] = a[0] * x0r - a[1] * x0i + b[0] * x1r - b[1] * x1i;
      st.im[i] = a[0] * x0i + a[1] * x0r + b[0] * x1i + b[1] * x1r;
      st.re[j] = c[0] * x0r - c[1] * x0i + d[0] * x1r - d[1] * x1i;
      st.im[j] = c[0] * x0i + c[1] * x0r + d[0] * x1i + d[1] * x1r;
    }
    return st;
  }

  var R2 = Math.SQRT1_2;

  var GATES = {
    I: [[1, 0], [0, 0], [0, 0], [1, 0]],
    X: [[0, 0], [1, 0], [1, 0], [0, 0]],
    Y: [[0, 0], [0, -1], [0, 1], [0, 0]],
    Z: [[1, 0], [0, 0], [0, 0], [-1, 0]],
    H: [[R2, 0], [R2, 0], [R2, 0], [-R2, 0]],
    S: [[1, 0], [0, 0], [0, 0], [0, 1]],
    SDG: [[1, 0], [0, 0], [0, 0], [0, -1]],
    T: [[1, 0], [0, 0], [0, 0], [R2, R2]]
  };

  /* Rotations follow Qiskit's convention exactly: RY(θ) = exp(-i θ Y / 2), so
     RY(θ)|0> = cos(θ/2)|0> + sin(θ/2)|1>. That identity is the backbone of
     Basecamp 1 (P(1) = sin²(θ/2)), so it has to be right. */
  function rx(t) {
    var c = Math.cos(t / 2), s = Math.sin(t / 2);
    return [[c, 0], [0, -s], [0, -s], [c, 0]];
  }
  function ry(t) {
    var c = Math.cos(t / 2), s = Math.sin(t / 2);
    return [[c, 0], [-s, 0], [s, 0], [c, 0]];
  }
  function rz(t) {
    return [[Math.cos(t / 2), -Math.sin(t / 2)], [0, 0],
            [0, 0], [Math.cos(t / 2), Math.sin(t / 2)]];
  }

  /** Controlled-NOT: flip `target` in every basis state where `control` is 1. */
  function applyCX(st, control, target) {
    var size = 1 << st.n, cb = 1 << control, tb = 1 << target;
    for (var i = 0; i < size; i++) {
      if (!(i & cb)) continue;
      if (i & tb) continue;                // swap each pair once
      var j = i ^ tb;
      var tr = st.re[i], ti = st.im[i];
      st.re[i] = st.re[j]; st.im[i] = st.im[j];
      st.re[j] = tr; st.im[j] = ti;
    }
    return st;
  }

  /** Controlled-Z (symmetric): phase of -1 when both qubits are 1. */
  function applyCZ(st, a, b) {
    var size = 1 << st.n, ab = (1 << a) | (1 << b);
    for (var i = 0; i < size; i++) {
      if ((i & ab) === ab) { st.re[i] = -st.re[i]; st.im[i] = -st.im[i]; }
    }
    return st;
  }

  /* RZZ(θ) = exp(-i θ/2 · Z⊗Z). Diagonal, so it only rephases amplitudes:
     basis states where the two bits AGREE get exp(-iθ/2) (ZZ eigenvalue +1),
     states where they DISAGREE get exp(+iθ/2) (eigenvalue -1). This is the
     cost-layer unitary of QAOA, and the sign convention matters — get it
     backwards and the optimizer climbs instead of descends. */
  function applyRZZ(st, a, b, theta) {
    var size = 1 << st.n, ab = 1 << a, bb = 1 << b;
    for (var i = 0; i < size; i++) {
      var same = (!!(i & ab)) === (!!(i & bb));
      var ang = same ? -theta / 2 : theta / 2;
      var c = Math.cos(ang), s = Math.sin(ang);
      var r = st.re[i], m = st.im[i];
      st.re[i] = r * c - m * s;
      st.im[i] = r * s + m * c;
    }
    return st;
  }

  /* -------------------------------------------------------- circuit runner */

  /* A circuit is a plain array of ops — deliberately data, not code, so the
     same description can be built by a click in the Lab, typed as Qiskit-style
     text, stored in a task definition, or checked by a test.
         { g: "H",   q: 0 }
         { g: "RY",  q: 0, p: 1.047 }
         { g: "CX",  q: 0, t: 1 }
         { g: "RZZ", q: 0, t: 1, p: 0.8 }                                    */
  function run(n, ops) {
    var st = zeroState(n);
    for (var i = 0; i < (ops || []).length; i++) apply(st, ops[i]);
    return st;
  }

  function apply(st, op) {
    var g = String(op.g || "").toUpperCase();
    if (g === "CX" || g === "CNOT") return applyCX(st, op.q, op.t);
    if (g === "CZ") return applyCZ(st, op.q, op.t);
    if (g === "RZZ") return applyRZZ(st, op.q, op.t, op.p);
    if (g === "RX") return applyGate1(st, op.q, rx(op.p));
    if (g === "RY") return applyGate1(st, op.q, ry(op.p));
    if (g === "RZ") return applyGate1(st, op.q, rz(op.p));
    if (g === "BARRIER" || g === "MEASURE") return st;   // no-ops for the sim
    if (GATES[g]) return applyGate1(st, op.q, GATES[g]);
    throw new Error("QSim: unknown gate '" + op.g + "'");
  }

  /* ------------------------------------------------- probabilities & shots */

  /** Born rule, exactly: P(basis state i) = |amplitude_i|². */
  function probabilities(st) {
    var size = 1 << st.n, p = new Float64Array(size);
    for (var i = 0; i < size; i++) p[i] = st.re[i] * st.re[i] + st.im[i] * st.im[i];
    return p;
  }

  /** Basis label for index i, in Qiskit's order: q[n-1]…q[1]q[0]. */
  function label(i, n) {
    var s = "";
    for (var q = n - 1; q >= 0; q--) s += (i >> q) & 1;
    return s;
  }

  /** Probability that qubit q reads 1 (its marginal — the no-signalling check). */
  function marginal1(st, q) {
    var p = probabilities(st), bit = 1 << q, acc = 0;
    for (var i = 0; i < p.length; i++) if (i & bit) acc += p[i];
    return acc;
  }

  /* Sample `shots` measurements. Returns a counts object keyed by bitstring,
     exactly like Qiskit's result.get_counts(). `rng` is injectable so tests
     (and the "same seed, same climb" reproducibility story) can be
     deterministic. */
  function sample(st, shots, rng) {
    rng = rng || Math.random;
    var p = probabilities(st), n = st.n, counts = {};
    var cum = new Float64Array(p.length), acc = 0;
    for (var i = 0; i < p.length; i++) { acc += p[i]; cum[i] = acc; }
    for (var s = 0; s < shots; s++) {
      var r = rng() * acc, lo = 0, hi = p.length - 1;
      while (lo < hi) { var mid = (lo + hi) >> 1; if (r > cum[mid]) lo = mid + 1; else hi = mid; }
      var k = label(lo, n);
      counts[k] = (counts[k] || 0) + 1;
    }
    return counts;
  }

  /** A small deterministic PRNG (mulberry32) so a lesson can be reproducible. */
  function seededRng(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* --------------------------------------------------- expectation values */

  /* <ψ|P|ψ> for a Pauli string like "ZZ", "IX", "ZIZ".
     The string is written in Qiskit's order (leftmost char = highest qubit
     index), so SparsePauliOp("ZI") and expectation(st, "ZI") mean the same
     operator — a learner can move between tracks without a silent sign flip.

     Method: rotate X and Y terms into the Z basis (H for X, S†then H for Y),
     then every Pauli string is diagonal and the expectation is just a signed
     sum of probabilities. Exact, no sampling. */
  function expectation(st, pauli) {
    var n = st.n;
    if (pauli.length !== n) throw new Error("QSim: Pauli string length must equal qubit count");
    var w = cloneState(st);
    var mask = 0;
    for (var c = 0; c < n; c++) {
      var ch = pauli[pauli.length - 1 - c].toUpperCase();   // char for qubit c
      if (ch === "I") continue;
      mask |= 1 << c;
      if (ch === "X") applyGate1(w, c, GATES.H);
      else if (ch === "Y") { applyGate1(w, c, GATES.SDG); applyGate1(w, c, GATES.H); }
      else if (ch !== "Z") throw new Error("QSim: bad Pauli character '" + ch + "'");
    }
    var p = probabilities(w), acc = 0;
    for (var i = 0; i < p.length; i++) acc += p[i] * parity(i & mask);
    return acc;
  }

  /** +1 for an even number of set bits, -1 for odd. */
  function parity(x) {
    var v = x, c = 0;
    while (v) { c ^= 1; v &= v - 1; }
    return c ? -1 : 1;
  }

  /** Expectation of a weighted sum of Pauli strings: [["Z",1],["X",0.5]]. */
  function expectationSum(st, terms) {
    var acc = 0;
    for (var i = 0; i < terms.length; i++) acc += terms[i][1] * expectation(st, terms[i][0]);
    return acc;
  }

  /* ------------------------------------------------------ Max-Cut helpers */

  /* Cut value of an assignment: how many edges have their endpoints in
     different groups. `bits` may be a bitstring (Qiskit order) or an integer. */
  function cutValue(edges, bits, n) {
    var v = typeof bits === "string" ? parseInt(bits, 2) : bits;
    if (typeof bits === "string") {          // re-index: leftmost char = qubit n-1
      v = 0;
      for (var k = 0; k < bits.length; k++) {
        if (bits[bits.length - 1 - k] === "1") v |= 1 << k;
      }
    }
    var cut = 0;
    for (var e = 0; e < edges.length; e++) {
      var a = (v >> edges[e][0]) & 1, b = (v >> edges[e][1]) & 1;
      if (a !== b) cut++;
    }
    return cut;
  }

  /* Brute-force maximum cut. Only ever called on the tiny graphs this course
     uses, and it exists so the learner can SEE the true optimum next to what
     QAOA found — which is the whole point of the word "Approximate". */
  function maxCut(edges, n) {
    var best = -1, argbest = [];
    for (var v = 0; v < (1 << n); v++) {
      var c = cutValue(edges, v, n);
      if (c > best) { best = c; argbest = [label(v, n)]; }
      else if (c === best) argbest.push(label(v, n));
    }
    return { value: best, assignments: argbest };
  }

  /* ------------------------------------------------------------ formatting */

  /** Human-readable ket, dropping negligible amplitudes. Real-and-positive
      amplitudes print bare, so Basecamp 1 never has to explain a phase. */
  function ketString(st, digits) {
    digits = digits == null ? 3 : digits;
    var p = probabilities(st), out = [];
    for (var i = 0; i < p.length; i++) {
      if (p[i] < 1e-9) continue;
      var re = st.re[i], im = st.im[i], term;
      if (Math.abs(im) < 1e-9) term = re.toFixed(digits);
      else if (Math.abs(re) < 1e-9) term = im.toFixed(digits) + "i";
      else term = "(" + re.toFixed(digits) + (im < 0 ? "-" : "+") + Math.abs(im).toFixed(digits) + "i)";
      out.push(term + "|" + label(i, st.n) + "⟩");
    }
    return out.length ? out.join(" + ") : "0";
  }

  return {
    zeroState: zeroState, cloneState: cloneState, run: run, apply: apply,
    applyGate1: applyGate1, applyCX: applyCX, applyCZ: applyCZ, applyRZZ: applyRZZ,
    gates: GATES, rx: rx, ry: ry, rz: rz,
    probabilities: probabilities, marginal1: marginal1, label: label,
    sample: sample, seededRng: seededRng,
    expectation: expectation, expectationSum: expectationSum,
    cutValue: cutValue, maxCut: maxCut, ketString: ketString
  };
})();

/* Node (tests) and browser (widgets) both get it. */
if (typeof module !== "undefined" && module.exports) module.exports = QSim;
