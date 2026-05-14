/**
 * text-reveal-mask — IntersectionObserver triggers mask reveal.
 * Adds class "is-revealed" to [data-animate="reveal"] elements
 * when they enter the viewport.
 *
 * ~20 lines of vanilla JS. No dependencies.
 */
(function () {
  'use strict';

  // Respect reduced motion — CSS already handles fallback, but we skip observer
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('[data-animate="reveal"]').forEach(function (el) {
      el.classList.add('is-revealed');
    });
    return;
  }

  var targets = document.querySelectorAll('[data-animate="reveal"]');
  if (!targets.length) return;

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed');
          // Unobserve after reveal — animation plays once
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }  /* Trigger when 15% of element is visible */
  );

  targets.forEach(function (el) { observer.observe(el); });
})();
