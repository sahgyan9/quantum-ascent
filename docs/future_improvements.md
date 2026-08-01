# Future Improvements & Scalability

**Quantum Ascent** ships complete: six basecamps, six notebooks, six widgets, a browser-native
Circuit Lab, quizzes, a pre/post diagnostic, and a test suite that executes every solution
notebook end to end. This document is about what comes *after* that — and it is deliberately
honest about the line between "built" and "planned."

> **Already shipped** (listed here because earlier drafts of this file described it as future
> work): all six basecamp curricula, quizzes and widgets; the `maxcut-painter` capstone widget;
> the browser-native Circuit Lab that makes the notebook optional; the Prediction Ledger; and
> the pre/post concept assessment.

---

## 1. Interactive Video Lecture Integration
* **The Problem:** WISER has a vast catalog of recorded video lectures, but passive video watching leads to low conceptual retention.
* **The Solution:** Create a **"Lecture Hall"** panel on the basecamp page that indexes relevant video lecture clips. We will link specific video timestamps directly to the corresponding concepts, widgets, and notebook code blocks.
* **Student Workflow:** A student stuck on a notebook task can click a "Watch Explainer" button to overlay the exact 2-minute video segment where an invited speaker explains the underlying mathematics.
* **Status:** not built. Needs the rights-cleared clip list from WISER before it can ship.

## 2. LMS Integration & Automated Grading
* **LTI (Learning Tools Interoperability) Compliance:** Implement LTI standards to allow the platform to plug directly into Canvas, Blackboard, or Google Classroom. Today the course embeds as an `<iframe>` and exports progress as JSON (see `docs/educator_guide.md`) — enough to *use* in a class, not enough to sync a gradebook.
* **Instructor Gradebook Sync:** *Half shipped.* Learners can now opt into Google sign-in, which
  mirrors their progress, prediction ledger and assessment scores to Firestore so a cleared cache
  or a new laptop no longer loses a climb. What does **not** exist is the instructor half: there
  is no roster, no class view, and no grade passback. Building that means deciding who is allowed
  to read a learner's record, which is a policy question before it is a technical one — so it is
  deliberately still open. Note the design constraint we kept: sign-in is a *mirror*, never the
  source of truth, so the course still works fully signed out and offline.
* **Autograding Pipelines:** Set up GitHub Actions or a basic backend sandbox runner to automatically run the notebook tests and grade submissions when students upload their notebook `.ipynb` files.

## 3. Adaptive Pedagogical Scaffolding
* **Dynamic Quiz Helper:** Upgrade the quiz engine to implement adaptive scaffolding. If a student answers a mathematical question incorrectly:
  * Do not just show the solution.
  * Serve a simplified, interactive widget sub-task (e.g., "Rotate the Bloch sphere until $P(1) = 0.75$, then copy the angle") to build physical intuition.
  * Re-evaluate the concept with a slightly modified mathematical question to verify recovery.
* **Partially shipped:** the *notebook* checkers already do a three-tier version of this
  (`q2q.hint`). Carrying the same ladder into the web quiz engine is the remaining work.

## 4. Fading the scaffolding

This one is a known gap in the pedagogy rather than a missing feature, and
[`pedagogical_style_guide.md`](pedagogical_style_guide.md) now points here rather than pretending
otherwise.

* **The problem.** Style guide rules 4 and 7 — predict first, and *teach-then-tweak* rather than
  a blank cell — apply with identical weight at Basecamp 6 as at Basecamp 1. Measured rather
  than asserted: **all twelve browser tasks have exactly three hint rungs and a multiple-choice
  prediction, from the first qubit to the QAOA summit.** The support never thins.
* **Why that is wrong.** The worked-example effect is well established for novices and is known
  to *reverse* as competence grows — the guidance that helps at the start begins to get in the
  way once a learner can generate the steps themselves. A summit that is scaffolded exactly as
  heavily as base camp also does not *feel* like a summit, which costs something real: the
  sense of having become capable is part of what the last basecamp is for.
* **What fading would look like here.** Later basecamps open closer to a blank canvas; the
  near-answer hint rung is withheld or deliberately costed at the summit; prediction questions
  shift from multiple choice to open response once the learner has met the vocabulary; the final
  task states a goal and a palette and no worked example.
* **Why it is not built.** Fading badly is worse than not fading — pull the support too early
  and the summit becomes frustrating rather than challenging, and we have no data yet on where
  learners actually are by Basecamp 5. Getting this right wants the aggregate evidence described
  in §6, not a guess. The completion-code contract between the two tracks would also have to
  survive whatever changes, since both must still mint the same code.
* **Status:** not built, deliberately. Named here so that a reader of the style guide can see
  the boundary of what we claim.

## 5. Localisation
* The glossary is already data-driven (`assets/data/glossary.json`), which makes it the
  natural first thing to translate. Full course localisation — notebook prose, quiz copy,
  widget labels — would require extracting every hardcoded string into a locale bundle. That
  refactor is scoped but not done, and we would rather say so than claim multi-language support
  we do not have.

## 6. Evidence at scale
* The pre/post diagnostic produces a per-learner delta locally. The next step is an opt-in,
  anonymous aggregate export so an instructor can report class-level gain — and so we can
  publish whether the course actually teaches what we claim it teaches, on more than a
  pilot-sized sample.
