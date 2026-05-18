---
type: block
name: ru-trust-05-manifesto-text
sources: ["block-library/trust/ru-trust-05-manifesto-text/meta.yaml"]
updated: 2026-05-13
triggers: []
stage: "07a"
uses:
  - block-composition
  - ux-composer
  - block-composer
  - block-library-management
tags:
  - trust
  - ru_market
  - b2c
  - services
  - local
  - opendesign
  - editorial
  - manifesto
---

# Манифест — засечная цитата с левой полосой и подписью

## Что делает

Вставляет блок-манифест в стиле editorial: двухколоночный макет с меткой слева и большой засечной цитатой справа, синяя вертикальная полоса, подпись с тире, бежевый пергаментный фон. Создаёт ощущение философии и ценностей бренда — «разрыв шаблона» между техническими блоками.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** и **07b (Block Compose)**: агент [[ux-composer]] выбирает блок из библиотеки по типу `trust`, агент [[block-composer]] инжектирует токены и подставляет текст из `prototype.yaml`.

Рекомендуется размещать **между hero и features** — там, где нужно переключить тональность с продающей на ценностно-смысловую. Хорошо подходит для сервисного b2c и локального бизнеса.

## Что на вход / на выход

**Слоты (входные данные):**

| Слот | Тип | Макс. символов | Обязателен |
|---|---|---|---|
| `section-label` | text | 50 | нет |
| `manifesto-text` | text | 500 | **да** |
| `sig-text` | text | 60 | нет |

**На выход:** HTML-секция с двухколоночным layout. Desktop — метка слева, цитата справа. Mobile — метка сверху, текст ниже. Шрифт Source Serif 4 (засечный), синяя левая полоса через CSS `border-left`, бежевый фон (`#f5f0e8` или аналог из `tokens.json`).

**Источник:** `opendesign` — `github.com/nexu-io/open-design: design-templates/kami-landing (Apache-2.0)`. Атрибуция обязательна через `THIRD_PARTY_NOTICES.md`.

## Рекомендуемые стили

- **Editorial & Magazine Style** — основной стиль блока
- **Minimalism & Swiss Style** — работает как альтернатива

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки на этапе 07a по категории `trust`
- [[block-composer]] — на этапе 07b инжектирует design-tokens и подставляет текст прототипа
- [[block-composition]] — скилл, управляющий процессом сборки composed.html
- [[block-library-management]] — скилл реестра блоков, отвечает за регистрацию `meta.yaml`

## Источник

- `block-library/trust/ru-trust-05-manifesto-text/meta.yaml`