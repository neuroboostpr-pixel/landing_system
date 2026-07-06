# Стандарт: единая система модальных форм

Применяется ко всем лендингам системы. Нарушение = несовместимые атрибуты,
дублирующийся код, невозможность переиспользовать скрипт между проектами.

## Проблема (зафиксировано на hibridcars-uae)

Три независимые системы в одном проекте:

| Файл | Форма | Открытие | Закрытие | Скрипт |
|---|---|---|---|---|
| Главная | `#customForm` | `data-open-cform` | `data-close-form` | `collage.js` |
| Брендовые страницы | `#tdModalForm` | `data-open-td` | `data-close-td` | `td-form.js` |
| Xiaomi md-modal | — | `data-model-details` | `data-close-md` | ❌ нет |

Итог: три набора атрибутов, три скрипта (один вообще не написан), баги в каждом.

## Единый стандарт

### Атрибуты

```html
<!-- Кнопка открытия — data-open-modal="<id модалки>" -->
<button type="button" data-open-modal="lead-form" data-modal-model="Li L7">
  Get an offer
</button>

<!-- Модалка -->
<div id="lead-form" class="lp-modal" role="dialog" aria-modal="true" hidden>
  <div class="lp-modal__backdrop" data-close-modal></div>
  <div class="lp-modal__dialog">
    <button type="button" class="lp-modal__close" data-close-modal aria-label="Close">×</button>
    <!-- контент -->
  </div>
</div>
```

**Правила:**
- Открытие: всегда `data-open-modal="<id>"`
- Закрытие: всегда `data-close-modal` (без значения — закрывает текущую открытую)
- Передача контекста (модель, источник): `data-modal-*` атрибуты на кнопке открытия
- CSS-классы модалки: `lp-modal`, `lp-modal__backdrop`, `lp-modal__dialog`, `lp-modal__close`

### Единый скрипт `modal.js`

Один файл на все проекты — живёт в `template/08_КОД/wp-theme/assets/js/modal.js`.

Отвечает за:
1. Открытие/закрытие по `data-open-modal` / `data-close-modal`
2. Передачу контекста из `data-modal-*` в форму (модель → select, source_block и т.д.)
3. Сброс формы и кнопки при каждом открытии (правило из form-submit-rules.md §3)
4. Закрытие по Escape и клику на backdrop
5. Блокировку скролла body при открытой модалке

### Единый скрипт `lead-form.js`

Один файл на все проекты — живёт в `template/08_КОД/wp-theme/assets/js/lead-form.js`.

Отвечает за:
1. Submit формы с `data-lead-form` атрибутом
2. Валидацию UAE телефона
3. `fetch POST /wp-json/landing/v1/lead` с полями name/phone/message/source_block/pd_consent/utm_*
4. Сброс `btn.disabled` в `.then` и `.catch` (правило из form-submit-rules.md)
5. Закрытие модалки через `data-close-modal` после успеха

```html
<form data-lead-form data-source-label="Request a test drive" novalidate>
  ...
</form>
```

## Миграция существующих проектов

### hibridcars-uae (задача 033)

Заменить:
- `data-open-cform` → `data-open-modal="lead-form"`
- `data-open-td` → `data-open-modal="lead-form"`
- `data-model-details` → `data-open-modal="md-<slug>"`
- `data-close-form` / `data-close-td` / `data-close-md` → `data-close-modal`
- `collage.js` (форм-часть) + `td-form.js` → единый `lead-form.js`
- Написать недостающий обработчик для `md-modal` на Xiaomi

### Новые проекты

Использовать только `modal.js` + `lead-form.js`. `collage.js` и `td-form.js`
не копировать как шаблон — они legacy hibridcars-uae.

## Связанные стандарты

- [form-submit-rules.md](form-submit-rules.md) — правила submit-обработчика (btn.disabled)
