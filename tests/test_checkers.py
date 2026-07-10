"""Unit tests for q2q.checkers — every checker must pass on correct input,
raise CheckError with a diagnostic on wrong input, and tolerate honest shot noise."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "notebooks"))

from q2q.checkers import (  # noqa: E402
    CheckError,
    run_and_tally,
    check_statevector,
    check_counts_close,
    check_unitary_equiv,
    check_expectation,
    check_optimum,
    check_maxcut_solution,
)

SQ2 = 1 / np.sqrt(2)


# ---------------------------------------------------------------- statevector

def test_statevector_exact_match():
    check_statevector([SQ2, SQ2], [SQ2, SQ2])


def test_statevector_global_phase_forgiven():
    check_statevector(np.array([SQ2, SQ2]) * np.exp(1j * 0.7), [SQ2, SQ2])


def test_statevector_accepts_circuit_and_statevector():
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    qc = QuantumCircuit(1)
    qc.h(0)
    check_statevector(qc, Statevector([SQ2, SQ2]))


def test_statevector_wrong_state_fails():
    with pytest.raises(CheckError):
        check_statevector([1, 0], [SQ2, SQ2])


def test_statevector_unnormalized_fails_with_hint(capsys):
    with pytest.raises(CheckError):
        check_statevector([1, 1], [SQ2, SQ2])
    assert "normalized" in capsys.readouterr().out


def test_statevector_probabilities_as_amplitudes_coached(capsys):
    # THE classic beginner slip: writing [P(0), P(1)] where amplitudes go.
    with pytest.raises(CheckError):
        check_statevector([0.75, 0.25], [np.sqrt(3) / 2, 0.5])
    assert "square root" in capsys.readouterr().out


def test_statevector_right_direction_unnormalized_coached(capsys):
    with pytest.raises(CheckError):
        check_statevector([1, 1], [SQ2, SQ2])
    assert "right direction" in capsys.readouterr().out


def test_statevector_wrong_dimension_fails():
    with pytest.raises(CheckError):
        check_statevector([1, 0, 0, 0], [SQ2, SQ2])


# ---------------------------------------------------------------- run_and_tally

def test_run_and_tally_none_circuit_coaches_without_raising(capsys):
    assert run_and_tally(None) is None  # friendly message, no exception
    assert "hasn't been built" in capsys.readouterr().out


def test_run_and_tally_missing_measurement_coaches_without_raising(capsys):
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(1)
    qc.h(0)
    assert run_and_tally(qc) is None
    assert "measure" in capsys.readouterr().out


def test_run_and_tally_valid_circuit_returns_counts():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure_all()
    counts = run_and_tally(qc, shots=64)
    assert sum(counts.values()) == 64


# ---------------------------------------------------------------- counts

def test_counts_accepts_realistic_shot_noise():
    rng = np.random.default_rng(7)
    for _ in range(5):
        n0 = rng.binomial(1024, 0.5)
        check_counts_close({"0": n0, "1": 1024 - n0}, {"0": 0.5, "1": 0.5})


def test_counts_rejects_wrong_distribution():
    with pytest.raises(CheckError):
        check_counts_close({"0": 900, "1": 124}, {"0": 0.5, "1": 0.5})


def test_counts_rejects_impossible_outcome():
    with pytest.raises(CheckError):
        check_counts_close({"00": 500, "11": 400, "01": 124},
                           {"00": 0.5, "11": 0.5, "01": 0.0, "10": 0.0})


def test_counts_missing_outcome_ok_if_insignificant():
    # 3 shots can easily miss an outcome — must not fail
    check_counts_close({"0": 3}, {"0": 0.5, "1": 0.5})


def test_counts_empty_fails():
    with pytest.raises(CheckError):
        check_counts_close({}, {"0": 1.0})


# ---------------------------------------------------------------- unitary

def test_unitary_equiv_hadamard():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(1)
    qc.h(0)
    H = SQ2 * np.array([[1, 1], [1, -1]])
    check_unitary_equiv(qc, H)


def test_unitary_equiv_global_phase_forgiven():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(1)
    qc.x(0)
    X_phased = np.exp(1j * 1.1) * np.array([[0, 1], [1, 0]])
    check_unitary_equiv(qc, X_phased)


def test_unitary_equiv_circuit_vs_circuit():
    from qiskit import QuantumCircuit

    a, b = QuantumCircuit(1), QuantumCircuit(1)
    a.h(0); a.h(0)  # identity
    check_unitary_equiv(a, b)


def test_unitary_equiv_wrong_gate_fails():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(1)
    qc.x(0)
    with pytest.raises(CheckError):
        check_unitary_equiv(qc, np.eye(2))


# ---------------------------------------------------------------- expectation

def test_expectation_within_tolerance():
    check_expectation(-1.495, -1.5, tol=0.01)


def test_expectation_outside_tolerance_fails():
    with pytest.raises(CheckError):
        check_expectation(-1.3, -1.5, tol=0.01)


def test_expectation_accepts_complex_with_tiny_imag():
    check_expectation(np.complex128(0.5 + 1e-12j), 0.5, tol=0.01)


# ---------------------------------------------------------------- optimum

def test_optimum_from_history():
    check_optimum([0.0, -0.8, -1.4, -1.5], target=-1.5, tol=0.05)


def test_optimum_from_scalar():
    check_optimum(-1.49, target=-1.5, tol=0.05)


def test_optimum_not_converged_fails():
    with pytest.raises(CheckError):
        check_optimum([0.0, -0.5, -0.9], target=-1.5, tol=0.05)


# ---------------------------------------------------------------- maxcut

TRIANGLE = [(0, 1), (1, 2), (0, 2)]  # max cut = 2


def test_maxcut_optimal_bitstring():
    check_maxcut_solution("001", TRIANGLE)  # node 0 alone: cuts (0,1) and (0,2)


def test_maxcut_suboptimal_fails_with_ratio(capsys):
    with pytest.raises(CheckError):
        check_maxcut_solution("000", TRIANGLE)  # cuts nothing
    assert "approximation ratio" in capsys.readouterr().out


def test_maxcut_weighted_edges():
    # heavy edge (0,1,w=10): optimal separates 0 from 1
    edges = [(0, 1, 10), (1, 2, 1), (0, 2, 1)]
    check_maxcut_solution("001", edges)  # cuts 10 + 1 = 11 (max)


def test_maxcut_wrong_length_fails():
    with pytest.raises(CheckError):
        check_maxcut_solution("01", TRIANGLE)


def test_maxcut_hidden_graph_is_deterministic_and_connected():
    from q2q.oracles import hidden_graph

    g1, g2 = hidden_graph(seed=42), hidden_graph(seed=42)
    assert g1 == g2
    # connectivity: union-find over 6 nodes
    parent = list(range(6))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for u, v in g1:
        parent[find(u)] = find(v)
    assert len({find(i) for i in range(6)}) == 1


def test_mystery_gate_is_unitary_blackbox():
    from qiskit.quantum_info import Operator
    from q2q.oracles import mystery_gate

    for seed in range(4):
        op = Operator(mystery_gate(seed))
        assert op.is_unitary()
