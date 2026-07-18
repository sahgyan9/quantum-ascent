/* Quantum Ascent — progress store.
   localStorage always; transparently syncs to Firestore when js/firebase.js
   is loaded AND the user signs in (progressive enhancement — the site is
   fully functional without Firebase). */
"use strict";

/* completion-code core — MUST stay identical to q2q/progress.py; the test
   tests/test_progress.py extracts this exact block and cross-checks it against
   Python so a learner's real notebook code is never silently rejected. Pure
   functions only: no DOM, no storage. */
const QA_SALT = "quantum-ascent";
function fnv1a(s) {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h >>> 0;
}
function codeFor(moduleId) {
  const mid = String(moduleId).padStart(2, "0");
  const hx = fnv1a("QA::" + mid + "::" + QA_SALT).toString(16).toUpperCase().padStart(8, "0");
  return "QA-" + mid + "-" + hx.slice(0, 4) + "-" + hx.slice(4);
}
/* end completion-code core */

const Progress = (() => {
  const KEY = "q2q_progress_v1";
  const NOTEBOOK_XP = 40;          // banked once when a notebook code is redeemed

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
    return (p.modules[id] ||= { opened: false, quizScore: null, completed: false, notebookDone: false });
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

    /* Redeem a completion code printed by the notebook (q2q.progress). Marks
       the basecamp's notebook step done and banks climber XP once. */
    redeemCode(raw) {
      const code = String(raw || "").trim().toUpperCase().replace(/\s+/g, "");
      const m = code.match(/^QA-(\d{2})-[0-9A-F]{4}-[0-9A-F]{4}$/);
      if (!m) return { ok: false, reason: "format" };
      const id = m[1];
      if (code !== codeFor(id)) return { ok: false, reason: "invalid" };
      const p = load(); const mm = mod(p, id);
      const already = !!mm.notebookDone;
      if (!already) { mm.notebookDone = true; p.xp += NOTEBOOK_XP; save(p); }
      return { ok: true, moduleId: id, already, xp: p.xp, gained: already ? 0 : NOTEBOOK_XP };
    },

    /* merge cloud data in, never losing local work (max per field) */
    merge(cloud) {
      const p = load();
      for (const [id, cm] of Object.entries(cloud.modules || {})) {
        const m = mod(p, id);
        m.opened ||= cm.opened;
        m.completed ||= cm.completed;
        m.notebookDone ||= cm.notebookDone;
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

  /* The pill is a live progress tracker AND a shortcut to the map — make that
     discoverable: it should look and behave like the control it is. */
  if (pill && pill.tagName !== "A") {
    pill.style.cursor = "pointer";
    pill.setAttribute("role", "link");
    pill.setAttribute("tabindex", "0");
    pill.setAttribute("aria-label", "Your climb: XP and basecamps completed. Opens the Ascent map.");
    const goMap = () => { location.href = "ascent.html"; };
    pill.addEventListener("click", goMap);
    pill.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); goMap(); } });
  }

  const renderPill = () => {
    if (!pill) return;
    const p = Progress.get();
    const done = Object.values(p.modules).filter(m => m.completed).length;
    pill.textContent = `⚡ ${p.xp} XP · ${done}/6`;
    pill.title = p.badges.length
      ? "Badges earned: " + p.badges.join(", ") + " — click to see your Ascent map"
      : "Your climb tracker: finish a basecamp quiz to earn XP and badges. Click to open the Ascent map.";
  };
  renderPill();
  document.addEventListener("progress-changed", renderPill);

  /* First-visit orientation: a one-time bubble so a newcomer knows what the
     mysterious "⚡ 0 XP · 0/6" pill is, instead of having to guess. */
  const COACH_KEY = "q2q_seen_pill_coach";
  if (pill && !localStorage.getItem(COACH_KEY) && Progress.get().xp === 0) {
    const coach = document.createElement("div");
    coach.className = "pill-coach";
    coach.innerHTML = `<b>⚡ This is your climb tracker.</b> Finish a basecamp quiz to earn XP
      and badges — reach the summit and collect all four. <button type="button" aria-label="Got it">Got it ✓</button>`;
    document.body.appendChild(coach);
    const place = () => {
      const r = pill.getBoundingClientRect();
      coach.style.top = (r.bottom + 10) + "px";
      coach.style.right = Math.max(12, window.innerWidth - r.right) + "px";
    };
    place();
    window.addEventListener("resize", place);
    const dismiss = () => { coach.remove(); localStorage.setItem(COACH_KEY, "1"); };
    coach.querySelector("button").addEventListener("click", dismiss);
    setTimeout(() => { if (document.body.contains(coach)) dismiss(); }, 12000);
  }

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
