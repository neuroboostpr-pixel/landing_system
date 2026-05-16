---
type: block
name: social-proof-minimal-stacked-antidiler-karpov-ru-4
sources: ["block-library/social-proof/social-proof-minimal-stacked-antidiler-karpov-ru-4/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition"]
tags: ["social-proof", "minimal", "stacked", "premium-auto", "luxury", "ru-market", "no-animation"]
---

# Social Proof — Серия тёмных кейсов (minimal stacked)

## Что делает
Отображает серию тёмных карточек с отзывами клиентов без крупных фотографий: имя, модель автомобиля (или услуга), краткий отзыв и акцентная кнопка. Подходит для лендингов премиального сегмента, где важна лаконичность и доверие без визуального шума.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Block Compose)** — агент [[block-composer]] подбирает блок при наличии секции social-proof в `prototype.yaml`. Также доступен агенту [[ux-composer]] на этапе 07a при построении wireframe.html. Нишевой приоритет: `premium-auto`, `luxury`, `services`.

## Что на вход / на выход
**Вход:**
- `prototype.yaml` — секция с отзывами/кейсами
- `tokens.json` — цвета и типографика для подстановки (тёмная палитра предпочтительна)
- Слот `heading` (text, обязателен) — заголовок секции

**Выход:**
- HTML-фрагмент блока, встроенный в `07b_COMPOSED/composed.html`
- Карточки стека без анимации (`has_animation: false`)
- Адаптивная раскладка `stacked` (вертикальный стек)

## Особенности
- **Нет крупных фото** — блок не требует слотов из PR-B (photo-curator); подходит, если клиент не предоставил портреты
- **Тёмный стиль** (`style_mood: minimal`) — хорошо сочетается с тёмными дизайн-токенами
- **Без анимации** — быстрая загрузка, подходит для performance-критичных лендингов
- **Только ru_market** — тексты и UX-паттерны ориентированы на российский рынок
- Импортирован с `antidiler-karpov.ru` методом `codex-block-generation` (2026-05-16)

## Связанные концепты
- [[block-composer]] — вставляет блок в composed.html на этапе 07b
- [[ux-composer]] — выбирает блок при рендере wireframe.html (этап 07a)
- [[block-composition]] — скилл, управляющий логикой подстановки токенов и текстов в блоки
- [[block-library-management]] — скилл поддержки библиотеки; ведёт meta.yaml всех блоков
- [[07b-composed]] — этап, на котором блок финально собирается с токенами и прототипным контентом

## Источник
- `block-library/social-proof/social-proof-minimal-stacked-antidiler-karpov-ru-4/meta.yaml`