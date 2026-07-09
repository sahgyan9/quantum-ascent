"""q2q — helper package for the Qubits->QAOA (Quantum Ascent) course notebooks.

Learners interact with three things:
- checkers: friendly self-check functions with pass/fail feedback and hints
- widgets:  show_widget() embeds the course's interactive HTML widgets
- oracles:  black-box circuits/graphs so you can *discover* the answers
"""

from .checkers import (
    CheckError,
    check_statevector,
    check_counts_close,
    check_unitary_equiv,
    check_expectation,
    check_optimum,
    check_maxcut_solution,
)
from .widgets import show_widget
from .latex_macros import macros_cell

__version__ = "0.1.0"
