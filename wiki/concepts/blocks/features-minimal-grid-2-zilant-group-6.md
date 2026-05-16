---
type: block
name: features-minimal-grid-2-zilant-group-6
sources: ["block-library/features/features-minimal-grid-2-zilant-group-6/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses:
  - ux-composer
  - block-composer
  - wireframe-rendering
  - block-composition
tags:
  - features
  - minimal
  - grid-2
  - ru-market
  - animation
  - services
  - b2b-saas
  - education
  - tech
---

# Features Minimal Grid-2 — Zilant Group 6

## Что делает

Светлая секция «для кого» с сегментированными аудиториями: отображает потребности разных групп клиентов в виде компактных карточек, сгруппированных в двухколоночную сетку. Подходит для лендингов, где важно показать несколько целевых сегментов одновременно.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** и **07b (Block Compose)**. Агент `ux-composer` подбирает блок из библиотеки при наличии в `prototype.yaml` секции с аудиториями или сегментами. Агент `block-composer` инжектирует токены дизайна и подставляет тексты из прототипа.

Подходит для ниш: **services, b2b-saas, education, tech**. Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — тексты сегментов/аудиторий и заголовок секции
- `tokens.json` — цвета, типографика, отступы из бренд-кита
- `selections.yaml` (07a) — подтверждённый выбор блока пользователем

**Выход:**
- HTML-фрагмент блока, встроенный в `wireframe.html` (этап 07a)
- HTML-фрагмент с подставленными токенами и текстами в `composed.html` (этап 07b)

**Слоты:**
| Слот | Тип | Обязательный |
|------|-----|--------------|
| `heading` | text | да |

**Анимация:** блок помечён `has_animation: true` — предполагает появление карточек при скролле (через GSAP или CSS transitions на этапе 08).

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при рендере wireframe.html
- [[block-composer]] — инжектирует design-tokens и тексты в composed.html
- [[wireframe-rendering]] — скилл рендера wireframe, использует этот блок
- [[block-composition]] — скилл этапа 07b, подставляет токены в блок
- [[block-library-management]] — скилл управления библиотекой, где хранится блок

## Источник

- `block-library/features/features-minimal-grid-2-zilant-group-6/meta.yaml`
- Импортировано с `https://zilant.group/` методом `codex-block-generation` (2026-05-16)