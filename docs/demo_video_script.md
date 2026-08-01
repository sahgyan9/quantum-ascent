# Demo Video Script — Quantum Ascent

**Status: living draft.** Record from this, then tweak the wording to sound like *you*.
The point is not to read it verbatim — it's to hit every beat that scores with the judges
without rambling or running long.

- **Target length:** ~8 minutes 20 (brief allows 5–10; this leaves room for the summit payoff
  while respecting the judge's time). If you run long, trim in this order: Beat 2 (the map is
  eye candy), then Beat 6 down to the no-signalling demo alone, then the Colab flip in Beat 4.
  **Do not cut Beats 4, 5 or 7** — those carry the strongest scoring material.
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
optimization problem with QAOA at the summit — and all six are live. You earn XP and badges as
you climb — self-paced, all saved right in your browser, no account needed."*

> Short. The map is eye candy; let it breathe, don't over-narrate.

---

## Beat 3 — Kit Check: remove the real barrier (1:45–2:20) 🎯 *Educational impact, Engagement*

🎬 Open **Kit Check** (`kit-check.html`). Answer the radians question **wrong on purpose** —
let the 90-second refresher slide open on camera.

🎙️ *"Before any physics, ten minutes of Basecamp Zero. Because here's what we learned reading
our own course as a beginner: nobody quits over quantum mechanics. They quit over a radian, or
a Python dictionary, arriving with no warning in the middle of a sentence about qubits — and
then they blame themselves. So we check the five things this course actually leans on, and a
wrong answer opens a refresher right there. Watch — I'll get one wrong. No score, no gate, and
notice the wording: wrong answers aren't failure here, they're the mechanism. And one more
thing — we removed complex numbers from our own prerequisites, because this course deliberately
never uses them. We were scaring off exactly the people we built it for."*

> Pure *educational impact*, and the kind of empathy judges rarely see. It also plants the
> honesty theme that carries the rest of the video.

---

## Beat 4 — Play, then do it — with nothing installed (2:20–4:00) 🎯 *Creativity, Implementation quality, Adoption*

🎬 Open **Basecamp 3** and land on the widget — poke it briefly. Then click
**Open the Browser Lab**.

🎙️ *"Every basecamp starts with something you poke before you read any maths."*

🎬 In the Lab: answer the **prediction question** first, then build the Bell pair by clicking
**H**, then **CNOT**. Point at the exact-state bars and the **Qiskit code appearing on the
right** as you click.

🎙️ *"Now the part I'm proudest of. This is the whole basecamp, running in the browser — no
install, no Google account, no ninety-second wait. And it's not a cartoon: that's an exact
statevector simulator, and our test suite checks it against real Qiskit to twelve decimal
places. Qiskit can't run in a browser — its core has been compiled Rust since version one — so
we wrote the physics ourselves rather than water it down.*

*Two details worth catching. First: it made me commit to a prediction before it would let me
build anything. Second — look at the right-hand panel — as I click, it's writing the real
Qiskit code. So a learner on a Chromebook is picking up the industry SDK's syntax for free."*

🎬 Click **Check my answer** → green pass. Then break it — remove a gate, or build Ψ⁺ instead
of Φ⁺ — and show the checker naming the **specific** mistake.

🎙️ *"The checker judges the physics, never the gate list, so any circuit producing the right
state passes. And when you're wrong it diagnoses what you actually did — here, that I built
the pair that always agrees when I was asked for the one that always disagrees. Get stuck and
you get a ladder: a nudge, then a strategy, then almost-the-answer. Never just 'go look at the
solution.'"*

🎬 Flip to the same basecamp's **Colab notebook** in another tab, briefly.

🎙️ *"And if you want the industry SDK — same tasks, real Qiskit, one click. Both tracks mint the
identical completion code, and the physics matches to twelve decimal places. What changes is the
toolchain, not the correctness."*

> Your strongest 100 seconds: creativity, adoption and implementation quality at once. Slow
> down, and make sure the Qiskit code mirror is legible at 1080p.

---

## Beat 5 — The Summit, honestly (4:00–5:30) 🎯 *Technical accuracy, Educational impact*

🎬 Open **Basecamp 6**. Show the 4-ring QAOA result — approximation ratio 1.0. Then scroll to
**section 7**.

🎙️ *"At the summit you build QAOA and solve Max-Cut end to end — cost layer, mixer, classical
optimizer — and you score a perfect approximation ratio. And then we tell you why that number
is misleading."*

🎬 Run the **triangle** brute-force cell: 3 edges, best cut 2.

🎙️ *"A four-node ring is bipartite. It's the one graph where this algorithm cannot fail — so
stopping there would teach you something false. Here's a triangle instead. Three roads, and
the best possible split cuts two. Not because the algorithm is weak: because two of three
mutually connected towns must end up together. That's the problem being frustrated, not the
solver failing — and telling those two apart is the actual job."*

