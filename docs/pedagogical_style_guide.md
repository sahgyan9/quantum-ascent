# Pedagogical Style Guide

These are the authoring rules for Quantum Ascent. They were written by hand *before* any
content, and every notebook cell, quiz question, widget label and line of website copy is held
to them. When an AI assistant drafted material (see [`ai_use.md`](ai_use.md)), this file is the
specification it was drafted against and reviewed against.

They are published here for two reasons: so a judge can check our content against our own
stated rules, and so an educator forking the course knows what the house style is.

---

## 0. The moat: what makes this course different

Most introductory quantum material fails in one of two directions. It either **lies to be
friendly** ("a qubit is 0 and 1 at the same time") or **hides behind rigor** (Dirac notation
and Hilbert spaces on page one). Both lose the beginner — the first by teaching something they
will later have to unlearn, the second by never letting them start.

Our position is that you can be **completely honest and still be gentle**, if you are willing
to do the harder authoring work:

- **Grounded physical analogies** over slogans. The spinning coin, not "both at once."
- **Direct visual intuition** over premature formalism. See rule 5 — probabilities are shown
  as literal physical proportions, never as decorative colour.
- **Step-by-step guidance** over "left as an exercise."

If a sentence would make a physicist wince, it does not ship — no matter how good it sounds.

---

## 1. Beginner friendliness and counselling

Adopt a supportive, reassuring, encouraging tone throughout.

- When introducing a potentially overwhelming topic or equation, **explicitly check in on the
  student**: *"If this feels like a lot, don't worry! We will build and understand these
  concepts slowly, step by step."*
- Incorporate study tips: *"If the math or concepts feel intimidating, the best way to grab
  them is to grab a physical pen and write them down on paper as we go."*
- Use clear physical analogies to resolve confusing pop-science descriptions — the **spinning
  coin** for measurement and collapse, never *"0 and 1 at the same time."*
- A stuck learner should never be made to feel slow. Time estimates are framed as
  *"≈ 50 minutes of content — take as long as you need,"* never as a target to hit.

## 2. Minimize upfront mathematical overhead

Do not open with dense linear algebra, complex numbers, or bra-ket notation.

- Introduce every concept **conceptually first** — analogy, visual signifier, or interactive
  widget — and only then, gently, the formal representation.
- **Syntax pre-requisites:** always show a small, complete, runnable example of any library
  call or data structure (a NumPy array, a `dict`, `def … return`) *before* a task asks the
  student to write it. Never assume prior programming knowledge for new syntax.
- State prerequisites honestly and *check* them. Don't scare people off with requirements the
  course never uses (this course keeps every amplitude real and non-negative, and says so).

## 3. Ignore-the-setup signifiers

Any bootstrap or macro cell (LaTeX definitions, imports, install commands) must be clearly
signposted as safe to ignore, so a student knows to skip it and focus on the concept rather
than wondering what they failed to understand.

## 4. Critical thinking over rote coding

- Emphasise **why** something works.
- **Predict before you run.** Ask for the prediction, capture it, then reveal the result. (This
  is what the Prediction Ledger operationalises — a prediction you never record teaches
  nothing.)
- Keep coding requirements focused on *verifying* concepts. Writing raw code is the part an AI
  can already do; forming and testing an expectation is not.
