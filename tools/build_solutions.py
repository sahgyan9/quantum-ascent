"""Generate student notebooks from solutions notebooks (the source of truth).

Usage:
    python tools/build_solutions.py            # regenerate all student notebooks
    python tools/build_solutions.py 01         # only module 01

Rules:
- notebooks/solutions/NN_name_solutions.ipynb  ->  notebooks/NN_name.ipynb
- Inside any code cell, the region between '### BEGIN SOLUTION' and
  '### END SOLUTION' is replaced by a '# YOUR CODE HERE' placeholder
  (indentation preserved).
- A line of the form '### STUDENT SAFETY: <code>' is a no-op comment in the
  solutions notebook (harmless, like the BEGIN/END markers), and is turned
  into real code '<code>' only in the student notebook. Use this to seed a
  blank with e.g. 'qc_spin = None  # remove None and define your circuit'
  directly under the blank it belongs to, so the cell still runs before the
  student fills it in AND the variable name is obvious from context.
- Cells tagged 'solution-only' (cell metadata tags) are dropped entirely.
- All outputs and execution counts are cleared in the student copy.

This guarantees student and solutions versions can never drift.
"""

import re
import sys
from pathlib import Path

import nbformat

REPO = Path(__file__).resolve().parent.parent
SOLUTIONS_DIR = REPO / "notebooks" / "solutions"
STUDENT_DIR = REPO / "notebooks"

PLACEHOLDER = "# YOUR CODE HERE"
REGION = re.compile(
    r"^(?P<indent>[ \t]*)### BEGIN SOLUTION.*?^[ \t]*### END SOLUTION[^\n]*",
    re.DOTALL | re.MULTILINE,
)
SAFETY_LINE = re.compile(
    r"^(?P<indent>[ \t]*)### STUDENT SAFETY: (?P<code>.*)$", re.MULTILINE,
)


def strip_solutions(source: str) -> str:
    source = REGION.sub(lambda m: m.group("indent") + PLACEHOLDER, source)
    return SAFETY_LINE.sub(lambda m: m.group("indent") + m.group("code"), source)


def build_student_notebook(solution_path: Path) -> Path:
    nb = nbformat.read(solution_path, as_version=4)
    kept = []
    for cell in nb.cells:
        tags = cell.get("metadata", {}).get("tags", [])
        if "solution-only" in tags:
            continue
        if cell.cell_type == "code":
            cell.source = strip_solutions(cell.source)
            cell.outputs = []
            cell.execution_count = None
        kept.append(cell)
    nb.cells = kept

    student_name = solution_path.name.replace("_solutions", "")
    out = STUDENT_DIR / student_name
    nbformat.write(nb, out)
    return out


def main() -> None:
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    sources = sorted(SOLUTIONS_DIR.glob(f"{only}*_solutions.ipynb"))
    if not sources:
        sys.exit(f"No solutions notebooks matching '{only}*' in {SOLUTIONS_DIR}")
    for src in sources:
        out = build_student_notebook(src)
        print(f"built {out.relative_to(REPO)}  <-  {src.relative_to(REPO)}")


if __name__ == "__main__":
    main()
