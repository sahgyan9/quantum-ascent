"""Embed the course's interactive HTML widgets inside notebooks.

The widgets are self-contained HTML/JS apps served from the course website
(Firebase Hosting). Embedding via iframe means they render everywhere a
notebook renders — Colab, Jupyter, nbviewer — and degrade to a plain link
when iframes are blocked.

Override the base URL for local development or tests:
    set Q2Q_WIDGET_BASE=http://localhost:8000/widgets
"""

from __future__ import annotations

import os

# Single source of truth for where widgets live. Change here, nowhere else.
WIDGET_BASE = os.environ.get(
    "Q2Q_WIDGET_BASE", "https://quantum-ascent-77617.web.app/widgets"
)


def show_widget(name: str, width: int = 900, height: int = 520, scale: float = 1.0):
    """Embed a course widget by folder name, e.g. show_widget("bloch-sampler").

    Renders an iframe clipped/scaled to fit the notebook, plus an
    "open in a new tab" fallback link that always works.
    """
    from IPython.display import HTML

    url = f"{WIDGET_BASE}/{name}/index.html"
    return HTML(
        f'<div style="width:{int(width * scale)}px;height:{int(height * scale)}px;'
        f'overflow:hidden;border:1px solid #ddd;border-radius:8px">'
        f'<iframe src="{url}" width="{width}" height="{height}" frameborder="0" '
        f'style="transform:scale({scale});transform-origin:0 0"></iframe></div>'
        f'<a href="{url}" target="_blank" rel="noopener">Open the '
        f'{name} widget in a new tab ↗</a>'
    )
