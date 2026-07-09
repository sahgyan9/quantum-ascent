"""The house LaTeX notation, shared by every notebook.

Each notebook's second cell is a markdown cell containing MACROS so that
bra-ket notation renders identically everywhere (QWorld convention).
tools/build_solutions.py and the tests verify the cell is present and identical.
"""

MACROS = r"""$
\gdef\ket#1{|#1\rangle}
\gdef\bra#1{\langle #1|}
\gdef\braket#1#2{\langle #1|#2\rangle}
\gdef\sqrttwo{\tfrac{1}{\sqrt{2}}}
\gdef\mymatrix#1#2{\begin{pmatrix} #2 \end{pmatrix}}
\gdef\myvector#1{\begin{pmatrix} #1 \end{pmatrix}}
\gdef\hadamard{\sqrttwo\mymatrix{}{1 & 1 \\ 1 & -1}}
$
<i>This cell defines the math notation used below — if formulas look broken,
run (or re-render) this cell first.</i>"""


def macros_cell() -> str:
    """Return the markdown source for the house macro cell."""
    return MACROS
