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
    "run_and_tally",
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


def _fail(msg: str, hint: str = "", raise_err: bool = True) -> None:
    hint_html = f'<br><b>Hint:</b> {hint}' if hint else ""
    hint_txt = f"\n   Hint: {hint}" if hint else ""
    _show(
        f'<div style="border-left:5px solid #e74c3c;background:#fdedec;'
        f'color:#78281f;padding:10px 14px;border-radius:4px;font-size:14px">'
        f'❌ <b>Not yet.</b> {msg}{hint_html}</div>',
        f"❌ Not yet. {msg}{hint_txt}",
    )
    if raise_err:
        raise CheckError(msg)


def _install_friendly_tracebacks() -> None:
    """Collapse CheckError tracebacks to one calm line inside IPython/Jupyter.

    The red box rendered by _fail already explains the problem and the fix, so
    the usual multi-screen traceback wall adds nothing but fear. The exception
    still propagates as a cell error, so nbclient/pytest/"Restart & Run All"
    fail hard on wrong answers exactly as before.
    """
    if not _in_ipython():
        return
    from IPython import get_ipython

    def _one_liner(shell, etype, value, tb, tb_offset=None):
        # IPython leaves ALL display to a custom handler, so publish the
        # compact "traceback" ourselves — one calm line for the student,
        # and the diagnostic for CI logs.
        stb = [
            f"CheckError: {value}",
            "⏸️ Check not passed — use the hint in the red box above, "
            "adjust your code, and re-run this cell.",
        ]
        shell._showtraceback(etype, value, stb)
        return stb

    get_ipython().set_custom_exc((CheckError,), _one_liner)


_install_friendly_tracebacks()


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
    if np.all(np.abs(v.imag) < 1e-9):  # spare beginners the "+0.000j" noise
        return "[" + ", ".join(f"{a.real:.3f}" for a in v) + "]"
    return "[" + ", ".join(f"{a.real:+.3f}{a.imag:+.3f}j" for a in v) + "]"


# ---------------------------------------------------------------- runners

def run_and_tally(circuit, shots: int = 1024):
    """Run a circuit on the Aer simulator and return its counts dictionary.

    Used as the "nothing to change below" plumbing of task cells: it wraps the
    same four steps taught in the worked examples (simulator -> run -> result
    -> get_counts), but coaches with a friendly message instead of a raw
    traceback while the student's circuit above is still unfinished.
    Returns None (without raising) when the circuit isn't ready.
    """
    from qiskit import QuantumCircuit

    if circuit is None:
        _fail(
            "Your circuit hasn't been built yet.",
            "Complete the steps above so your circuit variable holds a "
            "QuantumCircuit, then re-run this cell.",
            raise_err=False,
        )
        return None
    if not isinstance(circuit, QuantumCircuit):
        _fail(
            f"Expected a QuantumCircuit here, but got {type(circuit).__name__}.",
            "Make sure the steps above assign a QuantumCircuit to the circuit "
            "variable, e.g. qc = QuantumCircuit(1).",
            raise_err=False,
        )
        return None
    if len(circuit.data) == 0:
        _fail(
            "Your circuit is empty — no gates or measurements yet.",
            "Work through the steps above, then re-run this cell.",
            raise_err=False,
        )
        return None
    if not any(ci.operation.name == "measure" for ci in circuit.data):
        _fail(
            "Your circuit has gates but no measurement — the slap is missing!",
            "Add the measurement as the final step (measure_all()), then re-run.",
            raise_err=False,
        )
        return None

    from qiskit_aer import AerSimulator

    counts = AerSimulator().run(circuit, shots=shots).result().get_counts()
    print(f"counts = {counts}")
    return counts


# ---------------------------------------------------------------- checkers

def check_statevector(state, expected, tol: float = 1e-6) -> None:
    """Check a state equals the expected one, ignoring global phase.

    ``state``/``expected`` may be a Statevector, QuantumCircuit, list or array.
    """
    if state is None:
        _fail(
            "Your state vector is undefined (None).",
            "Make sure you have completed the task and assigned your array/state to the target variable.",
            raise_err=False,
        )
        return
    try:
        from qiskit import QuantumCircuit
        if isinstance(state, QuantumCircuit) and len(state.data) == 0:
            _fail(
                "Your circuit is empty (has no gates).",
                "Make sure you apply the quantum gates to the circuit before running the check.",
                raise_err=False,
            )
            return
    except ImportError:
        pass
    v = _to_vector(state)
    w = _to_vector(expected)
    if v.shape != w.shape:
        _fail(
            f"Your state has {v.size} amplitudes but {w.size} were expected.",
            "Check the number of qubits: n qubits means 2^n amplitudes.",
        )
    norm = np.linalg.norm(v)
    w_unit = w / np.linalg.norm(w)
    if abs(norm - 1.0) > 1e-6:
        # Coach the two classic slips with a targeted hint before falling
        # back to the generic normalization message (Don Norman feedback).
        if (np.all(np.abs(v.imag) < 1e-9) and np.all(v.real >= -1e-12)
                and abs(v.real.sum() - 1.0) < 1e-6):
            roots = np.sqrt(np.clip(v.real, 0.0, None))
            if abs(np.vdot(w_unit, roots)) ** 2 > 1.0 - tol:
                _fail(
                    f"So close! You wrote the *probabilities* {_fmt_vec(v)} in the "
                    f"array, but a state is built from *amplitudes* — and amplitudes "
                    f"are the square roots of the probabilities.",
                    "Take the square root of each entry, e.g. "
                    "np.sqrt(np.array([prob_0, prob_1])). Squaring the amplitudes "
                    "then gives your probabilities back.",
                )
        if abs(np.vdot(w_unit, v / norm)) ** 2 > 1.0 - tol:
            _fail(
                f"Your amplitudes point in exactly the right direction — but the "
                f"state is not normalized: its length is {norm:.4f} and a valid "
                f"quantum state must have length exactly 1.",
                "Divide the whole array by its length, e.g. "
                "your_array / np.sqrt((your_array**2).sum()) — for equal "
                "amplitudes that's the famous 1/sqrt(2) factor.",
            )
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
    so honest shot noise never fails a correct answer.
    """
    from scipy import stats

    if counts is None:
        _fail(
            "Your counts dictionary is undefined (None).",
            "Make sure you have run the simulation, retrieved the counts, and assigned them to the target variable.",
            raise_err=False,
        )
        return

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

    if circuit is None:
        _fail(
            "Your circuit is undefined (None).",
            "Make sure you have defined your QuantumCircuit and assigned it to the target variable.",
            raise_err=False,
        )
        return
    try:
        from qiskit import QuantumCircuit
        if isinstance(circuit, QuantumCircuit) and len(circuit.data) == 0:
            _fail(
                "Your circuit is empty (has no gates).",
                "Make sure you apply the quantum gates to the circuit before running the check.",
                raise_err=False,
            )
            return
    except ImportError:
        pass

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
    if value is None:
        _fail(
            "Your expectation value is undefined (None).",
            "Make sure you have computed the expectation value and assigned it to the target variable.",
            raise_err=False,
        )
        return
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
    if history is None:
        _fail(
            "Your cost history is undefined (None).",
            "Make sure you have completed the optimization and passed the cost history.",
            raise_err=False,
        )
        return
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
    if bitstring is None:
        _fail(
            "Your bitstring is undefined (None).",
            "Make sure you have selected the most frequent bitstring and passed it to the checker.",
            raise_err=False,
        )
        return
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
