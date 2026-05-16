---
type: block
name: footer-corporate-grid-3-sskrusgun-ru-14
sources: ["block-library/footer/footer-corporate-grid-3-sskrusgun-ru-14/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["footer", "corporate", "grid-3", "ru-market", "services", "education", "ecommerce"]
---

# Плотный корпоративный подвал — Grid-3 (sskrusgun)

## Что делает
Финальный блок страницы — плотный красный подвал с тремя колонками, в которых размещены контакты компании, навигационное меню и служебная информация (политика, копирайт и т. п.). Строгий корпоративный стиль, без анимации.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при подборе блоков для лендинга. `ux-composer` выбирает этот блок из библиотеки, когда:
- тип страницы — корпоративный или сервисный (услуги, образование, e-commerce),
- нужен плотный подвал с несколькими колонками информации,
- требуется выраженный фирменный цвет (красный / corporate).

На этапе **07b (Compose)** `block-composer` инжектирует design-tokens и заменяет placeholder-тексты на реальный контент из `prototype.yaml`.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — тексты для слотов (heading обязателен)
- `tokens.json` — цвета и типографика проекта
- `selections.yaml` — выбор блока пользователем через wireframe.html

**Слоты:**
| Слот | Тип | Обязателен |
|------|-----|-----------|
| `heading` | text | ✅ да |

**Выход:**
- HTML-фрагмент блока в составе `wireframe.html` (07a) или `composed.html` (07b)

## Ключевые характеристики
- **Категория:** footer
- **Раскладка:** grid-3 (три колонки)
- **Настроение:** corporate
- **Анимация:** нет
- **Рынок:** Россия (`ru_market: true`)
- **Подходящие ниши:** услуги, образование, e-commerce
- **Источник импорта:** sskrusgun.ru (codex-block-generation, 2026-05-16)

## Связанные концепты
- [[ux-composer]] — выбирает блок при построении wireframe на этапе 07a
- [[wireframe-rendering]] — рендерит блок в интерактивный wireframe.html
- [[block-composition]] — инжектирует токены и тексты на этапе 07b
- [[block-library-management]] — управляет хранением и индексацией блоков библиотеки

## Источник
- `block-library/footer/footer-corporate-grid-3-sskrusgun-ru-14/meta.yaml`