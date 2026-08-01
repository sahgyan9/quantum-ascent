"""Two stylesheets must not quietly fight over the same class name.

The bug this exists to prevent shipped, and it was invisible to every other
test in this suite:

    site.css            .track { padding: 14px 16px; ... }   /* a content card */
    circuit-builder.css .track { height: 15px; ... }         /* a probability bar */

Any page loading both (lab.html, myths.html) applied the card's 28px of vertical
padding to the bar rail. With border-box sizing that swallows the 15px height,
the content box collapses to zero, and the `.fill { height: 100% }` inside
resolves to 0px. Every Born-rule bar in the graded browser track rendered as an
empty rail — correct percentages beside a bar that showed nothing.

That is a direct violation of style guide rule 5, which calls the state-vector
rule non-negotiable: "A visual that is merely suggestive of the probabilities is
a bug." The numbers were right, so the checkers passed, the physics tests passed,
and the one thing a learner actually looks at was blank.

The rule enforced here: when two stylesheets loaded by the same page both define
a *bare* class selector (`.foo`, not `.scope .foo`), the later one must
re-declare every box-model property the earlier one sets. Scoped additions like
`.cb-root .panel` are deliberate layering and are left alone.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
WEBSITE = REPO / "website"

# Properties where an inherited surprise silently changes geometry.
BOX_PROPS = {"padding", "margin", "height", "width", "display", "box-sizing", "position"}

BARE_CLASS = re.compile(r"^\.([A-Za-z][\w-]*)$")
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
LINK = re.compile(r"""<link[^>]+rel=["']stylesheet["'][^>]+href=["']([^"']+)["']""", re.I)
STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)


def _strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def _bare_class_rules(css):
    """{class_name: set(of box properties it declares)} for bare `.foo` rules."""
    found = {}
    for sel_blob, body in RULE.findall(_strip_comments(css)):
        for sel in sel_blob.split(","):
            m = BARE_CLASS.match(sel.strip())
            if not m:
                continue
            props = {
                d.split(":", 1)[0].strip().lower()
                for d in body.split(";")
                if ":" in d
            }
            found.setdefault(m.group(1), set()).update(props & BOX_PROPS)
    return found


def _sheets_for(page: Path):
    """Every stylesheet a page applies, in load order: (label, css_text)."""
    html = page.read_text(encoding="utf-8")
    sheets = []
    for href in LINK.findall(html):
        if href.startswith(("http://", "https://", "//")):
            continue  # a CDN sheet is not ours to police
        path = (page.parent / href).resolve()
        if path.exists():
            sheets.append((href, path.read_text(encoding="utf-8")))
    for i, block in enumerate(STYLE.findall(html)):
        sheets.append((f"{page.name} inline <style> #{i + 1}", block))
    return sheets


PAGES = sorted(WEBSITE.glob("*.html")) + sorted(WEBSITE.glob("widgets/*/index.html"))


@pytest.mark.parametrize("page", PAGES, ids=lambda p: str(p.relative_to(WEBSITE)))
def test_no_unhandled_bare_class_collision(page):
    sheets = _sheets_for(page)
    if len(sheets) < 2:
        pytest.skip("single stylesheet — nothing can collide")

    parsed = [(label, _bare_class_rules(css)) for label, css in sheets]
    problems = []

    for i, (earlier_label, earlier) in enumerate(parsed):
        for later_label, later in parsed[i + 1:]:
            for cls in set(earlier) & set(later):
                unhandled = earlier[cls] - later[cls]
                if unhandled:
                    problems.append(
                        f".{cls}: {earlier_label} sets {sorted(unhandled)} and "
                        f"{later_label} redefines .{cls} without re-declaring "
                        f"{'it' if len(unhandled) == 1 else 'them'} — the two "
                        f"meanings of .{cls} will blend"
                    )

    assert not problems, f"{page.name} has colliding class definitions:\n  " + "\n  ".join(problems)


def test_probability_rails_pin_their_own_padding():
    """The specific regression, stated directly: a bar rail sets an explicit
    height, so it must also pin padding — otherwise any stray `.track` rule
    elsewhere collapses its content box and the fill inside becomes invisible."""
    targets = [
        WEBSITE / "assets" / "css" / "circuit-builder.css",
        WEBSITE / "myths.html",
    ]
    for path in targets:
        css = _strip_comments(path.read_text(encoding="utf-8"))
        rails = [
            body for sel, body in RULE.findall(css)
            if any(BARE_CLASS.match(s.strip()) and s.strip() == ".track" for s in sel.split(","))
        ]
        assert rails, f"no .track rule found in {path.name}"
        for body in rails:
            props = {d.split(":", 1)[0].strip().lower() for d in body.split(";") if ":" in d}
            if "height" in props:
                assert "padding" in props, (
                    f"{path.name}: .track sets an explicit height but no padding — "
                    f"a colliding .track rule will collapse the bar and hide the fill"
                )
