/* Quantum Ascent — the Prediction Ledger.
   =======================================

   The course asks "predict before you run" about twenty times. Until now every
   one of those predictions evaporated: the learner guessed, saw the answer,
   and moved on with no record of whether their intuition was any good.

   The Ledger captures each prediction at the moment it is made, alongside the
   correct answer and the concept it tests. At the Summit it turns that history
   into a CALIBRATION REPORT — not a score, but a mirror:

       You made 12 predictions and got 9 right on the first try.
       Strongest: entanglement, phase & interference.
       Weakest: Qiskit endianness — 0 of 2 first tries.

   Why this is worth building:
     - It turns the course's best pedagogical instinct from a slogan into data.
     - It is a MEASURABLE LEARNING OUTCOME, which the brief asks for and which
       a self-reported "I feel I understand it" can never be.
     - Calibration training is standard in forecasting and medical education
       and almost unknown in quantum computing teaching.

   Storage is localStorage only — same as the rest of the site. No account, no
   server, nothing leaves the browser. The learner can export or wipe it.
*/
"use strict";

var Ledger = (function () {
  var KEY = "q2q_ledger_v1";

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || { entries: [] }; }
    catch (e) { return { entries: [] }; }
  }
  function save(d) {
    localStorage.setItem(KEY, JSON.stringify(d));
    document.dispatchEvent(new CustomEvent("ledger-changed", { detail: d }));
  }

  /* Record one prediction. `attempt` counts from 1, so we can distinguish a
     first-try hit (real intuition) from an eventual hit (useful, but different).
     Re-answering the same task updates that task's entry rather than stacking
     duplicates — otherwise a learner who fiddles looks worse than one who
     guessed once and left. */
  function record(taskId, opts) {
    var d = load();
    var e = null;
    for (var i = 0; i < d.entries.length; i++) if (d.entries[i].taskId === taskId) e = d.entries[i];
    if (!e) {
      e = { taskId: taskId, topic: opts.topic || "general", attempts: 0,
            firstCorrect: null, correct: false, at: new Date().toISOString() };
      d.entries.push(e);
    }
    e.attempts++;
    if (e.firstCorrect === null) e.firstCorrect = !!opts.correct;
    e.correct = e.correct || !!opts.correct;
    e.chose = opts.chose;
    save(d);
    return e;
  }

  function entries() { return load().entries.slice(); }

  function forTask(taskId) {
    var es = load().entries;
    for (var i = 0; i < es.length; i++) if (es[i].taskId === taskId) return es[i];
    return null;
  }

  /* The calibration report. Deliberately reports FIRST-TRY accuracy, because
     that is the honest measure of intuition; eventual accuracy is a measure of
     persistence, which we report separately and never punish. */
  function report() {
    var es = load().entries;
    var total = es.length;
    var first = 0, eventual = 0;
    var byTopic = {};
    for (var i = 0; i < es.length; i++) {
      var e = es[i];
      if (e.firstCorrect) first++;
      if (e.correct) eventual++;
      var t = byTopic[e.topic] || (byTopic[e.topic] = { topic: e.topic, n: 0, hit: 0 });
      t.n++;
      if (e.firstCorrect) t.hit++;
    }
    var topics = Object.keys(byTopic).map(function (k) { return byTopic[k]; });
    topics.sort(function (a, b) {
      var d = (b.hit / b.n) - (a.hit / a.n);
      return d !== 0 ? d : b.n - a.n;
    });
    var strong = topics.filter(function (t) { return t.hit === t.n; });
    var weak = topics.filter(function (t) { return t.hit < t.n; });
    return {
      total: total,
      firstTry: first,
      eventual: eventual,
      firstTryRate: total ? first / total : 0,
      topics: topics,
      strongest: strong.map(function (t) { return t.topic; }),
      weakest: weak.map(function (t) { return t.topic; }),
      /* An honest one-liner. No praise inflation: if the rate is low we say
         what that actually means, which is that the predictions were doing
         their job. */
      verdict: (function () {
        if (!total) return "No predictions logged yet — they start at Basecamp 1.";
        var r = total ? first / total : 0;
        if (r >= 0.85) return "Your first instincts were right most of the time. That is a real, checkable claim about your intuition — not a feeling.";
        if (r >= 0.6) return "Your instincts were right more often than not, and the misses clustered — which is exactly what a useful weak spot looks like.";
        return "More than a third of your first guesses were wrong, and that is the point: each one was a misconception caught in the open rather than carried to the Summit.";
      })()
    };
  }

  function reset() { localStorage.removeItem(KEY); save({ entries: [] }); }

  return { record: record, entries: entries, forTask: forTask, report: report, reset: reset };
})();

if (typeof module !== "undefined" && module.exports) module.exports = Ledger;
