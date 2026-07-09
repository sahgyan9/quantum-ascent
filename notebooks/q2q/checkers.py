"""Self-check functions for course tasks.

Design rules (Don Norman feedback principle):
- Every check renders an unmissable green PASS or red FAIL box with a diagnostic,
  never a bare AssertionError traceback wall.
- Failures include a *hint* that coaches toward the fix.
- Failures still raise CheckError (an AssertionError subclass) so that
  "Restart & Run All" and pytest fail hard on wrong answers.
- Measurement-count checks use a chi-square test so honest shot noise never
  fails a correct answer.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "CheckError",
    "check_statevector",
    "check_counts_close",
    "check_unitary_equiv",
    "check_expectation",
    "check_optimum",
    "check_maxcut_solution",
]


class CheckError(AssertionError):
    """Raised when a self-check fails (after friendly feedback is shown)."""


# ---------------------------------------------------------------- rendering

def _in_ipython() -> bool:
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except ImportError:
        return False


def _show(html: str, text: str) -> None:
    if _in_ipython():
        from IPython.display import HTML, display
        display(HTML(html))
    else:
        print(text)


def _pass(msg: str) -> None:
    _show(
        f'<div style="border-left:5px solid #2ecc71;background:#eafaf1;'
        f'color:#145a32;padding:10px 14px;border-radius:4px;font-size:14px">'
        f'✅ <b>Correct!</b> {msg}</div>',
        f"✅ Correct! {msg}",
    )


def _fail(msg: str, hint: str = "") -> None:
    hint_html = f'<br><b>Hint:</b> {hint}' if hint else ""
    hint_txt = f"\n   Hint: {hint}" if hint else ""
    _show(
        f'<div style="border-left:5px solid #e74c3c;background:#fdedec;'
        f'color:#78281f;padding:10px 14px;border-radius:4px;font-size:14px">'
        f'❌ <b>Not yet.</b> {msg}{hint_html}</div>',
        f"❌ Not yet. {msg}{hint_txt}",
    )
    raise CheckError(msg)


# ---------------------------------------------------------------- helpers

def _to_vector(state) -> np.ndarray:
    """Accept a qiskit Statevector, QuantumCircuit, list, or ndarray."""
    try:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector
        if isinstance(state, QuantumCircuit):
            state = Statevector(state)
        if isinstance(state, Statevector):
            return np.asarray(state.data, dtype=complex)
    except ImportError:
        pass
    return np.asarray(state, dtype=complex).ravel()


def _fmt_vec(v: np.ndarray) -> str:
    return "[" + ", ".join(f"{a.real:+.3f}{a.imag:+.3f}j" for a in v) + "]"


# ---------------------------------------------------------------- checkers

def check_statevector(state, expected, tol: float = 1e-6) -> None:
    """Check a state equals the expected one, ignoring global phase.

    ``state``/``expected`` may be a Statevector, QuantumCircuit, list or array.
    """
    v = _to_vector(state)
    w = _to_vector(expected)
    if v.shape != w.shape:
        _fail(
            f"Your state has {v.size} amplitudes but {w.size} were expected.",
            "Check the number of qubits: n qubits means 2^n amplitudes.",
        )
    norm = np.linalg.norm(v)
    if abs(norm - 1.0) > 1e-6:
        _fail(
            f"Your state is not normalized: its length is {norm:.4f}, but a valid "
            f"quantum state must have length exactly 1.",
            "The squared magnitudes of all amplitudes must sum to 1. "
            "Did you forget a factor of 1/sqrt(2)?",
        )
    fidelity = abs(np.vdot(w / np.linalg.norm(w), v)) ** 2
    if fidelity < 1.0 - tol:
        _fail(
            f"Your state {_fmt_vec(v)} does not match the expected state "
            f"{_fmt_vec(w)} (fidelity = {fidelity:.4f}, want 1.0). "
            f"Global phase is already forgiven, so this is a real difference.",
            "Write out the amplitudes for each basis state by hand and compare "
            "term by term.",
        )
    _pass(f"State matches the target (fidelity = {fidelity:.6f}).")


def check_counts_close(counts, expected_probs, alpha: float = 1e-3) -> None:
    """Chi-square test that measurement ``counts`` match ``expected_probs``.

    ``counts``: dict bitstring -> shots (as from Result.get_counts()).
    ``expected_probs``: dict bitstring -> ideal probability.
    Passes unless the disagreement is statistically significant (p < alpha),
    so honest shot noise never fails a correct circuit.
    """
    from scipy import stats

    counts = dict(counts)
    shots = sum(counts.values())
    if shots == 0:
        _fail("No shots found in counts.", "Did you run the circuit and call get_counts()?")

    impossible = {k: v for k, v in counts.items()
                  if expected_probs.get(k, 0.0) == 0.0 and v > 0}
    if impossible:
        seen = ", ".join(f"'{k}' ({v} shots)" for k, v in impossible.items())
        _fail(
            f"You measured outcomes that should be impossible for the correct "
            f"circuit: {seen}.",
            "An outcome with probability 0 should never appear. Check your gates "
            "and remember Qiskit orders bitstrings with qubit 0 rightmost.",
        )

    keys = sorted(expected_probs)
    observed = np.array([counts.get(k, 0) for k in keys], dtype=float)
    expected = np.array([expected_probs[k] * shots for k in keys], dtype=float)
    # merge tiny expected bins into the largest to keep chi-square valid
    small = expected < 5
    if small.any() and (~small).any():
        big = int(np.argmax(expected))
        observed[big] += observed[small].sum()
        expected[big] += expected[small].sum()
        observed, expected = observed[~small], expected[~small]
    if len(observed) < 2:
        _pass(f"Counts are consistent with the expected distribution ({shots} shots).")
        return
    chi2, p = stats.chisquare(observed, expected)
    if p < alpha:
        obs_probs = {k: counts.get(k, 0) / shots for k in keys}
        table = " | ".join(
            f"'{k}': got {obs_probs[k]:.3f}, want {expected_probs[k]:.3f}" for k in keys
        )
        _fail(
            f"Your measurement statistics are too far from the expected "
            f"distribution (chi-square p = {p:.2e}). {table}",
            "If the shape looks close, increase shots. If an outcome is missing "
            "or swapped, re-check gate order and endianness.",
        )
    _pass(f"Counts are consistent with the expected distribution "
          f"(p = {p:.3f} across {shots} shots).")


def check_unitary_equiv(circuit, expected, tol: float = 1e-6) -> None:
    """Check a circuit implements ``expected`` up to global phase.

    ``expected`` may be a QuantumCircuit, qiskit Operator, or unitary matrix.
    """
    from qiskit.quantum_info import Operator

    U = Operator(circuit).data
    if isinstance(expected, (list, np.ndarray)):
        V = np.asarray(expected, dtype=complex)
    else:  # QuantumCircuit, Operator, or Gate
        V = Operator(expected).data
    if U.shape != V.shape:
        _fail(
            f"Your circuit acts on a {U.shape[0]}-dimensional space but the "
            f"target is {V.shape[0]}-dimensional.",
            "Check the number of qubits in your circuit.",
        )
    dim = U.shape[0]
    # |Tr(U† V)|/dim == 1 iff U = e^{iφ} V
    overlap = abs(np.trace(U.conj().T @ V)) / dim
    if overlap < 1.0 - tol:
        _fail(
            f"Your circuit's unitary differs from the target "
            f"(overlap = {overlap:.4f}, want 1.0; global phase is forgiven).",
            "Print Operator(your_circuit).data and compare entries with the "
            "target matrix. Remember gates apply left-to-right in circuit order.",
        )
    _pass(f"Circuit matches the target unitary (overlap = {overlap:.6f}).")


def check_expectation(value, target, tol: float = 1e-2) -> None:
    """Check a computed expectation value against the target."""
    value = float(np.real(value))
    diff = abs(value - target)
    if diff > tol:
        _fail(
            f"Your value: {value:.4f} | expected: {target:.4f} | "
            f"difference: {diff:.4f} (tolerance {tol}).",
            "If you estimated from shots, try more shots. If you computed "
            "exactly, re-check the operator and the state.",
        )
    _pass(f"Expectation value {value:.4f} matches the target {target:.4f} "
          f"(within ±{tol}).")


def check_optimum(history, target, tol: float = 1e-2) -> None:
    """Check an optimization converged to the known minimum.

    ``history`` may be the final cost (float) or the list of costs per iteration.
    """
    costs = np.atleast_1d(np.asarray(history, dtype=float))
    best = float(costs.min())
    if best > target + tol:
        _fail(
            f"Best cost reached: {best:.4f}, but the true minimum is "
            f"{target:.4f} (tolerance {tol}).",
            "Try more iterations, a different initial point, or check that "
            "your cost function returns the *expectation value* of the cost "
            "Hamiltonian.",
        )
    extra = f" after {costs.size} iterations" if costs.size > 1 else ""
    _pass(f"Converged to {best:.4f}{extra} — that's the ground-state energy!")


def _cut_value(assignment: str, edges) -> int:
    """Cut value of a partition given as a bitstring (leftmost = highest node)."""
    bits = assignment[::-1]  # bits[i] = side of node i (Qiskit convention)
    return sum(w for e in edges
               for (u, v, w) in [e if len(e) == 3 else (*e, 1)]
               if bits[u] != bits[v])


def check_maxcut_solution(bitstring, edges) -> None:
    """Check a bitstring achieves the maximum cut of the graph.

    ``edges``: list of (u, v) or (u, v, weight). Node indices 0..n-1.
    ``bitstring``: measurement outcome, Qiskit convention (qubit 0 rightmost).
    Brute-forces the graph (fine for teaching-sized graphs, n <= 16).
    """
    bitstring = str(bitstring).strip()
    n = 1 + max(max(e[0], e[1]) for e in edges)
    if len(bitstring) != n:
        _fail(
            f"Your bitstring has {len(bitstring)} bits but the graph has {n} nodes.",
            "Each qubit/bit corresponds to one node of the graph.",
        )
    if n > 16:
        raise ValueError("check_maxcut_solution brute-forces the graph; use n <= 16.")
    achieved = _cut_value(bitstring, edges)
    best = max(_cut_value(format(x, f"0{n}b"), edges) for x in range(2 ** n))
    ratio = achieved / best if best else 1.0
    if achieved < best:
        _fail(
            f"Your partition cuts {achieved} edge-weight, but the maximum cut is "
            f"{best} (approximation ratio {ratio:.3f}).",
            "Take the *most frequent* bitstring from your QAOA samples — or "
            "increase p (layers) / re-optimize the angles.",
        )
    _pass(f"Maximum cut found! Your partition cuts {achieved} edge-weight "
          f"(approximation ratio 1.000).")
