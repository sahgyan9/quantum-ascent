# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases
- Written in plain language, the same way you'd brief someone on your team

**Layer 2: Agents (The Decision-Maker)**
- This is your role. You're responsible for intelligent coordination.
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed
- You connect intent to execution without trying to do everything yourself
- Example: If you need to pull data from a website, don't attempt it directly. Read `workflows/scrape_website.md`, figure out the required inputs, then execute `tools/scrape_single_site.py`

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work
- API calls, data transformations, file operations, database queries
- Credentials and API keys are stored in `.env`
- These scripts are consistent, testable, and fast

**Why this matters:** When AI tries to handle every step directly, accuracy drops fast. If each step is 90% accurate, you're down to 59% success after just five steps. By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

## How to Operate

**1. Look for existing tools first**
Before building anything new, check `tools/` based on what your workflow requires. Only create new scripts when nothing exists for that task.

**2. Learn and adapt when things fail**
When you hit an error:
- Read the full error message and trace
- Fix the script and retest (if it uses paid API calls or credits, check with me before running again)
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behavior)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

**3. Keep workflows current**
Workflows should evolve as you learn. When you find better methods, discover constraints, or encounter recurring issues, update the workflow. That said, don't create or overwrite workflows without asking unless I explicitly tell you to. These are your instructions and need to be preserved and refined, not tossed after one use.

## The Self-Improvement Loop

Every failure is a chance to make the system stronger:
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow with the new approach
5. Move on with a more robust system

This loop is how the framework improves over time.

By Gyan ----
## Development Prioritization (Stability-First)

When writing code or making modifications to the system, you must strictly follow this chronological hierarchy of execution:

1. **Testing Infrastructure First:** Before writing any application logic, ensure the testing harness (unit tests, integration tests, CI/CD pipelines, mock data) is established and functioning. You cannot verify code without the tools to test it.
2. **Fixes Second:** If there are existing bugs, regressions, or failing tests, they MUST be resolved before any new work begins. Return the system to a known, stable, passing baseline ("fix before feature").
3. **Features Last:** Only when the testing infrastructure is solid and the existing codebase is completely stable (zero known bugs or failing tests) do you begin writing new features. All new features should be written against tests.
----

## File Structure

**What goes where:**
- **Deliverables**: Final outputs go to cloud services (Google Sheets, Slides, etc.) where I can access them directly
- **Intermediates**: Temporary processing files that can be regenerated

**Directory layout:**
```
.tmp/           # Temporary files (scraped data, intermediate exports). Regenerated as needed.
tools/          # Python scripts for deterministic execution
workflows/      # Markdown SOPs defining what to do and how
.env            # API keys and environment variables (NEVER store secrets anywhere else)
credentials.json, token.json  # Google OAuth (gitignored)
```

**Core principle:** Local files are just for processing. Anything I need to see or use lives in cloud services. Everything in `.tmp/` is disposable.

By Gyan----
## UX & Design Guidelines (Don Norman Principles)

When building user-facing interfaces (web, CLI, or otherwise), you MUST adhere to Don Norman's principles of design to ensure a seamless user experience:

1. **Discoverability (Visibility):** Make sure users can easily figure out what actions are possible and where things are. Never hide critical features.
2. **Feedback:** Provide immediate, clear, and unambiguous responses to user actions (e.g., loading states, success messages, error handling).
3. **Conceptual Model:** Design interfaces that map closely to how the user already thinks about the real-world task.
4. **Affordances & Signifiers:** Ensure UI elements clearly look like what they do (e.g., buttons should look clickable, inputs should look typable).
5. **Mapping:** Maintain a natural and logical relationship between controls and their effects (e.g., a "next" button should be on the right, "back" on the left).
6. **Constraints:** Prevent users from making errors by restricting invalid choices (e.g., disable buttons when a form is invalid instead of throwing an error after submission).
----

## Pedagogical & Content Preferences

**The Moat (Core Competitive Advantage):** This platform differentiates itself by strictly avoiding pop-science myths (e.g., "qubits are 0 and 1 at the same time") and overwhelming jargon. Instead, the focus is strictly on highly interactive, deeply grounded physical analogies (e.g., the spinning coin) coupled with step-by-step guidance. This approach MUST be documented and prioritized across all educational content.

When authoring or modifying educational Jupyter Notebooks and web resources:
1. **Beginner Friendliness & Counselling**: Adopt a supportive, reassuring, and encouraging tone throughout. 
   - When introducing potentially overwhelming topics or equations, explicitly check in on the student (e.g., *"If this feels like a lot, don't worry! We will build and understand these concepts slowly, step-by-step."*).
   - Incorporate helpful study tips (e.g., *"If the math or concepts feel intimidating, the best way to grab them is to grab a physical pen and write them down on paper as we go!"*).
   - Use clear, physical analogies to resolve confusing pop-science descriptions (e.g., use a *spinning coin analogy* to explain quantum measurement/collapse instead of the confusing *"0 and 1 at the same time"* slogan).
2. **Minimize Upfront Mathematical Overhead**: Do not overwhelm students with dense linear algebra, complex numbers, or bracket notation in early sections or at first exposure. Introduce concepts conceptually first using analogies, visual signifiers, or interactive widgets, and introduce formal mathematical representations gradually and gently.
   - **Syntax Pre-requisites**: Always provide a clear, simple code example demonstrating the exact syntax of any library functions or data structures (like NumPy arrays) before asking students to write them in a task. Never assume prior programming knowledge for new syntax.
3. **Ignore-Math-Setup Signifiers**: Clearly signpost any macro or bootstrap setup cells defining math notation (e.g., LaTeX macros) so that students know they can safely ignore the underlying code/setup blocks and only focus on the concepts.
4. **Develop Critical Thinking Over Rote Coding**: Emphasize why concepts work, predicting statistics before executing code, and analyzing outcomes. Keep coding requirements focused on verifying concepts (since writing raw code can be done by AI).
5. **Consistency Across Web/UI**: Apply these exact same tone, analogies, and step-by-step guidance rules to all course website copy, educational apps, and interactive UI widgets.

----

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
