"""Black-box helpers — circuits and graphs whose contents are hidden.

Peeking at this file spoils the exercises. The point of an oracle is that
you *discover* what's inside by doing quantum mechanics, not by reading code.
(If you're an educator: solutions are in notebooks/solutions/.)
"""

from __future__ import annotations

import random

_MYSTERY_SEQUENCES = {
    # seed -> gate sequence applied inside the mystery box (module 02 task:
    # find the circuit that *inverts* the box, i.e. the reversed adjoints)
    0: [("h", 0), ("z", 0)],
    1: [("x", 0), ("h", 0)],
    2: [("h", 0), ("s", 0)],
    3: [("ry", 0, 1.0471975511965976), ("z", 0)],  # RY(pi/3) then Z
}


def mystery_gate(seed: int = 0):
    """A 1-qubit black-box circuit. Build the circuit that undoes it.

    Verify with: check_unitary_equiv(your_fix.compose(mystery_gate(seed)),
                                     QuantumCircuit(1))  # identity
    """
    from qiskit import QuantumCircuit

    seq = _MYSTERY_SEQUENCES[seed % len(_MYSTERY_SEQUENCES)]
    qc = QuantumCircuit(1, name="mystery")
    for op in seq:
        getattr(qc, op[0])(*op[1:]) if op[0] != "ry" else qc.ry(op[2], op[1])
    boxed = QuantumCircuit(1, name=f"mystery[{seed}]")
    boxed.append(qc.to_gate(label=f"mystery[{seed}]"), [0])
    return boxed


def hidden_graph(seed: int = 42, n_nodes: int = 6):
    """A random connected graph for the QAOA capstone, as an edge list.

    You never see a picture of it — your QAOA pipeline must find its max cut.
    Deterministic for a given seed, so results are reproducible.
    """
    rng = random.Random(seed)
    nodes = list(range(n_nodes))
    rng.shuffle(nodes)
    # random spanning tree guarantees connectivity
    edges = set()
    for i in range(1, n_nodes):
        u, v = nodes[rng.randrange(i)], nodes[i]
        edges.add((min(u, v), max(u, v)))
    # sprinkle extra edges up to ~1.5x tree size
    target = int(1.5 * (n_nodes - 1))
    while len(edges) < target:
        u, v = rng.sample(range(n_nodes), 2)
        edges.add((min(u, v), max(u, v)))
    return sorted(edges)
