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


def _read_bundle(path):
    """A widget's HTML plus every local script/style it pulls in.

    Widgets are allowed to share code — circuit-lab mounts the same
    CircuitBuilder component that the graded browser track uses, precisely so
    the two can never drift. The behavioural checks below therefore have to
    look at what the widget actually *ships to the browser*, not just its own
    file, or extracting a component into a shared module would silently look
    like deleting a feature.
    """
    p = Path(path)
    html = _read(p)
    parts = [html]
    for ref in re.findall(r'(?:src|href)\s*=\s*["\']([^"\':]+)["\']', html):
        dep = (p.parent / ref).resolve()
        assert dep.is_file(), f"{p.parent.name} references a missing local file: {ref}"
        parts.append(dep.read_text(encoding="utf-8"))
    return "\n".join(parts)


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
    assert re.search(r"reset", _read_bundle(path), re.IGNORECASE), (
        "widget needs a Reset control (Don Norman: user can always recover)"
    )


@pytest.mark.parametrize("path", WIDGETS, ids=lambda p: Path(p).parent.name)
def test_widget_has_hint_bar(path):
    html = _read(path)
    assert 'class="hint' in html or 'id="hint' in html, (
        "widget needs a hint bar telling the user what to try (discoverability)"
    )


@pytest.mark.parametrize("path", WIDGETS, ids=lambda p: Path(p).parent.name)
def test_widget_local_dependencies_exist(path):
    """A relative src/href that 404s is invisible locally and fatal in
    production, so resolve every one of them."""
    _read_bundle(path)   # asserts each referenced local file is present


@pytest.mark.parametrize("path", WIDGETS, ids=lambda p: Path(p).parent.name)
def test_widget_has_live_text_mirror(path):
    """Accessibility floor: a canvas or a coloured bar is not a readout.

    Every widget must expose its current state as text in an aria-live region,
    so a screen-reader user (or anyone whose graphics failed to render) gets
    the same information at the same moment as everyone else.
    """
    bundle = _read_bundle(path)
    assert "aria-live" in bundle, (
        "widget needs an aria-live text mirror of its state — the primary "
        "teaching artifact must not be sight-only"
    )


def test_coin_spinner_has_bias_slider_and_prediction_ticks():
    """Module 01's 75/25 biased-coin narrative needs the bias slider, and the
    predict-before-you-look principle needs the green prediction ticks."""
    html = _read(str(REPO / "website" / "widgets" / "coin-spinner" / "index.html"))
    assert 'id="bias"' in html and 'type="range"' in html, "P(Heads) bias slider missing"
    assert 'id="t0"' in html and 'id="t1"' in html, "prediction tick marks missing"