- Where a well-known trap exists (Qiskit's little-endian bitstring order), walk the student
  **into it deliberately**, then teach the habit that prevents it.

## 5. The state-vector rule (non-negotiable)

Wherever a quantum state is drawn, the visual proportions **are** the Born-rule probabilities —
exactly, not approximately, and never decoratively. A bar that is 75% green means
$P(0) = 0.75$. This applies to every widget, every diagram, and every page. A visual that is
merely suggestive of the probabilities is a bug.

## 6. Consistency across notebook, web and widgets

The same tone, the same analogies, the same vocabulary, the same step-by-step guidance apply
everywhere — notebook prose, website copy, widget labels, quiz feedback, error messages. A
learner who moves from the site to a notebook to a widget should not feel they changed
teachers.

## 7. Narrative-first authoring order

Each concept is introduced in this order, and content that skips a step gets sent back:

> **story → recap → rename → math → widget**

Tell the physical story; recap what was just observed in plain words; *then* give the thing its
technical name; *then* the mathematics; *then* let them play with it. Tasks follow a
**teach-then-tweak** shape: the student is shown a working example and asked to change one
meaningful thing, rather than facing a blank cell.

## 8. Coach the predicted mistake

Checkers do not just say *wrong*. They diagnose the specific misconception behind the wrong
answer — degrees supplied where radians were wanted, a reversed bitstring, a probability that
doesn't normalise — and say so in plain language. Hints escalate over repeated failures
(intuition → strategy → near-answer) so that "I'm stuck" has an exit that is not "copy the
solution."

## 9. Honesty as a feature

Every real-world application card carries one honest sentence about current limits (*"no
quantum advantage has been demonstrated on this problem yet"*). We do not sell. The capstone
uses a graph where QAOA visibly **fails to reach the optimum**, because the word *Approximate*
has to be paid off. Being trustworthy is the product.

## 10. Teach before you ask

**No task may require a concept the learner has not met on the surface they are standing on.**

This rule exists because its absence let a real fault ship. The browser track carried twelve
graded tasks against 772 words of prose, and the only place it ever explained the Hadamard gate
was hint rung 2 of task 01-1 — reachable only by declaring yourself stuck. That inverts the hint
ladder: recovery had become first delivery, and a learner on the site met a colder teacher than
the one in the notebook covering identical ground (rule 6). Nothing in review caught it because
no rule forbade it.

Two consequences worth stating plainly:

- **Every surface teaches.** A page of tasks is not a lesson with the lesson removed. If the
  browser track and the notebook set the same task, they owe the same explanation first.
- **Hints are recovery, never delivery.** If a hint contains the only statement of an idea,
  that idea is missing from the lesson.

The one deliberate exception is a **discovery task**, where finding the thing out *is* the
exercise — the triangle whose best cut is still 2 of 3, the tilted landscape whose minimum is
not where you would guess. Those must not be spoiled in advance, and the honest post-mortem
belongs *after* the task, not before it.

> *Enforced by `tools/build_lessons.py` and `tests/test_lessons.py`: every concept a task
> declares it `requires` must appear in a beat rendered before it, and the discovery tasks have
> explicit spoiler guards.*

## 11. Retrieve, don't just cover

**An idea a learner meets once and never recalls is an idea you covered, not one they learned.**

Retrieval practice and distributed practice are the two techniques with the strongest evidence
behind them in the whole of learning science — stronger than anything else in this guide. The
course originally had neither: six quizzes, each testing only its own basecamp, so a learner
finished Basecamp 1 and was never asked about it again.

Every basecamp after the first now carries one question that reaches back. Three properties make
it practice rather than decoration:

- **Expanding intervals.** Basecamp 1 is retrieved twice, at widening gaps, because the Born
  rule and the half-angle are what everything above them rests on.
- **Placed where it pays.** Each recall lands in the camp about to use it again — endianness
  just before the Summit reads a split off a bitstring, $\langle ZZ\rangle$ just before Max-Cut
  is encoded with it. Retrieval *and* an immediate reason to care.
- **Labelled, not smuggled.** Each is marked *🔁 Recall · Basecamp N*. Learners consistently
  underrate retrieval — it feels less productive than re-reading while working considerably
  better — so saying "this is deliberate, and here is why" is part of the intervention.

Keep it to one per quiz. Spaced practice works by being frequent and small; a cumulative exam
would trade the effect for a chore.

> *Enforced by `tests/test_quizzes.py`, which also checks that adding a question never silently
> moves the 70% pass threshold.*

## 12. Normalise the struggle — don't only soothe it

Rule 1 asks for reassurance. This rule says what kind, because the two obvious ways to comfort a
stuck learner are not equally good.

*"Don't worry"* reassures by lowering the stakes, and can be heard as **I don't expect you to
get this**. *"Everyone trips on this one"* reassures by locating the difficulty in the
**material** rather than in the learner: you are not behind, you have arrived exactly where
everyone arrives. It keeps the standard high and removes the isolation, and that combination is
what keeps people working.

So pair them. Keep the warmth of rule 1 — *take a deep breath*, *grab a physical pen* — and
attach it to a named, specific place where people genuinely get stuck:

- *"That trap catches everyone once."*
- *"Almost everyone puts the gate on the wrong wire the first time — which is why we walk into
  it deliberately."*
- *"Einstein found this so troubling he argued quantum mechanics was incomplete. If it needs
  reading twice, that is not you being slow."*

Naming the specific slip is what makes it credible. Generic encouragement reads as politeness;
"most people stop at the half-angle" reads as someone who has watched learners do this.

> *Enforced by `tests/test_lessons.py`: reviewed basecamps must carry the counselling voice, and
> must normalise struggle in at least two beats — one instance reads as a throwaway, a pattern
> reads as the truth.*

---

*These rules are enforced in review, and increasingly in CI. Mechanically: no LaTeX macro ships
unexpanded, student and solution notebooks never drift, and every solution notebook executes end
to end. Pedagogically: rule 10 is checked by `tests/test_lessons.py` and `tools/build_lessons.py`,
rule 11 by `tests/test_quizzes.py`, and rule 12 by `tests/test_lessons.py`. A rule nobody can
fail is a preference; these are the ones we were willing to make failable.*

*What is **not** yet enforced, and is honestly still a gap: the scaffolding never fades. Rules 4
and 7 apply with equal weight at Basecamp 6 as at Basecamp 1, even though the worked-example
effect is known to reverse as competence grows. See
[`future_improvements.md`](future_improvements.md).*
