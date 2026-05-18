---
type: block
name: hero-cinematic-split-portfolio-kdm1-ru-2
sources: ["block-library/hero/hero-cinematic-split-portfolio-kdm1-ru-2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["hero", "cinematic", "split", "dark", "ru-market", "premium-auto", "ecommerce", "tech", "services"]
---

# Темный промо-блок с крупным заголовком и 3D-предметом (hero-cinematic-split)

## Что делает

Тёмный hero-блок в кинематографическом стиле с разделённой компоновкой (split): слева — крупный заголовок и CTA-кнопки, справа — 3D-объект (продукт или предмет). Снизу или поверх — плашки с ключевыми преимуществами. Создаёт ощущение премиума и визуальной силы без анимации.

## Когда вызывать / в каком этапе

Используется на **этапе 07a (Wireframe)** — `ux-composer` подбирает этот блок из библиотеки, если прототип предполагает hero-секцию с тёмным/кинематографическим настроением. На **этапе 07b (Compose)** — `block-composer` рендерит composed.html, подставляя токены дизайна и тексты прототипа в слот `heading`.

Подходит для ниш: **премиальный авто** (`premium-auto`), **электронная коммерция** (`ecommerce`), **услуги** (`services`), **технологии** (`tech`).

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — текст для слота `heading` (обязательный)
- `tokens.json` — цвета, шрифты бренда
- `composed.html` (контекст) — место вставки блока

**Выход:**
- Отрендеренный HTML-фрагмент блока с подставленным заголовком, CTA-кнопками-заглушками и placeholder для 3D-объекта (слот типа фото/визуал)
- Плашки преимуществ — placeholder до наполнения контентом

**Слоты:**
| Имя | Тип | Обязателен |
|-----|-----|-----------|
| `heading` | text | да |

**Ограничения:** `has_animation: false` — блок статичен, без GSAP/scroll-эффектов. Импортирован из внешнего PDF-портфолио (codex-block-generation).

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe.html
- [[block-composer]] — рендерит блок в composed.html с токенами и текстами
- [[wireframe-rendering]] — скилл этапа 07a, в рамках которого блок попадает в wireframe
- [[block-composition]] — скилл этапа 07b, инжектит design-tokens в блок
- [[block-library-management]] — управление каталогом блоков, к которому принадлежит этот блок
- [[scene-director]] — если проект cinematic-mode, может задавать motion-план поверх статичных блоков

## Источник

- `block-library/hero/hero-cinematic-split-portfolio-kdm1-ru-2/meta.yaml`