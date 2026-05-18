---
type: block
name: hover-effect-08-item-8
sources: ["block-library/_patterns/hover-effect-08-item-8/meta.yaml", "block-library/_patterns/hover-effect-08-item-8/styles.css", "block-library/_patterns/hover-effect-08-item-8/index.html"]
updated: 2026-05-16
triggers: []
stage: ""
uses: []
tags: ["pattern", "hover", "css", "animation", "ui-effect"]
---

# Hover 8 — CSS-паттерн эффекта наведения

## Что делает
Добавляет плавный эффект при наведении курсора на элемент: меняет фоновый цвет с анимацией 0.3 секунды. Паттерн извлечён из реального сайта методом CSS-pattern-extraction.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** и **08 (Build)** — когда нужно добавить интерактивность к карточкам, кнопкам или блокам без JavaScript. Подключается вручную дизайнером или агентом [[block-composer]] при сборке `composed.html`, либо [[frontend-builder]] при генерации блоков темы.

## Что на вход / на выход

**Вход:**
- HTML-элемент с классом `.item-8`
- CSS-переменные дизайн-токенов: `--t396-bgcolor-hover-color`, `--t396-bgcolor-color` (опционально — берётся из `tokens.json`)

**Выход:**
- Элемент с плавным переходом `transition: all 0.3s ease` при hover
- Фоновый цвет меняется через CSS-переменные — без хардкода, адаптируется к бренд-токенам проекта

## Технические детали
- Класс: `.item-8`
- Анимация: `transition: all 0.3s ease`
- Hover-состояние: `background-color` через CSS-переменные с fallback на `transparent`
- Происхождение: извлечён из Tilda-сайта (идентификатор элемента `#rec1232321881`)
- Метод импорта: `css-pattern-extraction`

## Связанные концепты
- [[block-composition]] — скилл сборки блоков, где паттерны подключаются в `composed.html`
- [[design-tokens-generation]] — генерирует `tokens.json` с CSS-переменными, которые использует паттерн
- [[frontend-builder]] — агент, встраивающий паттерны в `block.php` шаблоны WordPress

## Источник
- `block-library/_patterns/hover-effect-08-item-8/meta.yaml`
- `block-library/_patterns/hover-effect-08-item-8/styles.css`
- `block-library/_patterns/hover-effect-08-item-8/index.html`