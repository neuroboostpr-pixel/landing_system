---
type: block
name: features-technical-grid-4-project21993216-tild-2
sources: ["block-library/features/features-technical-grid-4-project21993216-tild-2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "grid-4", "technical", "b2b-saas", "services", "tech", "ru-market"]
---

# Features: Полоса с тезисом и четырьмя числовыми преимуществами

## Что делает

Блок-секция «features» в стиле технической сетки: светло-голубой фон, один короткий тезис-заголовок и четыре числовых преимущества в виде сетки из четырёх колонок. Подходит для страниц, где нужно быстро показать ключевые цифры или факты о продукте.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при формировании wireframe.html: агент [[ux-composer]] выбирает блок из библиотеки, если в прототипе есть секция с числовыми преимуществами или кратким перечислением сильных сторон. На этапе **07b (Compose)** агент [[block-composer]] инжектирует в него design-tokens и тексты из prototype.yaml. Подходит для ниш **b2b-saas**, **services**, **tech** на российском рынке.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — текст тезиса и четырёх числовых фактов
- `tokens.json` — цветовые токены (светло-голубой берётся из палитры бренда)
- `selections.yaml` — если пользователь выбрал этот вариант блока в wireframe

**Выход:**
- HTML-секция внутри `wireframe.html` (этап 07a) — скелет блока с placeholder-текстами
- HTML-секция внутри `composed.html` (этап 07b) — блок с реальными текстами и токенами

**Слоты:**
| Слот | Тип | Обязателен |
|------|-----|-----------|
| `heading` | text | да |

Четыре числовых карточки — часть паттерна `grid-4`; их тексты заполняются из prototype.yaml автоматически.

**Ограничения:** анимации отсутствуют (`has_animation: false`), блок статичный.

## Связанные концепты

- [[ux-composer]] — выбирает этот блок при рендере wireframe.html на этапе 07a
- [[block-composer]] — инжектирует токены и контент на этапе 07b
- [[wireframe-rendering]] — скилл, управляющий сборкой wireframe из библиотеки блоков
- [[block-composition]] — скилл этапа 07b, подставляющий design-tokens в блок
- [[block-library-management]] — скилл обслуживания и импорта блоков библиотеки

## Источник

- `block-library/features/features-technical-grid-4-project21993216-tild-2/meta.yaml`
- Импортирован с `https://project21993216.tilda.ws/` методом `codex-block-generation` (2026-05-16)