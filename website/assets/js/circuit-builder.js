/* Quantum Ascent — Circuit Builder: a click-to-build quantum circuit editor.
   ==========================================================================

   Mounted in two places, deliberately sharing one implementation so the free
   play surface and the graded surface can never teach different things:

     - widgets/circuit-lab/index.html  — free play, in the widget gallery
     - lab.html                        — the graded browser track

   It renders real physics via QSim (assets/js/qsim.js), which is pinned
   against Qiskit to 1e-12 by tests/test_qsim.py.

   DESIGN COMMITMENTS (Norman + docs/pedagogical_style_guide.md)
   - AFFORDANCE  palette buttons look like the gate boxes they place.
   - FEEDBACK    every action writes plain English into a status line that is
                 also an aria-live region: sighted and screen-reader users get
                 the same sentence at the same moment.
   - CONSTRAINTS a two-qubit gate cannot land on one wire; Undo always exists;
                 the qubit count is clamped to what a human can actually read.
   - MAPPING     the grid runs left-to-right in time, matching the Qiskit code
                 printed beside it.
   - HOUSE RULE  the probability bars ARE the Born probabilities, exactly.

   Usage:
       const cb = CircuitBuilder.mount(document.getElementById("host"), {
         n: 2, allowed: ["H","X","CX"], showCode: true,
         objective: { label: "Cut value", fn: st => ({ value, text }) },
         onChange: (circuit, state) => { ... }
       });
*/
"use strict";

