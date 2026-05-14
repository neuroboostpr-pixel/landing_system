/* headroom-nav — прятать nav при скролле вниз, показывать при скролле вверх
 * Source: github.com/nexu-io/open-design @ 75498838 | design-templates/open-design-landing/example.html:2572+
 * License: Apache-2.0
 *
 * Добавляет/убирает класс `lp-nav--hidden` на элемент навигации.
 * Работает с .lp-nav-shell (floating-pill-nav) и с обычным <nav>.
 *
 * Настройка: изменить NAV_SELECTOR и HIDE_CLASS.
 */
(function () {
  var NAV_SELECTOR = '#lp-nav';          // CSS-selector навигации
  var HIDE_CLASS   = 'lp-nav--hidden';  // класс из floating-pill-nav/snippet.css
  var THRESHOLD    = 80;                  // px — игнорировать первые 80px скролла
  var DELTA        = 5;                   // px — минимальный скролл для реакции

  var nav     = document.querySelector(NAV_SELECTOR);
  if (!nav) return;

  var lastY   = 0;
  var ticking = false;

  function update() {
    var curr = window.scrollY;
    var diff = curr - lastY;

    if (Math.abs(diff) > DELTA) {
      if (curr > THRESHOLD && diff > 0) {
        // Скролл вниз — прятать
        nav.classList.add(HIDE_CLASS);
      } else {
        // Скролл вверх или вверху страницы — показывать
        nav.classList.remove(HIDE_CLASS);
      }
      lastY = curr;
    }

    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) {
      requestAnimationFrame(update);
      ticking = true;
    }
  }, { passive: true });
})();
