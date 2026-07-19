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
