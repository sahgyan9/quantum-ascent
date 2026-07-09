"""House LaTeX shorthand, expanded to plain LaTeX at notebook-generation time.

Custom \\gdef macros defined in one markdown cell are NOT reliably carried to
later cells by every renderer (VSCode's KaTeX in particular does not persist
\\gdef across cells the way MathJax does), which caused undefined-macro
ParseErrors. To make math rendering renderer-agnostic (identical in Colab,
VSCode, and nbviewer), authors still write the short forms below in generator
source for readability, but expand() rewrites them into plain, portable LaTeX
before a cell is written — no \\gdef ever ships in a notebook.
"""

import re

_RULES = [
    (re.compile(r"\\braket\{([^{}]*)\}\{([^{}]*)\}"),
     lambda m: rf"\langle {m.group(1)}|{m.group(2)}\rangle"),
    (re.compile(r"\\ket\{([^{}]*)\}"),
     lambda m: rf"|{m.group(1)}\rangle"),
    (re.compile(r"\\bra\{([^{}]*)\}"),
     lambda m: rf"\langle {m.group(1)}|"),
    (re.compile(r"\\mymatrix\{[^{}]*\}\{([^{}]*)\}"),
     lambda m: rf"\begin{{pmatrix}} {m.group(1)} \end{{pmatrix}}"),
    (re.compile(r"\\myvector\{([^{}]*)\}"),
     lambda m: rf"\begin{{pmatrix}} {m.group(1)} \end{{pmatrix}}"),
    (re.compile(r"\\hadamard(?:\{\})?"),
     lambda m: r"\tfrac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}"),
    (re.compile(r"\\sqrttwo"),
     lambda m: r"\tfrac{1}{\sqrt{2}}"),
]


def expand(text: str) -> str:
    """Expand house LaTeX shorthand macros into plain, renderer-portable LaTeX."""
    for pattern, replacement in _RULES:
        text = pattern.sub(replacement, text)
    return text
