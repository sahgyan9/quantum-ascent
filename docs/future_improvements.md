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
* **Instructor Gradebook Sync:** Replace the browser-based `localStorage` progress tracking with a lightweight backend database (e.g. Firebase Firestore). This is a deliberate trade we made *against* for the submission: no backend means no accounts, no privacy surface, and a resource that still works in ten years.
* **Autograding Pipelines:** Set up GitHub Actions or a basic backend sandbox runner to automatically run the notebook tests and grade submissions when students upload their notebook `.ipynb` files.

## 3. Adaptive Pedagogical Scaffolding
* **Dynamic Quiz Helper:** Upgrade the quiz engine to implement adaptive scaffolding. If a student answers a mathematical question incorrectly:
  * Do not just show the solution.
  * Serve a simplified, interactive widget sub-task (e.g., "Rotate the Bloch sphere until $P(1) = 0.75$, then copy the angle") to build physical intuition.
  * Re-evaluate the concept with a slightly modified mathematical question to verify recovery.
* **Partially shipped:** the *notebook* checkers already do a three-tier version of this
  (`q2q.hint`). Carrying the same ladder into the web quiz engine is the remaining work.

## 4. Localisation
* The glossary is already data-driven (`assets/data/glossary.json`), which makes it the
  natural first thing to translate. Full course localisation — notebook prose, quiz copy,
  widget labels — would require extracting every hardcoded string into a locale bundle. That
  refactor is scoped but not done, and we would rather say so than claim multi-language support
  we do not have.

## 5. Evidence at scale
* The pre/post diagnostic produces a per-learner delta locally. The next step is an opt-in,
  anonymous aggregate export so an instructor can report class-level gain — and so we can
  publish whether the course actually teaches what we claim it teaches, on more than a
  pilot-sized sample.
