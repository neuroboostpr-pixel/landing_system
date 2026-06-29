/* gen-html — движок эффектов + мудов для composed.html.
 * Копируется в <script> макета. Зависит от классов base.css (.reveal/.on-load) и
 * токенов мода (--reveal-stagger, --parallax-*). Поддерживает 1..∞ мудов через [data-mood].
 *
 * Разметка-контракт:
 *   .on-load        — контент ПЕРВОГО экрана (above the fold): появляется при загрузке, НЕ по скроллу.
 *   .reveal         — секции НИЖЕ сгиба: появляются по скроллу (stagger-каскад).
 *   [data-px="--parallax-bg|decor|figure"] — слой с параллаксом (множитель из токена мода).
 *   #moodBar[data-preview=on] + #moodSelect — панель-переключатель мудов (превью; убрать на проде).
 */
(function(){
  var rm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function cssMs(name, def){
    var v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    var m = parseFloat(v); return isNaN(m) ? def : (v.indexOf('ms') > -1 ? m : m * 1000);
  }
  function px(name, def){
    var v = parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name));
    return isNaN(v) ? def : v;
  }

  // --- REVEAL по скроллу (только секции ниже сгиба), со stagger ---
  function applyReveal(){
    var rev = document.querySelectorAll('.reveal:not(.in)');
    if (rm || !('IntersectionObserver' in window)) { rev.forEach(function(e){ e.classList.add('in'); }); return; }
    var stagger = cssMs('--reveal-stagger', 80);
    var io = new IntersectionObserver(function(es){
      var i = 0;
      es.forEach(function(e){ if (e.isIntersecting){ var el = e.target; setTimeout(function(){ el.classList.add('in'); }, (i++) * stagger); io.unobserve(el); } });
    }, { threshold: .12, rootMargin: '0px 0px -8% 0px' });
    rev.forEach(function(e){ io.observe(e); });
  }
  applyReveal();

  // --- ON-LOAD первого экрана: класс .on-load анимируется CSS при загрузке (forwards); JS нужен лишь для re-trigger при смене мода ---
  function replayOnLoad(){
    if (rm) return;
    document.querySelectorAll('.on-load').forEach(function(e){ e.style.animation = 'none'; void e.offsetWidth; e.style.animation = ''; });
  }

  // --- PARALLAX по скроллу: transform слоёв с data-px ---
  var pxNodes = [].slice.call(document.querySelectorAll('[data-px]'));
  var raf = 0;
  function parallax(){
    raf = 0;
    var sc = window.pageYOffset || 0;
    pxNodes.forEach(function(n){
      var k = px(n.getAttribute('data-px') || '--parallax-decor', .1);
      n.style.transform = 'translate3d(0,' + (sc * k * -1).toFixed(1) + 'px,0)';
    });
  }
  if (!rm && pxNodes.length){
    window.addEventListener('scroll', function(){ if (!raf) raf = requestAnimationFrame(parallax); }, { passive: true });
    parallax();
  }

  // --- ПАНЕЛЬ МУДОВ: переключение [data-mood] (1..∞ мудов), localStorage, re-trigger эффектов ---
  var bar = document.getElementById('moodBar');
  if (bar && bar.getAttribute('data-preview') === 'on'){
    document.documentElement.setAttribute('data-preview-bar', '');
    var sel = document.getElementById('moodSelect');
    var saved = localStorage.getItem('lp_mood');
    if (saved && sel){ document.documentElement.setAttribute('data-mood', saved); sel.value = saved; }
    if (sel) sel.addEventListener('change', function(){
      document.documentElement.setAttribute('data-mood', sel.value);
      localStorage.setItem('lp_mood', sel.value);
      applyReveal();   // reveal для вновь показанной композиции (ниже сгиба)
      replayOnLoad();  // первый экран нового мода переиграет on-load
    });
  }
})();
