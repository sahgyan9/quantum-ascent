# User Guide

This guide details how to navigate and run the **Quantum Ascent** platform, structured for both independent learners and classroom educators.

---

## 1. Guide for Learners

Everything runs in the browser. There is **no account and nothing to install** unless you
choose the notebook track, and all progress is saved locally in your own browser.

### Before you start (about 20 minutes, and worth it)

1. **[Kit Check](https://quantum-ascent-77617.web.app/kit-check.html)** — five questions on the
   maths and Python this course actually leans on (radians, the half-angle, dictionaries,
   `def … return`, squaring a negative). Get one wrong and a 90-second refresher opens. It is
   not a test and it cannot stop you climbing. **You do not need complex numbers** for this
   course, whatever other quantum courses may have told you.
2. **[Concept Diagnostic](https://quantum-ascent-77617.web.app/assessment.html)** — take the
   *before* version now, while you still know nothing. It shows you no score and no answers on
   purpose. When you take it again after the Summit, the difference is your proof.

### The study path — for each basecamp

Open the basecamp from the [Ascent Map](https://quantum-ascent-77617.web.app/ascent.html), then:

1. **Play first.** Section 1 is an interactive widget. Poke it, make a prediction out loud,
   then measure. Let your hands build the intuition *before* any maths arrives — this order
   matters, and doing it backwards is the most common way to make the course harder than it is.
2. **Do the physics.** Section 2 offers **two equivalent tracks**. Pick whichever suits you
   today; they set the same tasks and mint the same completion code.
   * **🧪 Browser Lab** — build real circuits by clicking, right in the page. Nothing to
     install, no Google account, no waiting. It runs an exact statevector simulator, and the
     equivalent **Qiskit code is written out beside you as you click**, so you pick up the real
     syntax for free. Best for a first pass, a phone, or a locked-down lab machine.
   * **⛏️ Notebook** — the same tasks in Google Colab against **real Qiskit**. Worth doing at
     least once: it is the toolchain actual research uses. Budget 60–90 seconds for the first
     install.
3. **Predict before you run.** Each task asks you to commit to an answer first. Do it honestly
   — those predictions are recorded, and at the Summit you get a **calibration report** showing
   not just what you learned but how well you judge your own understanding.
4. **When you get stuck, ask for a hint before the answer.** Both tracks give a three-rung
   ladder: a nudge, then a strategy, then almost-the-answer. In the Lab it is the *"I'm
   stuck"* button; in a notebook it is `hints.hint("03-1")`, run again for the next rung.
   Nothing is recorded and nothing is penalised.
5. **Prove it.** Section 3 is the quiz. Score 70% or above to earn the basecamp XP and claim
   your badge.

### After the Summit

* Retake the **[Concept Diagnostic](https://quantum-ascent-77617.web.app/assessment.html)** —
  you get both scores, the delta, a concept-by-concept table, your calibration report, and a
  full explanation of every question.
* **Export your results** from the diagnostic if your teacher asked for them: one JSON file,
  no upload, no account.

### Two things worth using whenever you like

* **[Myth Autopsy](https://quantum-ascent-77617.web.app/myths.html)** — six famous claims about
  quantum computing, each dissected with a live simulation. Includes one where you hold both
  halves of an entangled pair and try to send a faster-than-light message. (You will fail. That
  is the lesson.)
* **[Analogy Studio](https://quantum-ascent-77617.web.app/analogy-studio.html)** — stuck on a
  concept? Pick it, type in one of your hobbies, and generate a prompt with the physics
  guard-rails baked in. Paste it into ChatGPT, Claude or Gemini. Then **paste the answer back**
  into the Studio's auditor: it flags the myth phrasings the AI was told not to use, and hands
  you a checklist to grade the rest yourself.

---

## 2. Guide for Educators

Quantum Ascent is built to be modular, allowing educators to adopt parts of the course or deploy the entire platform with minimal friction.

### A. Embedding Interactive Widgets in your LMS / Slides
Every widget is a self-contained HTML/JS/CSS page with zero remote dependencies. You can embed them directly into presentation slides (like Mentimeter) or Learning Management Systems (Canvas, Blackboard, Moodle) using an `iframe`:
```html
<iframe src="https://quantum-ascent-77617.web.app/widgets/bloch-sampler/index.html" 
        width="100%" height="560px" style="border: 1px solid #26304f; border-radius: 12px;"></iframe>
```
Available widgets:
* `coin-spinner` — measurement and collapse, without the "0 and 1 at once" myth
* `bloch-sampler` (Basecamp 1) — shows degrees **and** radians side by side
* `gate-playground` (Basecamp 2)
* `entanglement-explorer` (Basecamp 3)
* `energy-meter` (Basecamp 4)
* `qaoa-landscape` (Basecamp 5)
* `maxcut-painter` (Basecamp 6)
* `circuit-lab` — the full click-to-build circuit editor with a live Qiskit code mirror; this
  is the engine the whole browser track runs on, and it is useful on its own for any lesson
  where you want to build a circuit in front of a class

Every widget also carries an `aria-live` text mirror of its state, so screen-reader and
keyboard-only learners get the same reading at the same moment. Sliders are native range
inputs, so arrow keys work everywhere.

For whole basecamps rather than single widgets, embed
`https://quantum-ascent-77617.web.app/lab.html?id=03` (the graded browser track) or
`module.html?id=03` (the full basecamp page).

### B. Local Development & Hosting Setup
To run the platform or customize the files locally:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/sahgyan9/quantum-ascent.git
   cd quantum-ascent
   ```
2. **Install Dependencies:**
   Ensure Python 3.10+ is installed, then run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Local Web Server:**
   Launch the lightweight local development server:
   ```bash
   python tools/serve_local.py
   ```
   Open your browser and navigate to `http://localhost:8000`.
4. **Run the Testing Suite:**
   Verify that all checker algorithms, widgets, and notebooks compile and execute correctly:
   ```bash
   pytest
   ```

### C. Notebook & Assignment Generation
The repository utilizes an automated build script to separate student assignments from the solved instructor versions:
* **Source files:** Instructors write and test notebooks inside `notebooks/solutions/` containing full solution codes.
* **Build Script:** Run the python script to strip out the solution codes and replace them with student-facing `# YOUR CODE HERE` blocks and template exceptions:
  ```bash
  python tools/build_solutions.py
  ```
  This automatically compiles clean, ready-to-distribute student notebooks in the parent `notebooks/` directory.
