# Стандарт: форма с fetch — правила submit-обработчика

Применяется к любой форме лендинга с REST-отправкой (`fetch /wp-json/landing/v1/lead`).
Нарушение = дефект, блокирующий повторную отправку до перезагрузки страницы.

## Обязательные правила

### 1. btn.disabled сбрасывать в обоих ветках

```js
var btn = form.querySelector('button[type="submit"]');
btn.disabled = true;  // блокируем до ответа

fetch(url, { method: 'POST', body: body })
  .then(function (r) { return r.json(); })
  .then(function (data) {
    btn.textContent = originalText;  // вернуть оригинальный текст
    btn.disabled = false;             // ← ОБЯЗАТЕЛЬНО в .then
    form.reset();
    // закрыть модалку, показать thank-you и т.д.
  })
  .catch(function () {
    btn.disabled = false;             // ← ОБЯЗАТЕЛЬНО в .catch
    btn.textContent = originalText;
    // показать ошибку пользователю
  });
```

**Почему:** `btn.disabled = true` выставляется перед fetch. Если его не сбросить в `.then` — повторная отправка формы невозможна до перезагрузки страницы. `form.reset()` не затрагивает `disabled`.

### 2. Сохранять оригинальный текст кнопки до отправки

```js
var originalText = btn.textContent;
btn.disabled = true;
btn.textContent = 'Sending...';  // опционально
```

После успеха показать thank-you текст, но при следующем открытии модалки — восстановить оригинал. Либо сбрасывать текст в функции `openModal()`.

### 3. При переиспользуемой модалке — сбрасывать состояние при открытии

Если одна модалка открывается для разных карточек (как `#tdModal` на брендовых страницах):

```js
function openModal(model) {
  // Сбросить состояние формы
  form.reset();
  btn.disabled = false;
  btn.textContent = originalText;
  // ...открыть модалку
}
```

**Почему:** пользователь закрыл модалку после успешной отправки и открыл снова для другой модели — должен видеть чистую форму с активной кнопкой.

## Чеклист при code review

- [ ] `btn.disabled = false` есть в `.then`
- [ ] `btn.disabled = false` есть в `.catch`
- [ ] `btn.textContent` восстанавливается в обоих ветках (или в `openModal`)
- [ ] `form.reset()` вызывается после успеха
- [ ] При переиспользуемой модалке — `openModal()` сбрасывает `disabled` и `textContent`

## Известные нарушения (исправить по задаче 032)

- `hibridcars-uae/08_КОД/wp-theme/assets/js/collage.js` — форма главной страницы
- `hibridcars-uae/08_КОД/wp-theme/assets/js/td-form.js` — формы брендовых страниц
