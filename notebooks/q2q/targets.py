"""Task targets, kept out of the notebooks so checker calls don't spoil answers.

Peeking here spoils the exercises — the names are deliberately opaque.
"""

import numpy as np

_SQ2 = 1 / np.sqrt(2)

# Module 01
M1_PLUS = np.array([_SQ2, _SQ2])                        # the |+> state (worked example)
M1_TASK2 = np.array([np.sqrt(3) / 2, 1 / 2])            # RY(pi/3)|0> — the 75/25 biased coin

# Module 02
M2_FLIP = np.array([[0, 1], [1, 0]], dtype=complex)     # the X gate — what H·Z·H equals

# Module 03
M3_BELL = np.array([_SQ2, 0, 0, _SQ2])                 # (|00> + |11>)/√2 — the Φ+ Bell pair

# Module 04
M4_Z75 = 0.5                                           # <Z> of RY(pi/3)|0> (the 75/25 state): 3/4 - 1/4
M4_ZZ_ANTI = -1.0                                      # <ZZ> of the anti-correlated Bell pair: always disagree

# Module 05 — variational principle. Cost Hamiltonian H = Z + 0.5 X, ansatz RY(theta)|0>,
# so E(theta) = cos(theta) + 0.5 sin(theta). Its ground (lowest) energy is -sqrt(1.25).
M5_E_HALF = 0.5                                         # E(pi/2) = cos(pi/2) + 0.5 sin(pi/2) — a landscape sanity point
M5_GROUND = -np.sqrt(1.25)                              # -1.118034 — smallest eigenvalue of Z + 0.5 X

# Module 06 — QAOA Max-Cut on the 4-node ring, edges (0,1),(1,2),(2,3),(3,0).
# Cost Hamiltonian H_C = sum of Z_i Z_j over edges; minimizing <H_C> maximizes the cut.
# The checkerboard |0101> cuts all 4 edges, each contributing -1, so <H_C> = -4 (the ground).
M6_CUT_ENERGY = -4.0                                    # <H_C> of the perfect checkerboard cut
