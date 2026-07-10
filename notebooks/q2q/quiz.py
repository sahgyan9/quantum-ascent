"""Inline concept quizzes for course notebooks.

Design rules (Don Norman feedback principle, same visual language as checkers):
- quiz.ask("some-id") renders the question with clickable answer buttons.
- Clicking any option gives immediate green ✅ / red ❌ feedback with a
  coaching hint written specifically for THAT option (predicted-mistake
  coaching, not a generic "wrong").
- Retry is always allowed — keep clicking until the box turns green.
- Self-contained: inline HTML/CSS/JS only, no external resources, no extra
  dependencies. Headless (pytest/plain terminal) it prints the question and
  options without spoiling the answer, and never raises.

⚠️ Peeking at _BANK below spoils the quick checks — try them honestly first!
"""

from __future__ import annotations

import html as _html
import json
import re
import uuid

from .checkers import _in_ipython

__all__ = ["ask"]

# Colors match q2q.checkers' pass/fail boxes; the card itself gets its own
# violet so quick checks read as "thinking", not "coding task".
_CARD = "border-left:5px solid #6d28d9;background:#f5f1fb;color:#311b6b"
_OK = "border-left:5px solid #2ecc71;background:#eafaf1;color:#145a32"
_BAD = "border-left:5px solid #e74c3c;background:#fdedec;color:#78281f"

_BANK: dict[str, dict] = {
    # ------------------------------------------------ Module 01
    "m1-biased-prediction": dict(
        question=(
            "You drag the slider to <b>P(Heads) = 75%</b> and click "
            "<b>Slap ×100</b>. What do you expect the heads count to be?"
        ),
        options=[
            "Exactly 75 — every single run",
            "Around 75 — slightly different on every run",
            "No idea is possible — quantum outcomes are completely random",
        ],
        correct=1,
        feedback=[
            "Tempting! But each slap is its own random event, like a real "
            "coin flip. Run Slap ×100 a few times and watch: 71, 78, 74… "
            "hovering near 75, rarely landing on it exactly.",
            "One slap is unpredictable, but the <i>statistics</i> over many "
            "slaps are steady — about 75 heads, with a little honest wobble "
            "(shot noise). You'll meet this wobble again when we run circuits.",
            "Half right — a <i>single</i> slap really is unpredictable. But "
            "100 slaps have very predictable statistics: about 75 heads. "
            "Reading statistics over many shots is exactly how we read "
            "quantum data!",
        ],
    ),
    "m1-amplitude-vector": dict(
        question=(
            "Our 75/25 biased coin has P(heads) = 3/4 and P(tails) = 1/4. "
            "Which little vector of <b>amplitudes</b> describes it?"
        ),
        options=[
            "(3/4, 1/4)",
            "(√3/2, 1/2)",
            "(75, 25)",
        ],
        correct=1,
        feedback=[
            "Careful — those are the <i>probabilities</i>. Amplitudes are "
            "the <b>square roots</b> of probabilities: √(3/4) = √3/2 and "
            "√(1/4) = 1/2. (Check: (3/4)² + (1/4)² ≠ 1, so this vector "
            "isn't even normalized.)",
            "Square each entry: (√3/2)² = 3/4 and (1/2)² = 1/4 — the 75/25 "
            "coin exactly, and 3/4 + 1/4 = 1, so everything adds up to 1. "
            "Amplitudes → squares → probabilities!",
            "Percentages can't be amplitudes — the squares of the entries "
            "must add up to 1. Turn them into probabilities first "
            "(0.75, 0.25), then take square roots.",
        ],
    ),
    "m1-double-wire": dict(
        question=(
            "In your finished circuit drawing, what is the <b>double-line "
            "wire</b> at the bottom?"
        ),
        options=[
            "A second qubit that Qiskit added on its own",
            "A classical bit that stores the measurement result",
            "Just decoration to make the drawing look tidy",
        ],
        correct=1,
        feedback=[
            "A second qubit would be another <i>single</i>-line wire like "
            "the first. The double line is not quantum at all — it carries "
            "the plain 0-or-1 answer after the slap.",
            "The slap produces a plain, ordinary 0 or 1 — so it needs a "
            "plain, ordinary classical bit to live in. <code>measure_all()</code> "
            "added it for you automatically.",
            "Every element in a circuit drawing means something! The double "
            "line is the classical bit where your measurement result — the "
            "slapped coin's face — gets written down.",
        ],
    ),
}


