"""The Summit's prose makes numerical claims. Verify them, don't trust them.

Basecamp 6 tells the learner, in words and in a table:

    triangle  — max cut 2 of 3, so the best possible answer leaves an edge uncut
    5-cycle   — max cut 4 of 5; QAOA reaches ratio ~0.94 at p=1 and ~1.00 at p=2
    4-ring    — bipartite, max cut 4 of 4; ratio 0.75 at p=1, 1.00 at p=2

Those numbers are the entire payoff of the word *Approximate*, and prose drifts
from code silently. This module recomputes every one of them with Qiskit.

It also guards the mistake this section exists to fix: an earlier draft taught
the 4-ring alone and reported "approximation ratio 1.0" as if that were QAOA's
general behaviour, when it is a property of the one graph where QAOA cannot
fail.
"""

import math
from itertools import product

import numpy as np
import pytest

qiskit = pytest.importorskip("qiskit")
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Statevector  # noqa: E402
from scipy.optimize import minimize  # noqa: E402

TRIANGLE = [(0, 1), (1, 2), (0, 2)]
RING4 = [(0, 1), (1, 2), (2, 3), (3, 0)]
C5 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]


def cut_of(bits, edges):
    return sum(1 for (i, j) in edges if bits[i] != bits[j])


def brute_max_cut(edges, n):
    return max(cut_of([(v >> k) & 1 for k in range(n)], edges) for v in range(2 ** n))


def expected_cut(gammas, betas, edges, n):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for g, b in zip(gammas, betas):
        for (i, j) in edges:
            qc.rzz(2 * g, i, j)
        qc.rx(2 * b, range(n))
    probs = Statevector(qc).probabilities()
    return sum(pr * cut_of([(v >> k) & 1 for k in range(n)], edges)
               for v, pr in enumerate(probs))


def best_ratio(edges, n, p, starts=10):
    rng = np.random.default_rng(11)
    mx = brute_max_cut(edges, n)
    best = -math.inf
    for _ in range(starts):
        x0 = rng.uniform(0, math.pi, 2 * p)
        res = minimize(lambda x: -expected_cut(x[:p], x[p:], edges, n),
                       x0, method="COBYLA", options={"maxiter": 500})
        best = max(best, -res.fun)
    return best / mx


# --------------------------------------------------------------- max cuts
def test_triangle_is_frustrated():
    """3 edges, maximum cut 2. The claim the whole section rests on."""
    assert brute_max_cut(TRIANGLE, 3) == 2
    assert len(TRIANGLE) == 3


def test_ring4_is_bipartite():
    """Every edge cuttable — which is exactly why it cannot teach 'Approximate'."""
    assert brute_max_cut(RING4, 4) == len(RING4) == 4


def test_c5_is_frustrated_but_less_so():
    assert brute_max_cut(C5, 5) == 4
    assert len(C5) == 5


# ------------------------------------------------------------ the ratios
def test_triangle_ratio_is_one_even_at_p1():
    """The triangle's lesson is combinatorial, NOT algorithmic.

    An earlier plan assumed a triangle would show a ratio below 1. It does not —
    QAOA nails it at p=1. If this ever changes, the notebook's framing ("the
    problem is frustrated, not the solver") would become wrong.
    """
    assert best_ratio(TRIANGLE, 3, p=1) == pytest.approx(1.0, abs=0.01)


def test_c5_falls_short_at_p1_and_recovers_at_p2():
    """The 5-cycle is the graph that pays off the word Approximate."""
    r1 = best_ratio(C5, 5, p=1)
    r2 = best_ratio(C5, 5, p=2)
    assert r1 == pytest.approx(0.937, abs=0.01), f"notebook claims ~0.94 at p=1, got {r1}"
    assert r1 < 0.99, "p=1 must visibly fall short, or the lesson evaporates"
    assert r2 == pytest.approx(1.0, abs=0.01), f"notebook claims ~1.00 at p=2, got {r2}"
    assert r2 > r1


def test_ring4_ratio_table_is_right():
    """The comparison table's 4-ring column: 0.75 at p=1, 1.00 at p=2."""
    assert best_ratio(RING4, 4, p=1) == pytest.approx(0.75, abs=0.01)
    assert best_ratio(RING4, 4, p=2) == pytest.approx(1.0, abs=0.01)


def test_shared_angles_cannot_reach_the_optimum_on_c5():
    """Why the browser Lab gives each QAOA layer its own (gamma, beta).

    Sharing one pair across both layers caps the 5-cycle at ~0.962, so a hint
    promising ratio 1.0 from a single pair would send the learner chasing
    something unreachable.
    """
    grid = np.linspace(0, math.pi, 90)
    best = max(expected_cut([g, g], [b, b], C5, 5) for g, b in product(grid, grid))
    assert best / 4 < 0.99, f"shared angles unexpectedly reached {best / 4}"
    assert best / 4 == pytest.approx(0.962, abs=0.01)


def test_capstone_notebook_states_these_numbers():
    """The prose and the code must agree — check the words are actually there."""
    from pathlib import Path
    import json
    nb = json.loads((Path(__file__).resolve().parent.parent / "notebooks" /
                     "solutions" / "06_qaoa_maxcut_capstone_solutions.ipynb")
                    .read_text(encoding="utf-8"))
    text = "\n".join("".join(c["source"]) for c in nb["cells"])
    assert "frustration" in text.lower(), "the triangle section must name frustration"
    assert "0.94" in text and "0.75" in text, "the ratio table must quote the real numbers"
    assert "2 of 3" in text or "2 out of 3" in text
    # And it must no longer present ratio 1.0 as the general result.
    assert "approximation ratio 1.0**" not in text.lower() or "bipartite" in text.lower(), (
        "if the notebook still headlines ratio 1.0, it must explain the graph was bipartite"
    )
