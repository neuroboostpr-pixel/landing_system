/**
 * marquee-3d-perspective — Дублирует список для seamless loop + применяет скорость.
 * ~20 строк vanilla JS. Zero dependencies.
 *
 * Reads data-speed attribute (seconds) from .mq3d-list elements.
 * Duplicates the inner HTML once for seamless infinite scroll.
 *
 * prefers-reduced-motion: skips duplication (static list fallback).
 */
(function () {
  'use strict';

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  document.querySelectorAll('.mq3d-list').forEach(function (list) {
    // Apply speed from data attribute
    var speed = parseFloat(list.dataset.speed);
    if (speed && speed > 0) {
      list.style.setProperty('--mq3d-speed', speed + 's');
    }

    // Duplicate inner HTML once for seamless looping
    // CSS animation moves -50% which equals original content width
    var original = list.innerHTML;
    list.innerHTML = original + original;

    // Pause/resume on visibility (performance optimisation)
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          list.style.animationPlayState = entry.isIntersecting ? 'running' : 'paused';
        });
      }, { threshold: 0 });
      io.observe(list.parentElement || list);
    }
  });
})();
