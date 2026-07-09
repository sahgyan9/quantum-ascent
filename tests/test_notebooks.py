"""Sanity checks that run before any feature work is added, per the stability-first rule in CLAUDE.md."""
import glob
import sys
from pathlib import Path

import nbformat

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "notebooks"))


def _all_notebooks():
    return glob.glob(str(REPO / "notebooks" / "**" / "*.ipynb"), recursive=True)


def _course_notebooks():
    """Student-facing module notebooks (01_..06_) and their solutions."""
    return [p for p in _all_notebooks()
            if Path(p).name[0].isdigit() or "solutions" in Path(p).parts]


def test_all_notebooks_are_valid_nbformat():
    for path in _all_notebooks():
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)


def test_course_notebooks_have_house_macro_cell():
    from q2q.latex_macros import MACROS

    for path in _course_notebooks():
        nb = nbformat.read(path, as_version=4)
        sources = [c.source for c in nb.cells if c.cell_type == "markdown"]
        assert any(r"\gdef\ket" in s for s in sources), (
            f"{Path(path).name}: missing the house LaTeX macro cell "
            f"(q2q.latex_macros.MACROS)"
        )
        # the macro cell must be the canonical one, not a drifted copy
        macro_cells = [s for s in sources if r"\gdef\ket" in s]
        assert MACROS in macro_cells, (
            f"{Path(path).name}: macro cell differs from q2q.latex_macros.MACROS"
        )


def test_student_notebooks_reference_checkers():
    """Every student module notebook must contain at least one self-check call."""
    student = glob.glob(str(REPO / "notebooks" / "0*.ipynb"))
    for path in student:
        nb = nbformat.read(path, as_version=4)
        code = "\n".join(c.source for c in nb.cells if c.cell_type == "code")
        assert "check_" in code, (
            f"{Path(path).name}: no q2q checker calls found — students need "
            f"immediate feedback on their answers"
        )


def test_bootstrap_cell_identical_across_course_notebooks():
    """The Colab/setup bootstrap cell must not drift between notebooks."""
    bootstraps = {}
    for path in _course_notebooks():
        nb = nbformat.read(path, as_version=4)
        cells = [c.source for c in nb.cells
                 if c.cell_type == "code" and "_ensure_q2q" in c.source]
        if cells:
            bootstraps[Path(path).name] = cells[0]
    if len(bootstraps) > 1:
        canonical = next(iter(bootstraps.values()))
        for name, src in bootstraps.items():
            assert src == canonical, f"{name}: bootstrap cell drifted"