🎬 Run the **5-cycle** cell: p=1 ratio ≈ 0.94, p=2 ratio ≈ 1.00.

🎙️ *"Then a five-cycle, where the shortfall really is the algorithm's. Depth one tops out
around ratio 0.94; a second layer closes it. And we say the thing that usually gets left out —
more depth means more gates, and on real hardware more gates mean more noise. Nobody has
demonstrated quantum advantage on this problem. I'd rather a learner leave knowing that than
leave impressed."*

> This is the beat that separates you from every submission that stops at the easy graph. If a
> judge knows QAOA, this is where they sit up.

---

## Beat 6 — The Myth Autopsy: try to break physics (5:30–6:40) 🎯 *Creativity, Technical accuracy*

🎬 Open **Myth Autopsy** (`myths.html`), scroll to **myth 2**. Change Alice's basis, click
**Alice measures 500 times**, and point at **Bob's histogram refusing to move**.

🎙️ *"Our stated advantage is that we don't teach myths — so we turned that into a page people
can share. Six famous claims, each dissected with a simulation you run yourself, on the same
engine as the Lab.*

*This one's my favourite. You're holding both halves of an entangled pair, and your job is to
break physics: send Bob a message faster than light. Change Alice's basis. Measure five
hundred times. Bob's histogram sits at fifty-fifty, every single time. But look at the third
line of the readout — in the Z basis they agree one hundred percent. The correlation is
completely real, and Bob still can't see it on his own. You just tried to send a message,
failed, and you'll remember exactly why."*

🎬 Scroll to a **"Say this instead"** strip.

🎙️ *"And every myth ends with a replacement sentence — true, and short enough to actually use.
Correcting someone without giving them better words just leaves them repeating the myth with a
caveat attached."*

---

## Beat 7 — Proof it works, and proof it's right (6:40–7:45) 🎯 *Educational impact, Documentation, Implementation quality*

🎬 Open the **Diagnostic** (`assessment.html`) on a completed before/after: the two scores, the
delta, the concept table, and the **calibration report**.

🎙️ *"Design intent isn't evidence, so here's the evidence. The same ten questions before
Basecamp 1 and again after the Summit. The before-test deliberately shows you nothing — no
score, no answers — because if it revealed them, the after-test would be measuring the test
instead of the course.*

*Several of the wrong options are the popular myths, phrased the way you've actually read them,
so we can tell whether we dislodged those specific beliefs.*

*And this piece I haven't seen anywhere else in quantum education. Every task made you predict
before you ran anything, and we recorded those — so you also get a calibration report. Not
just what you learned, but how well you judge your own understanding. That's a measurable
learning outcome, which is exactly what the brief asks for."*

🎬 Cut to a terminal. Run `pytest`. Let the count land on screen.

🎙️ *"Underneath all of it, three hundred and forty-six tests. They execute every notebook end
to end, check the browser simulator against Qiskit, prove all twelve tasks are solvable — and
this one matters most — they recompute every number our prose claims, including the exact
angles our hints tell you to type. A hint that doesn't work is worse than no hint, because the
learner follows it, fails anyway, and blames themselves."*

---

## Beat 8 — Close: adopt it, fork it, AI disclosure (7:45–8:20) 🎯 *Scalability, Adoption, AI attribution*

🎬 Show `docs/educator_guide.md` briefly, then the home page footer.

🎙️ *"For educators: every widget is one self-contained file you can drop into Canvas with an
iframe, the whole site runs offline from a folder, and the content is CC-BY — fork it,
translate it, teach it. Fifteen minutes to first class.*

*AI assistance was used in development and it's documented in full — but no model runs anywhere
in the shipped course, and every physics claim is pinned by a test you can re-run with one
command.*

*That's Quantum Ascent: play first, predict, build it for real in your browser — and be told
the truth, including where the algorithm falls short. Thanks for watching."*

---

## Pre-record checklist

- [ ] Site is live and hard-refreshed (Ctrl+Shift+R); CDN not stale.
- [ ] Colab notebook opens and runs in an INCOGNITO window (proves the public bootstrap works).
- [ ] Browser Lab completed once for Basecamp 3 and 6 so the flow is muscle memory.
- [ ] Diagnostic has a real before/after in localStorage, and the Ledger has entries, so Beat 7 has something to show.
- [ ] Have the completion code path rehearsed so the confetti moment is clean.
- [ ] `pytest` runs green in the terminal you'll show.
- [ ] Browser zoom up so text is readable at 1080p; close noisy tabs/notifications.
- [ ] Mic check — quiet room, no clipping.
- [ ] Keep a stopwatch; if a beat runs long, cut Beat 2, then trim Beat 6 to the no-signalling demo only.

## Tips

- **One take per beat**, then stitch — far less stressful than one perfect 7-minute run.
- If you fumble a line, pause and redo the sentence; you'll cut it in editing.
- Silence while something loads is fine — narrate *around* loads, don't wait in dead air.
- It's okay to sound human. Enthusiasm reads better than polish.
