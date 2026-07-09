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


def test_course_notebooks_have_no_gdef_macros():
    """Custom \\gdef macros aren't reliably carried across cells by every
    renderer (VSCode's KaTeX doesn't persist \\gdef the way MathJax does),
    which used to cause "Undefined control sequence" ParseErrors. Notebooks
    must ship only plain, renderer-portable LaTeX — see q2q/latex_macros.py.
    """
    house_macro_names = ("ket", "bra", "braket", "sqrttwo", "mymatrix",
                          "myvector", "hadamard")
    for path in _course_notebooks():
        nb = nbformat.read(path, as_version=4)
        sources = [c.source for c in nb.cells if c.cell_type == "markdown"]
        text = "\n".join(sources)
        assert r"\gdef" not in text, (
            f"{Path(path).name}: contains a \\gdef — macros must be expanded "
            f"to plain LaTeX at generation time (see q2q.latex_macros.expand)"
        )
        for name in house_macro_names:
            assert f"\\{name}" not in text, (
                f"{Path(path).name}: unexpanded house macro \\{name} found — "
                f"run the tools/make_module_NN.py generator to regenerate"
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
