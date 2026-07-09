/* Quantum Ascent — quiz renderer with immediate per-question feedback. */
"use strict";

async function renderQuiz(containerId, moduleId, moduleMeta) {
  const el = document.getElementById(containerId);
  const questions = (await (await fetch("assets/data/quizzes.json")).json())[moduleId];
  if (!questions) {
    el.innerHTML = '<p class="muted">Quiz for this basecamp is on its way. ⛏️</p>';
    return;
  }

  let answered = 0, correct = 0;
  el.innerHTML = `<p class="muted">${questions.length} questions · answer each one to
    see the explanation · score ≥ 70% completes the basecamp</p>`;

  questions.forEach((item, qi) => {
    const box = document.createElement("div");
    box.className = "quiz-q panel";
    box.innerHTML = `<b>Q${qi + 1}.</b> ${item.q}`;
    item.options.forEach((opt, oi) => {
      const btn = document.createElement("button");
      btn.className = "quiz-opt";
      btn.textContent = opt;
      btn.addEventListener("click", () => {
        if (box.dataset.done) return;
        box.dataset.done = "1";
        answered++;
        const good = oi === item.answer;
        if (good) correct++;
        btn.classList.add(good ? "correct" : "wrong");
        [...box.querySelectorAll(".quiz-opt")].forEach((b, i) => {
          b.disabled = true;
          if (i === item.answer) b.classList.add("correct");
        });
        const ex = document.createElement("div");
        ex.className = "quiz-explain";
        ex.innerHTML = `<span style="font-weight:700; color: ${good ? 'var(--accent)' : 'var(--danger)'}">${good ? "✓ Correct: " : "✗ Incorrect: "}</span>` + item.explain;
        box.appendChild(ex);
        if (typeof renderMathInElement !== "undefined") {
          renderMathInElement(ex, {
            delimiters: [
              {left: '$$', right: '$$', display: true},
              {left: '$', right: '$', display: false}
            ],
            throwOnError: false
          });
        }
        if (answered === questions.length) finish();
      });
      box.appendChild(btn);
    });
    el.appendChild(box);
  });

  const typeset = () => {
    if (typeof renderMathInElement !== "undefined") {
      renderMathInElement(el, {
        delimiters: [
          {left: '$$', right: '$$', display: true},
          {left: '$', right: '$', display: false}
        ],
        throwOnError: false
      });
    } else {
      setTimeout(typeset, 50);
    }
  };
  typeset();

  function finish() {
    const score = correct / questions.length;
    const p = Progress.recordQuiz(moduleId, score, moduleMeta?.xp, moduleMeta?.badge);
    const done = score >= 0.7;
    const summary = document.createElement("div");
    summary.className = "panel";
    summary.style.borderColor = done ? "var(--green)" : "var(--violet)";
    summary.innerHTML = done
      ? `<b>🎉 ${correct}/${questions.length} — Basecamp ${moduleId} complete!</b>
         You earned ${moduleMeta?.xp ?? 100} XP${moduleMeta?.badge ? ` and the
         <span class="badge-chip">🏅 ${moduleMeta.badge}</span> badge` : ""}.
         Total: ⚡ ${p.xp} XP.`
      : `<b>${correct}/${questions.length}.</b> Almost — revisit the notebook sections
         for the questions you missed, then retake the quiz (your best score counts).
         <button class="btn ghost" onclick="location.reload()">Retake quiz</button>`;
    el.appendChild(summary);
    if (done && window.confettiBurst) window.confettiBurst();
  }
}
