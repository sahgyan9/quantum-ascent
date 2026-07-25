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

---

*These rules are enforced in review, and partly in CI: tests assert that no LaTeX macro ships
unexpanded, that student and solution notebooks never drift, and that every solution notebook
executes end to end.*
