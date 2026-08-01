"""The browser track must teach before it asks — style guide rule 10.

The failure this guards against actually shipped: twelve graded browser tasks
against 772 words of prose, with the Hadamard gate explained nowhere except hint
rung 2 of task 01-1. A learner could only be told what H does by first declaring
themselves stuck, which turns the hint ladder from recovery into first delivery
and breaks rule 6 — the notebook and the site were no longer the same teacher.

Nothing in review caught it because no rule forbade it. These tests are that
rule, made mechanical.
"""

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import build_lessons  # noqa: E402

LESSONS = json.loads(
    (REPO / "website" / "assets" / "data" / "lessons.json").read_text(encoding="utf-8")
)


def _modules():
    return {k: v for k, v in LESSONS.items() if not k.startswith("_")}


def test_no_task_is_met_cold():
    """Every concept a task requires is taught by an earlier beat, and every
    beat still matches the notebook section it was derived from."""
    problems = build_lessons.verify()
    assert problems == [], "\n".join(["Climb Notes are inconsistent:"] + problems)


def test_hadamard_is_taught_before_the_task_that_needs_it():
    """The specific regression. Task 01-1 asks for a fair coin; the learner must
    have met H in prose first, not only in a hint."""
    beats = LESSONS["01"]["beats"]
    before_first_task = [b for b in beats if b["before"] == "01-1"]
    assert before_first_task, "task 01-1 has no climb notes before it"

    prose = " ".join(b["html"] for b in before_first_task).lower()
    assert "hadamard" in prose
    assert "born rule" in prose


def test_the_half_angle_method_is_taught_without_giving_task_2_away():
    """Beat 01-c must teach how to invert sin²(θ/2) — but task 01-2's whole
    point is inverting it for P(1) = 0.25, and its prediction question asks for
    exactly that angle. Teaching the method on the target value would delete the
    task, so the worked case must be a different one."""
    beat = next(b for b in LESSONS["01"]["beats"] if b["id"] == "01-c")
    body = (beat["html"] + beat["math"]["html"]).lower()

    assert "sin²(θ/2)" in body, "the half-angle rule itself must be stated"
    assert "arcsine" in body or "which angle has sine" in body, "the inversion method must be shown"

    # Task 02's answer is 60° / π/3, reached from P(1) = 0.25.
    assert "60°" not in body, "beat 01-c gives away task 01-2's answer"
    assert "0.25" not in body, "beat 01-c solves task 01-2's prediction question for the learner"


def _beats_before(mod_id, task_id):
    """Every beat a learner has read by the time they reach `task_id`."""
    mod = LESSONS[mod_id]
    order = list(mod["requires"].keys())
    upto = order[: order.index(task_id) + 1]
    return [b for b in mod["beats"] if b["before"] in upto]


def _text_of(beats):
    out = []
    for b in beats:
        out.append(b.get("html", ""))
        out.append(json.dumps(b.get("math", {})))
        out.append(json.dumps(b.get("widget", {})))
    return " ".join(out).lower()


# (module, task, forbidden substring, why it would ruin the task)
SPOILERS = [
    ("05", "05-1", "207", "the angle that minimises the landscape IS task 05-1"),
    ("05", "05-1", "206", "the angle that minimises the landscape IS task 05-1"),
    ("05", "05-2", "1.118", "task 05-2 asks the learner to compute this number"),
    ("05", "05-2", "1.25", "task 05-2 asks the learner to compute √1.25 themselves"),
    ("06", "06-1", "frustrat", "discovering frustration IS task 06-1"),
    ("06", "06-1", "2 of 3", "the triangle's best cut IS task 06-1's answer"),
    ("06", "06-2", "3.75", "the p=1 result is task 06-2's prediction question"),
    ("06", "06-2", "0.94", "the p=1 ratio is task 06-2's prediction question"),
]


def test_beats_do_not_give_away_the_task_they_precede():
    """Several tasks are discoveries, not applications: the triangle's stubborn
    third edge, the tilted landscape's true minimum, how far p=1 QAOA actually
    gets. A beat that answers those in advance does not make the course gentler,
    it deletes the task. (The honest post-mortem is allowed — and required — in
    the closing beat, which renders after both tasks are done.)"""
    for mod_id, task_id, banned, why in SPOILERS:
        text = _text_of(_beats_before(mod_id, task_id))
        assert banned not in text, f"[{mod_id}] beat before {task_id} leaks {banned!r}: {why}"


def test_the_summit_still_delivers_its_honest_post_mortem():
    """The flip side of the rule above: frustration vs depth MUST be spelled out
    once the tasks are done. Cutting it to satisfy the spoiler test would trade
    a discovery for a missing lesson."""
    closing = next(b for b in LESSONS["06"]["beats"] if b["before"] == "end")
    body = closing["html"].lower()
    assert "frustration" in body
    assert "depth" in body
    assert "quantum advantage" in body, "the honest hardware caveat must survive"


# Basecamps whose Climb Notes have been through editorial review — meaning they
# carry the rule 1 counselling voice, not merely correct physics. All six have
# now had that pass. A new basecamp should be added here only once its notes
# check in on the learner and normalise the places people get stuck.
REVIEWED = {"01", "02", "03", "04", "05", "06"}


