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


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    os.chdir(WEBSITE)
    handler = http.server.SimpleHTTPRequestHandler
    with http.server.ThreadingHTTPServer(("", port), handler) as httpd:
        print(f"Quantum Ascent local server: http://localhost:{port}")
        print(f"Widget base for notebooks:   set Q2Q_WIDGET_BASE=http://localhost:{port}/widgets")
        print("Ctrl+C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
