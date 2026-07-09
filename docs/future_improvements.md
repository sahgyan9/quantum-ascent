# Future Improvements & Scalability

**Quantum Ascent** has a robust foundation but is designed for active expansion. Below is the roadmap for future development, pedagogical integrations, and technical scaling:

---

## 1. Content Expansion (Immediate Horizon)
* **Basecamps 2–6 Completion:** Develop and test the full Jupyter notebook curricula, quizzes, and widgets for the remaining 5 basecamps.
* **Capstone Refinement:** Build out the interactive `maxcut-painter` widget in Basecamp 6, allowing students to manually draw graphs on-screen and watch QAOA optimize the partitions in real-time.

## 2. Interactive Video Lecture Integration
* **The Problem:** WISER has a vast catalog of recorded video lectures, but passive video watching leads to low conceptual retention.
* **The Solution:** Create a **"Lecture Hall"** panel on the basecamp page that indexes relevant video lecture clips. We will link specific video timestamps directly to the corresponding concepts, widgets, and notebook code blocks.
* **Student Workflow:** A student stuck on a notebook task can click a "Watch Explainer" button to overlay the exact 2-minute video segment where an invited speaker explains the underlying mathematics.

## 3. LMS Integration & Automated Grading
* **LTI (Learning Tools Interoperability) Compliance:** Implement LTI standards to allow the platform to plug directly into Canvas, Blackboard, or Google Classroom.
* **Instructor Gradebook Sync:** Replace the browser-based `localStorage` progress tracking with a lightweight backend database (e.g., Firebase Firestore). When students complete a basecamp quiz or check in their notebook solutions, their grades and XP will sync directly to their university's gradebook.
* **Autograding Pipelines:** Set up GitHub Actions or a basic backend sandbox runner to automatically run the notebook tests and grade submissions when students upload their notebook `.ipynb` files.

## 4. Adaptive Pedagogical Scaffolding
* **Dynamic Quiz Helper:** Upgrade the quiz engine to implement adaptive scaffolding. If a student answers a mathematical question incorrectly:
  * Do not just show the solution.
  * Serve a simplified, interactive widget sub-task (e.g., "Rotate the Bloch sphere until $P(1) = 0.75$, then copy the angle") to build physical intuition.
  * Re-evaluate the concept with a slightly modified mathematical question to verify recovery.
