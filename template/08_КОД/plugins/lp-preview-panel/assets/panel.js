(function () {
  'use strict';

  var config = window.LP_PREVIEW_PANEL || { axes: {}, defaults: {} };
  var STORAGE_PREFIX = 'lp-axis-';

  function readUrl(axisKey) {
    try {
      var url = new URL(window.location.href);
      var v = url.searchParams.get(axisKey);
      return v || null;
    } catch (e) { return null; }
  }

  function readLs(axisKey) {
    try { return localStorage.getItem(STORAGE_PREFIX + axisKey); } catch (e) { return null; }
  }

  function writeLs(axisKey, value) {
    try { localStorage.setItem(STORAGE_PREFIX + axisKey, value); } catch (e) {}
  }

  function isValid(axis, value) {
    return value && Object.prototype.hasOwnProperty.call(axis.options, value);
  }

  function resolveInitial(axisKey, axis) {
    var fromUrl = readUrl(axisKey);
    if (isValid(axis, fromUrl)) return fromUrl;
    var fromLs = readLs(axisKey);
    if (isValid(axis, fromLs)) return fromLs;
    var fromServer = config.defaults && config.defaults[axisKey];
    if (isValid(axis, fromServer)) return fromServer;
    return axis.default;
  }

  function applyClass(prefix, oldValue, newValue) {
    var body = document.body;
    if (oldValue) body.classList.remove(prefix + oldValue);
    body.classList.add(prefix + newValue);
  }

  function initAxis(axisKey, axis) {
    var current = resolveInitial(axisKey, axis);
    applyClass(axis.body_class_prefix, null, current);

    var select = document.querySelector('[data-lp-axis="' + axisKey + '"]');
    if (!select) return;
    select.value = current;
    select.addEventListener('change', function () {
      var next = select.value;
      if (!isValid(axis, next)) return;
      applyClass(axis.body_class_prefix, current, next);
      writeLs(axisKey, next);
      current = next;
    });
  }

  function init() {
    Object.keys(config.axes || {}).forEach(function (k) {
      initAxis(k, config.axes[k]);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
