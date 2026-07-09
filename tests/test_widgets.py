"""Smoke checks for the interactive HTML widgets.

Widgets must be self-contained (no external scripts/styles — a judge opening
the file offline gets the full experience) and Don Norman compliant:
a visible Reset control and a hint bar telling the user what to try.
"""

import glob
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
WIDGETS = sorted(glob.glob(str(REPO / "website" / "widgets" / "*" / "index.html")))

ALLOWED_EXTERNAL = ()  # widgets get NO external resources, not even CDNs


def _read(path):
    return Path(path).read_text(encoding="utf-8")


@pytest.mark.parametrize("path", WIDGETS, ids=lambda p: Path(p).parent.name)
def test_widget_has_title(path):
    assert re.search(r"<title>[^<]+</title>", _read(path)), "widget needs a <title>"


@pytest.mark.parametrize("path", WIDGETS, ids=lambda p: Path(p).parent.name)
def test_widget_is_self_contained(path):
    html = _read(path)
    external = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', html)
    bad = [u for u in external if not u.startswith(ALLOWED_EXTERNAL)]
    assert not bad, f"widget loads external resources (breaks offline use): {bad}"


@pytest.mark.parametrize("path", WIDGETS, ids=lambda p: Path(p).parent.name)
def test_widget_has_reset_control(path):
    html = _read(path)
    assert re.search(r"reset", html, re.IGNORECASE), (
        "widget needs a Reset control (Don Norman: user can always recover)"
    )


@pytest.mark.parametrize("path", WIDGETS, ids=lambda p: Path(p).parent.name)
def test_widget_has_hint_bar(path):
    html = _read(path)
    assert 'class="hint' in html or 'id="hint' in html, (
        "widget needs a hint bar telling the user what to try (discoverability)"
    )
