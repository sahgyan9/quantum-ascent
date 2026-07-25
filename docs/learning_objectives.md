# Learning Objectives

By the end of the **Quantum Ascent** course, climbers will transition from theoretical intuition to active quantum algorithm developers. The curriculum is mapped across six structured basecamps:

---

### Basecamp 1: The Qubit & Superposition
* **Cognitive Goals:**
  * Explain the concept of superposition and describe a qubit mathematically as a normalized 2D vector in a 2-state space.
  * Formulate measurement outcomes using the Born Rule ($P = |\text{amplitude}|^2$) and differentiate between pre-measurement amplitudes and post-measurement collapses.
* **Skill Outcomes:**
  * Calculate probability distributions and sample measurement counts for basic state vectors.
  * Operate the Bloch Sampler widget to visualize how state vectors map to exact probabilities through proportional color segments.

---

### Basecamp 2: Gates & Circuits
* **Cognitive Goals:**
  * Describe quantum gates as unitary matrix operations that rotate state vectors on the Bloch sphere.
  * Identify how angles map to probabilities through $\sin^2$ and $\cos^2$ curves.
  * Explain Qiskit's unique right-to-left tensor endianness convention to avoid indexing traps.
* **Skill Outcomes:**
  * Assemble quantum circuits in Qiskit using $X$, $Z$, $H$, and $RY(\theta)$ gates.
  * Predict final state vector coefficients after series gate transformations.

---

### Basecamp 3: Entanglement
* **Cognitive Goals:**
  * Construct multi-qubit state vectors using Kronecker/tensor products.
  * Explain the concept of quantum entanglement and define the four Bell states.
  * Distinguish *correlation* from *communication*: show that a Bell pair's outcomes are
    perfectly correlated while each qubit's own marginal stays 50/50 — so entanglement
    carries no signal (the no-signalling argument, done by hand).
* **Skill Outcomes:**
  * Program circuits that entangle two qubits (H + CNOT) and read the resulting
    four-amplitude state vector.
  * Use the Entanglement Explorer widget to measure one half of a Bell pair repeatedly and
    watch the partner's outcome become determined — without either marginal ever budging.

---

### Basecamp 4: Hamiltonians & Energy
* **Cognitive Goals:**
  * Define observables as Hermitian operators and state their relation to measurement outcomes.
  * Explain how expectation values $\langle H \rangle$ represent average energy measurements over many shots.
  * Represent complex physical observables using Pauli strings (linear combinations of $I, X, Y, Z$).
* **Skill Outcomes:**
  * Construct expectation value estimators in Python using Qiskit's `SparsePauliOp`.
  * Compute expected values mathematically and simulate them under noisy shot counts.

---

### Basecamp 5: The Variational Principle
* **Cognitive Goals:**
  * Explain the Variational Quantum Eigensolver (VQE) algorithm's core theorem: the expectation value of any ansatz state is bounded below by the ground-state energy.
  * Read a one-parameter energy landscape: locate the minimum, and explain why a flat region
    of the curve makes an optimizer's job harder.
* **Skill Outcomes:**
  * Implement parameterized quantum circuits (ansatz) that dynamically alter their states based on numerical angle parameters.
  * Wire an expectation-value estimator to a classical optimizer (SciPy's COBYLA) and watch it
    descend to the ground-state energy.

---

### Basecamp 6: Summit — QAOA for Max-Cut
* **Cognitive Goals:**
  * Map combinatoric graph optimization problems (specifically Max-Cut) to diagonal Ising spin Hamiltonians.
  * Differentiate the Roles of Mixer Hamiltonians ($U_M$) and Cost Hamiltonians ($U_C$) in the Quantum Approximate Optimization Algorithm (QAOA).
  * Calculate the approximation ratio to judge algorithm success.
* **Skill Outcomes:**
  * Build a full QAOA circuit end-to-end, execute optimizations, and retrieve the binary bitstrings representing the optimal cuts.
  * Graph cuts and evaluate performance metrics dynamically on graph structures.
