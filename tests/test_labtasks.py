"""Every browser-track task must be solvable, and every hint must be true.

The browser track is only an honest alternative to the notebook if its twelve
tasks actually work. This module drives `labtasks.js` under Node and asserts,
for each task:

  * the intended solution PASSES its checker,
  * an empty / untouched circuit FAILS it (so nothing passes by accident),
  * the specific wrong answers the hints and feedback warn about really do
    produce the diagnosis we promise (e.g. "you used the half-angle"),
  * the numbers quoted inside the hint text are correct.

That last one matters more than it looks. A hint that says "set gamma to 67
degrees" and is wrong by ten degrees is worse than no hint at all: the learner
follows it, fails anyway, and concludes they cannot do this.
"""

import json
import math
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
JS = REPO / "website" / "assets" / "js"

node = shutil.which("node")
pytestmark = pytest.mark.skipif(node is None, reason="Node.js not installed")

DEG = math.pi / 180

# The intended solution for each task, kept test-side. `ops` for circuit tasks,
# `params` for slider tasks, `value` for numeric tasks.
SOLUTIONS = {
    "01-1": {"n": 1, "ops": [{"g": "H", "q": 0}]},
    "01-2": {"n": 1, "ops": [{"g": "RY", "q": 0, "p": 60 * DEG}]},
    "02-1": {"n": 1, "ops": [{"g": "H", "q": 0}, {"g": "Z", "q": 0}, {"g": "H", "q": 0}]},
    "02-2": {"n": 2, "ops": [{"g": "X", "q": 1}]},
    "03-1": {"n": 2, "ops": [{"g": "H", "q": 0}, {"g": "CX", "q": 0, "t": 1}]},
    "03-2": {"n": 2, "ops": [{"g": "H", "q": 0}, {"g": "CX", "q": 0, "t": 1}, {"g": "X", "q": 1}]},
    "04-1": {"n": 1, "ops": [{"g": "RY", "q": 0, "p": 60 * DEG}]},
    "04-2": {"n": 2, "ops": [{"g": "X", "q": 0}]},
    "05-1": {"params": {"theta": 207}},
    "05-2": {"value": -1.118},
    "06-1": {"n": 3, "ops": [{"g": "X", "q": 0}]},
    "06-2": {"params": {"gamma1": 67, "beta1": 113, "p": 1, "gamma2": 30, "beta2": 165}},
}

# The Summit's payoff claim, pinned: p=2 with per-layer angles reaches the
# optimum. Shared angles across layers cap out at 0.962, which is why the task
# gives each layer its own pair.
SUMMIT_P2 = {"gamma1": 105, "beta1": 148, "p": 2, "gamma2": 32, "beta2": 165}

# Wrong answers the copy explicitly promises to diagnose, and the phrase that
# must appear in the resulting message.
DIAGNOSTICS = [
    ("01-2", {"n": 1, "ops": [{"g": "RY", "q": 0, "p": 30 * DEG}]}, "half"),
    ("01-2", {"n": 1, "ops": [{"g": "RY", "q": 0, "p": 120 * DEG}]}, "upside down"),
    ("02-1", {"n": 1, "ops": [{"g": "H", "q": 0}, {"g": "H", "q": 0}]}, "undid each other"),
    ("02-2", {"n": 2, "ops": [{"g": "X", "q": 0}]}, "endianness"),
    ("03-1", {"n": 2, "ops": [{"g": "H", "q": 0}, {"g": "CX", "q": 0, "t": 1},
                              {"g": "X", "q": 1}]}, "anti"),
    ("03-1", {"n": 2, "ops": [{"g": "H", "q": 0}, {"g": "H", "q": 1}]}, "independent coins"),
    ("03-2", {"n": 2, "ops": [{"g": "H", "q": 0}, {"g": "CX", "q": 0, "t": 1}]}, "agreeing pair"),
    ("04-1", {"n": 1, "ops": [{"g": "RY", "q": 0, "p": 120 * DEG}]}, "sign backwards"),
    ("04-2", {"n": 2, "ops": []}, "always agree"),
    ("06-1", {"n": 3, "ops": []}, "same group"),
]

