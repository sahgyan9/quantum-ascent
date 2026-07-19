"""Serve the website (and widgets) locally for development and offline judging.

Usage:
    python tools/serve_local.py [port]

Then open http://localhost:8000 — everything works without Firebase
(progress falls back to localStorage; sign-in is simply hidden).
"""

import http.server
import os
import sys
from pathlib import Path

WEBSITE = Path(__file__).resolve().parent.parent / "website"


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    """Static handler that disables browser caching.

    The default handler sends no cache headers, so browsers heuristically
    cache JSON/JS. That once left an edited `quizzes.json` showing its stale
    "quiz on its way" fallback until a hard refresh — misleading for a
    developer, and a real risk for a judge evaluating offline. Forcing
    no-cache means what's on disk is always what the browser shows.
    """

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    os.chdir(WEBSITE)
    handler = NoCacheHandler
    with http.server.ThreadingHTTPServer(("", port), handler) as httpd:
        print(f"Quantum Ascent local server: http://localhost:{port}")
        print(f"Widget base for notebooks:   set Q2Q_WIDGET_BASE=http://localhost:{port}/widgets")
        print("Ctrl+C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
