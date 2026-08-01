"""The style guide must not claim enforcement it does not have.

`docs/pedagogical_style_guide.md` is published so that a judge can check the
content against our own stated rules, and so an educator forking the course
knows the house style. That only works if the document is true.

It used to overstate slightly: it closed with "enforced in review, and partly in
CI", but every check it named was mechanical — LaTeX macros, notebook drift,
execution. No *pedagogical* rule was enforced anywhere. Rules 10-12 changed that,
and the guide now names the specific files that enforce them.

Naming files in prose is a promise with a short shelf life: rename a test module
and the guide silently starts lying. These tests hold the two halves together —
the rules exist in the document, the files it points at exist on disk, and the
gap it admits to is still admitted rather than quietly dropped.

Rule 9 says being trustworthy is the product. This is that rule turned on the
guide itself.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GUIDE = REPO / "docs" / "pedagogical_style_guide.md"
TEXT = GUIDE.read_text(encoding="utf-8")

# Rules the guide states AND claims are machine-checked.
ENFORCED_RULES = {
    "10": "Teach before you ask",
    "11": "Retrieve, don't just cover",
    "12": "Normalise the struggle",
}


@pytest.mark.parametrize("num,heading", sorted(ENFORCED_RULES.items()))
def test_rule_is_present_with_its_heading(num, heading):
    pattern = re.compile(rf"^## {num}\. .*", re.M)
    m = pattern.search(TEXT)
    assert m, f"rule {num} is missing from the style guide"
    assert heading.lower() in m.group(0).lower(), (
        f"rule {num} is titled {m.group(0)!r}; expected it to be about {heading!r}"
    )


def test_rules_are_numbered_without_gaps_or_repeats():
    nums = [int(n) for n in re.findall(r"^## (\d+)\. ", TEXT, re.M)]
    assert nums == sorted(nums), f"rules are out of order: {nums}"
    assert len(nums) == len(set(nums)), f"duplicate rule numbers: {nums}"
    assert nums == list(range(nums[0], nums[0] + len(nums))), f"gap in numbering: {nums}"


def test_every_file_the_guide_names_as_enforcement_actually_exists():
    """The guide points at test modules and tools by path. If one is renamed,
    the document becomes false in a way no reader can detect."""
    referenced = set(re.findall(r"`((?:tests|tools|docs)/[\w./-]+)`", TEXT))
    assert referenced, "the guide no longer names any enforcing file — did the claims get cut?"
    missing = sorted(p for p in referenced if not (REPO / p).exists())
    assert not missing, f"the style guide names files that do not exist: {missing}"


def test_the_unenforced_gap_is_still_declared():
    """Rule 4 and rule 7 apply at full strength all the way to the summit; the
    scaffolding never fades. That is a real gap, the guide admits it, and the
    admission should not quietly disappear the next time this file is tidied."""
    tail = TEXT[TEXT.rindex("---"):]
    assert "not** yet enforced" in tail or "not yet enforced" in tail, (
        "the guide no longer states which of its rules are unenforced"
    )
    assert "future_improvements" in tail, (
        "the admitted gap should point a reader to where it is written up"
    )


def test_the_gap_is_written_up_where_the_guide_says_it_is():
    fut = (REPO / "docs" / "future_improvements.md").read_text(encoding="utf-8")
    assert re.search(r"^## \d+\. Fading the scaffolding", fut, re.M), (
        "the style guide defers the fading gap to future_improvements.md, "
        "which does not cover it"
    )


def test_future_improvements_sections_are_numbered_cleanly():
    nums = [int(n) for n in re.findall(r"^## (\d+)\. ",
            (REPO / "docs" / "future_improvements.md").read_text(encoding="utf-8"), re.M)]
    assert len(nums) == len(set(nums)), f"duplicate section numbers: {nums}"
    assert nums == sorted(nums), f"sections out of order: {nums}"
