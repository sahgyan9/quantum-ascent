"""QSim (the browser track's simulator) must agree with Qiskit — exactly.

The browser track lets a learner finish the whole course without ever installing
Python. That is only defensible if the JavaScript simulator behind it is *real*
quantum mechanics rather than a plausible-looking animation.

So this module runs `website/assets/js/qsim.js` under Node, runs the same
circuits through Qiskit + Aer, and asserts they agree to 1e-12. If the two
tracks ever drift — a sign convention, an endianness flip, a rotation
half-angle — the build fails, and no learner is ever taught two different
physics depending on which button they clicked.

The endianness tests matter most: Basecamp 2 teaches Qiskit's little-endian
bitstring order *deliberately as a trap*. A browser track with the opposite
convention would teach that trap backwards.
"""

import json
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parent.parent
QSIM_JS = REPO / "website" / "assets" / "js" / "qsim.js"

qiskit = pytest.importorskip("qiskit")
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import SparsePauliOp, Statevector  # noqa: E402

node = shutil.which("node")
requires_node = pytest.mark.skipif(node is None, reason="Node.js not installed")


# --------------------------------------------------------------------------
# The shared circuit corpus. Each entry is (name, qubit count, op list).
# Ops use QSim's data format; the Qiskit builder below mirrors it exactly.
# --------------------------------------------------------------------------
CIRCUITS = [
    ("h_single", 1, [{"g": "H", "q": 0}]),
    ("x_single", 1, [{"g": "X", "q": 0}]),
    ("hzh_is_x", 1, [{"g": "H", "q": 0}, {"g": "Z", "q": 0}, {"g": "H", "q": 0}]),
    ("ry_60deg", 1, [{"g": "RY", "q": 0, "p": math.pi / 3}]),
    ("ry_two_thirds", 1, [{"g": "RY", "q": 0, "p": 2 * math.acos(math.sqrt(0.25))}]),
    ("rx_arb", 1, [{"g": "RX", "q": 0, "p": 0.7351}]),
    ("rz_after_h", 1, [{"g": "H", "q": 0}, {"g": "RZ", "q": 0, "p": 1.2345}]),
    ("s_and_t", 1, [{"g": "H", "q": 0}, {"g": "S", "q": 0}, {"g": "T", "q": 0}]),
    ("y_gate", 1, [{"g": "H", "q": 0}, {"g": "Y", "q": 0}]),
    # Two qubits — including the asymmetric cases that expose an endianness bug.
    ("bell", 2, [{"g": "H", "q": 0}, {"g": "CX", "q": 0, "t": 1}]),
    ("bell_phi_minus", 2, [{"g": "H", "q": 0}, {"g": "Z", "q": 0}, {"g": "CX", "q": 0, "t": 1}]),
    ("x_on_q0_only", 2, [{"g": "X", "q": 0}]),
    ("x_on_q1_only", 2, [{"g": "X", "q": 1}]),
    ("cx_reversed", 2, [{"g": "H", "q": 1}, {"g": "CX", "q": 1, "t": 0}]),
    ("cz_pair", 2, [{"g": "H", "q": 0}, {"g": "H", "q": 1}, {"g": "CZ", "q": 0, "t": 1}]),
    ("rzz_cost_layer", 2, [{"g": "H", "q": 0}, {"g": "H", "q": 1},
                           {"g": "RZZ", "q": 0, "t": 1, "p": 0.8}]),
    ("mixed_rotations", 2, [{"g": "RY", "q": 0, "p": 0.3}, {"g": "RX", "q": 1, "p": 1.9},
                            {"g": "CX", "q": 0, "t": 1}, {"g": "RZ", "q": 1, "p": 0.55}]),
    # Three and four qubits — the QAOA shapes.
    ("ghz3", 3, [{"g": "H", "q": 0}, {"g": "CX", "q": 0, "t": 1}, {"g": "CX", "q": 1, "t": 2}]),
    ("w_ish_3", 3, [{"g": "RY", "q": 0, "p": 1.1}, {"g": "CX", "q": 0, "t": 2},
                    {"g": "RY", "q": 1, "p": 0.4}, {"g": "CZ", "q": 1, "t": 2}]),
    ("qaoa_triangle_p1", 3, [
        {"g": "H", "q": 0}, {"g": "H", "q": 1}, {"g": "H", "q": 2},
        {"g": "RZZ", "q": 0, "t": 1, "p": 1.2}, {"g": "RZZ", "q": 1, "t": 2, "p": 1.2},
        {"g": "RZZ", "q": 0, "t": 2, "p": 1.2},
        {"g": "RX", "q": 0, "p": 0.9}, {"g": "RX", "q": 1, "p": 0.9}, {"g": "RX", "q": 2, "p": 0.9},
    ]),
    # Near-optimal p=1 angles (gamma=1.9702, beta=1.1714); ops carry 2*gamma
    # and 2*beta because that is what rzz/rx take.
    ("qaoa_ring_p1", 4, [
        {"g": "H", "q": 0}, {"g": "H", "q": 1}, {"g": "H", "q": 2}, {"g": "H", "q": 3},
        {"g": "RZZ", "q": 0, "t": 1, "p": 3.9404}, {"g": "RZZ", "q": 1, "t": 2, "p": 3.9404},
        {"g": "RZZ", "q": 2, "t": 3, "p": 3.9404}, {"g": "RZZ", "q": 3, "t": 0, "p": 3.9404},
        {"g": "RX", "q": 0, "p": 2.3428}, {"g": "RX", "q": 1, "p": 2.3428},
        {"g": "RX", "q": 2, "p": 2.3428}, {"g": "RX", "q": 3, "p": 2.3428},
    ]),
]

