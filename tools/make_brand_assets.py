"""Generate the social-share image and favicons from the Quantum Ascent mark.

Run:  python tools/make_brand_assets.py

Why generated rather than hand-drawn: the logo geometry lives in exactly one
place (website/assets/logo.svg, mirrored by MARK below), so the favicon, the
touch icon and the 1200x630 Open Graph card can never drift away from the mark
used on the site itself.

Everything is drawn supersampled at 4x and downscaled, because PIL has no
antialiased primitives — drawing a 42px circle directly gives visibly jagged
edges, and a jagged favicon is the kind of small thing that reads as unfinished.

No cairosvg dependency: the mark is simple enough (one circle, one polyline,
one dot) to draw directly, and adding a native-binary dependency to a project
whose whole pitch is "clone it and it works" would be a poor trade.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
WEB = REPO / "website"
ASSETS = WEB / "assets"

# Brand tokens — keep in sync with website/assets/css/site.css :root
PAPER = (248, 246, 241)
PAPER2 = (241, 238, 230)
INK = (26, 26, 24)
GREEN = (31, 122, 77)
MUTED = (107, 104, 96)
LINE = (226, 223, 216)

SS = 4  # supersampling factor

# The mark, in the logo.svg 100x100 coordinate space.
MARK_CIRCLE = (50, 50, 42)                                   # cx, cy, r
MARK_PATH = [(18, 66), (40, 38), (50, 50), (63, 28), (82, 66)]
MARK_DOT = (63, 28, 4.5)


def _font(names, size):
    """First available system font at `size`, else PIL's default.

    Georgia stands in for Playfair Display and Segoe UI for Inter — the same
    fallback chain the stylesheet already declares, so the card looks like the
    site rather than like a different product.
    """
    for n in names:
        for base in (Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype"),
                     Path("/Library/Fonts"), Path("/System/Library/Fonts")):
            p = base / n
            if p.is_file():
                try:
                    return ImageFont.truetype(str(p), size)
                except OSError:
                    pass
    try:
        return ImageFont.truetype("DejaVuSerif.ttf", size)
    except OSError:
        return ImageFont.load_default()


SERIF = ["georgia.ttf", "Georgia.ttf", "times.ttf", "DejaVuSerif.ttf"]
SERIF_B = ["georgiab.ttf", "Georgia Bold.ttf", "timesbd.ttf", "DejaVuSerif-Bold.ttf"]
SANS = ["segoeui.ttf", "SegoeUI.ttf", "arial.ttf", "DejaVuSans.ttf"]
SANS_B = ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]


def draw_mark(draw, x, y, size, stroke_scale=1.0, ink=INK, dot=GREEN):
    """Draw the mountain-in-a-circle mark with its top-left at (x, y)."""
    k = size / 100.0
    cx, cy, r = MARK_CIRCLE
    w_ring = max(1, round(3.5 * k * stroke_scale))
    w_path = max(1, round(4.0 * k * stroke_scale))

    draw.ellipse([x + (cx - r) * k, y + (cy - r) * k,
                  x + (cx + r) * k, y + (cy + r) * k],
                 outline=ink, width=w_ring)

    pts = [(x + px * k, y + py * k) for px, py in MARK_PATH]
    draw.line(pts, fill=ink, width=w_path, joint="curve")
    # joint="curve" rounds the joins but not the two end caps; add them.
    for px, py in (pts[0], pts[-1]):
        rr = w_path / 2
        draw.ellipse([px - rr, py - rr, px + rr, py + rr], fill=ink)

    dx, dy, dr = MARK_DOT
    draw.ellipse([x + (dx - dr) * k, y + (dy - dr) * k,
                  x + (dx + dr) * k, y + (dy + dr) * k], fill=dot)


def make_og_image():
    """1200x630 — the size every platform crops from without letterboxing."""
    W, H = 1200, 630
    im = Image.new("RGB", (W * SS, H * SS), PAPER)
    d = ImageDraw.Draw(im)

    # A soft paper band so the card is not a flat rectangle.
    d.rectangle([0, int(H * 0.72) * SS, W * SS, H * SS], fill=PAPER2)
    d.line([0, int(H * 0.72) * SS, W * SS, int(H * 0.72) * SS], fill=LINE, width=2 * SS)
    # Brand rule at the very top.
    d.rectangle([0, 0, W * SS, 10 * SS], fill=GREEN)

    draw_mark(d, 84 * SS, 96 * SS, 132 * SS)

    f_title = _font(SERIF, 92 * SS)
    f_sub = _font(SANS, 35 * SS)
    f_small = _font(SANS_B, 25 * SS)

    d.text((248 * SS, 104 * SS), "Quantum Ascent", font=f_title, fill=INK)
    d.text((250 * SS, 214 * SS), "Learn quantum computing by climbing",
           font=f_sub, fill=MUTED)

    d.text((84 * SS, 330 * SS),
           "From your first qubit to solving a real\noptimization problem with QAOA.",
           font=_font(SERIF, 44 * SS), fill=INK, spacing=16 * SS)

    # Honest, specific proof points — the things that actually differentiate it.
    chips = ["6 basecamps", "Runs in your browser", "No install", "Free & open"]
    x = 84 * SS
    y = 486 * SS
    for c in chips:
        bbox = d.textbbox((0, 0), c, font=f_small)
        w = bbox[2] - bbox[0]
        pad = 20 * SS
        d.rounded_rectangle([x, y, x + w + pad * 2, y + 56 * SS],
                            radius=28 * SS, outline=GREEN, width=2 * SS)
        d.text((x + pad, y + 13 * SS), c, font=f_small, fill=GREEN)
        x += w + pad * 2 + 16 * SS

    im = im.resize((W, H), Image.LANCZOS)
    out = ASSETS / "og-image.png"
    im.save(out, "PNG", optimize=True)
    return out, im.size


def make_favicons():
    """A favicon is 16px: the full mark turns to mush, so drop the ring and
    thicken the mountain until it still reads at that size."""
    made = []

    # SVG favicon — crisp at any size, and what modern browsers prefer.
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <title>Quantum Ascent</title>
  <rect width="100" height="100" rx="20" fill="#f8f6f1"/>
  <polyline points="12,72 38,34 50,49 65,22 88,72"
            fill="none" stroke="#1a1a18" stroke-width="9"
            stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="65" cy="22" r="9" fill="#1f7a4d"/>
</svg>
"""
    (WEB / "favicon.svg").write_text(svg, encoding="utf-8")
    made.append(WEB / "favicon.svg")

    def simple_mark(size, bg=PAPER, radius_frac=0.2):
        im = Image.new("RGB", (size * SS, size * SS), bg)
        d = ImageDraw.Draw(im)
        k = size * SS / 100.0
        pts = [(12 * k, 72 * k), (38 * k, 34 * k), (50 * k, 49 * k),
               (65 * k, 22 * k), (88 * k, 72 * k)]
        w = max(1, round(9 * k))
        d.line(pts, fill=INK, width=w, joint="curve")
        for px, py in (pts[0], pts[-1]):
            rr = w / 2
            d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=INK)
        dr = 9 * k
        d.ellipse([65 * k - dr, 22 * k - dr, 65 * k + dr, 22 * k + dr], fill=GREEN)
        return im.resize((size, size), Image.LANCZOS)

    ico = WEB / "favicon.ico"
    simple_mark(64).save(ico, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    made.append(ico)

    touch = WEB / "apple-touch-icon.png"
    simple_mark(180).save(touch, "PNG", optimize=True)
    made.append(touch)

    return made


def main():
    out, size = make_og_image()
    print(f"wrote {out.relative_to(REPO)}  {size[0]}x{size[1]}  "
          f"{out.stat().st_size // 1024} KB")
    for p in make_favicons():
        print(f"wrote {p.relative_to(REPO)}  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
