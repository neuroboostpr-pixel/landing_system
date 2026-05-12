(function () {
  'use strict';
  var STORAGE_PREFIX = 'lp-axis-';

  function fillFromLocalStorage() {
    var selects = document.querySelectorAll('[data-lp-admin-axis]');
    selects.forEach(function (sel) {
      var key = sel.getAttribute('data-lp-admin-axis');
      var v = null;
      try { v = localStorage.getItem(STORAGE_PREFIX + key); } catch (e) {}
      if (!v) return;
      var match = Array.prototype.find.call(sel.options, function (o) { return o.value === v; });
      if (match) sel.value = v;
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.querySelector('[data-lp-fill-from-ls]');
    if (btn) btn.addEventListener('click', fillFromLocalStorage);
  });
})();
