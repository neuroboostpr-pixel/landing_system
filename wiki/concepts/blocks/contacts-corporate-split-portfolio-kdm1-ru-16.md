---
type: block
name: contacts-corporate-split-portfolio-kdm1-ru-16
sources: ["block-library/contacts/contacts-corporate-split-portfolio-kdm1-ru-16/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "wireframe-rendering"]
tags: ["contacts", "corporate", "split", "ru-market", "b2b", "services", "education"]
---

# Финальный контактный экран — корпоративный split-макет

## Что делает
Финальный экран лендинга для захвата лидов: крупный заголовок, форма выбора удобного времени и яркая CTA-кнопка. Макет разделён на две колонки (split-паттерн) в строгом корпоративном стиле.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при сборке секции контактов / финального призыва к действию. Агент [[ux-composer]] выбирает блок из библиотеки согласно `prototype.yaml`, если прототип предполагает форму записи или обратной связи. Подходит для ниш **услуги, онлайн-образование, b2b-saas** на русскоязычном рынке.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — описание секции contacts с заголовком и типом формы
- `tokens.json` — дизайн-токены проекта (цвета, шрифты) для подстановки
- Слот `heading` (обязательный, тип text) — крупный заголовок экрана

**Выход:**
- HTML-фрагмент блока, встроенный в `07a_WIREFRAME/wireframe.html` или `07b_COMPOSED/composed.html`
- Placeholder для формы выбора времени (заполняется на этапе 08 через [[integrations-engineer]] / Fluent Forms)
- Placeholder для CTA-кнопки с брендовым акцентным цветом из токенов

## Особенности
- **Анимация:** отсутствует (`has_animation: false`) — подходит для проектов без GSAP
- **Рынок:** адаптирован для RU-рынка (`ru_market: true`)
- **Паттерн:** split (двухколоночный) в `corporate` настроении — строгий, без лишних декораций
- **Источник:** импортирован из портфолио kdm1.ru методом `codex-block-generation` (2026-05-16)

## Связанные концепты
- [[ux-composer]] — выбирает этот блок из библиотеки при сборке wireframe
- [[block-composition]] — подставляет токены и тексты из prototype.yaml в этапе 07b
- [[wireframe-rendering]] — рендерит блок в интерактивный wireframe.html
- [[integrations-engineer]] — подключает реальную форму Fluent Forms вместо placeholder на этапе 08
- [[block-library-management]] — управляет каталогом, в котором хранится этот блок

## Источник
- `block-library/contacts/contacts-corporate-split-portfolio-kdm1-ru-16/meta.yaml`