---
type: block
name: ru-quiz-04-lead-form
sources: ["block-library/quiz/ru-quiz-04-lead-form/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "wireframe-rendering", "prototype-import"]
tags: ["quiz", "lead-form", "ru-market", "b2c", "services", "local", "152-фз", "telegram", "messenger"]
---

# Квиз — финальная форма захвата (ru-quiz-04-lead-form)

## Что делает
Финальный экран квиза: собирает телефон, предлагает выбрать удобный мессенджер (Telegram / Max / Звонок) и отправляет заявку. Соответствует российскому законодательству — только разрешённые в РФ каналы, обязательное согласие на обработку персональных данных по 152-ФЗ.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** — подключается агентом [[ux-composer]] при сборке интерактивного wireframe.html из prototype.yaml. Выбирается, когда в прототипе есть квизовый сценарий и нужен последний шаг с захватом контакта. Актуален для ниш: услуги, B2C, локальный бизнес.

## Что на вход / на выход

**Вход (слоты):**
| Слот | Тип | Обязательный | Макс. символов |
|---|---|---|---|
| `headline` | text | да | 80 |
| `subhead` | text | нет | 140 |
| `name-input` | text | нет | 50 |
| `phone-input` | text | да | 20 |
| `channel-choice` | text | да | — |
| `submit-cta` | cta | да | — (дефолт: «Получить расчёт») |
| `agreement-text` | text | да | 200 |

**Выход:**
Готовый HTML-блок финального экрана квиза с полем телефона, переключателем мессенджера и согласием на ПД. Интегрируется в `wireframe.html` → `composed.html` на этапах 07a–07b.

**Ключевые ограничения по conversion:**
- Чекбокс 152-ФЗ **не проставляется по умолчанию** (not pre-checked).
- Messenger Max обязателен в списке выбора.
- Только разрешённые в РФ мессенджеры — WhatsApp/Viber не используются.

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при рендере wireframe.html
- [[block-composition]] — этап 07b, инжектирует design-tokens и подставляет тексты слотов в готовый блок
- [[wireframe-rendering]] — скилл, управляющий сборкой wireframe из prototype.yaml + block-library
- [[prototype-import]] — нормализует прототип в prototype.yaml, откуда ux-composer берёт описание квизового сценария

## Источник
- `block-library/quiz/ru-quiz-04-lead-form/meta.yaml`