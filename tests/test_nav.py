"""Navigation structure: the nav must physically fit, and its shape must teach
the route.

The nav is a fixed pill — 940px wide, 52px tall (see site.css). Six flat links
plus the sign-in button plus the XP pill wanted roughly 1120px inside it, so
every label wrapped onto two lines at *every* desktop width. It looked broken
because it was broken.

The deeper problem was editorial, not typographic. Three of those six links are
steps on the route (Start here / The Ascent / Diagnostic) and three are
reference material you dip into (Widget Gallery, Analogy Studio, Myth Autopsy).
Presented as six equal peers, nothing told a newcomer which was which — so they
guessed, and skipped Basecamp 0 entirely.

These tests pin both properties: a hard cap on top-level entries so the pill can
never silently overflow again, and the route/toolbox split so the hierarchy
survives future edits.
"""

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
WEB = REPO / "website"

sys.path.insert(0, str(REPO / "tools"))
import build_nav  # noqa: E402  — the generator is the source of truth


def _is_content_page(p):
    # See test_site.py: the Search Console token is a token, not a page.
    return not p.name.startswith("google")


PAGES = sorted(p for p in WEB.glob("*.html") if _is_content_page(p))

# What lives at the top level of the pill, in order. Anything more than this
# does not fit alongside the logo, the sign-in button and the XP pill.
TOP_LEVEL = ["Start here", "The Ascent", "Toolbox", "Diagnostic"]
MAX_TOP_LEVEL = 4

# Reference pages, grouped behind the Toolbox disclosure.
# Derived from the generator rather than restated here. This list used to be a
# hand-kept copy of build_nav.TOOLBOX, which meant adding one Toolbox entry
# failed ten tests for the wrong reason — they were reporting a stale duplicate,
# not a broken nav. What these tests should pin is that the *rendered pages*
# match the declared structure, plus the constraints that are genuinely about
# fit (below).
TOOLBOX = [href for href, _label, _note in build_nav.TOOLBOX]

# The pill itself is capped at MAX_TOP_LEVEL; the disclosure can hold more, but
# not without limit — past this it stops being a menu and becomes a directory.
MAX_TOOLBOX = 6

NAV_BLOCK = re.compile(
    r'<div class="nav-links" id="nav-menu">(.*?)\n  </div>', re.S)


def _text(p):
    return p.read_text(encoding="utf-8")


def _nav(page):
    m = NAV_BLOCK.search(_text(page))
    assert m, f"{page.name} has no recognisable nav-links block"
    return m.group(1)


def _top_level_entries(nav):
    """Direct children of .nav-links that a user sees as a menu entry.

    Links nested inside the Toolbox disclosure do not count — they are one
    click further in, which is the whole point of grouping them.
    """
    without_drop = re.sub(r'<div class="nav-drop">.*?</div>', "", nav, flags=re.S)
    labels = []
    for m in re.finditer(r"<(a|summary)\b[^>]*>(.*?)</\1>", without_drop, re.S):
        text = re.sub(r"<[^>]+>", "", m.group(2))
        labels.append(" ".join(text.split()))
    return labels


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_nav_fits_the_pill(page):
    """Hard cap on top-level entries.

    This is the test that would have caught the wrapping. It is a proxy for
    width, but a reliable one: the pill comfortably fits four short entries
    plus the sign-in button and the XP pill, and does not fit five.
    """
    entries = _top_level_entries(_nav(page))
    assert len(entries) <= MAX_TOP_LEVEL, (
        f"{page.name} nav has {len(entries)} top-level entries "
        f"({entries}) — more than {MAX_TOP_LEVEL} overflows the 940px pill "
        f"and wraps the labels onto two lines")


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_nav_entries_are_the_route_in_order(page):
    """Left-to-right must match the order you actually do things (mapping)."""
    assert _top_level_entries(_nav(page)) == TOP_LEVEL, (
        f"{page.name} nav entries differ from the canonical route")


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_toolbox_is_a_native_disclosure(page):
    """<details>/<summary>, not a JS dropdown.

    It is keyboard-operable and screen-reader-announced for free, and it still
    opens if the JavaScript fails to load. A div-and-click-handler gets none of
    that without work we would have to keep re-proving.
    """
    nav = _nav(page)
    assert "<details" in nav, f"{page.name} Toolbox is not a <details> element"
    assert "<summary>Toolbox</summary>" in nav, (
        f"{page.name} Toolbox has no <summary> — it cannot be opened by keyboard")


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_toolbox_holds_every_reference_page(page):
    """Grouping must not orphan anything: all four are still one click away."""
    m = re.search(r'<div class="nav-drop">(.*?)</div>', _nav(page), re.S)
    assert m, f"{page.name} has no Toolbox contents"
    for href in TOOLBOX:
        assert f'href="{href}"' in m.group(1), (
            f"{page.name} Toolbox is missing {href}")


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_toolbox_entries_say_what_they_are(page):
    """A bare label like 'Analogy Studio' means nothing before you have used it.

    Each entry carries a one-line note, which is the affordance the flat nav
    never had room for — grouping bought us the space to explain.
    """
    m = re.search(r'<div class="nav-drop">(.*?)</div>', _nav(page), re.S)
    notes = re.findall(r'class="nav-drop-note">([^<]+)<', m.group(1))
    assert len(notes) == len(TOOLBOX), (
        f"{page.name}: {len(notes)} Toolbox notes for {len(TOOLBOX)} entries")
    assert len(TOOLBOX) <= MAX_TOOLBOX, (
        f"{len(TOOLBOX)} Toolbox entries — past {MAX_TOOLBOX} the disclosure "
        f"stops being a menu and becomes a directory")


