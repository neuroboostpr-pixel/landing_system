/* scroll-reveal — vanilla IntersectionObserver
 * Устанавливает data-revealed="true" когда элемент входит в viewport (top 85%).
 * Работает только если пользователь не выбрал prefers-reduced-motion.
 * Source: github.com/nexu-io/open-design @ 75498838 (Apache-2.0)
 */
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.dataset.revealed = 'true';
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08, rootMargin: '0px 0px -10% 0px' }
  );

  document.querySelectorAll('[data-reveal]').forEach(function (el) {
    observer.observe(el);
  });
})();
