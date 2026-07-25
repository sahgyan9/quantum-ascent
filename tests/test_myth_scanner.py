"""The Analogy Studio's red-flag scanner must catch myths without crying wolf.

The scanner is the second half of a loop the Studio previously left open: we
engineered the prompt but never checked the response. It is a regex pass, not a
judge, and the page says so — but a regex pass still has to be right, in both
directions:

  * it must fire on the stock myth phrasings an LLM actually produces, and
  * it must NOT fire on correct physics, or learners will be taught to distrust
    accurate explanations, which is worse than the myths.

The patterns are extracted from analogy-studio.html and exercised under Node,
so this tests the code that actually ships rather than a copy of it.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "website" / "analogy-studio.html"

node = shutil.which("node")
pytestmark = pytest.mark.skipif(node is None, reason="Node.js not installed")

# Text that MUST be flagged, and the label expected.
MYTHS = [
    ("A qubit is 0 and 1 at the same time, which is what gives it power.", "0 and 1"),
    ("Think of it as being zero and one simultaneously.", "0 and 1"),
    ("The register holds all values at once until you look.", "all values at once"),
    ("The machine tries every combination simultaneously and picks the winner.", "every answer at once"),
    ("It checks all possible routes in parallel, then returns the shortest.", "every answer at once"),
    ("Each branch is computed in a parallel universe.", "parallel universes"),
    ("Measuring one instantly affects the other faster than light.", "faster-than-light"),
    ("This enables instantaneous communication across the galaxy.", "faster-than-light"),
    ("Quantum computers are exponentially faster than classical ones.", "exponentially"),
    ("The wavefunction collapses when a conscious observer measures it.", "consciousness"),
    ("A qubit is like a coin spinning very fast between the two faces.", "spinning"),
]

# Correct physics that must NOT be flagged.
CLEAN = [
    "A qubit in superposition has no definite value yet, but definite amplitudes that fix the odds.",
    "Measuring returns one definite outcome; the superposition is gone afterwards.",
    "Entanglement produces correlated outcomes, but neither side can see the correlation alone, "
    "so no message is transmitted.",
    "For certain structured problems, such as factoring, the best known quantum algorithm is "
    "exponentially faster than the best known classical one.",
    "Observation means any interaction that records information about the system, such as a "
    "detector firing or a stray photon scattering.",
    "The amplitudes are arranged so that wrong answers cancel and the right answer becomes the "
    "likely one to measure.",
    "A spinning coin is undetermined: its face is not yet a fact, though the odds are exact.",
    "Adding qubits without an algorithm that concentrates amplitude only makes the search harder.",
]

DRIVER = r"""
const src = require("fs").readFileSync(process.argv[2], "utf8");
const m = src.match(/const RED_FLAGS = \[([\s\S]*?)\n\];/);
if (!m) { console.error("RED_FLAGS block not found in the page"); process.exit(2); }
const RED_FLAGS = eval("[" + m[1] + "\n]");
const cases = JSON.parse(require("fs").readFileSync(process.argv[3], "utf8"));
const out = { count: RED_FLAGS.length, results: [] };
for (const c of cases) {
  // Mirrors the page's filter, including the `unless` stand-down.
  const hits = RED_FLAGS.filter(f => f.re.test(c.text) && !(f.unless && f.unless.test(c.text)));
  out.results.push({ text: c.text, tag: c.tag,
                     labels: hits.map(h => h.label),
                     fixes: hits.map(h => h.fix) });
}
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def scan(tmp_path_factory):
    d = tmp_path_factory.mktemp("myth")
    cases = ([{"text": t, "tag": "myth"} for t, _ in MYTHS] +
             [{"text": t, "tag": "clean"} for t in CLEAN])
    spec = d / "cases.json"
    spec.write_text(json.dumps(cases), encoding="utf-8")
    drv = d / "drv.js"
    drv.write_text(DRIVER, encoding="utf-8")
    proc = subprocess.run([node, str(drv), str(PAGE), str(spec)],
                          capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert proc.returncode == 0, f"scanner driver failed:\n{proc.stderr}"
    data = json.loads(proc.stdout)
    data["by_text"] = {r["text"]: r for r in data["results"]}
    return data


def test_scanner_has_patterns(scan):
    assert scan["count"] >= 6, "too few red-flag patterns to be useful"


@pytest.mark.parametrize("text,expect", MYTHS, ids=[m[1] + "|" + m[0][:24] for m in MYTHS])
def test_myths_are_flagged(scan, text, expect):
    r = scan["by_text"][text]
    assert r["labels"], f"scanner missed a myth: {text!r}"
    joined = " ".join(r["labels"]).lower()
    assert expect.lower() in joined, (
        f"flagged, but with the wrong label: expected {expect!r}, got {r['labels']}"
    )


@pytest.mark.parametrize("text", CLEAN, ids=[t[:34] for t in CLEAN])
def test_correct_physics_is_not_flagged(scan, text):
    """False positives are worse than misses here — they would teach a learner
    to distrust an accurate explanation."""
    r = scan["by_text"][text]
    assert not r["labels"], f"false positive on correct physics: {r['labels']} for {text!r}"


def test_every_flag_offers_a_correction(scan):
    """A flag that only says 'wrong' teaches nothing; each must say what to say
    instead."""
    for r in scan["results"]:
        for fix in r["fixes"]:
            assert len(fix) > 60, f"correction too thin to be useful: {fix!r}"


def test_page_admits_the_scanner_is_not_a_judge():
    """Honesty rule: a green result must not read as 'verified correct'."""
    html = PAGE.read_text(encoding="utf-8")
    assert "cannot tell you whether the physics is right" in html, (
        "a clean scan must explicitly disclaim that it verified the physics"
    )
    assert "Now you grade it" in html, "the learner must be handed the real judgement"
