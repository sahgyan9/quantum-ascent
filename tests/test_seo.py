"""SEO contract: every page must be indexable, describable, and shareable.

Search and social crawlers are the one audience that cannot ask a question or
click around to work out what a page is. Everything they need has to be in the
static HTML, correct, and unique per page.

This is written as a test rather than a checklist because SEO tags rot silently:
nobody notices a missing canonical or a duplicated description until traffic is
already gone. `tools/build_seo.py` regenerates the managed blocks; this module
is what proves the result is actually right.

Deliberately NOT asserted here: rankings. On-page work makes a page eligible to
rank; it cannot make it rank. See docs/seo.md for what this does and does not buy.
"""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
WEB = REPO / "website"
# Google Search Console drops a verification token at the site root. It is a
# plain-text file that happens to end in .html and it must be served EXACTLY as
# Google generated it — adding a <title> or a nav to it breaks verification. It
# is a token, not a page, so it is excluded from every page-level check.
def _is_content_page(p):
    return not p.name.startswith("google")


PAGES = sorted(p for p in WEB.glob("*.html") if _is_content_page(p))
SITE = "https://quantum-ascent-77617.web.app"

# Query-string pages: one static file serving many logical URLs.
PARAM_PAGES = {"module.html", "lab.html"}


def _text(p):
    return p.read_text(encoding="utf-8")


def _head(p):
    """Just the <head>, so a match in body copy can't fake a passing tag."""
    html = _text(p)
    m = re.search(r"<head\b[^>]*>(.*?)</head>", html, re.S | re.I)
    return m.group(1) if m else html


def _meta(head, attr, value):
    """Content of <meta {attr}="{value}" content="...">, order-independent."""
    pat = re.compile(
        r'<meta[^>]*\b' + attr + r'\s*=\s*["\']' + re.escape(value) + r'["\'][^>]*>',
        re.I)
    m = pat.search(head)
    if not m:
        return None
    c = re.search(r'content\s*=\s*["\'](.*?)["\']', m.group(0), re.S | re.I)
    return c.group(1) if c else None


def _title(head):
    m = re.search(r"<title>(.*?)</title>", head, re.S | re.I)
    return m.group(1).strip() if m else None


# --------------------------------------------------------------- basics

@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_page_has_lang(page):
    assert re.search(r'<html[^>]*\blang\s*=\s*["\']en["\']', _text(page), re.I), (
        "every page needs <html lang> — it drives language targeting and screen-reader voice"
    )


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_title_present_and_sane_length(page):
    t = _title(_head(page))
    assert t, "missing <title>"
    # Google truncates around 60 chars; short titles waste the strongest signal.
    assert 15 <= len(t) <= 65, f"title is {len(t)} chars, want 15-65: {t!r}"
    assert "Quantum Ascent" in t, "keep the brand in every title for disambiguation"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_description_present_and_sane_length(page):
    d = _meta(_head(page), "name", "description")
    assert d, "missing meta description"
    assert 70 <= len(d) <= 165, f"description is {len(d)} chars, want 70-165: {d!r}"


def test_titles_and_descriptions_are_unique():
    """Duplicate titles/descriptions make pages compete with each other."""
    titles, descs = {}, {}
    for p in PAGES:
        h = _head(p)
        t, d = _title(h), _meta(h, "name", "description")
        assert t not in titles, f"{p.name} duplicates the title of {titles.get(t)}"
        assert d not in descs, f"{p.name} duplicates the description of {descs.get(d)}"
        titles[t], descs[d] = p.name, p.name


# ------------------------------------------------------- canonical & robots

@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_canonical_is_absolute_https(page):
    m = re.search(r'<link[^>]*rel\s*=\s*["\']canonical["\'][^>]*>', _head(page), re.I)
    assert m, "missing <link rel=canonical> — required to consolidate duplicate URLs"
    href = re.search(r'href\s*=\s*["\'](.*?)["\']', m.group(0), re.I).group(1)
    assert href.startswith(SITE), f"canonical must be absolute and on-site: {href}"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_no_accidental_noindex(page):
    robots = _meta(_head(page), "name", "robots")
    if robots:
        assert "noindex" not in robots.lower(), f"{page.name} is blocked from indexing"


# ------------------------------------------------------------ social cards

OG_REQUIRED = ["og:title", "og:description", "og:image", "og:url", "og:type", "og:site_name"]


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
@pytest.mark.parametrize("prop", OG_REQUIRED)
def test_open_graph_tags(page, prop):
    v = _meta(_head(page), "property", prop)
    assert v, f"missing {prop}"
    if prop in ("og:image", "og:url"):
        assert v.startswith("https://"), f"{prop} must be an absolute URL, got {v!r}"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_twitter_card(page):
    card = _meta(_head(page), "name", "twitter:card")
    assert card == "summary_large_image", f"want summary_large_image, got {card!r}"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_og_image_dimensions_declared(page):
    """Declaring size lets a crawler lay the card out before fetching the image."""
    assert _meta(_head(page), "property", "og:image:width") == "1200"
    assert _meta(_head(page), "property", "og:image:height") == "630"
    assert _meta(_head(page), "property", "og:image:alt"), "og:image needs alt text"


def test_og_image_file_exists_and_is_correct_size():
    img = WEB / "assets" / "og-image.png"
    assert img.is_file(), "assets/og-image.png missing — social shares will be blank"
    PIL = pytest.importorskip("PIL.Image")
    with PIL.open(img) as im:
        assert im.size == (1200, 630), f"og:image must be 1200x630, got {im.size}"
    assert img.stat().st_size < 900_000, "og:image is too heavy for a preview fetch"


# --------------------------------------------------------------- favicons

