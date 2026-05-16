---
type: block
name: ru-features-02-bento-grid
sources: ["block-library/features/ru-features-02-bento-grid/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses:
  - ux-composer
  - block-composer
  - photo-curator
  - visual-curator
tags: ["features", "bento-grid", "photo", "icons", "ru-market", "b2c", "services", "local"]
---

# Bento-сетка: фото + 3 карточки

## Что делает

Блок «Преимущества» в формате сетки 2×2: слева крупное фото (50% ширины), справа три компактные карточки с иконкой, заголовком и коротким текстом. Большое фото якорит взгляд, карточки лаконично перечисляют выгоды — без лишних слов.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** — [[ux-composer]] выбирает этот блок из библиотеки, если нужен раздел «Особенности» или «Почему мы» для услуг (b2c, local, сервисный бизнес). На этапе **07b (Compose)** — [[block-composer]] наполняет слоты токенами и прототипным текстом. Рекомендованные визуальные стили: **Glassmorphism** и **Bento Grid**.

## Что на вход / на выход

**Слоты на вход:**

| Слот | Тип | Обязателен | Ограничение |
|---|---|---|---|
| `headline` | text | да | 60 символов |
| `feature-photo` | photo | да | ratio 1:1 |
| `bento-1-icon` | icon | нет | — |
| `bento-1-title` | text | да | 30 символов |
| `bento-1-text` | text | да | 80 символов |
| `bento-2-icon` | icon | нет | — |
| `bento-2-title` | text | да | 30 символов |
| `bento-2-text` | text | да | 80 символов |
| `bento-3-icon` | icon | нет | — |
| `bento-3-title` | text | да | 30 символов |
| `bento-3-text` | text | да | 80 символов |

**На выход:** HTML-фрагмент блока с заполненными слотами, встроенный в `wireframe.html` (07a) или `composed.html` (07b). Фото-слот `feature-photo` заполняется [[photo-curator]], иконки `bento-*-icon` — [[visual-curator]] (через [[icon-generator]]).

## Связанные концепты

- [[ux-composer]] — выбирает блок при построении wireframe.html на этапе 07a
- [[block-composer]] — инжектирует design-токены и прототипный текст на этапе 07b
- [[photo-curator]] — обрабатывает слот `feature-photo` (ratio 1:1)
- [[visual-curator]] — генерирует иконки для слотов `bento-*-icon`
- [[icon-generator]] — создаёт PNG для каждого icon-слота через codex image_gen
- [[block-library-management]] — скилл управления библиотекой, в которую входит этот блок

## Источник

- `block-library/features/ru-features-02-bento-grid/meta.yaml`