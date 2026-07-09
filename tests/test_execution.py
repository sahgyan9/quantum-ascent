"""Execute every solutions/assignment/appendix notebook end-to-end with nbclient.

Student notebooks are NOT executed — their gap-fill holes are intentionally
incomplete. The solutions notebooks are the source of truth and must run clean.
"""

import glob
import os
from pathlib import Path

import nbformat
import pytest

REPO = Path(__file__).resolve().parent.parent

EXECUTABLE = sorted(
    glob.glob(str(REPO / "notebooks" / "solutions" / "*.ipynb"))
    + glob.glob(str(REPO / "notebooks" / "appendix_*.ipynb"))
)


@pytest.mark.parametrize("path", EXECUTABLE, ids=lambda p: Path(p).name)
def test_notebook_executes_clean(path):
    from nbclient import NotebookClient

    # widgets must not require the live site during tests
    os.environ.setdefault("Q2Q_WIDGET_BASE", "http://localhost:8000/widgets")

    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=300,
        kernel_name="python3",
        resources={"metadata": {"path": str(Path(path).parent)}},
    )
    client.execute()  # raises CellExecutionError on any failing cell


def test_there_is_something_to_execute_once_content_lands():
    """Turns red if solutions notebooks vanish after modules exist."""
    student = glob.glob(str(REPO / "notebooks" / "0*.ipynb"))
    if student:
        assert EXECUTABLE, (
            "Student notebooks exist but no solutions notebooks found — "
            "solutions are the source of truth and must be present."
        )
