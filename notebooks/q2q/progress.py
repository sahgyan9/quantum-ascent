"""Cross-world completion codes — close the web↔Colab loop.

The learning lives in Colab; the map, XP and badges live on the website. Those
two worlds never talked to each other, so finishing the notebook left the
basecamp on the map dark. This module is the handshake:

    notebook  ──(you finish the tasks)──▶  prints a code  ──▶  website lights up

A code is emitted **only after the student's own task objects verify** in this
kernel, so it is genuinely earned. The website recomputes the same code with an
identical FNV-1a hash (see website/assets/js/progress.js) to accept it offline —
no server, no accounts. This is an honour-system handshake, not security: the
point is a real, earned link between the two halves of the course.
"""

from __future__ import annotations

import numpy as np

__all__ = ["code_for", "claim_basecamp_1", "claim_basecamp_2"]

# Shared with the website — DO NOT change without updating progress.js in lockstep
# (tests/test_progress.py cross-checks the two implementations).
_SALT = "quantum-ascent"


def _fnv1a(s: str) -> int:
    """32-bit FNV-1a hash. ASCII in, unsigned 32-bit out — trivially portable to
    JavaScript (Math.imul), which is why we hand-roll it instead of hashlib."""
    h = 0x811C9DC5
    for b in s.encode("ascii"):
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def code_for(module_id) -> str:
    """The completion code for a basecamp, e.g. code_for(1) -> 'QA-01-XXXX-XXXX'."""
    mid = str(module_id).zfill(2)
    hx = f"{_fnv1a(f'QA::{mid}::{_SALT}'):08X}"
    return f"QA-{mid}-{hx[:4]}-{hx[4:]}"


# ---------------------------------------------------------------- verification

def _has_op(circuit, name: str) -> bool:
    try:
        return any(ci.operation.name == name for ci in circuit.data)
    except Exception:
        return False


def _statevector_matches(circuit, expected, tol: float = 1e-6) -> bool:
    """True if `circuit`'s statevector equals `expected` up to global phase."""
    from .checkers import _to_vector
    try:
        v = _to_vector(circuit)
        w = _to_vector(expected)
    except Exception:
        return False
    if v.shape != w.shape:
        return False
    nv, nw = np.linalg.norm(v), np.linalg.norm(w)
    if nv < 1e-12 or nw < 1e-12:
        return False
    fidelity = abs(np.vdot(w / nw, v / nv)) ** 2
    return fidelity > 1.0 - tol


# ---------------------------------------------------------------- presentation

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


def _celebrate(module_id, code: str) -> None:
    mid = str(module_id).zfill(2)
    url = f"https://quantum-ascent-77617.web.app/module.html?id={mid}#claim"
    _show(
        f'<div style="border:2px solid #1f7a4d;background:#eaf6ee;color:#0f3d22;'
        f'padding:16px 18px;border-radius:10px">'
        f'<b>🎓 Basecamp {mid} verified — you earned your completion code!</b>'
        f'<div style="font:700 26px/1.4 Consolas,monospace;letter-spacing:2px;'
        f'color:#0e5c34;margin:10px 0;text-align:center">{code}</div>'
        f'Paste it into the <b>“Log your notebook”</b> box on the '
        f'<a href="{url}">basecamp page</a> to light up this camp on your Ascent '
        f'map and bank your climber XP. 🏔️</div>',
        f"\n🎓 Basecamp {mid} verified — completion code:\n\n    {code}\n\n"
        f"Paste it into the 'Log your notebook' box at {url}\n",
    )


def _nudge(reasons) -> None:
    items = "".join(f"<li>{r}</li>" for r in reasons)
    text = "\n".join("  - " + r for r in reasons)
    _show(
        f'<div style="border-left:5px solid #b45309;background:#fdf3e7;color:#5c2d0c;'
        f'padding:12px 16px;border-radius:4px">'
        f'<b>Almost there — nothing to claim yet.</b> Finish these, re-run the '
        f'task cells above, then run this cell again:<ul>{items}</ul></div>',
        f"\nAlmost there — finish these, then re-run:\n{text}\n",
    )


