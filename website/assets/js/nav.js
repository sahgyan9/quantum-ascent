// Floating pill navbar: add a stronger shadow once the page is scrolled.
(function () {
  var nav = document.getElementById('nav');
  if (!nav) return;
  var onScroll = function () {
    nav.classList.toggle('scrolled', window.scrollY > 8);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
})();
