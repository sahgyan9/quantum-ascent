"""Shared building blocks for authoring course notebooks.

Every tools/make_module_NN.py imports from here so all notebooks share
identical bootstrap cells, macro cells, and callout styling — the tests
in tests/test_notebooks.py enforce this.
"""

import sys
from pathlib import Path

import nbformat.v4 as nbf

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "notebooks"))

from q2q.latex_macros import MACROS  # noqa: E402

# Colors of the Quantum Ascent brand (match website/assets/css/site.css)
CYAN = "#0891b2"
VIOLET = "#7c3aed"
GREEN = "#059669"

BOOTSTRAP = '''\
# ✅ Setup — run me first! (works locally and on Google Colab)
import importlib.util, os, sys, subprocess, urllib.request

def _ensure_q2q():
    for rel in (".", "..", "../.."):
        if os.path.isdir(os.path.join(rel, "q2q")):
            sys.path.insert(0, os.path.abspath(rel))
            break
    if importlib.util.find_spec("q2q") is not None:
        return
    # On Colab: install the pinned SDKs and fetch the course helpers
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "qiskit==2.3.1", "qiskit-aer==0.17.2", "pylatexenc"], check=False)
    base = ("https://raw.githubusercontent.com/sahgyan9/quantum-ascent/"
            "main/notebooks/q2q/")
    os.makedirs("q2q", exist_ok=True)
    for fname in ("__init__.py", "checkers.py", "widgets.py",
                  "oracles.py", "latex_macros.py", "targets.py"):
        urllib.request.urlretrieve(base + fname, os.path.join("q2q", fname))
    sys.path.insert(0, os.path.abspath("."))

_ensure_q2q()
from q2q import checkers, targets
from q2q.widgets import show_widget
print("Setup complete — you're ready to climb. 🏔️")'''


def md(source, tags=None):
    cell = nbf.new_markdown_cell(source)
    if tags:
        cell.metadata["tags"] = tags
    return cell


def code(source, tags=None):
    cell = nbf.new_code_cell(source)
    if tags:
        cell.metadata["tags"] = tags
    return cell


def macro_cell():
    return md(MACROS)


def bootstrap_cell():
    return code(BOOTSTRAP)


def briefing(module_no, title, mission, objectives, minutes):
    obj = "\n".join(f"- {o}" for o in objectives)
    return md(
        f"# 🏔️ Quantum Ascent — Basecamp {module_no}: {title}\n\n"
        f'<div style="border-left:5px solid {VIOLET};background:#f5f3ff;'
        f'padding:12px 16px;border-radius:4px">\n'
        f"<b>📋 Mission briefing.</b> {mission}\n</div>\n\n"
        f"**By the end of this basecamp you can:**\n{obj}\n\n"
        f"*Estimated time: {minutes} min · Best experienced with the "
        f"[course website](https://quantum-ascent-77617.web.app) open in another tab.*"
    )


def exercise(n, text):
    """Widget-interaction exercise callout (NVIDIA-style, our branding)."""
    return md(
        f'<div style="border-left:5px solid {CYAN};background:#ecfeff;'
        f'padding:12px 16px;border-radius:4px">\n'
        f'<b>🔭 Exercise {n}.</b> {text}\n</div>'
    )


def task(n, text):
    """Gap-fill coding task header."""
    return md(
        f'<div style="border-left:5px solid {GREEN};background:#ecfdf5;'
        f'padding:12px 16px;border-radius:4px">\n'
        f'<b>⛏️ Task {n}.</b> {text}\n</div>'
    )


def analysis(text):
    return md(f"#### 🔬 Analysis\n\n{text}")


def analogy_callout(concept_title, prompt_body):
    return md(
        f'<div style="border:1px dashed {VIOLET};background:#faf5ff;'
        f'padding:12px 16px;border-radius:8px">\n'
        f"<b>🎨 Make it yours — analogy time.</b> Everyone's brain hooks onto "
        f"different things. Copy the prompt below into <i>your</i> favorite AI "
        f"(ChatGPT, Claude, Gemini) and get <b>{concept_title}</b> explained "
        f"through <i>your</i> world. The precise definition is baked into the "
        f"prompt, so the AI can't drift into pop-science myths. Want more "
        f'control? Use the <a href="https://quantum-ascent-77617.web.app/'
        f'analogy-studio.html">Analogy Studio</a>.\n\n'
        f"<pre style=\"white-space:pre-wrap;background:#fff;border:1px solid "
        f"#e9d5ff;border-radius:6px;padding:10px\">{prompt_body}</pre>\n</div>"
    )


def basecamp_footer(module_no, summary, quiz_url, next_label, solutions_relpath):
    return md(
        f'<div style="border-left:5px solid {VIOLET};background:#f5f3ff;'
        f'padding:12px 16px;border-radius:4px">\n'
        f"<b>🚩 Basecamp {module_no} reached!</b> {summary}\n</div>\n\n"
        f"**Next steps:**\n"
        f"1. 🧠 Take the [Basecamp {module_no} quiz]({quiz_url}) on the website "
        f"to earn your XP and badge.\n"
        f"2. 🧗 Continue the ascent: **{next_label}**.\n\n"
        f"---\n"
        f"*Stuck on a task? Compare with the worked solutions: "
        f"[`{solutions_relpath}`]({solutions_relpath}). Try honestly first — "
        f"the struggle is where the learning happens.*"
    )


def write_notebook(cells, out_path):
    nb = nbf.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3", "language": "python", "name": "python3",
    }
    nb.metadata["language_info"] = {"name": "python"}
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nbformat_write(nb, out_path)
    print(f"wrote {out_path}")


def nbformat_write(nb, path):
    import nbformat
    nbformat.write(nb, str(path))