DRIVER = r"""
global.QSim = require(process.argv[2]);
const LabTasks = require(process.argv[3]);
const spec = JSON.parse(require("fs").readFileSync(process.argv[4], "utf8"));
const out = { tasks: {}, checks: [] };

for (const [mid, tasks] of Object.entries(LabTasks.all)) {
  for (const t of tasks) {
    out.tasks[t.id] = {
      module: mid, title: t.title, kind: t.kind || "circuit",
      hints: (t.hints || []).length,
      hasPredict: !!t.predict,
      predictOptions: t.predict ? t.predict.options.length : 0,
      predictFeedback: t.predict ? (t.predict.feedback || []).length : 0,
      predictAnswer: t.predict ? t.predict.answer : null,
      hasObjective: !!t.objective,
      params: (t.params || []).map(p => p.name),
      answer: t.answer, tol: t.tol
    };
  }
}

function findTask(id) {
  for (const tasks of Object.values(LabTasks.all))
    for (const t of tasks) if (t.id === id) return t;
  throw new Error("no task " + id);
}

for (const c of spec.cases) {
  const t = findTask(c.id);
  let res, circ;
  if (c.value !== undefined) {
    res = { ok: Math.abs(c.value - t.answer) <= t.tol,
            msg: "numeric" };
    circ = null;
  } else {
    circ = c.params ? t.circuit(c.params) : { n: c.n, ops: c.ops };
    const st = QSim.run(circ.n, circ.ops);
    res = t.check(circ, st);
    if (t.objective) res.objective = t.objective.fn(st, {}).value;
  }
  out.checks.push({ id: c.id, tag: c.tag, ok: res.ok, msg: res.msg,
                    objective: res.objective, nops: circ ? circ.ops.length : 0 });
}
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def lab(tmp_path_factory):
    cases = []
    for tid, sol in SOLUTIONS.items():
        c = {"id": tid, "tag": "solution"}
        c.update(sol)
        cases.append(c)
    # An untouched circuit must never pass.
    for tid, sol in SOLUTIONS.items():
        if "ops" in sol:
            cases.append({"id": tid, "tag": "empty", "n": sol["n"], "ops": []})
    for tid, circ, _phrase in DIAGNOSTICS:
        c = {"id": tid, "tag": "diag"}
        c.update(circ)
        cases.append(c)
    cases.append({"id": "06-2", "tag": "p2", "params": SUMMIT_P2})

    d = tmp_path_factory.mktemp("lab")
    spec = d / "spec.json"
    spec.write_text(json.dumps({"cases": cases}), encoding="utf-8")
    drv = d / "drv.js"
    drv.write_text(DRIVER, encoding="utf-8")
    # encoding is explicit: the checker messages contain ⟨Z⟩, √, − and friends,
    # and the Windows default codec cannot decode them.
    proc = subprocess.run(
        [node, str(drv), str(JS / "qsim.js"), str(JS / "labtasks.js"), str(spec)],
        capture_output=True, text=True, encoding="utf-8", timeout=120,
    )
    assert proc.returncode == 0, f"labtasks driver failed:\n{proc.stderr}"
    data = json.loads(proc.stdout)
    data["byTag"] = {}
    for row in data["checks"]:
        data["byTag"].setdefault((row["id"], row["tag"]), []).append(row)
    return data


def test_every_basecamp_has_two_tasks(lab):
    per_module = {}
    for meta in lab["tasks"].values():
        per_module.setdefault(meta["module"], 0)
        per_module[meta["module"]] += 1
    assert sorted(per_module) == ["01", "02", "03", "04", "05", "06"], per_module
    assert all(v == 2 for v in per_module.values()), per_module


@pytest.mark.parametrize("tid", sorted(SOLUTIONS))
def test_intended_solution_passes(lab, tid):
    rows = lab["byTag"][(tid, "solution")]
    assert rows[0]["ok"], f"{tid}: intended solution rejected — {rows[0]['msg']}"


@pytest.mark.parametrize("tid", sorted(t for t, s in SOLUTIONS.items() if "ops" in s))
def test_empty_circuit_fails(lab, tid):
    """Nothing may pass by simply being opened."""
    rows = lab["byTag"][(tid, "empty")]
    assert not rows[0]["ok"], f"{tid}: an empty circuit passed the checker"


@pytest.mark.parametrize("tid,phrase", [(t, p) for t, _c, p in DIAGNOSTICS],
                         ids=[f"{t}-{p[:14]}" for t, _c, p in DIAGNOSTICS])
def test_predicted_mistakes_are_diagnosed(lab, tid, phrase):
    """A wrong answer must be met with the specific diagnosis, not just 'no'."""
    rows = [r for r in lab["byTag"][(tid, "diag")] if phrase.lower() in (r["msg"] or "").lower()]
    assert rows, (
        f"{tid}: the predicted mistake was not diagnosed with '{phrase}'. "
        f"Got: {[r['msg'] for r in lab['byTag'][(tid, 'diag')]]}"
    )
    assert not rows[0]["ok"]


def test_every_task_has_three_hints_and_a_prediction(lab):
    for tid, meta in lab["tasks"].items():
        assert meta["hints"] == 3, f"{tid} has {meta['hints']} hints, expected a 3-rung ladder"
        assert meta["hasPredict"], f"{tid} has no prediction question"
        assert meta["predictOptions"] == meta["predictFeedback"], (
            f"{tid}: every option needs its own feedback line"
        )
        assert 0 <= meta["predictAnswer"] < meta["predictOptions"], f"{tid}: bad answer index"


def test_hint_numbers_are_true(lab):
    """The numbers quoted in hint text must actually work.

    A hint that says 'set gamma to 67 degrees' and is wrong is worse than no
    hint: the learner follows it, fails, and blames themselves.
    """
    # 05-1: the hint promises theta ~ 207 bottoms out at -1.1180.
    e = [r for r in lab["byTag"][("05-1", "solution")]][0]["objective"]
    assert e == pytest.approx(-math.sqrt(1.25), abs=5e-4), (
        f"hint says theta=207 gives -1.1180, got {e}"
    )
    # 06-2: the hint promises gamma~67, beta~113 reaches <C> ~ 3.75 of 4.
    c = [r for r in lab["byTag"][("06-2", "solution")]][0]["objective"]
    assert c == pytest.approx(3.75, abs=0.02), (
        f"hint says gamma=67/beta=113 gives <C>~3.75, got {c}"
    )
    assert c / 4 < 1.0, "p=1 must fall short of optimal — that is the lesson"


def test_summit_p2_beats_p1_and_reaches_the_optimum(lab):
    """The Summit's payoff claim, verified rather than asserted in prose.

    p=1 must fall short (so "Approximate" means something) and p=2 with
    per-layer angles must reach the optimum (so "depth helps" is not a promise
    the learner cannot cash). The exact angles quoted in hint 3 are the ones
    used here — if they stop working, this test fails before a learner does.
    """
    c1 = [r for r in lab["byTag"][("06-2", "solution")]][0]["objective"]
    c2 = [r for r in lab["byTag"][("06-2", "p2")]][0]["objective"]
    assert 3.7 <= c1 < 3.8, f"p=1 should land near 3.75, got {c1}"
    assert c2 == pytest.approx(4.0, abs=0.01), f"p=2 hint angles should reach 4.0, got {c2}"
    assert c2 > c1, "depth must actually buy something"
    assert [r for r in lab["byTag"][("06-2", "p2")]][0]["ok"], "p=2 solution must pass"
