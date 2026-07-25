"""The hint ladder: same twelve tasks, same three rungs, on both tracks.

A learner can switch between the browser Lab and the notebook at any point. If
the two offered different help — or if one offered help and the other did not —
the tracks would stop being equivalent in the way we claim they are.

Also guards the failure mode that makes hints worse than useless: a hint that
quotes a number which does not work. The learner follows it, fails anyway, and
concludes they are the problem. The capstone angles quoted in rung 3 are
recomputed in tests/test_capstone_claims.py; here we check that both tracks
quote the *same* ones.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "notebooks"))

from q2q import hints  # noqa: E402

LABTASKS = (REPO / "website" / "assets" / "js" / "labtasks.js").read_text(encoding="utf-8")
NB_COMMON = (REPO / "tools" / "nb_common.py").read_text(encoding="utf-8")


def js_task_ids():
    return sorted(set(re.findall(r'id:\s*"(\d\d-\d)"', LABTASKS)))


def test_same_twelve_tasks_on_both_tracks():
    assert hints.available() == js_task_ids(), (
        "the notebook hint ladder and the browser Lab cover different tasks"
    )
    assert len(hints.available()) == 12


@pytest.mark.parametrize("task_id", sorted(hints.TASKS))
def test_every_task_has_exactly_three_rungs(task_id):
    _title, rungs = hints.TASKS[task_id]
    assert len(rungs) == 3, f"{task_id}: a ladder is three rungs"
    for i, r in enumerate(rungs):
        assert len(r) > 60, f"{task_id} rung {i + 1} is too thin to help"


@pytest.mark.parametrize("task_id", sorted(hints.TASKS))
def test_rung_one_gives_no_formula_or_code(task_id):
    """Rung 1 is intuition. Handing over `qc.h(0)` immediately defeats the
    whole point of a ladder."""
    nudge = hints.TASKS[task_id][0 if False else 1][0]
    assert "qc." not in nudge, f"{task_id}: rung 1 leaks code"
    assert "np.pi" not in nudge, f"{task_id}: rung 1 leaks the answer angle"


@pytest.mark.parametrize("task_id", sorted(hints.TASKS))
def test_rung_three_is_concrete(task_id):
    """The last rung must actually unstick someone: a gate, a number, or a
    named angle. 'Think harder' is not a third hint."""
    near = hints.TASKS[task_id][1][2]
    assert re.search(r"qc\.|\d", near), f"{task_id}: rung 3 is not concrete enough"


def test_ladder_advances_and_resets(capsys):
    hints.reset("01-1")
    hints.hint("01-1")
    first = capsys.readouterr().out
    assert "Hint 1/3" in first and "Nudge" in first

    hints.hint("01-1")
    second = capsys.readouterr().out
    assert "Hint 2/3" in second and "Strategy" in second

    hints.hint("01-1")
    third = capsys.readouterr().out
    assert "Hint 3/3" in third
    assert "last hint" in third

    hints.hint("01-1")            # clamped, never crashes or wraps around
    assert "Hint 3/3" in capsys.readouterr().out

    hints.reset("01-1")
    hints.hint("01-1")
    assert "Hint 1/3" in capsys.readouterr().out


def test_explicit_level_and_unknown_task(capsys):
    hints.hint("05-1", level=3)
    out = capsys.readouterr().out
    assert "Hint 3/3" in out and "206" in out

    hints.hint("99-9")
    out = capsys.readouterr().out
    assert "No hints" in out and "01-1" in out, "an unknown id must list the real ones"


def test_capstone_angles_agree_across_tracks():
    """Both tracks must quote the SAME p=2 angles for the 5-cycle.

    tests/test_capstone_claims.py proves these reach ratio 1.000; this proves
    the notebook and the browser do not send learners to different numbers.
    """
    near_py = hints.TASKS["06-2"][1][2]
    for value in ("105", "148", "32", "165"):
        assert value in near_py, f"notebook rung 3 lost the angle {value}"
        assert value in LABTASKS, f"browser hint lost the angle {value}"
    # and the p=1 pair
    for value in ("67", "113"):
        assert value in hints.TASKS["06-2"][1][1]
        assert value in LABTASKS


def test_half_angle_trap_is_named_on_both_tracks():
    """The single most common Basecamp 1 slip. Both tracks must call it out."""
    py = " ".join(hints.TASKS["01-2"][1]).lower()
    assert "half" in py and "60" in py and "30" in py
    js = LABTASKS.lower()
    assert "half-angle" in js or "half</i>-angle" in js


def test_notebook_footer_points_at_hints_before_solutions():
    """The footer used to send a stuck beginner straight to the answer key."""
    assert "hints.hint(" in NB_COMMON, "the footer must offer the ladder"
    i_hint = NB_COMMON.index("hints.hint(")
    i_sol = NB_COMMON.index("worked solutions")
    assert i_hint < i_sol, "hints must be offered BEFORE the worked solutions"


def test_colab_bootstrap_fetches_hints_module():
    """The bootstrap downloads a hardcoded file list. Forgetting to add a new
    module here breaks every notebook in Colab while working fine locally —
    which is the worst possible way for it to fail."""
    assert '"hints.py"' in NB_COMMON, "hints.py missing from the Colab bootstrap file list"
    shipped = {p.name for p in (REPO / "notebooks" / "q2q").glob("*.py")}
    listed = set(re.findall(r'"(\w+\.py)"', NB_COMMON))
    missing = shipped - listed
    assert not missing, f"q2q modules the Colab bootstrap would not download: {sorted(missing)}"


def test_generated_notebooks_carry_the_bootstrap_and_footer():
    import json
    for nb_path in sorted((REPO / "notebooks").glob("0*.ipynb")):
        text = "\n".join(
            "".join(c["source"])
            for c in json.loads(nb_path.read_text(encoding="utf-8"))["cells"]
        )
        assert "hints.py" in text, f"{nb_path.name}: bootstrap missing hints.py"
        assert "hints.hint(" in text, f"{nb_path.name}: footer does not offer the hint ladder"
