#!/usr/bin/env python3
"""Own the navigation block on every page, the way build_seo.py owns <head>.

Why a generator instead of nine hand-edited copies: the nav was already
byte-identical across all nine pages apart from one `class="active"` marker, so
every change meant nine edits and one chance in nine of a silent drift. Worse,
the drift is invisible — a missing link in one page's nav is not a broken link,
it is just a dead end nobody notices.

Structure (see tests/test_nav.py for the contract):

    Start here · The Ascent · Toolbox ▾ · Diagnostic     [Sign in]  ⚡ XP

Four top-level entries, because that is what fits in the 940px pill next to the
logo, the sign-in button and the XP pill. The three reference pages plus Kit
Check live behind the Toolbox disclosure — grouped not to save space but to say
something: the top level is the route, the Toolbox is what you reach for along
the way.

Usage:
    python tools/build_nav.py            # rewrite the nav on every page
    python tools/build_nav.py --check    # fail if any page is out of date
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WEB = REPO / "website"

# Pages whose "you are here" marker belongs on The Ascent: they are steps on
# the route rather than destinations in their own right.
UNDER_ASCENT = {"ascent.html", "module.html", "lab.html"}

# Reference pages, grouped behind the disclosure. The note is not decoration —
# a bare "Analogy Studio" is meaningless until you have already used it once,
# and grouping is what bought us the room to explain.
TOOLBOX = [
    ("widgets.html", "Widget Gallery", "All 12 interactive widgets in one place"),
    ("analogy-studio.html", "Analogy Studio", "Quantum explained through your own hobby"),
    ("myths.html", "Myth Autopsy", "Nine pop-science myths, dissected"),
    ("kit-check.html", "Kit Check", "Basecamp 0 · set up Python and Qiskit"),
]

NAV_RE = re.compile(r"<nav id=\"nav\">.*?</nav>", re.S)


def _toolbox(page):
    rows = []
    for href, label, note in TOOLBOX:
        active = ' class="active"' if page == href else ""
        rows.append(
            f'        <a href="{href}"{active}>{label}'
            f'<span class="nav-drop-note">{note}</span></a>')
    open_group = " active" if page in {h for h, _, _ in TOOLBOX} else ""
    return open_group, "\n".join(rows)


def nav_for(page):
    """The complete <nav> block for one page filename."""
    group_active, rows = _toolbox(page)
    here = ' class="active"' if page == "index.html" else ""
    ascent = ' class="active"' if page in UNDER_ASCENT else ""
    diag = ' class="active"' if page == "assessment.html" else ""
    return f"""<nav id="nav">
  <a href="index.html" class="nav-name"><img src="assets/logo.svg" alt="" width="24" height="24"> Quantum <span>Ascent</span></a>
  <a href="#nav-menu" class="nav-burger" id="nav-burger" aria-label="Toggle menu">
    <span></span><span></span><span></span>
  </a>
  <div class="nav-links" id="nav-menu">
    <a href="index.html#start-here"{here}>Start here</a>
    <a href="ascent.html"{ascent}>The Ascent</a>
    <details class="nav-group{group_active}">
      <summary>Toolbox</summary>
      <div class="nav-drop">
{rows}
      </div>
    </details>
    <a href="assessment.html"{diag}>Diagnostic</a>
    <span id="xp-pill">⚡ 0 XP · 0/6</span>
  </div>
</nav>"""


def pages():
    # The Search Console token ends in .html but is a plain-text token, not a
    # page — giving it a nav would break domain verification.
    return sorted(p for p in WEB.glob("*.html") if not p.name.startswith("google"))


def main(argv):
    check = "--check" in argv
    stale = []
    for p in pages():
        html = p.read_text(encoding="utf-8")
        want = nav_for(p.name)
        if not NAV_RE.search(html):
            stale.append(f"{p.name}: no <nav id=\"nav\"> block found")
            continue
        new = NAV_RE.sub(lambda _: want, html, count=1)
        if new == html:
            continue
        if check:
            stale.append(f"{p.name}: nav is out of date")
        else:
            p.write_text(new, encoding="utf-8")
            print(f"updated {p.name}")

    if stale:
        print("\n".join(stale), file=sys.stderr)
        return 1
    print("nav up to date" if check else "done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
