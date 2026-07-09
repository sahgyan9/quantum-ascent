/* Quantum Ascent — the single source of truth for concept definitions.
   Used by the Analogy Studio and the glossary hover-cards.
   Every "rules" entry is a precise physical fact, reviewed against the
   corresponding notebook's math. Edit with care: accuracy > catchiness. */
"use strict";

const CONCEPTS = {
  superposition: {
    title: "superposition and measurement",
    module: "01",
    oneLiner: "A qubit holds two complex amplitudes that only become a definite 0 or 1 when measured.",
    rules: [
      "A qubit state is two amplitudes (α, β) — complex numbers with |α|²+|β|²=1. It is NOT 'both 0 and 1 at once'.",
      "Measurement gives outcome 0 with probability |α|² and 1 with probability |β|² (the Born rule), and the state then collapses to that outcome.",
      "Amplitudes can be negative or complex and can cancel each other (interference); probabilities cannot.",
      "One measurement reveals almost nothing; statistics over many shots reveal the amplitudes.",
    ],
  },
  born_rule: {
    title: "the Born rule and shot statistics",
    module: "01",
    oneLiner: "Probabilities are the squared magnitudes of amplitudes, revealed only through repeated measurements.",
    rules: [
      "The probability of an outcome is the squared magnitude of its amplitude: P(x) = |amplitude of x|².",
      "Each run ('shot') of a quantum circuit gives one random outcome sampled from this distribution.",
      "Finite samples fluctuate: 1024 shots of a 50/50 state will NOT give exactly 512/512, and that is expected, not an error.",
      "Quantum algorithms are designed so the answer is readable from these statistics.",
    ],
  },
  quantum_gates: {
    title: "quantum gates as rotations",
    module: "02",
    oneLiner: "Gates are reversible rotations of the state vector — they redistribute amplitudes without ever 'reading' the qubit.",
    rules: [
      "A gate is a unitary (reversible, length-preserving) transformation of the amplitudes — a rotation of the state vector.",
      "Gates never produce randomness by themselves; all randomness enters at measurement.",
      "Every gate has an exact inverse: running a circuit backwards (with each gate inverted) undoes it perfectly.",
      "The Hadamard gate maps |0⟩ to an equal superposition — it is a fixed rotation, not a 'randomizer'.",
    ],
  },
};

/* Node-friendly export so tests can validate the definitions. */
if (typeof module !== "undefined") module.exports = { CONCEPTS };