@pytest.mark.parametrize("mod_id", sorted(REVIEWED))
def test_reviewed_basecamps_keep_the_counselling_voice(mod_id):
    """Style guide rule 1: check in on the learner, and offer a study tip. The
    notebooks do this constantly — "take a deep breath", "grab a physical pen".
    The browser track originally shipped with none of it, which made it a colder
    teacher than the notebook covering identical ground (a rule 6 break)."""
    beats = LESSONS[mod_id]["beats"]
    notes = [b["reassure"] for b in beats if b.get("reassure")]
    assert notes, f"basecamp {mod_id} has no reassurance notes at all"

    for n in notes:
        assert (n.get("position") or "after") in ("before", "after")
        assert n["html"].strip(), "an empty reassurance is worse than none"
        assert n.get("title", "").strip(), "a note with no heading reads as a warning box"


def test_the_hand_writing_study_tip_survives_across_the_course():
    """The notebooks' signature encouragement is "grab a physical pen and write
    it down". It must not vanish from the browser track — but it must not be
    stamped onto all six basecamps either. Repeating one device everywhere is
    the hollow kind of consistency, and the Summit (where the learner is tuning
    sliders, not deriving anything) has no use for it. So: present across most
    of the course, required nowhere in particular."""
    carrying = [
        mod_id for mod_id, mod in _modules().items()
        if "pen" in " ".join(
            json.dumps(b.get("reassure", {})) for b in mod["beats"]
        ).lower()
    ]
    assert len(carrying) >= 3, (
        f"the write-it-by-hand tip appears in only {carrying} — it is the "
        f"notebooks' signature study tip and should reach the maths-heavy "
        f"basecamps of the browser track too"
    )
    assert "01" in carrying, "Basecamp 1 is where the habit has to be established"


@pytest.mark.parametrize("mod_id", sorted(REVIEWED))
def test_struggle_is_normalised_not_merely_soothed(mod_id):
    """There are two ways to encourage a stuck learner, and they are not equal.

    "Don't worry" reassures by lowering the stakes, and can read as *I don't
    expect you to get this*. "Everyone trips on this one" reassures by locating
    the difficulty in the material rather than in the learner — you are not
    behind, you have arrived exactly where everyone arrives. It keeps the
    standard high and removes the isolation, which is the combination that
    actually keeps people going.

    The notebooks already do this ("This trap catches everyone once", "Be
    honest — nobody can"). The beats must too, or the browser track is the
    lonelier place to get stuck."""
    beats = LESSONS[mod_id]["beats"]
    NORMALISERS = (
        "everyone", "everybody", "nobody", "anyone else", "good company",
        "most common", "common slip", "classic slip", "most people",
    )

    def text(b):
        return (b.get("html", "") + json.dumps(b.get("reassure", {}))
                + json.dumps(b.get("widget", {}))).lower()

    carriers = [b["id"] for b in beats if any(w in text(b) for w in NORMALISERS)]
    assert len(carriers) >= 2, (
        f"basecamp {mod_id} normalises struggle in {carriers or 'no beats'} — a "
        f"learner should meet 'everyone trips here' more than once across a "
        f"basecamp, not only be told not to worry"
    )


@pytest.mark.parametrize("mod_id", sorted(REVIEWED))
def test_heavy_maths_is_preceded_by_a_check_in(mod_id):
    """A beat that opens the trigonometry must warn the learner kindly *before*
    the formulas, not after them — that is the whole point of the placement."""
    for b in LESSONS[mod_id]["beats"]:
        body = b.get("html", "")
        heavy = "cos²" in body or "sin²" in body
        if heavy:
            r = b.get("reassure")
            assert r and (r.get("position") or "after") == "before", (
                f"[{mod_id}/{b['id']}] presents trigonometry with no check-in "
                f"before it — rule 1 asks for the deep breath first"
            )


def test_beats_carry_no_cdn_dependency():
    """lab.html loads no CDN and promises to keep working with the network
    unplugged (unlike module.html, which does load KaTeX). Beats are injected as
    raw HTML, so a stray <script src> or LaTeX delimiter would break that promise
    silently — the maths would simply render as source."""
    for mod_id, mod in _modules().items():
        for b in mod.get("beats", []):
            blob = b.get("html", "") + json.dumps(b.get("math", {}))
            assert "src=\"http" not in blob and "src='http" not in blob, (
                f"[{mod_id}/{b['id']}] pulls in a remote asset"
            )
            assert "\\(" not in blob and "$$" not in blob, (
                f"[{mod_id}/{b['id']}] uses LaTeX, which lab.html cannot render — "
                f"write formulas in Unicode as the rest of the site does"
            )


def test_every_widget_referenced_by_a_beat_exists():
    for mod_id, mod in _modules().items():
        for b in mod.get("beats", []):
            w = b.get("widget")
            if not w:
                continue
            path = REPO / "website" / "widgets" / w["name"] / "index.html"
            assert path.exists(), f"[{mod_id}/{b['id']}] missing widget {w['name']}"
