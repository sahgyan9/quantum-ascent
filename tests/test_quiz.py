"""Unit tests for q2q.quiz — inline concept quizzes.

Contract: quiz.ask(qid) renders a self-contained interactive question with
per-option coaching feedback (checkers' green/red visual language), never
raises inside a student notebook, and works headless (plain text, no spoilers).
"""

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "notebooks"))

from q2q import quiz  # noqa: E402


# ---------------------------------------------------------------- bank integrity

def test_bank_is_nonempty():
    assert len(quiz._BANK) >= 1


def test_bank_entries_are_well_formed():
    for qid, q in quiz._BANK.items():
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", qid), (
            f"{qid}: quiz ids must be kebab-case")
        assert isinstance(q["question"], str) and q["question"].strip()
        assert 2 <= len(q["options"]) <= 5, f"{qid}: need 2-5 options"
        assert all(isinstance(o, str) and o.strip() for o in q["options"])
        assert q["correct"] in range(len(q["options"])), (
            f"{qid}: correct index out of range")
        assert len(q["feedback"]) == len(q["options"]), (
            f"{qid}: every option needs its own coaching feedback")
        assert all(isinstance(f, str) and f.strip() for f in q["feedback"])


def test_unknown_quiz_id_raises_with_known_ids_listed():
    with pytest.raises(KeyError) as exc:
        quiz.ask("no-such-quiz")
    assert "no-such-quiz" in str(exc.value)


# ---------------------------------------------------------------- rendering

def _any_qid():
    return next(iter(quiz._BANK))


def test_html_contains_question_options_and_both_verdicts():
    qid = _any_qid()
    q = quiz._BANK[qid]
    html = quiz._render_html(q)
    assert q["question"] in html
    for opt in q["options"]:
        assert opt.replace("&", "&amp;") in html or opt in html
    # both feedback faces must be wired in so clicking gives instant feedback
    assert "✅" in html and "❌" in html
    # one clickable button per option
    assert html.count("<button") == len(q["options"])


def test_html_is_self_contained():
    """Widget rule from CLAUDE.md applies to inline quizzes too: no external
    resources — the quiz must work offline and inside any notebook host."""
    for q in quiz._BANK.values():
        html = quiz._render_html(q)
        assert "http://" not in html and "https://" not in html
        assert "src=" not in html


def test_two_renders_do_not_collide():
    """JupyterLab keeps every output in one shared DOM — element ids must be
    unique per render or clicking quiz A would answer quiz B."""
    q = quiz._BANK[_any_qid()]
    ids_a = set(re.findall(r'id="([^"]+)"', quiz._render_html(q)))
    ids_b = set(re.findall(r'id="([^"]+)"', quiz._render_html(q)))
    assert ids_a and ids_b and not (ids_a & ids_b)


# ---------------------------------------------------------------- headless path

def test_headless_ask_prints_question_without_spoilers(capsys):
    qid = _any_qid()
    q = quiz._BANK[qid]
    assert quiz.ask(qid) is None  # never raises, returns nothing
    out = capsys.readouterr().out
    assert q["options"][0][:20] in out
    for fb in q["feedback"]:
        assert fb[:30] not in out, "headless print must not spoil the answer"


# ---------------------------------------------------------------- notebook wiring

def test_notebook_quiz_ids_exist_in_bank():
    """Every quiz.ask("...") in any course notebook must reference a real id."""
    import glob

    import nbformat

    for path in glob.glob(str(REPO / "notebooks" / "**" / "*.ipynb"),
                          recursive=True):
        nb = nbformat.read(path, as_version=4)
        code = "\n".join(c.source for c in nb.cells if c.cell_type == "code")
        for qid in re.findall(r'quiz\.ask\(\s*["\']([^"\']+)["\']', code):
            assert qid in quiz._BANK, (
                f"{Path(path).name}: quiz.ask('{qid}') has no bank entry")


def test_module_01_has_inline_quizzes():
    import nbformat

    nb = nbformat.read(
        str(REPO / "notebooks" / "01_qubits_and_superposition.ipynb"),
        as_version=4)
    code = "\n".join(c.source for c in nb.cells if c.cell_type == "code")
    assert code.count("quiz.ask(") >= 3
