# Target Audience

**Quantum Ascent** is designed to bridge the gap between pop-science conceptual overviews and advanced mathematical textbooks. It targets two primary user groups:

## 1. Primary Learners (Students)
* **Undergraduate & Advanced High School Students:** Learners in Computer Science, Physics, Mathematics, or Engineering who want to acquire a concrete, functional understanding of quantum computing.
* **Self-Taught Developers:** Coders curious about quantum computing who want to build and execute actual circuits rather than just read theoretical papers.
* **Entry Requirements (Prerequisites):**

  We list these precisely, because vague prerequisites scare off people who would do fine.
  Every item below is *checked and repaired* by **Basecamp 0 — Kit Check**, a ten-minute
  self-diagnostic that opens the course. Nothing here is a barrier; it is a packing list.

  * **Mathematics:**
    * High-school algebra — rearranging an equation, taking a square root.
    * Trigonometry to the level of "$\sin$ and $\cos$ are numbers between $-1$ and $1$ that
      depend on an angle," plus **angles measured in radians** ($180° = \pi$). The radian
      habit is the single most common stumbling block in Basecamp 1, so Kit Check drills it
      and every widget shows degrees and radians side by side.
    * Squaring a number, and reading $\sin^2(\theta/2)$ as "take $\sin$ of half the angle,
      then square it."
  * **Programming:** Enough Python to read a `for` loop and call a function. Kit Check covers
    the two structures the course actually leans on — **dictionaries** (measurement counts
    arrive as one) and **functions that `return` a value**. Every new library call is shown in
    a complete, runnable example before any task asks you to write it.
  * **Complex numbers: not required.** This course deliberately keeps every amplitude **real
    and non-negative**, so the Born rule stays $P = (\text{amplitude})^2$ and you never meet
    an $i$. (Earlier drafts of this document listed complex numbers as a prerequisite. That
    was wrong, and it was scaring off exactly the learners we built this for.)
  * **Quantum Physics:** **Zero prior knowledge required.** The course builds the quantum state vector, superposition, and gates from first physical principles.
* **Two ways to take it, same course:**
  * **Browser track** — every basecamp is completable on the website with nothing installed
    and no account, using the in-browser Circuit Lab. Best for a first pass, a classroom, a
    Chromebook, or a phone.
  * **Notebook track** — the same tasks in Jupyter/Colab against **real Qiskit**, for learners
    who want the industry SDK on their CV. Optional, not required.

## 2. Secondary Learners (Educators)
* **High School Teachers & University Professors:** Educators looking for modular, interactive materials to integrate into Computer Science, Physics, or STEM enrichment courses.
* **Benefits for Educators:**
  * **Zero-Setup Widgets:** Self-contained visualization widgets (HTML/JS) that can be embedded into slides or learning management systems (Canvas, Blackboard) using a simple `<iframe>` tag.
  * **Instant-Feedback Homework:** Guided Jupyter notebooks with local unit checkers, allowing educators to assign tasks that grade themselves locally and explain *why* errors occur.
