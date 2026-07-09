# Quantum Ascent — Brand Guidelines

This document defines the visual system for the **Quantum Ascent** learning platform: an editorial, minimalist design language shared across the website (`website/assets/css/site.css`) and the course notebooks (`tools/nb_common.py`, `notebooks/q2q/latex_macros.py`).

The direction: calm and academic rather than flashy — closer to a well-typeset journal than a SaaS dashboard. The mountain/basecamp metaphor stays, but expressed with restraint: one accent color, hairline borders, generous whitespace, light-only.

---

## 1. Logo

`website/assets/logo.svg` (source concept: `brand_assets/logo_final.svg`) — a badge mark: a thin circle containing a single-stroke mountain ridge, with one small filled dot marking the summit.

- Two colors only: ink (`#1a1a18`) for the circle and ridge, accent green (`#1f7a4d`) for the summit dot. No gradients, no glow, no drop shadow.
- Minimum size: 20px (favicon-safe — the mark stays legible because it's built from few, thick strokes rather than fine detail).
- Always pair with the wordmark in the nav: logo mark + "Quantum" + *Ascent* (italic, see Typography) — never the mark alone in page chrome, since "Quantum Ascent" is the recognizable unit at this stage of the brand.
- Don't recolor the mark per-page or add effects (glow, gradient fill, drop shadow) — consistency of the mark is what makes it recognizable across notebooks, favicon, and site.

## 2. Color

One accent, used everywhere something needs to draw the eye. A second, distinct color is reserved for task/XP-energy moments so it never gets confused with brand identity.

| Token | Hex | Use |
|---|---|---|
| `--bg` | `#f8f6f1` | Page background — warm paper, not pure white |
| `--bg2` | `#f1eee6` | Secondary surfaces (code blocks, input fields, hover panels) |
| `--panel` | `#ffffff` | Cards |
| `--line` | `#e2dfd8` | Hairline borders — the primary way structure is shown, not shadows |
| `--text` | `#1a1a18` | Body/heading ink |
| `--muted` | `#6b6860` | Secondary text |
| `--accent` | `#1f7a4d` | **The** brand color — links, buttons, logo dot, "done" states, brand-identity callouts |
| `--accent-bg` | `#eaf6ee` | Pale accent tint for hover/selected states |
| `--amber` | `#b45309` | XP pill, task/gap-fill callouts, badge chips — deliberately *not* the brand accent, so task energy and brand identity stay visually distinct |
| `--danger` | `#b3261e` | Wrong-answer states only |

Rules:
- **Light-only.** No dark mode toggle in the site chrome. (Notebook callouts hardcode both background and text color per-box regardless, so they stay readable in whatever theme the notebook host — VSCode, Colab, Jupyter — happens to be in.)
- **One accent for brand identity.** Don't introduce a second "brand" hue (no more cyan/violet multi-accent). If something needs a second color for *semantic* reasons (success vs. warning vs. task), use amber or danger, not a new brand color.
- **No glow, no gradient text, no glassmorphism.** Borders and whitespace carry the structure. Shadows, where used at all, are whisper-soft (`0 2px 8px rgba(26,26,24,0.03)`), never colored.
- The interactive widgets (`website/widgets/*`) intentionally keep their own separate dark "instrument readout" palette (`website/widgets/_base/widget.css`) — that's a deliberate contrast (a device screen embedded in a paper page), not a site-theme leak. Don't try to reconcile it with `--bg`/`--accent`.

## 3. Typography

| Role | Font | Weight | Notes |
|---|---|---|---|
| Headings | Playfair Display | 400 (occasionally italic) | Light serif, never bold. Italic for the emphasized word in a hero line (e.g. "*Climb* the mountain") and for the wordmark's "Ascent". |
| Body / UI | Inter | 400 body, 500–700 for labels/buttons | `line-height: 1.7` for reading comfort |
| Code | system monospace stack | 400 | No custom mono font import — keep the font-loading footprint small |

Both fonts load from a single Google Fonts request in `site.css`. Don't add more font families — the two-font pairing (serif display + sans body) is the whole visual signature; a third face dilutes it.

## 4. Layout & Spacing

- Reading column: content pages read comfortably up to `--max-w-wide: 1080px`; prose-heavy sections should feel closer to a ~780px measure where practical (the notebook markdown, being plain text, naturally reads this way already).
- Structure via hairline `1px solid var(--line)` borders and whitespace, not boxes-with-shadows.
- Radii are modest and consistent: `4px` small elements, `10px` inputs/buttons, `16px` cards. Never pill-shaped except the nav's XP pill and badge chips (a deliberate small exception, both borrowed from a "chip" convention).

## 5. Components

- **Buttons** (`.btn`): solid accent fill, white text, 1px border matching the fill. `.btn.ghost` is transparent with a hairline border. `.btn.violet` (class name kept for backward compatibility) is now an accent-outline secondary style — not actually violet.
- **Cards** (`.panel`): white background, hairline border, tiny lift (`translateY(-3px)`) and border-color shift to accent on hover — no shadow glow.
- **Quiz options**: hairline border, accent border+tint on hover/correct, danger border+tint on wrong. No color-mixing tricks — flat `--accent-bg`/`--danger-bg` tints.
- **Ascent map nodes**: hairline circle, accent fill for done/available states. No drop-shadow glow.
- **Notebook callouts** (`tools/nb_common.py`): each callout type hardcodes both a background and a text color together (never relies on the host's default text color — that was the original readability bug). Briefing/footer/analogy use the accent green; exercise callouts use teal; task callouts use amber, kept visually distinct from the brand-accent callouts so "here's a task" never reads as "here's brand chrome."

## 6. Voice

Encouraging, plain-spoken, never condescending. Reassure before introducing anything that might look intimidating (new notation, a block of math) rather than apologizing after. Prefer "let's break this down together" over "don't worry, this is easy." See `CLAUDE.md`'s pedagogical rules for the full house style — this document only covers the visual system.
