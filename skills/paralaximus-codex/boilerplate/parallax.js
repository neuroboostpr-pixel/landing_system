/* Parallax hero — drive --scroll-x/y, --move-x/y (mouse), --float-x/y (idle).
   Activate by adding [data-parallax-hero] to the .lp-hero element. */
(function () {
  'use strict';

  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return; // user prefers no motion — leave CSS variables at 0
  }

  function init(hero) {
    if (!hero || hero._lpParallaxInit) return;
    hero._lpParallaxInit = true;

    let scrollX = 0, scrollY = 0;
    let moveX = 0, moveY = 0;        // mouse offset from center, range [-1, 1]
    let scrollRotate = 0;
    let scaleAdd = 0;
    let raf = 0;
    let phase = 0;

    function onScroll() {
      const rect = hero.getBoundingClientRect();
      const vh = window.innerHeight || 1;
      // Hero center distance from viewport center (normalized roughly to pixels).
      const center = rect.top + rect.height / 2;
      scrollY = (center - vh / 2) * -0.6;
      scrollX = scrollY * 0.4;
      scrollRotate = scrollY * 1.2;
      scaleAdd = Math.abs(scrollY);
      schedule();
    }

    function onMouse(e) {
      const r = hero.getBoundingClientRect();
      const cx = r.left + r.width / 2;
      const cy = r.top + r.height / 2;
      // signed pixel offset from center
      moveX = (e.clientX - cx);
      moveY = (e.clientY - cy);
      schedule();
    }

    function onLeave() {
      moveX *= 0.5;
      moveY *= 0.5;
      schedule();
    }

    function loop() {
      phase += 0.012;
      const fx = Math.sin(phase) * 1.0;
      const fy = Math.cos(phase * 0.85) * 1.0;
      hero.style.setProperty('--scroll-x', scrollX.toFixed(2));
      hero.style.setProperty('--scroll-y', scrollY.toFixed(2));
      hero.style.setProperty('--move-x', moveX.toFixed(2));
      hero.style.setProperty('--move-y', moveY.toFixed(2));
      hero.style.setProperty('--scroll-rotate', scrollRotate.toFixed(2));
      hero.style.setProperty('--scale-add', scaleAdd.toFixed(2));
      hero.style.setProperty('--float-x', fx.toFixed(3));
      hero.style.setProperty('--float-y', fy.toFixed(3));
      raf = requestAnimationFrame(loop);
    }

    function schedule() {
      if (!raf) raf = requestAnimationFrame(loop);
    }

    // Listeners
    window.addEventListener('scroll', onScroll, { passive: true });
    hero.addEventListener('mousemove', onMouse);
    hero.addEventListener('mouseleave', onLeave);
    onScroll();
    schedule();
  }

  function ready() {
    document.querySelectorAll('[data-parallax-hero]').forEach(init);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ready);
  } else {
    ready();
  }
})();
