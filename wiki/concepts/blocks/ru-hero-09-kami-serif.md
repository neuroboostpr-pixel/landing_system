---
type: block
name: ru-hero-09-kami-serif
sources: ["block-library/hero/ru-hero-09-kami-serif/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["hero", "ru_market", "serif", "metrics", "b2c", "services", "two-column"]
---

# Ками-герой — пергамент, засечный шрифт, метрики

## Что делает
Двухколоночный hero-блок в японском стиле «kami» (紙 — бумага): слева крупный засечный заголовок и кнопки CTA, справа — три карточки с ключевыми метриками бизнеса. Фон — тёплый пергамент, акцентный цвет — профессиональный синий #1B365D. На мобайле колонки складываются в стек, карточки идут перед CTA.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при выборе hero-блока для сервисных и B2C лендингов. Подходит для ниш, где важно доверие: финансы, право, архитектура, образование. Рекомендован в стилях Minimalism & Swiss Style, Editorial & Magazine Style, Corporate Clean. Не требует отдельного trust-блока — метрики встроены в hero.

## Что на вход / на выход

**Слоты входа (контент):**
| Слот | Тип | Обязательный | Макс. символов |
|---|---|---|---|
| `eyebrow-left` / `eyebrow-right` | text | нет | 40 |
| `headline` | text | **да** | 80 |
| `subhead` | text | нет | 220 |
| `metric-1/2/3-value` | text | нет | 10 |
| `metric-1/2/3-label` | text | нет | 25 |
| `primary-cta` | cta | **да** | — |
| `secondary-cta` | cta | нет | — |

**Выход:** HTML-блок с двухколоночной раскладкой, адаптивным стеком на mobile, токенами цветов и шрифтов из `tokens.json`.

## Связанные концепты
- [[ux-composer]] — выбирает этот блок при рендере wireframe.html из prototype.yaml
- [[block-composer]] — инжектирует design-tokens и подставляет тексты прототипа в слоты
- [[wireframe-rendering]] — скилл, в рамках которого блок используется на этапе 07a
- [[block-composition]] — скилл этапа 07b, финальная сборка с реальными данными
- [[block-library-management]] — управляет регистрацией и обновлением блоков библиотеки

## Источник
- `block-library/hero/ru-hero-09-kami-serif/meta.yaml`
- Адаптировано из `github.com/nexu-io/open-design: design-templates/kami-landing` (Apache-2.0)