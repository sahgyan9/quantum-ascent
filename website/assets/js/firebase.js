/* Quantum Ascent — optional Google sign-in and cloud progress sync.
   ================================================================

   THIS FILE IS A PROGRESSIVE ENHANCEMENT AND MUST STAY ONE.

   The course's core promise is that it works with no account, no server and no
   network. That promise is not negotiable: every page still functions if this
   script fails to load, if Firebase is unreachable, or if the learner never
   signs in. localStorage remains the source of truth at all times; the cloud
   is a *mirror*, never the master.

   What signing in actually buys the learner:
     - their climb survives a cleared cache, a new laptop, or a phone
     - an educator can be handed a real completion record instead of a
       screenshot (see docs/educator_guide.md)

   What it costs them, stated plainly in the UI before they click:
     - their name, email and progress leave the browser and live in Firestore

   Security: the Firebase web config below is PUBLIC BY DESIGN. A Firebase
   "apiKey" is a project identifier, not a credential — it grants nothing on
   its own. Access is controlled entirely by firestore.rules (a signed-in user
   can read and write exactly one document: their own) plus the authorized-
   domains list in the Auth console. Committing it is the documented, intended
   practice, and there is no secret in this repository.
*/
"use strict";

(function () {

  var CFG = {
    apiKey: "AIzaSyCoil1gfca5NCzCbpK921wmG7qk3sOmtSc",
    authDomain: "quantum-ascent-77617.firebaseapp.com",
    projectId: "quantum-ascent-77617",
    storageBucket: "quantum-ascent-77617.firebasestorage.app",
    messagingSenderId: "1072138409983",
    appId: "1:1072138409983:web:96dff56dfac6ec20c479ca"
  };

  var SDK = "https://www.gstatic.com/firebasejs/10.12.2/";
  var LEDGER_KEY = "q2q_ledger_v1";
  var ASSESS_KEY = "q2q_assessment_v1";

  var state = { user: null, db: null, auth: null, doc: null, ready: false, busy: false };

  /* ------------------------------------------------------------ helpers */
  /* progress.js declares `const Progress = ...` at the top level of a classic
     script, which creates a LEXICAL binding — it is reachable as a bare
     identifier but is NOT a property of window. Testing `window.Progress`
     therefore reports "missing" even when it is right there, which would have
     silently disabled every sync path in this file. */
  function hasProgress() { return typeof Progress !== "undefined" && Progress && typeof Progress.get === "function"; }

  function readKey(k) {
    try { return JSON.parse(localStorage.getItem(k)) || null; } catch (e) { return null; }
  }
  function writeKey(k, v) {
    if (v) localStorage.setItem(k, JSON.stringify(v));
  }

  /* Merge two ledgers by task id, keeping the earliest first-attempt verdict
     (that is the honest measure of intuition) and the higher attempt count. */
  function mergeLedger(a, b) {
    var out = {}, i, e;
    var all = ((a && a.entries) || []).concat((b && b.entries) || []);
    for (i = 0; i < all.length; i++) {
      e = all[i];
      var prev = out[e.taskId];
      if (!prev) { out[e.taskId] = Object.assign({}, e); continue; }
      prev.attempts = Math.max(prev.attempts || 0, e.attempts || 0);
      prev.correct = prev.correct || e.correct;
      // firstCorrect: whichever record was written first wins
      if (new Date(e.at) < new Date(prev.at)) {
        prev.at = e.at;
        prev.firstCorrect = e.firstCorrect;
        prev.chose = e.chose;
      }
    }
    return { entries: Object.keys(out).map(function (k) { return out[k]; }) };
  }

  /* Assessment: never overwrite an existing pre-test with a later one. The
     baseline is the whole point — silently replacing it would destroy the
     only evidence the course produces. */
  function mergeAssessment(a, b) {
    a = a || {}; b = b || {};
    var out = {};
    ["pre", "post"].forEach(function (k) {
      if (a[k] && b[k]) out[k] = new Date(a[k].at) <= new Date(b[k].at) ? a[k] : b[k];
      else out[k] = a[k] || b[k];
    });
    if (!out.pre) delete out.pre;
    if (!out.post) delete out.post;
    return out;
  }

  /* ------------------------------------------------------------- the UI */
  /* Injected at runtime rather than pasted into every page's <nav>, so that a
     page which never loads this script is not left with a dead button. */
  function mountButton() {
    var menu = document.getElementById("nav-menu");
    if (!menu || document.getElementById("gsi-btn")) return;
    var b = document.createElement("button");
    b.id = "gsi-btn";
    b.type = "button";
    b.className = "gsi-btn";
    b.addEventListener("click", onClick);
    menu.insertBefore(b, document.getElementById("xp-pill"));
    paint();
  }

  function paint() {
    var b = document.getElementById("gsi-btn");
    if (!b) return;
    if (state.busy) {
      b.textContent = "…";
      b.disabled = true;
      b.setAttribute("aria-label", "Working");
      return;
    }
    b.disabled = false;
    if (state.user) {
      var name = (state.user.displayName || state.user.email || "you").split(" ")[0];
      b.innerHTML = '<span class="gsi-dot" aria-hidden="true"></span>Synced · ' + esc(name);
      b.title = "Signed in as " + (state.user.email || "") + " — your climb is backed up. Click to sign out.";
      b.setAttribute("aria-label", "Signed in and syncing. Activate to sign out.");
    } else {
      b.textContent = "Sign in to save";
      b.title = "Optional: sign in with Google to back up your climb across devices. Everything works without it.";
      b.setAttribute("aria-label", "Sign in with Google to back up your progress. Optional.");
    }
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function toast(msg, bad) {
    var t = document.createElement("div");
    t.className = "gsi-toast" + (bad ? " bad" : "");
    t.setAttribute("role", "status");
    t.setAttribute("aria-live", "polite");
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function () { t.classList.add("out"); }, 4200);
    setTimeout(function () { t.remove(); }, 5000);
  }

  /* Consent before the popup, not after. The learner is about to move data out
     of their own browser, and they should be told that in plain words first —
     the rest of this site promises the opposite. */
  function confirmSignIn() {
    return window.confirm(
      "Sign in with Google to back up your climb?\n\n" +
      "What gets stored: your progress, XP and badges, your prediction ledger, " +
      "and your assessment scores — plus your name and email so you can be " +
      "identified across devices.\n\n" +
      "Where: this course's own Firebase project. Only you can read your record.\n\n" +
      "You do NOT need this. The whole course works signed out, offline, with " +
      "everything kept in this browser only."
    );
  }

  function onClick() {
    if (state.busy) return;
    if (state.user) {
      if (window.confirm("Sign out?\n\nYour progress stays in this browser and stays in the cloud — nothing is deleted."))
        state.signOut();
      return;
    }
    if (!confirmSignIn()) return;
    state.signIn();
  }

  /* ---------------------------------------------------------- the sync */
  function boot() {
    /* Dynamic import keeps the whole SDK off the critical path: a page paints
       and is fully usable before Firebase is even fetched, and a blocked CDN
       degrades to the offline-first site rather than a broken one. */
    Promise.all([
      import(SDK + "firebase-app.js"),
      import(SDK + "firebase-auth.js"),
      import(SDK + "firebase-firestore.js")
    ]).then(function (mods) {
      var appMod = mods[0], authMod = mods[1], fsMod = mods[2];
      var app = appMod.initializeApp(CFG);
      var auth = authMod.getAuth(app);
      var db = fsMod.getFirestore(app);
      state.auth = auth;
      state.db = db;

      state.signIn = function () {
        state.busy = true; paint();
        var provider = new authMod.GoogleAuthProvider();
        authMod.signInWithPopup(auth, provider).catch(function (e) {
          state.busy = false; paint();
          if (e && e.code === "auth/popup-closed-by-user") return;   // silent: they chose to
          if (e && e.code === "auth/popup-blocked") {
            toast("Your browser blocked the sign-in popup — allow popups for this site and try again.", true);
          } else if (e && e.code === "auth/unauthorized-domain") {
            toast("This domain is not authorised for sign-in yet.", true);
          } else {
            toast("Sign-in failed: " + ((e && e.message) || "unknown error"), true);
          }
        });
      };

      state.signOut = function () {
        authMod.signOut(auth).then(function () { toast("Signed out. Your climb is still saved in this browser."); });
      };

      authMod.onAuthStateChanged(auth, function (user) {
        state.user = user;
        state.busy = false;
        paint();
        if (user) syncOnLogin(fsMod, db, user);
      });

      state.ready = true;
      window.FirebaseSync = {
        /* Called by Progress.save() on every change. Fire-and-forget: a failed
           push must never block or break local progress. */
        push: function (progress) {
          if (!state.user || !state.db) return;
          pushAll(fsMod, db, state.user, progress);
        },
        isSignedIn: function () { return !!state.user; },
        user: function () { return state.user; }
      };
    }).catch(function (e) {
      /* No network, blocked CDN, or an ad blocker eating gstatic. This is a
         supported state, not an error state — say nothing, break nothing. */
      var b = document.getElementById("gsi-btn");
      if (b) b.remove();
      if (window.console) console.info("Quantum Ascent: cloud sync unavailable, running local-only.", e && e.message);
    });
  }

  var pushTimer = null;
  function pushAll(fsMod, db, user, progress) {
    /* Debounced: the quiz engine can fire several progress-changed events in a
       second, and each one is a billable write on a free-tier project. */
    clearTimeout(pushTimer);
    pushTimer = setTimeout(function () {
      var payload = {
        schema: 1,
        progress: progress || (hasProgress() ? Progress.get() : null),
        ledger: readKey(LEDGER_KEY),
        assessment: readKey(ASSESS_KEY),
        profile: {
          displayName: user.displayName || null,
          email: user.email || null,
          photoURL: user.photoURL || null
        },
        updatedAt: new Date().toISOString()
      };
      fsMod.setDoc(fsMod.doc(db, "users", user.uid), payload, { merge: true })
        .catch(function (e) {
          if (window.console) console.warn("Quantum Ascent: cloud save failed (local progress is safe).", e.message);
        });
    }, 800);
  }

  /* On sign-in: pull, merge (never clobber), write back, tell the learner what
     happened. Merging matters — someone who worked signed-out on a train and
     then signs in must not lose that work to an older cloud copy. */
  function syncOnLogin(fsMod, db, user) {
    state.busy = true; paint();
    fsMod.getDoc(fsMod.doc(db, "users", user.uid)).then(function (snap) {
      var cloud = snap.exists() ? snap.data() : null;
      var gained = false;

      if (cloud) {
        if (cloud.progress && hasProgress()) {
          var before = Progress.get().xp;
          Progress.merge(cloud.progress);
          if (Progress.get().xp > before) gained = true;
        }
        if (cloud.ledger) writeKey(LEDGER_KEY, mergeLedger(readKey(LEDGER_KEY), cloud.ledger));
        if (cloud.assessment) writeKey(ASSESS_KEY, mergeAssessment(readKey(ASSESS_KEY), cloud.assessment));
      }

      state.busy = false; paint();
      pushAll(fsMod, db, user, hasProgress() ? Progress.get() : null);
      toast(cloud
        ? (gained ? "Welcome back — your saved climb has been restored." : "Signed in. Your climb is now backed up.")
        : "Signed in. Your climb is now backed up to your account.");
      /* Pages that render from storage at load time need to know. */
      document.dispatchEvent(new CustomEvent("cloud-synced"));
    }).catch(function (e) {
      state.busy = false; paint();
      toast("Signed in, but the backup could not be read: " + e.message, true);
    });
  }

  /* ------------------------------------------------------------- styles */
  var css = document.createElement("style");
  css.textContent =
    ".gsi-btn{font:inherit;font-size:13px;font-weight:600;cursor:pointer;padding:5px 12px;" +
    "border:1px solid var(--line);border-radius:20px;background:var(--panel);color:var(--text);" +
    "display:inline-flex;align-items:center;gap:6px;white-space:nowrap;margin:0}" +
    ".gsi-btn:hover:not(:disabled){border-color:var(--accent);color:var(--accent-strong)}" +
    ".gsi-btn:disabled{opacity:.6;cursor:default}" +
    ".gsi-dot{width:7px;height:7px;border-radius:50%;background:var(--accent);flex:none}" +
    ".gsi-toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:9999;" +
    "max-width:min(92vw,460px);background:var(--panel);color:var(--text);border:1px solid var(--accent);" +
    "border-left:4px solid var(--accent);border-radius:10px;padding:11px 16px;font-size:14px;" +
    "box-shadow:0 6px 24px rgba(26,26,24,.16);transition:opacity .5s,transform .5s}" +
    ".gsi-toast.bad{border-color:var(--danger);border-left-color:var(--danger)}" +
    ".gsi-toast.out{opacity:0;transform:translateX(-50%) translateY(8px)}";
  document.head.appendChild(css);

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", function () { mountButton(); boot(); });
  else { mountButton(); boot(); }
})();
