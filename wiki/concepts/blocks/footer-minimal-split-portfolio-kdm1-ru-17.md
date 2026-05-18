---
type: block
name: footer-minimal-split-portfolio-kdm1-ru-17
sources: ["block-library/footer/footer-minimal-split-portfolio-kdm1-ru-17/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a, 07b"
uses: ["block-composition", "ux-composer", "block-composer"]
tags: ["footer", "minimal", "split", "ru-market", "services", "education", "b2b-saas"]
---

# Footer Minimal Split — тёмная полоса реквизитов

## Что делает

Блок нижнего колонтитула в виде тёмной горизонтальной полосы: делит содержимое на левую и правую части (split-паттерн) и компактно размещает реквизиты компании, контактные данные и служебные ссылки. Анимаций нет — строгий, быстрый футер.

## Когда вызывать / в каком этапе

Используется на этапах **07a (wireframe)** и **07b (compose)**. Агент `ux-composer` выбирает блок из библиотеки при построении wireframe, если прототип предполагает минималистичный подвал. `block-composer` подставляет токены и тексты при сборке `composed.html`.

Подходит для ниш: **услуги** (services), **образование** (education), **B2B SaaS**. Оптимален когда нужен деловой, сдержанный финал страницы без излишеств.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — как правило, название компании или короткий дескриптор
- Токены дизайна из `tokens.json` (цвета, типографика)
- Тексты из `prototype.yaml` (реквизиты, телефон, email, ссылки)

**Выход:**
- HTML-фрагмент футера, встроенный в `composed.html`
- Визуальных плейсхолдеров нет — блок полностью текстовый

## Связанные концепты

- [[ux-composer]] — выбирает блок при генерации wireframe из block-library
- [[block-composer]] — рендерит composed.html, подставляет токены и прототипный текст в слоты
- [[block-composition]] — скилл, описывающий правила сборки блоков в composed.html
- [[block-library-management]] — скилл управления библиотекой; определяет как импортируются и версионируются блоки
- [[07b-composed]] — этап, на котором блок окончательно вставляется в страницу

## Источник

- `block-library/footer/footer-minimal-split-portfolio-kdm1-ru-17/meta.yaml`
- Импортирован: 2026-05-16, метод: `codex-block-generation`
- Оригинал: `https://portfolio.kdm1.ru/upload/iblock/b31/...`