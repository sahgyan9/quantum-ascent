/* Tiny dependency-free confetti burst (celebration feedback). */
"use strict";
window.confettiBurst = function () {
  const cv = document.createElement("canvas");
  Object.assign(cv.style, { position: "fixed", inset: 0, pointerEvents: "none", zIndex: 999 });
  cv.width = innerWidth; cv.height = innerHeight;
  document.body.appendChild(cv);
  const ctx = cv.getContext("2d");
  const colors = ["#22d3ee", "#8b5cf6", "#34d399", "#fbbf24", "#f87171"];
  const parts = Array.from({ length: 140 }, () => ({
    x: cv.width / 2, y: cv.height / 3,
    vx: (Math.random() - 0.5) * 14, vy: Math.random() * -11 - 3,
    s: Math.random() * 7 + 3, r: Math.random() * Math.PI,
    c: colors[Math.random() * colors.length | 0],
  }));
  let frames = 0;
  (function tick() {
    ctx.clearRect(0, 0, cv.width, cv.height);
    for (const p of parts) {
      p.x += p.vx; p.y += p.vy; p.vy += 0.35; p.r += 0.1;
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r);
      ctx.fillStyle = p.c; ctx.fillRect(-p.s / 2, -p.s / 2, p.s, p.s);
      ctx.restore();
    }
    if (++frames < 110) requestAnimationFrame(tick); else cv.remove();
  })();
};
