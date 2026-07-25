"""Three-rung hints for the notebook track.

Every notebook used to end the same way: *"Stuck on a task? Compare with the
worked solutions."* For a beginner that reads as "go copy the answer", and it
throws away the one thing this course actually has — checkers that already know
*why* an answer is wrong.

So `q2q.hints.hint("01-2")` gives a ladder instead, one rung per call:

    1. NUDGE     physical intuition, plain English, no formula
    2. STRATEGY  the mathematical route, still not the answer
    3. NEAR      the near-answer with the last step left to the learner

The rungs and their wording are shared, deliberately, with the browser track's
`website/assets/js/labtasks.js`, so a learner who switches tracks meets the
same voice and the same help. `tests/test_hints.py` asserts the two never drift.

Design notes that are not obvious:

* Rung 3 stops short of a paste-able solution for circuit tasks. It names the
  gates and the angle, which is what an unstuck learner needs, and leaves the
  typing — because the typing is where it becomes yours.
* The ladder is *stateful per task* and resets per kernel, so re-running a cell
  does not silently re-serve rung 1 forever.
* Asking for a hint is never penalised or recorded. Nothing here feeds the
  Prediction Ledger; a learner who is stuck should reach for help without
  wondering whether it counts against them.
"""

from __future__ import annotations

__all__ = ["hint", "reset", "available", "TASKS"]

# taskid -> (title, [nudge, strategy, near])
TASKS: dict[str, tuple[str, list[str]]] = {
    "01-1": (
        "Build a fair coin",
        [
            "You want to go from 'definitely 0' to 'genuinely undecided'. Which single gate "
            "*creates* an even split out of a definite state?",
            "The Hadamard gate H takes |0> to an equal mix of |0> and |1>. Both amplitudes are "
            "1/sqrt(2) ~ 0.707, and 0.707^2 = 0.5 — that is the Born rule handing you the 50%.",
            "One line: qc.h(0). Then measure and check the counts land near 50/50 (they will "
            "wander by ten or so — that is shot noise, not an error).",
        ],
    ),
    "01-2": (
        "Build a 75/25 qubit",
        [
            "You are solving for an angle. Start from what you want — P(1) = 0.25 — and work "
            "backwards through the squaring and then the sine.",
            "sin^2(theta/2) = 0.25  ->  sin(theta/2) = 0.5  ->  theta/2 = 30 deg  ->  theta = 60 deg. "
            "The classic slip is stopping at 30: that is the HALF-angle, not the angle.",
            "60 degrees is pi/3 radians, and Qiskit wants radians: qc.ry(np.pi/3, 0). If you "
            "write qc.ry(60, 0) you have just asked for 60 radians, which is a very different "
            "state.",
        ],
    ),
    "02-1": (
        "Prove that H.Z.H = X",
        [
            "Z does nothing visible to a qubit sitting at |0>. So Z cannot usefully go first — "
            "something has to put the qubit somewhere Z can act on.",
            "Put the qubit into superposition, flip the sign of the |1> half, then fold it back. "
            "The fold is what turns an invisible phase into a visible probability.",
            "Three gates on qubit 0, in this order: H, then Z, then H. Compare the resulting "
            "unitary against Qiskit's X and watch them match.",
        ],
    ),
    "02-2": (
        "The endianness trap",
        [
            "Write the target bitstring out with labels underneath it. Which character belongs "
            "to which qubit?",
            "Qiskit prints the highest-numbered qubit on the LEFT, so a 2-qubit string reads "
            "q1q0. In '10', the 1 belongs to q1 and the 0 to q0.",
            "One X gate, on qubit 1: qc.x(1). If you get '01' instead, you flipped q0 — which is "
            "the single most common Qiskit bug in the wild, and worth meeting here rather than "
            "in your own research code.",
        ],
    ),
    "03-1": (
        "Make a Bell pair",
        [
            "You need one qubit to become undetermined, and then the second to copy whatever the "
            "first turns out to be. Two different gates, in that order.",
            "H on q0 makes it a fair coin. CNOT with q0 as control and q1 as target then flips "
            "q1 exactly when q0 is 1 — so the two always match.",
            "qc.h(0) then qc.cx(0, 1). Check the statevector: amplitude 0.707 on |00> and on "
            "|11>, and exactly zero on |01> and |10>.",
        ],
    ),
    "03-2": (
        "The anti-correlated twin",
        [
            "You already know how to build the pair that always agrees. Turning 'always agrees' "
            "into 'always disagrees' means flipping one of them.",
            "Take the Bell pair and add a single X on one wire — before or after the CNOT, both "
            "work. Try both and convince yourself they give the same state.",
            "qc.h(0); qc.cx(0, 1); qc.x(1). Then check <ZZ>: it should read -1 rather than +1. "
            "That one sign is the whole difference between 'same' and 'opposite'.",
        ],
    ),
    "04-1": (
        "Dial an expectation value",
        [
            "<Z> = P(0) - P(1), and the two probabilities add to 1. Two facts, one unknown — "
            "solve them together for P(0).",
            "P(0) = 0.75. And from Basecamp 1 you know P(1) = sin^2(theta/2), so you need "
            "sin^2(theta/2) = 0.25 — an angle you have already found once.",
            "It is the same 60-degree state as Basecamp 1's loaded coin: qc.ry(np.pi/3, 0). "
            "Note that no single shot ever returns 0.5; only the average lands there.",
        ],
    ),
    "04-2": (
        "The cost Hamiltonian's favourite state",
        [
            "<ZZ> = -1 means the two qubits NEVER come out the same. What is the simplest state "
            "where they always differ?",
            "A single X on one wire gives |01>, and the bits disagree in every shot — that is "
            "already <ZZ> = -1. The entangled Psi+ from Basecamp 3 also works, which is worth "
            "noticing: <ZZ> cannot tell those two states apart.",
            "qc.x(0) is enough. Then build Psi+ instead (H, CNOT, X) and watch <ZZ> read -1 for "
            "that too — same observable, very different states.",
        ],
    ),
    "05-1": (
        "Descend to the ground state",
        [
            "Both terms matter. cos(theta) is most negative at 180 degrees, but 0.5*sin(theta) "
            "is POSITIVE there — so the true minimum sits a little past 180.",
            "Minimise cos(theta) + 0.5*sin(theta) by setting the derivative to zero: "
            "-sin(theta) + 0.5*cos(theta) = 0, so tan(theta) = 0.5.",
            "theta ~ 180 + 26.57 = 206.57 degrees (about 3.606 rad). The energy bottoms out at "
            "-1.1180, which is -sqrt(1.25). Notice how FLAT the curve is down there — that "
            "flatness is exactly what makes an optimizer's job hard.",
        ],
    ),
    "05-2": (
        "Name the floor",
        [
            "You are being asked for a number you can get from a calculator: the negative square "
            "root of a sum of two squares.",
            "The two coefficients in H = Z + 0.5*X are 1 and 0.5. Square each one, add them, "
            "take the square root, and make it negative: you want -sqrt(1^2 + 0.5^2) = -sqrt(1.25).",
            "-1.118. And the reason it is not -1.5 is that Z and X do not commute — no state "
            "makes both terms as negative as possible at the same time, so you get the vector "
            "length instead of the sum.",
        ],
    ),
    "06-1": (
        "The triangle you cannot cut",
        [
            "Try the obvious thing first: put one node in group B, leave two in group A, and "
            "count the edges that now run between the groups.",
            "Any split of three nodes into two groups leaves at least two nodes together — and "
            "the edge between THOSE two can never be cut. So 2 is the ceiling, not a failure.",
            "Any single node on its own side does it: 2 of 3 edges cut, and no arrangement beats "
            "that. This is frustration, a property of the problem rather than of the solver.",
        ],
    ),
    "06-2": (
        "Summit: QAOA on a 5-cycle",
        [
            "Move gamma first with beta held still and watch the expected cut rise and fall — you "
            "are hand-drawing a slice through the energy landscape. Then do the same with beta. "
            "Most of the range is bad; a narrow band is good.",
            "Good p=1 angles for this ring live near gamma ~ 67 deg, beta ~ 113 deg (and, by "
            "symmetry, the swap of those). That reaches <C> ~ 3.75 — ratio 0.937, which is "
            "genuinely NOT the optimum.",
            "For the full 1.000 you need p=2 AND a second, independent pair of angles: "
            "gamma1=105, beta1=148, gamma2=32, beta2=165 (degrees). Sharing one pair across both "
            "layers caps you at 0.962 — the extra parameters are what depth actually buys.",
        ],
    ),
}

