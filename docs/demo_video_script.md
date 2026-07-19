# Demo Video Script — Quantum Ascent

**Status: living draft.** Record from this, then tweak the wording to sound like *you*.
The point is not to read it verbatim — it's to hit every beat that scores with the judges
without rambling or running long.

- **Target length:** ~7 minutes (brief allows 5–10; 7 leaves breathing room and respects
  the judge's time).
- **Format:** screen recording + your voice (a small webcam corner is optional but warms it
  up). 1080p, record the browser at a comfortable zoom so text is legible.
- **Golden rule:** *show, don't tell.* Every claim should happen on screen while you say it.
- **The one message to land:** *"We make a hard concept click — by hand, not by hand-waving —
  and we prove it's correct."* That is literally the challenge's "Key Focus."

Each beat below lists ⏱️ time · 🎬 what's on screen · 🎙️ roughly what you say · 🎯 which
judging criterion it targets.

---

## Beat 0 — Cold open / hook (0:00–0:30) 🎯 *Engagement, Creativity*

🎬 Start **on the live widget already moving** — the Bloch Sampler, dragging the slider so the
arrow tilts and the green/amber split shifts. No title card yet.

🎙️ *"This arrow is a qubit. Watch the colour: green is the chance of measuring 0, amber the
chance of 1 — the exact probabilities, shown as physical proportions. I haven't written a
single equation yet, and you already understand superposition. That's the whole idea behind
Quantum Ascent."*

> Why open here: judges see engagement and the core innovation in the first 30 seconds,
> before any preamble. Hook first, context second.

---

## Beat 1 — The problem & who it's for (0:30–1:15) 🎯 *Educational impact, Adoption*

🎬 Cut to the **home page** ([quantum-ascent-77617.web.app](https://quantum-ascent-77617.web.app)),
scroll slowly through the pitch.

🎙️ *"Most quantum courses hand you slides and dense linear algebra on page one, and learners
bounce off. Quantum Ascent is for the motivated beginner — a STEM student or a developer who's
curious but not yet a physicist. Our fix is a simple loop repeated for every concept: play
with it first, then code it, then make it personal. Let me show you the climb."*

> Name the learning gap out loud — the brief explicitly rewards teams that "identify a
> specific learning gap." Keep it to two sentences.

---

## Beat 2 — The Ascent map / structure (1:15–1:45) 🎯 *Creativity, Engagement*

🎬 Open the **Ascent map** (`ascent.html`). Point at the six basecamps, XP, badges.

🎙️ *"The course is a mountain. Six basecamps, from your first qubit up to solving a real
optimization problem with QAOA at the summit. You earn XP and badges as you climb — self-paced,
all saved right in your browser, no account needed."*

> Short. The map is eye candy; let it breathe, don't over-narrate.

---

## Beat 3 — Inside a basecamp: PLAY (1:45–3:00) 🎯 *Educational impact, Technical accuracy*

🎬 Open **Basecamp 2 (Gates & Circuits)**. Land on the **Gate Playground** widget. Tap **H** —
show the arrow snap to the equator, 50/50. Tap **H** again — back to a definite 0. Then tap
**Z** and narrate that the *probabilities don't move but the hidden phase does*.

🎙️ *"Every basecamp starts with a widget you poke before you read any math. Here's the Gate
Playground. Tap Hadamard — the qubit goes to a fair 50/50 spin. Tap it again — it snaps right
back, because H is its own undo. Now watch Z: the colours don't change at all — the odds are
identical — but the hidden phase flips. That invisible phase is the seed of interference, and
the widget's plain-language explanation updates to say exactly what I'm seeing on screen."*

> This is your strongest 90 seconds: it's the moat (visual probability + myth-free framing)
> *and* it's technically precise. Slow down here.

---

## Beat 4 — Inside a basecamp: CODE + the proof of correctness (3:00–4:45) 🎯 *Technical accuracy, Implementation quality*

🎬 Click **Open in Colab** on the same basecamp. Scroll the notebook: show a **gap-fill task**
(`# YOUR CODE HERE`). Fill it in, run it, show the **checker's green pass**. Then deliberately
run a *wrong* answer once and show the checker's **specific, coaching feedback** (not just
"wrong"). Mention shot-noise tolerance.

🎙️ *"Reading isn't doing, so the notebooks make you write the quantum code — we give the
scaffolding, you fill the gap. When you run it, an instant checker responds. And it's honest:
it uses a statistical test, so a correct answer never fails just because quantum sampling
fluttered a little. If you're wrong, it tells you *why*, in plain language — like a patient
tutor, not a red X."*

🎬 Scroll to the end, run the final cell — the **completion code** appears
(`QA-02-8754-50BF`). Copy it, go **back to the website's "Log your climb" box**, paste it, hit
enter — **confetti, XP, basecamp lights up on the map.**

🎙️ *"Finish the tasks and the notebook mints a completion code. Paste it back on the website
and the basecamp lights up — XP banked, badge earned. The browser and the notebook are two
worlds, and this code is the handshake between them — verified offline, with no server and no
account, by re-computing the exact same hash in JavaScript that Python produced."*

> This round-trip is memorable and unique — make sure it lands on camera. It hits *technical
> accuracy* (real checkers) and *implementation quality* (the cross-world handshake) at once.

---

## Beat 5 — Make it personal: Analogy Studio (4:45–5:30) 🎯 *Creativity, Educational impact*

🎬 Open the **Analogy Studio**. Type a hobby (e.g. *cricket* or *baking*). Show the generated,
guard-railed prompt. (Optionally paste into an LLM in another tab and show the result — but
keep it quick.)

🎙️ *"The third step is personalization. Tell the Analogy Studio what you love — cricket,
music, cooking — and it engineers a prompt for whatever AI you already use. Crucially, it bakes
in physical ground rules, so the AI explains the concept through your world *without* drifting
into the usual pop-science myths. Notice the course itself never calls an AI — it hands you the
prompt. It costs nothing to run and works offline."*

> The "no AI at runtime" line pre-empts a judge's reliability/cost worry and shows
> intentional design.

---

## Beat 6 — Under the hood: correctness & reproducibility (5:30–6:20) 🎯 *Documentation, Technical accuracy, Scalability*

🎬 Switch to the repo / terminal. Run **`pytest`** live and let it finish — show the green
**"68 passed."** Flash the `docs/` folder and `tools/` briefly.

🎙️ *"Everything you just saw is backed by a test suite. One command runs it: it executes every
solution notebook end to end, smoke-tests every widget, and even checks that the Python and
JavaScript versions of that completion code agree. Sixty-eight tests, all green. We build
tests first, then features — so an educator can clone this repo, run one install, and trust
that every notebook works."*

> Running the suite live is worth more than any slide claiming "well-tested." This is your
> reproducibility and adoption proof.

---

## Beat 7 — Close: roadmap, AI disclosure, sign-off (6:20–7:00) 🎯 *Scalability, AI attribution*

🎬 Back to the Ascent map showing basecamps lit. Optionally the `docs/ai_use.md` on screen.

🎙️ *"Two basecamps are live today; the pipeline that generated them makes the climb to the
summit a matter of authoring, not re-engineering. We built this with the Claude Code assistant
and documented exactly how in our AI-use disclosure — but every piece of physics is
human-verified and pinned by those tests. That's Quantum Ascent: play it, code it, make it
yours — hard ideas made clear, and proven correct. Thanks for climbing with us."*

> End on the one-message. Don't trail off — a crisp sign-off reads as confidence.

---

## Pre-record checklist

- [ ] Site is live and hard-refreshed (Ctrl+Shift+R); CDN not stale.
- [ ] Colab notebook opens and runs (test the round-trip once *before* recording).
- [ ] Have the completion code path rehearsed so the confetti moment is clean.
- [ ] `pytest` runs green in the terminal you'll show.
- [ ] Browser zoom up so text is readable at 1080p; close noisy tabs/notifications.
- [ ] Mic check — quiet room, no clipping.
- [ ] Keep a stopwatch; if a beat runs long, cut Beat 2 or the LLM paste in Beat 5 first.

## Tips

- **One take per beat**, then stitch — far less stressful than one perfect 7-minute run.
- If you fumble a line, pause and redo the sentence; you'll cut it in editing.
- Silence while something loads is fine — narrate *around* loads, don't wait in dead air.
- It's okay to sound human. Enthusiasm reads better than polish.
