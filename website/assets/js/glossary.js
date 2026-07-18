/* Quantum Ascent — inline glossary.
   Gives a beginner a safety net: the first time a key term appears in ordinary
   prose, it gets a dotted underline and a hover/tap definition — so nobody is
   left stranded on a word like "amplitude" two paragraphs after it was defined.

   Usage:  Glossary.enhance(document.getElementById("content"));
   It only ever wraps plain text nodes, never touches existing markup, and marks
   each term just once per page so the copy never turns into a sea of underlines. */
"use strict";

const Glossary = (() => {
  // Ancestors whose text we must never rewrite (structure, controls, math, code).
  const SKIP = new Set(["A", "BUTTON", "CODE", "PRE", "SCRIPT", "STYLE",
                        "H1", "H2", "H3", "LABEL", "TEXTAREA", "INPUT", "SELECT"]);
  const SKIP_CLASS = ["gterm", "katex", "badge-chip", "soon-chip"];

  function skip(node) {
    for (let el = node.parentNode; el && el !== document.body; el = el.parentNode) {
      if (el.nodeType !== 1) continue;
      if (SKIP.has(el.tagName)) return true;
      if (SKIP_CLASS.some(c => el.classList?.contains(c))) return true;
      if (el.hasAttribute?.("data-no-glossary")) return true;
    }
    return false;
  }

  async function enhance(root) {
    if (!root) return;
    let terms;
    try {
      terms = (await (await fetch("assets/data/glossary.json")).json()).terms;
    } catch { return; }               // glossary is a nicety — never block the page
    // Longest first so "Bloch sphere" wins over "Bloch", and allow a trailing "s".
    terms = terms.map(t => ({
      ...t,
      re: new RegExp("\\b(" + t.term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")s?\\b", "i")
    }));
    const used = new Set();

    // Snapshot text nodes first (we mutate the tree as we go).
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    for (let n = walker.nextNode(); n; n = walker.nextNode()) nodes.push(n);

    for (const node of nodes) {
      if (!node.nodeValue.trim() || skip(node)) continue;
      // Find the earliest match among terms not yet used on this page.
      let best = null;
      for (const t of terms) {
        if (used.has(t.term)) continue;
        const m = t.re.exec(node.nodeValue);
        if (m && (!best || m.index < best.index)) best = { t, index: m.index, text: m[0] };
      }
      if (!best) continue;
      used.add(best.t.term);

      const after = node.splitText(best.index);
      after.nodeValue = after.nodeValue.slice(best.text.length);

      const span = document.createElement("span");
      span.className = "gterm";
      span.tabIndex = 0;
      span.setAttribute("role", "button");
      span.setAttribute("aria-label", best.text + ": " + best.t.def);
      span.textContent = best.text;
      const tip = document.createElement("span");
      tip.className = "gtip";
      tip.setAttribute("role", "tooltip");
      tip.textContent = best.t.def;
      span.appendChild(tip);
      after.parentNode.insertBefore(span, after);
    }
  }

  return { enhance };
})();
