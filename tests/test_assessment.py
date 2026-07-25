"""The pre/post concept diagnostic — structure and pedagogical contract.

This is the page a judge clicks first when looking for evidence of learning
outcomes, and the one an educator collects results from. It shipped for a while
as a stub describing a feature that did not exist; these tests make sure it can
never quietly regress to that.

The content checks are not decoration. The diagnostic's value depends on the
distractors being the *popular myths*, phrased attractively — a test where the
wrong answers are obviously wrong measures reading comprehension, not physics.
"""

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WEB = REPO / "website"
BANK = json.loads((WEB / "assets" / "data" / "assessment.json").read_text(encoding="utf-8"))
PAGE = (WEB / "assessment.html").read_text(encoding="utf-8")


def test_ten_questions():
    assert len(BANK["questions"]) == 10, "the diagnostic is advertised as ten questions"


def test_every_question_is_well_formed():
    seen = set()
    for q in BANK["questions"]:
        assert q["id"] not in seen, f"duplicate question id {q['id']}"
        seen.add(q["id"])
        assert len(q["options"]) >= 3, f"{q['id']}: too few options to be diagnostic"
        assert 0 <= q["answer"] < len(q["options"]), f"{q['id']}: answer index out of range"
        assert q["q"].strip().endswith("?"), f"{q['id']}: question should ask something"
        assert len(q["why"]) > 80, f"{q['id']}: explanation is too thin to teach anything"
        assert q["concept"] and q["basecamp"], f"{q['id']}: needs concept + basecamp for the breakdown"


def test_answers_are_not_all_in_one_position():
    """A learner who notices every answer is option B scores 10/10 knowing nothing."""
    positions = [q["answer"] for q in BANK["questions"]]
    assert len(set(positions)) > 1, f"every correct answer sits at index {positions[0]}"


def test_every_basecamp_is_represented():
    camps = {q["basecamp"] for q in BANK["questions"]}
    assert camps == {"01", "02", "03", "04", "05", "06"}, f"coverage gap: {sorted(camps)}"


def test_the_myths_appear_as_distractors():
    """The course's stated moat is myth-avoidance, so the diagnostic has to
    actually offer the myths — otherwise it cannot detect whether they were
    dislodged. Each phrase below must appear as a WRONG option somewhere."""
    myths = [
        "0 and 1 at the same time",
        "tries every possible answer at once",
        "parallel universe",
        "faster-than-light",
    ]
    wrong_options = []
    for q in BANK["questions"]:
        for i, opt in enumerate(q["options"]):
            if i != q["answer"]:
                wrong_options.append(opt.lower())
    blob = " || ".join(wrong_options)
    for myth in myths:
        assert myth.lower() in blob, f"the myth {myth!r} is never offered as a distractor"


def test_no_myth_is_ever_a_correct_answer():
    """The inverse, and the more important direction."""
    banned = ["at the same time", "tries all", "tries every possible answer at once",
              "parallel universe", "faster-than-light"]
    for q in BANK["questions"]:
        correct = q["options"][q["answer"]].lower()
        for phrase in banned:
            assert phrase not in correct, (
                f"{q['id']}: the correct answer contains the myth phrase {phrase!r}"
            )


def test_page_is_no_longer_a_stub():
    """It once shipped saying a feature was 'on the way'. Never again."""
    for phrase in ["on the way", "coming soon", "under construction"]:
        assert phrase not in PAGE.lower(), f"assessment.html still promises something: {phrase!r}"
    assert "assessment.json" in PAGE, "the page must actually load the question bank"


def test_pretest_does_not_reveal_answers():
    """The measurement is only valid if the before-test teaches nothing.

    If the pre-test showed explanations, the post-test would be measuring the
    pre-test rather than the course.
    """
    assert re.search(r"not.{0,40}showing you your score", PAGE, re.I | re.S), (
        "the post-pre-test screen must explicitly withhold the score"
    )
    # `why` text is only rendered from the results view, which requires s.post.
    body = PAGE[PAGE.index("function results()"):]
    assert "q.why" in body, "explanations must render in the results view"
    pre_branch = PAGE[PAGE.index("function runTest"):PAGE.index("function results()")]
    assert "q.why" not in pre_branch, "explanations must never render during the test itself"


def test_results_export_includes_ledger_and_progress():
    """An educator collecting JSON needs all three signals in one file."""
    assert "assessment: load()" in PAGE
    assert "Ledger.entries()" in PAGE
    assert "Progress.get()" in PAGE