@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_favicon_declared(page):
    head = _head(page)
    assert re.search(r'rel\s*=\s*["\'][^"\']*icon', head, re.I), "no favicon link"


def test_favicon_files_exist():
    for name in ("favicon.svg", "favicon.ico", "apple-touch-icon.png"):
        assert (WEB / name).is_file() or (WEB / "assets" / name).is_file(), f"{name} missing"


# ------------------------------------------------------ robots & sitemap

def test_robots_txt():
    r = WEB / "robots.txt"
    assert r.is_file(), "robots.txt missing"
    body = r.read_text(encoding="utf-8")
    assert re.search(r"^User-agent:\s*\*", body, re.M | re.I)
    assert re.search(r"^Sitemap:\s*https://", body, re.M | re.I), (
        "robots.txt must point at the sitemap — it is how a crawler finds every page"
    )
    assert not re.search(r"^Disallow:\s*/\s*$", body, re.M | re.I), (
        "Disallow: / would block the entire site"
    )


def test_sitemap_is_valid_and_complete():
    s = WEB / "sitemap.xml"
    assert s.is_file(), "sitemap.xml missing"
    root = ET.fromstring(s.read_text(encoding="utf-8"))
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    locs = [e.text for e in root.iter(ns + "loc")]
    assert locs, "sitemap has no <loc> entries"

    for loc in locs:
        assert loc.startswith(SITE + "/"), f"sitemap URL not absolute/on-site: {loc}"

    # Every real page must be listed exactly once.
    listed = {loc[len(SITE) + 1:].split("?")[0] or "index.html" for loc in locs}
    for p in PAGES:
        assert p.name in listed, f"{p.name} is missing from sitemap.xml"
    assert len(locs) == len(set(locs)), "sitemap contains duplicate URLs"

    # The six basecamps are the real content; they must be crawlable as URLs.
    for i in range(1, 7):
        want = f"{SITE}/module.html?id={i:02d}"
        assert want in locs, f"sitemap missing basecamp URL {want}"


def test_sitemap_urls_have_no_dead_targets():
    s = ET.fromstring((WEB / "sitemap.xml").read_text(encoding="utf-8"))
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    for e in s.iter(ns + "loc"):
        path = e.text[len(SITE) + 1:].split("?")[0] or "index.html"
        assert (WEB / path).is_file(), f"sitemap points at a missing file: {path}"


# ------------------------------------------------------- structured data

def _jsonld(page):
    out = []
    for m in re.finditer(
            r'<script[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            _text(page), re.S | re.I):
        out.append(json.loads(m.group(1)))   # raises if malformed
    return out


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_jsonld_parses(page):
    """Malformed JSON-LD is worse than none: Google discards the whole block."""
    for block in _jsonld(page):
        assert block.get("@context", "").endswith("schema.org"), "missing @context"
        assert block.get("@type"), "JSON-LD block needs an @type"


def test_home_declares_website_and_course():
    types = {b.get("@type") for b in _jsonld(WEB / "index.html")}
    assert "WebSite" in types, "home page needs WebSite schema (brand/sitelinks)"
    assert "Course" in types, "home page needs Course schema — this IS a course"


def test_course_schema_is_complete():
    course = next(b for b in _jsonld(WEB / "index.html") if b.get("@type") == "Course")
    for field in ("name", "description", "provider", "url"):
        assert course.get(field), f"Course schema missing {field}"
    # Google requires an offer/instance or it will not show the rich result.
    assert course.get("hasCourseInstance"), "Course needs hasCourseInstance to be eligible"


def test_myths_page_declares_faq():
    """The Myth Autopsy is literally a list of question/answer pairs, which is
    the single best rich-result opportunity on the site."""
    blocks = _jsonld(WEB / "myths.html")
    faq = next((b for b in blocks if b.get("@type") == "FAQPage"), None)
    assert faq, "myths.html should declare FAQPage schema"
    qs = faq.get("mainEntity", [])
    assert len(qs) >= 5, f"FAQPage should carry every myth, found {len(qs)}"
    for q in qs:
        assert q.get("@type") == "Question"
        assert q.get("name"), "each Question needs its text"
        ans = q.get("acceptedAnswer", {})
        assert ans.get("@type") == "Answer" and ans.get("text"), "each Question needs an Answer"


def test_breadcrumbs_on_subpages():
    for name in ("myths.html", "assessment.html", "kit-check.html"):
        types = {b.get("@type") for b in _jsonld(WEB / name)}
        assert "BreadcrumbList" in types, f"{name} should declare BreadcrumbList"


# ---------------------------------------------------- query-string pages

@pytest.mark.parametrize("name", sorted(PARAM_PAGES))
def test_param_pages_set_canonical_at_runtime(name):
    """module.html and lab.html serve six logical URLs each from one file.

    The static canonical can only name one of them, so the page must rewrite
    canonical/og:url once it knows its ?id= — otherwise all six basecamps
    collapse into one indexed URL and five of them are invisible.
    """
    body = _text(WEB / name)
    assert re.search(r'rel\s*=\s*["\']canonical["\']', body), "no canonical to rewrite"

    # Find a script that reads ?id= and writes the canonical back.
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", body, re.S | re.I)
    rewriter = [s for s in scripts
                if "canonical" in s and re.search(r'["\']id["\']', s)]
    assert rewriter, f"{name} has no script that rewrites canonical for the current ?id="

    src = rewriter[0]
    assert "setAttribute" in src, "the rewriter must actually write the href"
    assert "og:url" in src, "og:url must be corrected alongside canonical"

    # It has to run in the head, before the page renders — a crawler that
    # snapshots early must already see the corrected value.
    head_end = body.lower().index("</head>")
    assert body.index(src) < head_end, "the canonical rewriter must live in <head>"
