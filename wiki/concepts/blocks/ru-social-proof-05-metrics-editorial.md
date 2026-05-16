---
type: block
name: ru-social-proof-05-metrics-editorial
sources: ["block-library/social-proof/ru-social-proof-05-metrics-editorial/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["social-proof", "metrics", "editorial", "ru-market", "services", "b2c", "local"]
---

# Редакционные метрики — Social Proof блок

## Что делает

Показывает ключевые числа компании в редакционном стиле: одна крупная героическая цифра с пояснительным текстом и две карточки-сателлита с дополнительными показателями. Воспринимается как объективная статистика, а не реклама.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при сборке блоков лендинга через [[ux-composer]] и на этапе **07b (Compose)** через [[block-composer]]. Подходит для сервисных B2C-лендингов на русскоязычный рынок, когда нужно быстро передать доверие через цифры — без перегруза и агрессивного рекламного тона.

Рекомендуемые визуальные стили: **Editorial**, **Neumorphism**. Тёплый фон, округлые карточки, сеточная органическая композиция в духе Field Notes.

## Что на вход / на выход

**На вход — 7 текстовых слотов:**

| Слот | Лимит | Назначение |
|---|---|---|
| `hero-metric` | 10 символов | Главная цифра (%, число, год) |
| `hero-context` | 160 символов | Пояснение к главной цифре + опциональная цитата |
| `metric-2-label` | 40 символов | Подпись второго показателя |
| `metric-2-value` | 12 символов | Значение второго показателя |
| `metric-3-label` | 40 символов | Подпись третьего показателя |
| `metric-3-value` | 12 символов | Значение третьего показателя |
| `headline` | 60 символов | Заголовок всего блока |

**На выход:** готовый HTML-фрагмент блока, встраиваемый в `wireframe.html` (07a) или `composed.html` (07b) с подставленными токенами дизайна из `tokens.json`.

## Связанные концепты

- [[ux-composer]] — выбирает этот блок при формировании wireframe.html по prototype.yaml
- [[block-composer]] — рендерит composed.html с реальными текстами и токенами
- [[wireframe-rendering]] — скилл, который использует блок на этапе 07a
- [[block-composition]] — скилл, который использует блок на этапе 07b
- [[block-library-management]] — управление библиотекой, в которой живёт этот блок
- [[content-writer]] — заполняет слоты текстами на основе prototype.yaml и seo-copy.md

## Источник

- `block-library/social-proof/ru-social-proof-05-metrics-editorial/meta.yaml`
- Вдохновлён: OpenDesign / Field Notes Editorial Template (`/tmp/open-design/skills/field-notes-editorial-template/example.html`), лицензия Apache-2.0