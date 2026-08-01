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

/* The Toolbox is a native <details>, so it already opens by click and by
   keyboard and announces its own expanded state. The two things the element
   does NOT do are the two things people expect of a menu: close when you click
   away, and close on Escape. Without them an open panel just sits there
   covering the page, which reads as a bug. */
(function () {
  var group = document.querySelector('.nav-group');
  if (!group) return;

  document.addEventListener('click', function (e) {
    if (group.open && !group.contains(e.target)) group.open = false;
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' || !group.open) return;
    group.open = false;
    var summary = group.querySelector('summary');
    if (summary) summary.focus();   // don't strand the keyboard user
  });

  // Following a link inside the panel navigates away; on same-page anchors it
  // would otherwise stay open behind the new content.
  group.addEventListener('click', function (e) {
    if (e.target.closest('.nav-drop a')) group.open = false;
  });
})();
