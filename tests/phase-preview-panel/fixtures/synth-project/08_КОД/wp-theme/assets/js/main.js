(function () {
  function unrelated() { return 1; }

  function initThemeSwitcher() {
    var STORAGE_KEY = 'nu-palette';
    var DEFAULT = 'i';
    var VALID = ['h', 'i', 'j', 'k'];
    function applyTheme(p) {
      var body = document.body;
      VALID.forEach(function (v) { body.classList.remove('theme-' + v); });
      body.classList.add('theme-' + p);
    }
    applyTheme(DEFAULT);
  }

  document.addEventListener('DOMContentLoaded', function () {
    unrelated();
    initThemeSwitcher();
  });
})();