# ---------------------------------------------------------------- public claim

def claim_basecamp_1(qc_spin=None, qc3=None):
    """Verify the Basecamp 1 tasks in this kernel and, if correct, print the
    website completion code. Returns the code string on success, else None.

    - qc_spin (Task 1): a 1-qubit circuit with a Hadamard and a measurement.
    - qc3   (Task 2): a circuit preparing the 75/25 state (√3/2, 1/2).
    """
    from .targets import M1_TASK2
    try:
        from qiskit import QuantumCircuit
    except ImportError:            # no qiskit (shouldn't happen post-bootstrap)
        QuantumCircuit = None

    reasons = []
    ok_spin = (QuantumCircuit is not None and isinstance(qc_spin, QuantumCircuit)
               and _has_op(qc_spin, "h") and _has_op(qc_spin, "measure"))
    if not ok_spin:
        reasons.append("<b>Task 1</b>: build <code>qc_spin</code> — a 1-qubit "
                       "circuit with <code>.h(0)</code> then <code>.measure_all()</code>.")

    ok3 = qc3 is not None and _statevector_matches(qc3, M1_TASK2)
    if not ok3:
        reasons.append("<b>Task 2</b>: make <code>qc3</code> prepare the 75/25 "
                       "state with <code>.ry(np.pi/3, 0)</code>.")

    if reasons:
        _nudge(reasons)
        return None

    code = code_for("01")
    _celebrate("01", code)
    return code


def _unitary_matches(circuit, expected, tol: float = 1e-6) -> bool:
    """True if `circuit` implements the `expected` matrix up to global phase."""
    try:
        from qiskit.quantum_info import Operator
        U = Operator(circuit).data
        V = np.asarray(expected, dtype=complex)
        if U.shape != V.shape:
            return False
        return abs(np.trace(U.conj().T @ V)) / U.shape[0] > 1.0 - tol
    except Exception:
        return False


def _top_bitstring(circuit, shots: int = 256):
    """The most frequent measurement outcome (spaces stripped), or None."""
    try:
        from qiskit_aer import AerSimulator
        counts = AerSimulator().run(circuit, shots=shots).result().get_counts()
        return max(counts, key=counts.get).replace(" ", "")
    except Exception:
        return None


def claim_basecamp_2(qc_flip=None, qc_endian=None):
    """Verify the Basecamp 2 tasks in this kernel and, if correct, print the
    website completion code. Returns the code string on success, else None.

    - qc_flip   (Task 1): a 1-qubit circuit H·Z·H, which equals the X gate.
    - qc_endian (Task 2): a 2-qubit circuit with X on qubit 0 + measurement,
      which Qiskit reads out as the bitstring '01'.
    """
    from .targets import M2_FLIP
    try:
        from qiskit import QuantumCircuit
    except ImportError:            # no qiskit (shouldn't happen post-bootstrap)
        QuantumCircuit = None

    reasons = []
    ok_flip = (QuantumCircuit is not None and isinstance(qc_flip, QuantumCircuit)
               and qc_flip.num_qubits == 1 and _unitary_matches(qc_flip, M2_FLIP))
    if not ok_flip:
        reasons.append("<b>Task 1</b>: build <code>qc_flip</code> — apply "
                       "<code>.h(0)</code>, <code>.z(0)</code>, <code>.h(0)</code> "
                       "on one qubit (it equals X).")

    ok_end = (QuantumCircuit is not None and isinstance(qc_endian, QuantumCircuit)
              and qc_endian.num_qubits == 2 and _top_bitstring(qc_endian) == "01")
    if not ok_end:
        reasons.append("<b>Task 2</b>: build <code>qc_endian</code> — a 2-qubit "
                       "circuit with <code>.x(0)</code> then <code>.measure_all()</code>, "
                       "so it reads <code>'01'</code>.")

    if reasons:
        _nudge(reasons)
        return None

    code = code_for("02")
    _celebrate("02", code)
    return code
