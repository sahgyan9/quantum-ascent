/* Quantum Ascent — progress store.
   localStorage always; transparently syncs to Firestore when js/firebase.js
   is loaded AND the user signs in (progressive enhancement — the site is
   fully functional without Firebase). */
"use strict";

const Progress = (() => {
  const KEY = "q2q_progress_v1";

  const empty = () => ({ modules: {}, xp: 0, badges: [], updatedAt: null });

  function load() {
    try { return { ...empty(), ...JSON.parse(localStorage.getItem(KEY)) }; }
    catch { return empty(); }
  }

  function save(p) {
    p.updatedAt = new Date().toISOString();
    localStorage.setItem(KEY, JSON.stringify(p));
    document.dispatchEvent(new CustomEvent("progress-changed", { detail: p }));
    if (window.FirebaseSync) window.FirebaseSync.push(p); // no-op if absent
  }

  function mod(p, id) {
    return (p.modules[id] ||= { opened: false, quizScore: null, completed: false });
  }

  return {
    get: load,

    markOpened(id) {
      const p = load(); mod(p, id).opened = true; save(p);
    },

    recordQuiz(id, score, xpValue, badge) {
      const p = load(); const m = mod(p, id);
      const first = m.quizScore === null;
      m.quizScore = Math.max(m.quizScore ?? 0, score);
      if (score >= 0.7 && !m.completed) {
        m.completed = true;
        p.xp += xpValue || 100;
        if (badge && !p.badges.includes(badge)) p.badges.push(badge);
      } else if (first && score > 0) {
        p.xp += Math.round((xpValue || 100) * 0.2 * score); // effort XP
      }
      save(p);
      return p;
    },

    markComplete(id, xpValue, badge) {   // manual "mark complete" checkbox
      const p = load(); const m = mod(p, id);
      if (!m.completed) {
        m.completed = true; p.xp += xpValue || 100;
        if (badge && !p.badges.includes(badge)) p.badges.push(badge);
      }
      save(p); return p;
    },

    /* merge cloud data in, never losing local work (max per field) */
    merge(cloud) {
      const p = load();
      for (const [id, cm] of Object.entries(cloud.modules || {})) {
        const m = mod(p, id);
        m.opened ||= cm.opened;
        m.completed ||= cm.completed;
        m.quizScore = Math.max(m.quizScore ?? -1, cm.quizScore ?? -1);
        if (m.quizScore < 0) m.quizScore = null;
      }
      p.xp = Math.max(p.xp, cloud.xp || 0);
      p.badges = [...new Set([...p.badges, ...(cloud.badges || [])])];
      save(p); return p;
    },

    reset() {
      if (confirm("Reset ALL progress, XP and badges? This cannot be undone.")) {
        localStorage.removeItem(KEY);
        document.dispatchEvent(new CustomEvent("progress-changed", { detail: empty() }));
      }
    },

    export() {
      const blob = new Blob([JSON.stringify(load(), null, 2)], { type: "application/json" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "quantum-ascent-progress.json";
      a.click();
    },
  };
})();

/* -------- shared nav helpers (XP pill + theme toggle) -------- */
document.addEventListener("DOMContentLoaded", () => {
  const pill = document.getElementById("xp-pill");
  const renderPill = () => {
    if (!pill) return;
    const p = Progress.get();
    const done = Object.values(p.modules).filter(m => m.completed).length;
    pill.textContent = `⚡ ${p.xp} XP · ${done}/6`;
    pill.title = p.badges.length ? "Badges: " + p.badges.join(", ") : "Complete basecamps to earn badges";
  };
  renderPill();
  document.addEventListener("progress-changed", renderPill);

  const toggle = document.getElementById("theme-toggle");
  const applyTheme = t => {
    document.documentElement.dataset.theme = t;
    localStorage.setItem("q2q_theme", t);
    if (toggle) toggle.textContent = t === "light" ? "🌙 Dark" : "☀️ Light";
  };
  applyTheme(localStorage.getItem("q2q_theme") || "light");
  if (toggle) toggle.addEventListener("click", () =>
    applyTheme(document.documentElement.dataset.theme === "light" ? "dark" : "light"));
});
