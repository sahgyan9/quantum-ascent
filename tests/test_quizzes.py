"""The website quiz bank: structural integrity, and cumulative retrieval.

Two gaps this closes.

**It was untested.** `notebooks/q2q/quiz.py` — the *notebook* quiz bank — has had
thorough validation since it was written (tests/test_quiz.py). The website bank
in `website/assets/data/quizzes.json`, which is what every browser-track learner
actually answers, had none. An out-of-range `answer` index would have shipped as
a question with no correct option and nothing would have caught it.

**It had no spacing.** Every quiz tested only its own basecamp, so a learner
finished Basecamp 1 and was never asked about it again. Retrieval practice and
distributed practice are the two techniques Dunlosky et al. (2013) rate "high
utility" — above anything else in the course's pedagogy — and the course used
neither. Each quiz from Basecamp 2 on now carries one question that reaches back.

The spacing is deliberate rather than uniform: Basecamp 1 is retrieved twice at
expanding intervals (quizzes 2 and 3), and every recall is placed in the camp
where that idea is about to be used again — endianness just before the Summit
reads a bitstring off a register, ⟨ZZ⟩ just before Max-Cut is encoded with it.
Retrieval plus an immediate reason to care.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BANK = json.loads(
    (REPO / "website" / "assets" / "data" / "quizzes.json").read_text(encoding="utf-8")
)
MODULES = sorted(BANK)


# ------------------------------------------------------------ structural
@pytest.mark.parametrize("mod", MODULES)
def test_every_question_is_well_formed(mod):
    for i, q in enumerate(BANK[mod]):
        where = f"{mod}[{i}]"
        assert q.get("q", "").strip(), f"{where}: empty question"
        opts = q.get("options", [])
        assert 2 <= len(opts) <= 5, f"{where}: need 2-5 options, got {len(opts)}"
        assert all(str(o).strip() for o in opts), f"{where}: blank option"
        assert len(set(opts)) == len(opts), f"{where}: duplicate options"
        assert isinstance(q.get("answer"), int), f"{where}: answer must be an index"
        assert q["answer"] in range(len(opts)), (
            f"{where}: answer index {q['answer']} is out of range for {len(opts)} options — "
            f"this question has no correct button"
        )
        assert q.get("explain", "").strip(), (
            f"{where}: no explanation. Style guide rule 8 — a checker that only says "
            f"'wrong' teaches nothing"
        )


@pytest.mark.parametrize("mod", MODULES)
def test_latex_delimiters_are_balanced(mod):
    """module.html renders these through KaTeX. An odd number of $ leaves half the
    question as raw source on the page, which looks like a broken site."""
    for i, q in enumerate(BANK[mod]):
        blob = " ".join([q["q"], *map(str, q["options"]), q["explain"]])
        singles = len(re.findall(r"(?<!\$)\$(?!\$)", blob))
        assert singles % 2 == 0, f"{mod}[{i}]: odd number of $ delimiters ({singles})"


def test_the_quiz_bank_covers_every_basecamp():
    modules = json.loads(
        (REPO / "website" / "assets" / "data" / "modules.json").read_text(encoding="utf-8")
    )["modules"]
    assert MODULES == sorted(m["id"] for m in modules)


# ------------------------------------------------------- cumulative retrieval
def _recalls(mod):
    return [q for q in BANK[mod] if q.get("recall")]


def test_every_basecamp_after_the_first_reaches_back():
    missing = [m for m in MODULES if m != "01" and not _recalls(m)]
    assert not missing, (
        f"basecamps {missing} test only themselves. Without a backward-looking "
        f"question a learner meets each idea once and never retrieves it again, "
        f"which is the single largest evidence-backed gap this course had"
    )


@pytest.mark.parametrize("mod", [m for m in MODULES if m != "01"])
def test_recall_questions_point_strictly_backwards(mod):
    for q in _recalls(mod):
        target = q["recall"]
        assert target in BANK, f"{mod}: recalls unknown basecamp {target!r}"
        assert target < mod, (
            f"{mod}: recalls basecamp {target}, which the learner has not reached — "
            f"a recall question must test something already taught"
        )


def test_the_first_basecamp_has_nothing_to_recall():
    """Not a technicality: it documents why 01 is exempt, so nobody later 'fixes'
    the asymmetry by inventing a recall question with no prior camp to draw on."""
    assert not _recalls("01")


def test_recall_load_stays_light():
    """One per quiz. Spaced practice works by being frequent and small; turning
    each quiz into a cumulative exam would trade the effect for a chore."""
    for mod in MODULES:
        assert len(_recalls(mod)) <= 1, f"{mod} has {len(_recalls(mod))} recall questions"


def test_basecamp_one_is_retrieved_more_than_once():
    """It carries the Born rule and the half-angle, which every later basecamp
    leans on, so it earns a second retrieval at a longer interval."""
    targets = [q["recall"] for m in MODULES for q in _recalls(m)]
    assert targets.count("01") >= 2, (
        f"Basecamp 1 is retrieved {targets.count('01')} time(s); the ideas the "
        f"whole course rests on should come back at expanding intervals"
    )


def test_passing_still_allows_exactly_one_mistake():
    """quiz.js completes a basecamp at >= 70%. Adding a fifth question must not
    quietly raise the bar: 3/4 and 4/5 both allow one wrong answer, 2/4 and 3/5
    both fail. Check it rather than trust the arithmetic."""
    for mod in MODULES:
        n = len(BANK[mod])
        allowed = max(k for k in range(n + 1) if (n - k) / n >= 0.7)
        assert allowed == 1, (
            f"basecamp {mod}: {n} questions lets you get {allowed} wrong at the 70% "
            f"threshold — the pass bar shifted when the question count changed"
        )
