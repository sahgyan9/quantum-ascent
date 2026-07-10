# User Guide

This guide details how to navigate and run the **Quantum Ascent** platform, structured for both independent learners and classroom educators.

---

## 1. Guide for Learners

The learning flow is managed through the browser dashboard:

* **Navigate the Ascent:** Open the [Ascent Map](https://quantum-ascent-77617.web.app/ascent.html) to see your climbing route. Available basecamps are displayed as clickable nodes.
* **The Study Path:** For each active basecamp:
  1. Scroll to **Section 2: Do the physics** and click **Open in Google Colab**. This launches a Jupyter notebook in the cloud with zero installation. Read the notebook line by line, complete the gap-fill coding tasks, and run the checker cells to verify your answers.
  2. Return to the basecamp page and play with the **Interactive Widget** in **Section 1**. Adjust parameters (like Bloch sphere angles) to visually connect what you coded to real-time physical states.
  3. Complete **Section 3: The Quiz**. Score $70\%$ or above to earn the basecamp XP and claim your digital badge!
* **Analogy Studio:** When struggling with a concept, navigate to the **Analogy Studio**, select the concept, input one of your hobbies/backgrounds, and click generate. Copy the custom engineered prompt and paste it into ChatGPT, Claude, or Gemini to receive a physically-grounded analogy customized to your life.

---

## 2. Guide for Educators

Quantum Ascent is built to be modular, allowing educators to adopt parts of the course or deploy the entire platform with minimal friction.

### A. Embedding Interactive Widgets in your LMS / Slides
Every widget is a self-contained HTML/JS/CSS page with zero remote dependencies. You can embed them directly into presentation slides (like Mentimeter) or Learning Management Systems (Canvas, Blackboard, Moodle) using an `iframe`:
```html
<iframe src="https://quantum-ascent-77617.web.app/widgets/bloch-sampler/index.html" 
        width="100%" height="560px" style="border: 1px solid #26304f; border-radius: 12px;"></iframe>
```
Available widgets include:
* `bloch-sampler` (Basecamps 1 & 4)
* `gate-playground` (Basecamp 2)
* `entanglement-explorer` (Basecamp 3)
* `qaoa-landscape` (Basecamp 5)
* `maxcut-painter` (Basecamp 6)

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
