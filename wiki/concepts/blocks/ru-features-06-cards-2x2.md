---
type: block
name: ru-features-06-cards-2x2
sources: ["block-library/features/ru-features-06-cards-2x2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "cards", "2x2", "ru-market", "b2c", "services", "local", "opendesign"]
---

# Четыре карточки 2×2 — bone-фон, тени, курсивные числа

## Что делает
Блок «Преимущества / Услуги» с четырьмя карточками в сетке 2×2. Слева — заголовочная колонка с kicker, заголовком и подзаголовком, справа — четыре карточки с порядковыми номерами 01–04, тегом-меткой и описанием. Тёплый bone-фон карточек с тенями и скруглёнными углами создаёт визуальный контраст с фоном страницы. На мобильном заголовок уходит вверх, сетка 2×2 остаётся ниже.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** — агент [[ux-composer]] выбирает блок из библиотеки при сборке wireframe.html. Затем на этапе **07b (Compose)** агент [[block-composer]] подставляет дизайн-токены и текст из прототипа. Подходит когда нужно показать ровно четыре равнозначных услуги, направления или возможности продукта. Оптимален для b2c, локального бизнеса и сервисных компаний.

## Что на вход / на выход

**Слоты (вход):**
| Слот | Обязательный | Лимит |
|---|---|---|
| `kicker` | нет | 50 символов |
| `headline` | **да** | 70 символов |
| `subhead` | нет | 200 символов |
| `card-N-title` (×4) | **да** | 40 символов |
| `card-N-desc` (×4) | **да** | 140 символов |
| `card-N-tag` (×4) | нет | 20 символов |

**Выход:** HTML-блок с двухколоночным макетом (заголовок + сетка 2×2), hover-анимацией `translateY` без JS, адаптивным mobile-видом.

**Источник дизайна:** OpenDesign Landing (Apache-2.0), паттерн `capabilities-grid`.

## Связанные концепты
- [[ux-composer]] — выбирает этот блок при сборке wireframe из prototype.yaml
- [[block-composer]] — рендерит composed.html с реальными токенами и текстами
- [[wireframe-rendering]] — скилл, управляющий 07a этапом
- [[block-composition]] — скилл, управляющий 07b этапом
- [[block-library-management]] — скилл обслуживания и расширения библиотеки блоков

## Источник
- `block-library/features/ru-features-06-cards-2x2/meta.yaml`
- Атрибуция: `github.com/nexu-io/open-design: design-templates/open-design-landing (Apache-2.0)`