_RUNG_NAMES = ("Nudge", "Strategy", "Almost the answer")
_served: dict[str, int] = {}


def available() -> list[str]:
    """Task ids that have a hint ladder."""
    return sorted(TASKS)


def reset(task_id: str | None = None) -> None:
    """Start the ladder again — for one task, or all of them."""
    if task_id is None:
        _served.clear()
    else:
        _served.pop(task_id, None)


def hint(task_id: str, level: int | None = None) -> None:
    """Print the next rung of help for a task.

    Call it again for the next rung. Pass `level` (1, 2 or 3) to jump straight
    to one — no judgement either way, this is not recorded anywhere.
    """
    key = str(task_id).strip()
    if key not in TASKS:
        opts = ", ".join(available())
        print(f"No hints for task {key!r}. Known tasks: {opts}")
        return

    title, rungs = TASKS[key]
    if level is None:
        level = _served.get(key, 0) + 1
    level = max(1, min(int(level), len(rungs)))
    _served[key] = level

    body = rungs[level - 1]
    header = f"Hint {level}/{len(rungs)} — {_RUNG_NAMES[level - 1]}  ·  Task {key}: {title}"
    print("\n" + "─" * min(len(header), 78))
    print(header)
    print("─" * min(len(header), 78))
    for line in _wrap(body, 78):
        print(line)
    if level < len(rungs):
        print(f"\nStill stuck? Run this cell again for hint {level + 1} of {len(rungs)}.")
    else:
        print("\nThat is the last hint — the rest is yours. You are closer than it feels.")
    print()


def _wrap(text: str, width: int) -> list[str]:
    """Plain-text wrap. No textwrap import so this file stays dependency-free
    and safe to fetch standalone in the Colab bootstrap."""
    out, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out
