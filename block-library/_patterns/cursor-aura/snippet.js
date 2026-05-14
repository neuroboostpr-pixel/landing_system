/**
 * cursor-aura — Light spot follows the cursor.
 * ~12 lines of vanilla JS. No dependencies.
 *
 * Usage:
 *   1. Add class "cursor-aura" to any container.
 *   2. Include this script (deferred, at end of body).
 *
 * Mobile: auto-disabled when pointer is coarse (touch screen).
 * prefers-reduced-motion: auto-disabled.
 */
(function () {
  'use strict';

  // Bail on touch devices and reduced-motion preference
  if (
    window.matchMedia('(hover: none) and (pointer: coarse)').matches ||
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  ) return;

  var elements = document.querySelectorAll('.cursor-aura');
  if (!elements.length) return;

  function onMove(e) {
    for (var i = 0; i < elements.length; i++) {
      var rect = elements[i].getBoundingClientRect();
      var x = e.clientX - rect.left;
      var y = e.clientY - rect.top;
      elements[i].style.setProperty('--aura-x', x + 'px');
      elements[i].style.setProperty('--aura-y', y + 'px');
    }
  }

  // Single mousemove listener on document — more efficient than per-element
  document.addEventListener('mousemove', onMove, { passive: true });
})();