var CircuitBuilder = (function () {

  var ONE = ["H", "X", "Y", "Z", "S", "T"];
  var ROT = ["RX", "RY", "RZ"];
  var TWO = ["CX", "CZ", "RZZ"];

  var GATE_HELP = {
    H: "Hadamard — turns a definite 0 into an even 50/50 undetermined state",
    X: "X — the quantum NOT: swaps |0⟩ and |1⟩",
    Y: "Y — a half-turn about the Y axis (flips and adds a phase)",
    Z: "Z — flips the sign of |1⟩. Changes no probabilities on its own",
    S: "S — a quarter phase turn on |1⟩",
    T: "T — an eighth phase turn on |1⟩",
    RX: "RX(θ) — rotate by θ about the X axis",
    RY: "RY(θ) — rotate by θ about Y. P(1) = sin²(θ/2): the Basecamp 1 workhorse",
    RZ: "RZ(θ) — rotate by θ about Z. Changes phase, never probabilities",
    CX: "CNOT — flip the target wire only where the control wire is 1. Makes entanglement",
    CZ: "CZ — flip the sign only when both wires are 1",
    RZZ: "RZZ(θ) — the QAOA cost layer: phases pairs by whether their bits agree"
  };

  var LABEL = { CX: "CNOT", CZ: "CZ", RZZ: "RZZ(θ)", RX: "RX(θ)", RY: "RY(θ)", RZ: "RZ(θ)" };

  var seq = 0;
  var rad = function (d) { return d * Math.PI / 180; };
  var isRot = function (g) { return ROT.indexOf(g) >= 0 || g === "RZZ"; };
  var isTwo = function (g) { return TWO.indexOf(g) >= 0; };

  /* Beginners lose Basecamp 1 to the degrees/radians gap more often than to
     physics, so every angle is shown BOTH ways, always, and π-fractions are
     named rather than printed as 1.5708. */
  var RADS = [[0, "0"], [30, "π/6"], [45, "π/4"], [60, "π/3"], [90, "π/2"], [120, "2π/3"],
              [135, "3π/4"], [150, "5π/6"], [180, "π"], [210, "7π/6"], [225, "5π/4"],
              [240, "4π/3"], [270, "3π/2"], [300, "5π/3"], [315, "7π/4"], [330, "11π/6"],
              [360, "2π"]];
  function radLabel(deg) {
    for (var i = 0; i < RADS.length; i++) if (RADS[i][0] === deg) return RADS[i][1];
    return rad(deg).toFixed(3);
  }
  var PYRAD = { 0: "0", 30: "np.pi/6", 45: "np.pi/4", 60: "np.pi/3", 90: "np.pi/2",
                120: "2*np.pi/3", 135: "3*np.pi/4", 150: "5*np.pi/6", 180: "np.pi",
                270: "3*np.pi/2", 360: "2*np.pi" };
  function pyAngle(r) {
    var deg = Math.round(r * 180 / Math.PI);
    if (PYRAD[deg] != null && Math.abs(rad(deg) - r) < 1e-9) return PYRAD[deg];
    return r.toFixed(4);
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function mount(host, opts) {
    opts = opts || {};
    var uid = "cb" + (++seq);
    var S = {
      n: opts.n || 2,
      minN: opts.minN || 1,
      maxN: opts.maxN || 5,
      lockQubits: !!opts.lockQubits,
      allowed: opts.allowed || ONE.concat(ROT, TWO),
      ops: (opts.ops || []).slice(),
      sel: null, angle: opts.angle == null ? 90 : opts.angle,
      pending: null, editing: -1,
      counts: {}, shots: 0
    };
    var showCode = opts.showCode !== false;
    var showObs = opts.showObs !== false;
    var showMeasure = opts.showMeasure !== false;
    var objective = opts.objective || null;

    var pal1 = S.allowed.filter(function (g) { return ONE.indexOf(g) >= 0; });
    var palR = S.allowed.filter(function (g) { return ROT.indexOf(g) >= 0; });
    var pal2 = S.allowed.filter(function (g) { return TWO.indexOf(g) >= 0; });

    /* ---------------------------------------------------------- skeleton */
    host.classList.add("cb-root");
    host.innerHTML =
      '<div class="cols">' +
        '<div class="col-left">' +
          '<div class="panel">' +
            (S.lockQubits ? "" :
              '<div class="palette-group" style="margin-bottom:6px">' +
                '<span class="palette-label">Qubits</span>' +
                '<button class="gbtn" data-act="nminus" aria-label="Remove a qubit">−</button>' +
                '<span class="chip" data-el="nq">2</span>' +
                '<button class="gbtn" data-act="nplus" aria-label="Add a qubit">+</button>' +
                '<span style="flex:1"></span>' +
                '<button class="gbtn" data-act="undo">↶ Undo</button>' +
                '<button class="gbtn" data-act="reset">Reset</button>' +
              '</div>') +
            (S.lockQubits ?
              '<div class="palette-group" style="margin-bottom:6px;justify-content:flex-end">' +
                '<span style="flex:1"></span>' +
                '<button class="gbtn" data-act="undo">↶ Undo</button>' +
                '<button class="gbtn" data-act="reset">Reset</button>' +
              '</div>' : "") +
            (pal1.length ? '<span class="palette-label">1-qubit gates</span><div class="palette" data-el="pal1"></div>' : "") +
            (palR.length ? '<span class="palette-label">Rotations — set the angle below</span><div class="palette" data-el="palr"></div>' : "") +
            (pal2.length ? '<span class="palette-label">2-qubit gates — click the control wire, then the target</span><div class="palette" data-el="pal2"></div>' : "") +
            (palR.length ?
              '<div class="angle-row" data-el="anglerow" hidden>' +
                '<label for="' + uid + '-angle" style="margin:0;white-space:nowrap">Angle θ</label>' +
                '<input type="range" id="' + uid + '-angle" data-el="angle" min="0" max="360" step="1" value="' + S.angle + '">' +
                '<span class="chip" data-el="angdeg">90°</span>' +
                '<span class="chip" data-el="angrad">π/2 rad</span>' +
              '</div>' +
              '<p class="muted" style="font-size:12px;margin-top:6px">Qiskit takes angles in ' +
              '<b>radians</b>, so both are always shown here. 180° = π.</p>' : "") +
          '</div>' +
          '<div data-el="board" class="cb-board" style="margin-top:10px"></div>' +
          '<div data-el="status" role="status" aria-live="polite" class="cb-status"></div>' +
        '</div>' +
        '<div class="col-right">' +
          '<div class="panel">' +
            '<div style="display:flex;justify-content:space-between;align-items:baseline">' +
              '<b style="font-size:13px">Exact state — before you look</b>' +
              '<span class="chip" data-el="nstates"></span></div>' +
            '<div class="muted" style="font-size:12px;margin:2px 0 8px">Bar length <i>is</i> the probability: P = (amplitude)².</div>' +
            '<div class="bars" data-el="probs"></div>' +
            '<div style="margin-top:8px;font-size:12px" class="muted">|ψ⟩ = <span data-el="ket" style="color:var(--text)"></span></div>' +
            (objective ? '<div class="cb-objective" data-el="objective"></div>' : "") +
          '</div>' +
          (showMeasure ?
          '<div class="panel">' +
            '<div style="display:flex;justify-content:space-between;align-items:baseline">' +
              '<b style="font-size:13px">Measured — after you look</b>' +
              '<span class="chip"><span data-el="shots">0</span> shots</span></div>' +
            '<div class="bars" data-el="counts" style="margin-top:8px"></div>' +
            '<div data-el="flash" style="min-height:20px;font-weight:700;font-size:13px;margin-top:6px"></div>' +
            '<button data-act="m1">Measure ×1</button>' +
            '<button data-act="m100" class="violet">Measure ×100</button>' +
            '<button data-act="m1000" class="violet">×1000</button>' +
            '<button data-act="cleartally" class="secondary">Clear tally</button>' +
          '</div>' : "") +
          ((showCode || showObs) ?
          '<div class="panel">' +
            '<div class="tabs" role="tablist">' +
              (showCode ? '<button role="tab" data-tab="code" aria-selected="true">Qiskit code</button>' : "") +
              (showObs ? '<button role="tab" data-tab="obs" aria-selected="' + (showCode ? "false" : "true") + '">Observables</button>' : "") +
            '</div>' +
            (showCode ? '<div data-pane="code" role="tabpanel"><pre class="code" data-el="code"></pre>' +
              '<p class="muted" style="font-size:11.5px;margin-top:6px">Genuine, runnable Qiskit — the ' +
              'exact circuit the notebook track builds. Copy it into Colab if you want to run it for real.</p></div>' : "") +
            (showObs ? '<div data-pane="obs" role="tabpanel"' + (showCode ? " hidden" : "") + '><table class="mirror" data-el="obs"></table>' +
              '<p class="muted" style="font-size:11.5px;margin-top:6px">⟨Z⟩ = P(0) − P(1) for that qubit: ' +
              '+1 means certainly 0, −1 means certainly 1, and 0 is a perfect coin.</p></div>' : "") +
          '</div>' : "") +
        '</div>' +
      '</div>' +
      '<div class="sr-only" data-el="a11y" aria-live="polite"></div>';

    var q = function (name) { return host.querySelector('[data-el="' + name + '"]'); };

    /* ---------------------------------------------------------- palette */
    function mkBtn(g, cls) {
      var b = el("button", "gbtn" + (cls ? " " + cls : ""), LABEL[g] || g);
      b.dataset.g = g;
      b.title = GATE_HELP[g] || g;
      b.setAttribute("aria-pressed", "false");
      b.addEventListener("click", function () { selectGate(g); });
      return b;
    }
    if (pal1.length) q("pal1").replaceChildren.apply(q("pal1"), pal1.map(function (g) { return mkBtn(g); }));
    if (palR.length) q("palr").replaceChildren.apply(q("palr"), palR.map(function (g) { return mkBtn(g, "rot"); }));
    if (pal2.length) q("pal2").replaceChildren.apply(q("pal2"), pal2.map(function (g) { return mkBtn(g, "two"); }));

    function selectGate(g) {
      S.sel = g; S.pending = null; S.editing = -1;
      var btns = host.querySelectorAll(".gbtn[data-g]");
      for (var i = 0; i < btns.length; i++)
        btns[i].setAttribute("aria-pressed", String(btns[i].dataset.g === g));
      if (q("anglerow")) q("anglerow").hidden = !isRot(g);
      say(isRot(g) ? g + " selected. Set the angle, then click a wire to place it."
        : isTwo(g) ? g + " selected. Click the CONTROL wire first, then the target wire."
        : g + " selected. Click a wire to place it.");
      render();
    }

    /* -------------------------------------------------------- placement */
    function place(qi) {
      var g = S.sel;
      if (!g) { say("Pick a gate from the palette first, then click a wire."); return; }
      if (isTwo(g)) {
        if (S.pending === null) {
          S.pending = { g: g, q: qi };
          say(g + ": control on q" + qi + ". Now click a DIFFERENT wire for the target.");
          render(); return;
        }
        if (S.pending.q === qi) { say("A " + g + " needs two different wires — pick another one."); return; }
        var op2 = { g: g, q: S.pending.q, t: qi };
        if (g === "RZZ") op2.p = rad(S.angle);
        S.ops.push(op2); S.pending = null;
        say(g + " placed: q" + op2.q + " → q" + op2.t + ".");
      } else {
        var op = { g: g, q: qi };
        if (isRot(g)) op.p = rad(S.angle);
        S.ops.push(op);
        say(g + (isRot(g) ? "(" + S.angle + "°)" : "") + " placed on q" + qi + ".");
      }
      clearTally(); render();
    }

    function removeOp(i) {
      var op = S.ops[i];
      S.ops.splice(i, 1); S.editing = -1;
      say("Removed " + op.g + " from q" + op.q + ".");
      clearTally(); render();
    }

    /* Clicking a placed rotation re-opens its angle — "what if it were 60°?"
       is the very next thing a learner wants, so it must not require a delete
       and a re-place. */
    function editOp(i) {
      var op = S.ops[i];
      if (!isRot(op.g) || S.editing === i) { removeOp(i); return; }
      S.editing = i;
      S.angle = Math.round(op.p * 180 / Math.PI);
      if (q("angle")) { q("angle").value = S.angle; q("anglerow").hidden = false; }
      syncAngle();
      say("Editing " + op.g + " on q" + op.q + ". Drag the angle, or click it again to delete.");
      render();
    }

    /* ---------------------------------------------------------- layout */
    /* Pack each op into the earliest column where all its wires are free —
       cosmetic, but it turns a diagonal staircase into a readable circuit. */
    function layout() {
      var cols = [], colOf = [];
      for (var i = 0; i < S.ops.length; i++) {
        var op = S.ops[i];
        var lo = op.t == null ? op.q : Math.min(op.q, op.t);
        var hi = op.t == null ? op.q : Math.max(op.q, op.t);
        var c = 0;
        for (; c < cols.length; c++) {
          var free = true;
          for (var w = lo; w <= hi; w++) if (cols[c][w]) { free = false; break; }
          if (free) break;
        }
        if (c === cols.length) cols.push({});
        for (var w2 = lo; w2 <= hi; w2++) cols[c][w2] = true;
        colOf.push(c);
      }
      return { colOf: colOf, ncols: cols.length };
    }

    function render() {
      var L = layout(), showCols = L.ncols + 1;
      var t = el("table", "grid");
      t.setAttribute("role", "grid");
      t.setAttribute("aria-label", "Quantum circuit. Rows are qubits, columns are time steps.");
      for (var qi = S.n - 1; qi >= 0; qi--) {
        var tr = el("tr");
        tr.appendChild(el("td", "qlabel", "q" + qi + " |0⟩"));
        for (var c = 0; c < showCols; c++) {
          var td = el("td"), cell = el("div", "cell");
          cell.appendChild(el("div", "wire"));
          var idx = findOp(L.colOf, c, qi);
          if (idx >= 0) renderOp(cell, S.ops[idx], idx, qi);
          else {
            var btn = el("button", "slot", "+");
            btn.setAttribute("aria-label", "Place " + (S.sel || "a gate") + " on qubit " + qi + ", step " + (c + 1));
            (function (qq) { btn.addEventListener("click", function () { place(qq); }); })(qi);
            cell.appendChild(btn);
          }
          if (spans(L.colOf, c, qi)) {
            var v = el("div", "vlink"); v.style.top = "0"; v.style.bottom = "0"; cell.appendChild(v);
          }
          td.appendChild(cell); tr.appendChild(td);
        }
        t.appendChild(tr);
      }
      q("board").replaceChildren(t);
      if (S.pending) {
        var p = el("div", "muted", S.pending.g + " control is on q" + S.pending.q + " — now click the target wire.");
        p.style.cssText = "font-size:12px;margin-top:6px";
        q("board").appendChild(p);
      }
      draw();
    }

    function findOp(colOf, c, qi) {
      for (var i = 0; i < S.ops.length; i++)
        if (colOf[i] === c && (S.ops[i].q === qi || S.ops[i].t === qi)) return i;
      return -1;
    }
    function spans(colOf, c, qi) {
      for (var i = 0; i < S.ops.length; i++) {
        var op = S.ops[i];
        if (colOf[i] === c && op.t != null &&
            Math.min(op.q, op.t) < qi && qi < Math.max(op.q, op.t)) return true;
      }
      return false;
    }

    function renderOp(cell, op, idx, qi) {
      var two = op.t != null, isControl = two && op.q === qi;
      function halfLink(down) {
        var h = el("div", "vlink");
        if (down) { h.style.top = "50%"; h.style.bottom = "0"; }
        else { h.style.top = "0"; h.style.bottom = "50%"; }
        return h;
      }
      function hitbox(label) {
        var b = el("button", "slot");
        b.setAttribute("aria-label", label);
        b.addEventListener("click", function () { removeOp(idx); });
        return b;
      }
      if (two && op.g !== "RZZ") {
        var otherAbove = (isControl ? op.t : op.q) > qi;
        cell.appendChild(el("div", (op.g === "CX" && !isControl) ? "targ" : "ctrl-dot"));
        cell.appendChild(halfLink(!otherAbove));
        cell.appendChild(hitbox(op.g + (isControl ? " control" : " target") + " on qubit " + qi + ". Activate to remove."));
        return;
      }
      var deg = op.p != null ? Math.round(op.p * 180 / Math.PI) : null;
      var box = el("div", "gate" + (isRot(op.g) ? " rot" : "") + (S.editing === idx ? " sel" : ""),
        isRot(op.g) ? op.g + " " + deg + "°" : op.g);
      if (two) {                                   // RZZ: draw on both wires
        cell.appendChild(halfLink((isControl ? op.t : op.q) < qi ? false : true));
      }
      box.setAttribute("role", "button");
      box.setAttribute("tabindex", "0");
      box.setAttribute("aria-label", isRot(op.g)
        ? op.g + " of " + deg + " degrees on qubit " + qi + ". Activate to edit, again to remove."
        : op.g + " on qubit " + qi + ". Activate to remove.");
      box.addEventListener("click", function () { editOp(idx); });
      box.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); editOp(idx); }
        if (e.key === "Delete" || e.key === "Backspace") { e.preventDefault(); removeOp(idx); }
      });
      cell.appendChild(box);
    }

    /* -------------------------------------------------------- readouts */
    function state() {
      try { return QSim.run(S.n, S.ops); }
      catch (e) { say("⚠ " + e.message); return QSim.zeroState(S.n); }
    }

    function draw() {
      var st = state(), p = QSim.probabilities(st), N = 1 << S.n;
      if (q("nq")) q("nq").textContent = S.n;
      q("nstates").textContent = N + " outcome" + (N === 1 ? "" : "s");
      q("ket").textContent = QSim.ketString(st);

      fillBars(q("probs"), N, function (i) {
        return { key: "|" + QSim.label(i, S.n) + "⟩", frac: p[i], num: (100 * p[i]).toFixed(1) + "%" };
      }, "p");

      if (showMeasure) {
        fillBars(q("counts"), N, function (i) {
          var lab = QSim.label(i, S.n), c = S.counts[lab] || 0;
          return { key: lab, frac: S.shots ? c / S.shots : 0, num: String(c) };
        }, "s");
        q("shots").textContent = S.shots;
      }

      if (showObs) {
        var rows = ["<tr><th>Qubit</th><th>P(1)</th><th>⟨Z⟩</th></tr>"];
        for (var qq = 0; qq < S.n; qq++) {
          var m = QSim.marginal1(st, qq);
          rows.push("<tr><td>q" + qq + "</td><td>" + (100 * m).toFixed(1) + "%</td><td>" +
            (1 - 2 * m).toFixed(3) + "</td></tr>");
        }
        if (S.n >= 2) {
          var zz = QSim.expectation(st, new Array(S.n - 1).join("I") + "ZZ");
          rows.push("<tr><td>q1·q0</td><td>—</td><td>⟨ZZ⟩ = " + zz.toFixed(3) + "</td></tr>");
        }
        q("obs").innerHTML = rows.join("");
      }

      if (showCode) q("code").textContent = qiskitCode();

      var objText = "";
      if (objective) {
        var o = objective.fn(st, S) || {};
        objText = (objective.label || "Objective") + ": " + (o.text != null ? o.text : o.value);
        q("objective").innerHTML = '<span class="cb-obj-label">' + (objective.label || "Objective") +
          '</span><span class="cb-obj-value">' + (o.text != null ? o.text : o.value) + "</span>";
      }

      var parts = [];
      for (var i2 = 0; i2 < N; i2++) parts.push(QSim.label(i2, S.n) + ": " + (100 * p[i2]).toFixed(1) + "%");
      q("a11y").textContent =
        "Circuit with " + S.ops.length + " gate" + (S.ops.length === 1 ? "" : "s") +
        " on " + S.n + " qubits. Exact probabilities — " + parts.join(", ") + ". " +
        (objText ? objText + ". " : "") +
        (S.shots ? "Measured " + S.shots + " shots: " + Object.keys(S.counts).sort().map(function (k) {
          return k + " " + S.counts[k];
        }).join(", ") + "." : "No shots taken yet.");

      if (opts.onChange) opts.onChange({ n: S.n, ops: S.ops.slice() }, st);
    }

    function fillBars(container, N, get, cls) {
      container.replaceChildren();
      for (var i = 0; i < N; i++) {
        var d = get(i);
        container.appendChild(el("span", "lab-k", d.key));
        var tr = el("div", "track"), f = el("div", "fill " + cls);
        f.style.width = (100 * d.frac) + "%";
        tr.appendChild(f); container.appendChild(tr);
        container.appendChild(el("span", "num", d.num));
      }
    }

    /* The code mirror: a browser-track learner reads real Qiskit for free, so
       moving to the notebook later is recognition, not a fresh start. */
    function qiskitCode() {
      var body = [];
      for (var i = 0; i < S.ops.length; i++) {
        var op = S.ops[i], a = op.p != null ? pyAngle(op.p) : null;
        if (op.g === "CX") body.push("qc.cx(" + op.q + ", " + op.t + ")");
        else if (op.g === "CZ") body.push("qc.cz(" + op.q + ", " + op.t + ")");
        else if (op.g === "RZZ") body.push("qc.rzz(" + a + ", " + op.q + ", " + op.t + ")");
        else if (isRot(op.g)) body.push("qc." + op.g.toLowerCase() + "(" + a + ", " + op.q + ")");
        else body.push("qc." + op.g.toLowerCase() + "(" + op.q + ")");
      }
      if (!body.length) body.push("# (empty — place a gate to see it appear here)");
      var head = ["from qiskit import QuantumCircuit", "from qiskit_aer import AerSimulator"];
      var needsNp = body.join("").indexOf("np.") >= 0;
      if (needsNp) head.push("import numpy as np");
      return head.concat([""], ["qc = QuantumCircuit(" + S.n + ")"], body,
        ["qc.measure_all()", "", "sim = AerSimulator()",
         "counts = sim.run(qc, shots=" + (S.shots || 1000) + ").result().get_counts()",
         "print(counts)"]).join("\n");
    }

    /* -------------------------------------------------------- measuring */
    function measure(k) {
      var c = QSim.sample(state(), k);
      for (var key in c) S.counts[key] = (S.counts[key] || 0) + c[key];
      S.shots += k;
      var f = q("flash");
      f.textContent = k === 1 ? "→ this shot collapsed to " + Object.keys(c)[0]
                              : "→ " + k + " shots sampled";
      f.style.color = "var(--amber-strong)";
      say(k === 1 ? "Measured once: got " + Object.keys(c)[0] + "."
                  : "Measured " + k + " times. Total " + S.shots + " shots.");
      draw();
    }
    function clearTally() {
      S.counts = {}; S.shots = 0;
      if (q("flash")) q("flash").textContent = "";
    }
    function say(msg) { q("status").textContent = msg; }
    function syncAngle() {
      if (!q("angdeg")) return;
      q("angdeg").textContent = S.angle + "°";
      q("angrad").textContent = radLabel(S.angle) + " rad";
    }

    /* ---------------------------------------------------------- wiring */
    host.addEventListener("click", function (e) {
      var b = e.target.closest("[data-act]");
      if (!b || !host.contains(b)) return;
      var a = b.dataset.act;
      if (a === "nplus") {
        if (S.n >= S.maxN) { say(S.maxN + " qubits is this Lab's ceiling — " + (1 << S.maxN) + " amplitudes is already a lot to read."); return; }
        S.n++; say("Added q" + (S.n - 1) + "."); clearTally(); render();
      } else if (a === "nminus") {
        if (S.n <= S.minN) { say("You need at least " + S.minN + " qubit" + (S.minN > 1 ? "s" : "") + "."); return; }
        var gone = S.n - 1;
        S.ops = S.ops.filter(function (o) { return o.q !== gone && o.t !== gone; });
        S.n--; say("Removed q" + gone + " (and any gate on it)."); clearTally(); render();
      } else if (a === "undo") {
        if (!S.ops.length) { say("Nothing to undo — the circuit is already empty."); return; }
        var op = S.ops.pop(); say("Undid " + op.g + " on q" + op.q + "."); clearTally(); render();
      } else if (a === "reset") {
        S.ops = (opts.ops || []).slice(); S.pending = null; S.editing = -1; clearTally();
        say("Circuit cleared. Every qubit is back at |0⟩."); render();
      } else if (a === "m1") measure(1);
      else if (a === "m100") measure(100);
      else if (a === "m1000") measure(1000);
      else if (a === "cleartally") { clearTally(); say("Tally cleared."); draw(); }
    });

    if (q("angle")) q("angle").addEventListener("input", function (e) {
      S.angle = +e.target.value;
      syncAngle();
      if (S.editing >= 0 && S.ops[S.editing]) { S.ops[S.editing].p = rad(S.angle); clearTally(); }
      render();
    });

    var tabs = host.querySelectorAll("[data-tab]");
    for (var ti = 0; ti < tabs.length; ti++) {
      tabs[ti].addEventListener("click", function (e) {
        var want = e.target.dataset.tab;
        for (var j = 0; j < tabs.length; j++) {
          var name = tabs[j].dataset.tab;
          tabs[j].setAttribute("aria-selected", String(name === want));
          var pane = host.querySelector('[data-pane="' + name + '"]');
          if (pane) pane.hidden = name !== want;
        }
      });
    }

    syncAngle();
    selectGate(S.allowed[0]);

    return {
      host: host,
      getCircuit: function () { return { n: S.n, ops: S.ops.slice() }; },
      getState: state,
      setCircuit: function (n, ops) { S.n = n; S.ops = (ops || []).slice(); clearTally(); render(); },
      say: say,
      refresh: render
    };
  }

  return { mount: mount, radLabel: radLabel, pyAngle: pyAngle };
})();

if (typeof module !== "undefined" && module.exports) module.exports = CircuitBuilder;