def ask(quiz_id: str) -> None:
    """Render the quick-check question with clickable, instantly-graded options."""
    if quiz_id not in _BANK:
        raise KeyError(
            f"Unknown quiz id {quiz_id!r} — known ids: {sorted(_BANK)}")
    q = _BANK[quiz_id]
    if _in_ipython():
        from IPython.display import HTML, display
        display(HTML(_render_html(q)))
    else:
        _print_fallback(q)


# ---------------------------------------------------------------- rendering

def _render_html(q: dict) -> str:
    uid = "q2qquiz" + uuid.uuid4().hex[:10]
    # Data island keeps feedback out of onclick attributes (no escaping traps).
    # "</" is broken up so feedback text can never close the script tag early.
    data = json.dumps(
        {"correct": q["correct"], "feedback": q["feedback"],
         "n": len(q["options"])}
    ).replace("</", "<\\/")
    buttons = "".join(
        f'<button id="{uid}-b{i}" class="{uid}-opt" '
        f'onclick="{uid}_pick({i})" '
        f'style="display:block;width:100%;text-align:left;margin:6px 0;'
        f'padding:8px 12px;border:1.5px solid #b9c2c9;border-radius:6px;'
        f'background:#ffffff;color:#1c2733;cursor:pointer;font-size:14px">'
        f'{_html.escape(opt)}</button>'
        for i, opt in enumerate(q["options"])
    )
    return (
        f'<style>.{uid}-opt:hover{{border-color:#6d28d9 !important}}</style>'
        f'<div style="{_CARD};padding:12px 16px;border-radius:4px;'
        f'font-size:14px;max-width:640px">'
        f'🧠 <b>Quick check.</b> {q["question"]}'
        f'{buttons}'
        f'<div id="{uid}-fb"></div>'
        f'</div>'
        f'<script type="application/json" id="{uid}-data">{data}</script>'
        f'<script>'
        f'window.{uid}_pick = function (i) {{'
        f'  var d = JSON.parse(document.getElementById("{uid}-data").textContent);'
        f'  for (var j = 0; j < d.n; j++) {{'
        f'    var b = document.getElementById("{uid}-b" + j);'
        f'    b.style.borderColor = "#b9c2c9"; b.style.background = "#ffffff";'
        f'  }}'
        f'  var ok = (i === d.correct);'
        f'  var b = document.getElementById("{uid}-b" + i);'
        f'  b.style.borderColor = ok ? "#2ecc71" : "#e74c3c";'
        f'  b.style.background = ok ? "#eafaf1" : "#fdedec";'
        f'  document.getElementById("{uid}-fb").innerHTML = ok'
        f'    ? \'<div style="{_OK};padding:10px 14px;border-radius:4px;'
        f'margin-top:8px">✅ <b>Correct!</b> \' + d.feedback[i] + "</div>"'
        f'    : \'<div style="{_BAD};padding:10px 14px;border-radius:4px;'
        f'margin-top:8px">❌ <b>Not quite.</b> \' + d.feedback[i] +'
        f'      " <i>Think it through — then try another option!</i></div>";'
        f'}};'
        f'</script>'
    )


def _print_fallback(q: dict) -> None:
    """Plain-terminal rendering: question + options, no answer spoilers."""
    strip = re.compile(r"<[^>]+>")
    print("🧠 Quick check: " + strip.sub("", q["question"]))
    for i, opt in enumerate(q["options"]):
        print(f"   {chr(65 + i)}) {strip.sub('', opt)}")
    print("   (Open this notebook in Jupyter or VS Code to click an answer "
          "and get instant feedback.)")
