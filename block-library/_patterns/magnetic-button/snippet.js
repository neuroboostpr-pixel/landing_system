/**
 * magnetic-button — Button притягивается к курсору в радиусе hover.
 * ~20 lines of vanilla JS. Zero dependencies.
 *
 * HTML: <button class="mag-btn" data-mag-strength="0.4" data-mag-radius="80">
 *
 * data-mag-strength: 0.1 (subtle) → 0.8 (strong). Default: 0.4
 * data-mag-radius: pixel radius for magnetic zone. Default: 80
 *
 * Mobile: auto-disabled for touch devices.
 * prefers-reduced-motion: auto-disabled.
 */
(function () {
  'use strict';

  // Bail on touch/reduced-motion
  if (
    window.matchMedia('(hover: none) and (pointer: coarse)').matches ||
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  ) return;

  document.querySelectorAll('.mag-btn').forEach(function (btn) {
    var strength = parseFloat(btn.dataset.magStrength) || 0.4;
    var radius = parseFloat(btn.dataset.magRadius) || 80;

    btn.addEventListener('mousemove', function (e) {
      var rect = btn.getBoundingClientRect();
      var cx = rect.left + rect.width / 2;
      var cy = rect.top + rect.height / 2;
      var dx = e.clientX - cx;
      var dy = e.clientY - cy;
      var dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < radius + rect.width / 2) {
        var tx = dx * strength;
        var ty = dy * strength;
        btn.style.setProperty('--mag-tx', tx + 'px');
        btn.style.setProperty('--mag-ty', ty + 'px');
      }
    });

    btn.addEventListener('mouseleave', function () {
      btn.style.setProperty('--mag-tx', '0');
      btn.style.setProperty('--mag-ty', '0');
    });
  });
})();
