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
    # ------------------------------------------------ Module 02
    "m2-order-matters": dict(
        question=(
            "In the Gate Playground you build <b>H then Z</b>. Then you Reset "
            "and build <b>Z then H</b>. Do the two circuits leave the qubit in "
            "the same state?"
        ),
        options=[
            "Yes — same gates, so the result is the same",
            "No — the order you apply gates in can change the result",
            "Only if you measure in between",
        ],
        correct=1,
        feedback=[
            "Same ingredients, different recipe! Watch the arrow: H-then-Z "
            "lands it somewhere different from Z-then-H. Gates are actions, and "
            "(like 'socks then shoes' vs 'shoes then socks') the order matters.",
            "Exactly — quantum gates generally <i>don't commute</i>. H-then-Z "
            "sends |0⟩ to a different state than Z-then-H. The order is part of "
            "the circuit, not an afterthought.",
            "Measurement isn't the issue — even with no measurement at all, the "
            "final <i>state</i> depends on the order. Build both in the widget "
            "and compare the arrow.",
        ],
    ),
    "m2-unitary-undo": dict(
        question=(
            "You apply the <b>H</b> gate to a qubit, then apply <b>H</b> again. "
            "Where does the qubit end up?"
        ),
        options=[
            "Right back where it started — two H's cancel",
            "Twice as far — the effect doubles",
            "In an error state — you can't repeat a gate",
        ],
        correct=0,
        feedback=[
            "Right! H is its own undo (H·H = identity). Every quantum gate is "
            "<b>reversible</b> — that's what 'unitary' means, and it's why a "
            "quantum computer never quietly loses information.",
            "Gates aren't like walking — repeating one doesn't 'go further'. H "
            "is its own inverse, so the second H exactly undoes the first, "
            "landing you back at the start.",
            "Repeating a gate is perfectly fine! In fact H·H does something very "
            "tidy: it returns the qubit to exactly where it began.",
        ],
    ),
    "m2-endianness": dict(
        question=(
            "You make a <b>2-qubit</b> circuit and apply <b>X to qubit 0</b> "
            "only, then measure. In Qiskit's output, which bitstring appears?"
        ),
        options=[
            "'10'",
            "'01'",
            "Either one — it's ambiguous",
        ],
        correct=1,
        feedback=[
            "This is <i>the</i> classic trap. Qiskit writes qubit 0 on the "
            "<b>right</b>, so flipping qubit 0 lights up the rightmost bit: "
            "'01', not '10'.",
            "Correct — Qiskit is 'little-endian': qubit 0 is the <b>rightmost</b> "
            "character. X on qubit 0 gives '01'. Read bitstrings right-to-left "
            "and this trap disappears.",
            "It isn't ambiguous — Qiskit has a firm rule: qubit 0 is the "
            "rightmost bit. So the answer is a definite '01'.",
        ],
    ),
    # ------------------------------------------------ Module 03
    "m3-bell-outcomes": dict(
        question=(
            "In the Explorer you set the link to <b>Correlated (Bell pair)</b> "
            "and measure many times. Which pairs of outcomes actually show up?"
        ),
        options=[
            "All four: 00, 01, 10, 11 — each about 25%",
            "Only 00 and 11, each about 50%",
            "Only 00 — the qubits are stuck",
        ],
        correct=1,
        feedback=[
            "That's the <i>independent</i> link, not the entangled one. Switch to "
            "Correlated and watch 01 and 10 vanish — the two qubits stop being "
            "free to disagree.",
            "Right. The Bell pair Φ⁺ only ever gives 00 or 11, so the two coins "
            "<b>always agree</b>. Each individual coin is still a fair 50/50 — "
            "it's the <i>link between them</i> that's certain.",
            "They're not stuck — each qubit alone is a perfectly fair 50/50. What's "
            "fixed is only the <i>relationship</i>: whenever you look, the two "
            "match. So both 00 and 11 appear, about half the time each.",
        ],
    ),
    "m3-measure-partner": dict(
        question=(
            "Two qubits are in the Bell pair Φ⁺. You measure <b>only qubit A</b> "
            "and get a <b>0</b>. Without touching qubit B, what can you say about it?"
        ),
        options=[
            "Nothing — B is still a 50/50 coin flip",
            "B is now certainly 0 too — the outcomes are locked together",
            "B is now certainly 1 — measuring flips its partner",
        ],
        correct=1,
        feedback=[
            "Before you measured, yes — B alone looked 50/50. But Φ⁺ only allows "
            "00 and 11, so the instant A reads 0, the pair must be 00, and B is "
            "pinned to 0.",
            "Exactly. Φ⁺ = (|00⟩+|11⟩)/√2 has no 01 or 10 term, so matching is "
            "guaranteed: A = 0 forces B = 0. (This is correlation, not a signal — "
            "you can't use it to send a message, as you'll see.)",
            "Close, but this is the <i>correlated</i> pair, not the anti-correlated "
            "one. Φ⁺ makes them <b>agree</b>, so A = 0 means B = 0. The 'always "
            "disagree' behaviour is the other Bell pair, Ψ⁺.",
        ],
    ),
    "m3-entangled-or-not": dict(
        question=(
            "Which two-qubit state is <b>entangled</b> — impossible to describe as "
            "'qubit A is doing X <i>and</i> qubit B is doing Y' separately?"
        ),
        options=[
            "Both qubits fair and independent: ½(|00⟩+|01⟩+|10⟩+|11⟩)",
            "The Bell pair (|00⟩+|11⟩)/√2",
            "Both qubits definitely 0: |00⟩",
        ],
        correct=1,
        feedback=[
            "This one <i>factors</i>: it's just |+⟩ on A and |+⟩ on B, two separate "
            "stories side by side. Independent, not entangled.",
            "Correct. (|00⟩+|11⟩)/√2 can't be split into 'A does this, B does that' "
            "— the only way to describe it is as one joint state. That "
            "unfactorable-ness <b>is</b> entanglement.",
            "|00⟩ factors cleanly into 'A is 0' and 'B is 0' — two independent "
            "certainties. No entanglement there.",
        ],
    ),
    # ------------------------------------------------ Module 04
    "m4-z-scoreboard": dict(
        question=(
            "The <b>Z observable</b> is a scoreboard: it hands the outcome "
            "<b>0</b> a score of <b>+1</b> and the outcome <b>1</b> a score of "
            "<b>−1</b>. A qubit is in state |0⟩. What is its Z-score?"
        ),
        options=[
            "0 — because the qubit is |0⟩",
            "+1 — Z scores the outcome 0 as +1",
            "−1 — because 0 is the 'off' state",
        ],
        correct=1,
        feedback=[
            "Careful — the <i>label</i> is 0, but the <i>score</i> Z assigns to "
            "outcome 0 is +1, not 0. Z isn't reading the bit value; it's looking "
            "up a payout on its scoreboard.",
            "Exactly. Z pays +1 for outcome 0 and −1 for outcome 1. A qubit that "
            "always reads 0 always scores +1, so its average Z-score (its energy) "
            "is +1. It's a lookup, not the bit itself.",
            "That's the score for outcome <i>1</i>, not 0. Z's scoreboard is "
            "0 → +1 and 1 → −1 — the opposite sign to what the bit labels might "
            "suggest.",
        ],
    ),
    "m4-expectation-average": dict(
        question=(
            "You put a qubit in the fair state |+⟩ (a 50/50 coin) and ask for its "
            "<b>expectation value</b> ⟨Z⟩. Each single measurement can only be "
            "+1 or −1, so what is ⟨Z⟩?"
        ),
        options=[
            "Impossible — you can never actually measure the value 0",
            "0 — it's the long-run <i>average</i> score: half +1, half −1",
            "+1 — measurement always rounds up",
        ],
        correct=1,
        feedback=[
            "True that no single shot ever <i>reads</i> 0 — but ⟨Z⟩ isn't one "
            "shot. It's the average over many, and averaging +1 and −1 in equal "
            "amounts lands squarely on 0.",
            "Right. ⟨Z⟩ = (+1)·P(0) + (−1)·P(1) = ½ − ½ = 0. No single slap gives "
            "0, yet the <i>average</i> does — exactly the predict-the-statistics "
            "move from Basecamp 1, now measuring energy instead of counting heads.",
            "Not quite — measurement doesn't round. Half the shots give +1 and "
            "half give −1; their average is 0, the honest expectation value.",
        ],
    ),
    "m4-zz-agreement": dict(
        question=(
            "The <b>ZZ</b> Hamiltonian scores a two-qubit outcome +1 when the "
            "qubits <b>agree</b> (00 or 11) and −1 when they <b>disagree</b> (01 "
            "or 10). For the Bell pair (|00⟩+|11⟩)/√2, what is the energy ⟨ZZ⟩?"
        ),
        options=[
            "0 — each qubit alone is a fair 50/50",
            "+1 — the qubits always agree, so every shot scores +1",
            "−1 — entangled qubits always disagree",
        ],
        correct=1,
        feedback=[
            "Each qubit <i>alone</i> is 50/50, true — but ⟨ZZ⟩ scores the "
            "<b>pair</b>, not either coin. The Bell pair only ever gives 00 or 11, "
            "so it agrees every time.",
            "Exactly. Φ⁺ gives only 00 or 11 — agreement on every shot — so every "
            "score is +1 and the average energy is +1. Flip one qubit (the Ψ⁺ "
            "pair) and they always disagree instead: ⟨ZZ⟩ = −1.",
            "That's the <i>anti</i>-correlated pair Ψ⁺. The plain Bell pair Φ⁺ "
            "always <b>agrees</b> (00 or 11), so its ZZ energy is +1, not −1.",
        ],
    ),
    # ------------------------------------------------ Module 05
    "m5-why-parameter": dict(
        question=(
            "You want the state with the <b>lowest energy</b> under some "
            "Hamiltonian, but you don't know which state that is. What's the "
            "<b>variational</b> strategy?"
        ),
        options=[
            "Measure the |0⟩ state once — whatever you get is the answer",
            "Build a state with a tunable knob θ, read its energy, and adjust θ "
            "to push the energy down",
            "Try all infinitely many states one by one until you find the lowest",
        ],
        correct=1,
        feedback=[
            "A single measurement of a fixed state can't search — it just reports "
            "one state's behaviour. The whole point is to <i>vary</i> the state and "
            "hunt for the best one.",
            "Exactly. A <b>parameterized circuit</b> gives you a dial (or several). "
            "You read the energy at your current setting, nudge the dial to lower "
            "it, and repeat — descending the landscape toward the ground state.",
            "You can't enumerate infinitely many states. Instead you make the state "
            "depend on a knob and let a smart search follow the slope downhill — "
            "far fewer evaluations than brute force.",
        ],
    ),
    "m5-who-does-what": dict(
        question=(
            "In the variational loop, the quantum computer prepares the state and "
            "reports its <b>energy</b>. Who decides the <b>next</b> angle to try?"
        ),
        options=[
            "The quantum computer, by measuring harder",
            "A classical optimizer running on your laptop",
            "Nobody — the angle is fixed from the start",
        ],
        correct=1,
        feedback=[
            "The quantum device is the <i>energy meter</i>, not the navigator. It "
            "tells you how high you are; it doesn't choose where to step next.",
            "Right — it's a partnership. Quantum hardware evaluates the energy at a "
            "given θ (a job classical computers find hard), and a plain classical "
            "optimizer (like COBYLA) uses those readings to pick the next θ. Back "
            "and forth until it reaches the valley floor.",
            "If the angle never changed there'd be no search at all. The angle is "
            "exactly what the classical optimizer keeps adjusting.",
        ],
    ),
    "m5-ground-state": dict(
        question=(
            "Your optimizer keeps lowering the energy and finally stops at "
            "<b>E = −1.118</b>, unable to go lower. What have you found?"
        ),
        options=[
            "A mistake — energy should never be negative",
            "The ground state: the lowest-energy state the Hamiltonian allows",
            "The |1⟩ state, always",
        ],
        correct=1,
        feedback=[
            "Negative energy is perfectly normal here — the Z scoreboard pays −1 "
            "for outcome 1, so energies routinely go below zero. Nothing broke.",
            "Yes. The lowest point of the landscape is the <b>ground state</b>, and "
            "its energy is the smallest eigenvalue of the Hamiltonian. Reaching it "
            "is the goal — and for a cost Hamiltonian, that bottom encodes the "
            "answer to your problem.",
            "Not necessarily |1⟩ — for H = Z + 0.5·X the ground state is a tilted "
            "mix, not a basis state. That's exactly why we needed to <i>search</i> "
            "for it instead of guessing.",
        ],
    ),
    # ------------------------------------------------ Module 06 (Summit)
    "m6-maxcut-goal": dict(
        question=(
            "In <b>Max-Cut</b> you split a graph's nodes into two groups. Which "
            "edges score a point for your cut?"
        ),
        options=[
            "Edges whose two endpoints are in the <b>same</b> group",
            "Edges whose two endpoints are in <b>different</b> groups (they cross "
            "the divide)",
            "All edges, always",
        ],
        correct=1,
        feedback=[
            "The opposite — an edge inside a single group is <i>not</i> cut. You "
            "score only when an edge is severed by the split.",
            "Right. A cut edge crosses between the two groups. Max-Cut asks for the "
            "split that severs the <b>most</b> edges — and on the 4-node ring the "
            "best you can do is the checkerboard, cutting all 4.",
            "Not all — an edge with both ends in the same group stays intact and "
            "scores nothing. Only edges that <i>straddle</i> the two groups count.",
        ],
    ),
    "m6-cost-encoding": dict(
        question=(
            "We give each node a qubit and use the cost $H_C = \\sum_{\\text{edges}} "
            "Z_iZ_j$. Recall $Z_iZ_j$ scores $+1$ when two qubits <b>agree</b> and "
            "$-1$ when they <b>disagree</b>. Why does <b>minimizing</b> $\\langle "
            "H_C\\rangle$ solve Max-Cut?"
        ),
        options=[
            "It doesn't — minimizing agreement destroys the cut",
            "A cut edge = two nodes in different groups = qubits disagree = score "
            "−1, so the lowest energy has the most cut edges",
            "Minimizing energy just picks the state |0000⟩",
        ],
        correct=1,
        feedback=[
            "Look again at the signs: disagreeing qubits (a cut edge) score −1, so "
            "<i>more</i> cuts means <i>lower</i> energy. Minimizing is exactly what "
            "we want.",
            "Exactly — this is the whole encoding. Each cut edge is a disagreement "
            "worth −1, so the state with the lowest total energy is the one that "
            "cuts the most edges. Max-Cut becomes 'find the ground state', and "
            "that's a job for the variational loop from Basecamp 5.",
            "|0000⟩ puts every node in the same group — zero cuts — which is the "
            "<i>highest</i> energy (+4 here), not the lowest. Minimizing drives you "
            "toward the checkerboard instead.",
        ],
    ),
    "m6-qaoa-mixer": dict(
        question=(
            "A QAOA layer has a <b>cost</b> part (built from the edges) and a "
            "<b>mixer</b> part (RX rotations on every qubit). What breaks if you "
            "leave out the mixer?"
        ),
        options=[
            "Nothing — the cost layer alone solves it",
            "The cost layer only adds phases to |+⟩ⁿ, so measurement stays a "
            "uniform coin-flip — the mixer is what turns those phases into a real "
            "preference",
            "The circuit won't run at all",
        ],
        correct=1,
        feedback=[
            "If only that were true! The cost layer is diagonal — on its own it "
            "leaves the measurement probabilities of |+⟩ⁿ perfectly uniform. No "
            "answer emerges.",
            "Exactly. The cost layer stamps a phase onto each configuration, but "
            "phases are invisible to a Z-measurement until the <b>mixer</b> rotates "
            "them into amplitude differences (interference). Cost marks the good "
            "solutions; mixer makes them <i>likely</i>. You need both.",
            "It runs fine — that's the trap. It runs and returns useless uniform "
            "noise, because without the mixer there's no interference to "
            "concentrate probability on the good cuts.",
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
