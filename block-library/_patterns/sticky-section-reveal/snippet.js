/**
 * sticky-section-reveal — Section pinning with state changes on scroll.
 * Apple AirPods Pro style: section stays fixed while scroll drives state transitions.
 *
 * Dependencies: GSAP + ScrollTrigger (load before this script)
 *   <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
 *   <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>
 *
 * Graceful degradation: if GSAP is not loaded, falls back to IntersectionObserver.
 */
(function () {
  'use strict';

  // ── GSAP path ────────────────────────────────────────────────────────
  if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);

    document.querySelectorAll('.ssr-section').forEach(function (section) {
      var states = section.querySelectorAll('.ssr-state');
      var sticky = section.querySelector('.ssr-sticky');
      var dots = section.querySelectorAll('.ssr-progress-dot');
      if (!states.length) return;

      var stateCount = states.length;
      section.style.setProperty('--ssr-states', stateCount);

      // Activate first state immediately
      states[0].classList.add('is-active');
      if (dots[0]) dots[0].classList.add('is-active');

      // Create a timeline that plays through all states over the scroll distance
      var tl = gsap.timeline({
        scrollTrigger: {
          trigger: section,
          start: 'top top',
          end: 'bottom bottom',
          scrub: false,        /* Not scrubbed — states snap */
          pin: sticky,
          onUpdate: function (self) {
            var progress = self.progress;
            var newIndex = Math.min(
              Math.floor(progress * stateCount),
              stateCount - 1
            );

            states.forEach(function (s, i) {
              s.classList.toggle('is-active', i === newIndex);
              s.classList.toggle('is-exiting', i < newIndex);
            });

            if (dots.length) {
              dots.forEach(function (d, i) {
                d.classList.toggle('is-active', i === newIndex);
              });
            }
          }
        }
      });
    });

  // ── Fallback: IntersectionObserver ───────────────────────────────────
  } else {
    var sections = document.querySelectorAll('.ssr-section');
    sections.forEach(function (section) {
      var states = section.querySelectorAll('.ssr-state');
      if (states[0]) states[0].classList.add('is-active');

      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            states.forEach(function (s) { s.classList.remove('is-active'); });
            entry.target.classList.add('is-active');
          }
        });
      }, { threshold: 0.5 });

      states.forEach(function (s) { observer.observe(s); });
    });
  }
})();