# Pauli strings to check per qubit count (Qiskit order: leftmost = highest qubit).
PAULIS = {
    1: ["I", "X", "Y", "Z"],
    2: ["ZZ", "ZI", "IZ", "XX", "XI", "IX", "YY", "ZX", "XZ", "YZ"],
    3: ["ZZZ", "ZZI", "IZZ", "ZIZ", "XII", "IXI", "IIX", "XYZ"],
    4: ["ZZII", "IZZI", "IIZZ", "ZIIZ", "XIII", "IIIX"],
}


def build_qiskit(n, ops):
    qc = QuantumCircuit(n)
    for op in ops:
        g = op["g"].upper()
        if g == "CX":
            qc.cx(op["q"], op["t"])
        elif g == "CZ":
            qc.cz(op["q"], op["t"])
        elif g == "RZZ":
            qc.rzz(op["p"], op["q"], op["t"])
        elif g == "RX":
            qc.rx(op["p"], op["q"])
        elif g == "RY":
            qc.ry(op["p"], op["q"])
        elif g == "RZ":
            qc.rz(op["p"], op["q"])
        elif g == "SDG":
            qc.sdg(op["q"])
        else:
            getattr(qc, g.lower())(op["q"])
    return qc


NODE_DRIVER = r"""
const QSim = require(process.argv[2]);
const spec = JSON.parse(require("fs").readFileSync(process.argv[3], "utf8"));
const out = {};
for (const c of spec.circuits) {
  const st = QSim.run(c.n, c.ops);
  const probs = Array.from(QSim.probabilities(st));
  const labels = probs.map((_, i) => QSim.label(i, c.n));
  const exp = {};
  for (const p of c.paulis) exp[p] = QSim.expectation(st, p);
  const marg = [];
  for (let q = 0; q < c.n; q++) marg.push(QSim.marginal1(st, q));
  out[c.name] = { probs, labels, exp, marg, ket: QSim.ketString(st) };
}
// Deterministic sampling: same seed must give the same counts every run.
const st = QSim.run(2, [{g:"H",q:0},{g:"CX",q:0,t:1}]);
out.__sample = QSim.sample(st, 2000, QSim.seededRng(12345));
out.__sample2 = QSim.sample(st, 2000, QSim.seededRng(12345));
// Max-Cut helpers.
out.__maxcut_triangle = QSim.maxCut([[0,1],[1,2],[0,2]], 3);
out.__maxcut_ring4 = QSim.maxCut([[0,1],[1,2],[2,3],[3,0]], 4);
out.__maxcut_c5 = QSim.maxCut([[0,1],[1,2],[2,3],[3,4],[4,0]], 5);
out.__cut_str = QSim.cutValue([[0,1],[1,2],[0,2]], "010", 3);
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def js_results(tmp_path_factory):
    """Run every circuit through QSim under Node, once, and return the results."""
    if node is None:
        pytest.skip("Node.js not installed")
    d = tmp_path_factory.mktemp("qsim")
    spec = {"circuits": [
        {"name": name, "n": n, "ops": ops, "paulis": PAULIS[n]}
        for name, n, ops in CIRCUITS
    ]}
    spec_path = d / "spec.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    driver = d / "driver.js"
    driver.write_text(NODE_DRIVER, encoding="utf-8")
    proc = subprocess.run(
        [node, str(driver), str(QSIM_JS), str(spec_path)],
        capture_output=True, text=True, encoding="utf-8", timeout=120,
    )
    assert proc.returncode == 0, f"node driver failed:\n{proc.stderr}"
    return json.loads(proc.stdout)


@pytest.mark.parametrize("name,n,ops", CIRCUITS, ids=[c[0] for c in CIRCUITS])
@requires_node
def test_probabilities_match_qiskit(js_results, name, n, ops):
    """The Born-rule distribution must be identical in both tracks."""
    sv = Statevector(build_qiskit(n, ops))
    want = np.asarray(sv.probabilities())
    got = np.asarray(js_results[name]["probs"])
    np.testing.assert_allclose(got, want, atol=1e-12, err_msg=f"{name}: probabilities differ")


@pytest.mark.parametrize("name,n,ops", CIRCUITS, ids=[c[0] for c in CIRCUITS])
@requires_node
def test_expectations_match_qiskit(js_results, name, n, ops):
    """Pauli expectation values — the Basecamp 4/5/6 backbone — must agree,
    including the string ORDER convention of SparsePauliOp."""
    sv = Statevector(build_qiskit(n, ops))
    for pauli in PAULIS[n]:
        want = float(np.real(sv.expectation_value(SparsePauliOp(pauli))))
        got = js_results[name]["exp"][pauli]
        assert got == pytest.approx(want, abs=1e-12), f"{name}: <{pauli}> differs"


@pytest.mark.parametrize("name,n,ops", CIRCUITS, ids=[c[0] for c in CIRCUITS])
@requires_node
def test_bitstring_labels_match_qiskit_endianness(js_results, name, n, ops):
    """QSim's basis labels must be Qiskit's: index i -> q[n-1]...q[0].

    This is the test that would catch a reversed browser track. Basecamp 2
    teaches the little-endian trap on purpose; teaching it backwards in the
    other track would be worse than not teaching it at all.
    """
    labels = js_results[name]["labels"]
    assert labels == [format(i, f"0{n}b") for i in range(2 ** n)]
    # And the probability attached to each label must match Qiskit's dict.
    qiskit_probs = Statevector(build_qiskit(n, ops)).probabilities_dict()
    for lab, p in zip(labels, js_results[name]["probs"]):
        assert p == pytest.approx(qiskit_probs.get(lab, 0.0), abs=1e-12), (
            f"{name}: P({lab}) differs — endianness or amplitude bug"
        )


@requires_node
def test_x_on_q0_is_not_x_on_q1(js_results):
    """A direct, human-readable statement of the endianness contract."""
    assert js_results["x_on_q0_only"]["labels"][1] == "01"
    p_q0 = js_results["x_on_q0_only"]["probs"]
    p_q1 = js_results["x_on_q1_only"]["probs"]
    assert p_q0[0b01] == pytest.approx(1.0)   # X on qubit 0 -> bitstring "01"
    assert p_q1[0b10] == pytest.approx(1.0)   # X on qubit 1 -> bitstring "10"


@requires_node
def test_bell_marginals_are_flat(js_results):
    """No-signalling, the Basecamp 3 lesson: each half of a Bell pair is 50/50."""
    for m in js_results["bell"]["marg"]:
        assert m == pytest.approx(0.5, abs=1e-12)


@requires_node
def test_born_rule_normalisation(js_results):
    for name, _, _ in CIRCUITS:
        assert sum(js_results[name]["probs"]) == pytest.approx(1.0, abs=1e-12), name


@requires_node
def test_sampling_is_seed_reproducible(js_results):
    """Same seed, same climb — a lesson can be replayed exactly."""
    assert js_results["__sample"] == js_results["__sample2"]
    assert sum(js_results["__sample"].values()) == 2000
    # A Bell pair only ever yields 00 or 11 — never 01 or 10.
    assert set(js_results["__sample"]) <= {"00", "11"}


@requires_node
def test_sampling_matches_born_rule_statistically(js_results):
    counts = js_results["__sample"]
    frac = counts.get("00", 0) / 2000
    assert 0.45 < frac < 0.55, f"Bell sampling looks biased: {counts}"


@requires_node
def test_maxcut_bruteforce_is_right(js_results):
    """These three graphs carry the capstone's pedagogy, so pin their answers.

    The triangle is the honest one: 3 edges but a maximum cut of only 2, so the
    approximation ratio can never be 1.0 by construction. The 4-ring is
    bipartite and cuts every edge — which is exactly why it alone was hiding
    what 'Approximate' means.
    """
    assert js_results["__maxcut_triangle"]["value"] == 2
    assert js_results["__maxcut_ring4"]["value"] == 4     # bipartite: all edges
    assert js_results["__maxcut_c5"]["value"] == 4        # 5 edges, max cut 4
    assert js_results["__cut_str"] == 2                   # "010" splits 1 from {0,2}


def _expected_cut(probs, edges):
    def cut(i):
        return sum(1 for a, b in edges if ((i >> a) & 1) != ((i >> b) & 1))
    return sum(p * cut(i) for i, p in enumerate(probs))


@requires_node
def test_qaoa_ring_beats_random_but_falls_short_of_optimal(js_results):
    """The capstone's whole lesson, as an assertion.

    At p=1 with near-optimal angles the 4-ring reaches <C> ~ 3.0 against a
    maximum cut of 4 — clearly better than the random-guess baseline of 2.0,
    and clearly NOT the optimum. If either half of that stops being true, the
    capstone is either teaching that QAOA is useless or that it is magic.
    """
    got = _expected_cut(js_results["qaoa_ring_p1"]["probs"], [(0, 1), (1, 2), (2, 3), (3, 0)])
    assert got > 2.0, f"no better than random guessing: {got}"
    assert got < 4.0, f"p=1 should not reach the optimum: {got}"
    assert got == pytest.approx(3.0, abs=0.05)


@requires_node
def test_triangle_cannot_cut_every_edge(js_results):
    """The frustration lesson: a triangle has 3 edges but a maximum cut of 2.

    No algorithm — quantum, classical, or divine — cuts all three. This is why
    Basecamp 6 opens on the triangle: it separates 'the best answer' from 'a
    perfect answer' before QAOA is even introduced, so the approximation ratio
    is not mistaken for an algorithmic failure.
    """
    tri = js_results["__maxcut_triangle"]
    assert tri["value"] == 2
    assert len(tri["assignments"]) == 6      # every split except all-one-side
    assert "000" not in tri["assignments"] and "111" not in tri["assignments"]