def test_current_page_is_marked_even_inside_the_toolbox():
    """'Where am I?' must survive the grouping.

    A page hidden behind a closed disclosure would otherwise lose its active
    marker entirely, so the disclosure itself carries it.
    """
    for page in PAGES:
        nav = _nav(page)
        if page.name in TOOLBOX:
            assert 'class="nav-group active"' in nav, (
                f"{page.name} lives in the Toolbox but the group is not marked active")
        elif f'href="{page.name}"' in nav:
            assert re.search(rf'href="{re.escape(page.name)}"[^>]*class="active"', nav), (
                f"{page.name} does not mark itself active in the nav")


# ---------------------------------------------------------------- home page

def test_home_page_states_the_route_before_the_basecamps():
    """The complaint this whole change answers: a visitor lands, sees 'Start
    the ascent', and has no idea Kit Check or the diagnostic exist.

    The route has to be on the page, in order, above the basecamp grid.
    """
    html = _text(WEB / "index.html")
    assert 'id="start-here"' in html, "home page has no Start-here section"
    start = html.index('id="start-here"')
    grid = html.index("The route")
    assert start < grid, "Start here must come before the basecamp grid"

    band = html[start:grid]
    for href in ["assessment.html", "kit-check.html", "ascent.html"]:
        assert href in band, f"Start-here band never mentions {href}"


def test_home_page_distinguishes_the_two_tracks():
    """'No install required' is only true of the browser track. The step that
    sends people to Kit Check must say who actually needs it, or notebook users
    hit a wall and browser users do pointless setup."""
    html = _text(WEB / "index.html")
    band = html[html.index('id="start-here"'):html.index("The route")]
    assert "lab.html" in band or "browser" in band.lower(), (
        "Start-here band does not offer the browser track")
    assert "Basecamp 0" in band, (
        "Kit Check is framed as Basecamp 0 on its own page; say so here too")


def test_hero_ctas_do_not_mean_the_same_thing():
    """The hero used to offer 'Start the ascent' and 'Jump into Basecamp 1'
    side by side — two buttons for what is, to a newcomer, one action. The
    secondary one should instead answer the question they actually have, which
    is 'what IS this and where do I begin?'."""
    html = _text(WEB / "index.html")
    hero = html[html.index('class="hero-content"'):html.index('class="hero-visual"')]
    ghost = re.search(r'class="btn ghost"\s+href="([^"]+)"', hero)
    assert ghost, "hero has no secondary action"
    assert ghost.group(1) == "#start-here", (
        f"secondary CTA points at {ghost.group(1)}; it should send an "
        f"unsure visitor to the route, not duplicate the primary button")


def test_anchor_targets_clear_the_fixed_nav():
    """The hero's secondary CTA is an in-page jump, and the nav is fixed 84px
    tall — without scroll-margin the target lands underneath it, so the visitor
    who asked 'where do I begin?' arrives mid-sentence."""
    css = _text(WEB / "assets" / "css" / "site.css")
    assert re.search(r"\[id\]\s*\{[^}]*scroll-margin-top", css), (
        "no scroll-margin-top for anchor targets; #start-here will land "
        "behind the fixed nav pill")


# ---------------------------------------------------------------- coach mark

def test_coach_mark_waits_until_xp_is_earned():
    """The bubble explaining the XP pill used to fire on page load, over the
    hero, to explain a counter reading zero. Feedback follows an action; it
    should appear the moment the first XP lands, when the pill means something.
    """
    js = _text(WEB / "assets" / "js" / "progress.js")
    coach = js[js.index("q2q_seen_pill_coach"):]
    assert "Progress.get().xp === 0" not in coach, (
        "coach mark is still gated on xp === 0, i.e. it fires before the "
        "visitor has done anything")
    assert re.search(r"xp\s*>\s*0", coach), (
        "coach mark should be triggered by earning XP, not by page load")
