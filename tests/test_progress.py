"""Tests for q2q.progress — the cross-world completion-code handshake.

Guards two contracts:
1. Codes are deterministic and correctly formatted.
2. The Python code generator and the website's JS generator agree exactly
   (a drift there would silently reject every learner's real code).
3. claim_basecamp_1 only emits a code when the student's circuits verify.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "notebooks"))

from q2q import progress  # noqa: E402


def test_code_format_and_determinism():
    code = progress.code_for(1)
    assert re.fullmatch(r"QA-01-[0-9A-F]{4}-[0-9A-F]{4}", code), code
    assert progress.code_for(1) == code          # deterministic
    assert progress.code_for("01") == code       # int/str agree
    assert progress.code_for(2) != code          # per-module


def test_fnv1a_known_vector():
    # FNV-1a("") is the offset basis; FNV-1a("a") is a well-known constant.
    assert progress._fnv1a("") == 0x811C9DC5
    assert progress._fnv1a("a") == 0xE40C292C


def test_js_and_python_codes_agree():
    """The website must accept the exact code the notebook prints."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available to cross-check the JS implementation")
    js = REPO / "website" / "assets" / "js" / "progress.js"
    src = js.read_text(encoding="utf-8")
    # Pull the shared helpers out of progress.js and print codes for 01..06.
    snippet = src[src.index("/* completion-code core"):src.index("/* end completion-code core")]
    prog = snippet + "\nfor (let i=1;i<=6;i++) console.log(codeFor(i));\n"
    out = subprocess.run([node, "-e", prog], capture_output=True, text=True, check=True)
    js_codes = out.stdout.split()
    py_codes = [progress.code_for(i) for i in range(1, 7)]
    assert js_codes == py_codes, f"JS {js_codes} != PY {py_codes}"


def test_claim_rejects_incomplete_work():
    assert progress.claim_basecamp_1(None, None) is None


def test_claim_accepts_correct_circuits():
    qiskit = pytest.importorskip("qiskit")
    import numpy as np
    from qiskit import QuantumCircuit

    qc_spin = QuantumCircuit(1)
    qc_spin.h(0)
    qc_spin.measure_all()

    qc3 = QuantumCircuit(1)
    qc3.ry(np.pi / 3, 0)

    code = progress.claim_basecamp_1(qc_spin, qc3)
    assert code == progress.code_for("01")


def test_claim_rejects_wrong_angle():
    pytest.importorskip("qiskit")
    import numpy as np
    from qiskit import QuantumCircuit

    qc_spin = QuantumCircuit(1)
    qc_spin.h(0)
    qc_spin.measure_all()

    qc3 = QuantumCircuit(1)
    qc3.ry(np.pi / 2, 0)          # fair coin, not the 75/25 target

    assert progress.claim_basecamp_1(qc_spin, qc3) is None
