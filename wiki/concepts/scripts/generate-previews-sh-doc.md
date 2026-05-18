---
type: rule
name: generate-previews
sources: ["scripts/generate-previews.sh"]
updated: 2026-05-18
triggers: []
stage: "07b"
uses: ["block-composer", "07b-composed"]
tags: ["scripts", "preview", "composed", "desktop", "mobile", "responsive"]
---

# generate-previews.sh — генератор preview-обёрток

## Что делает

Bash-скрипт, который берёт готовый `composed.html` и создаёт три HTML-файла для просмотра лендинга в эмуляции разных устройств: отдельный Desktop-preview (1280×800), отдельный Mobile-preview (375×812, iPhone 14) и единый индекс с переключателем — Mobile / Tablet / Desktop / Wide — прямо в браузере.

## Когда вызывать / в каком этапе

Запускается вручную после того, как этап **07b (Compose)** завершён и файл `07b_COMPOSED/composed.html` уже существует. Вызывается командой:

```bash
bash scripts/generate-previews.sh <путь/к/проекту>
```

Используется маркетологом или разработчиком для быстрой визуальной проверки адаптивности лендинга перед переходом к этапу 08 (сборка WordPress-темы).

## Что на вход / на выход

**Вход:**
- `$1` — путь к папке проекта (обязательный аргумент)
- `<project>/07b_COMPOSED/composed.html` — готовый скомпонованный лендинг

**Выход (3 файла в `07b_COMPOSED/`):**
- `composed-desktop-preview.html` — iframe 1280×800 в тёмной рамке
- `composed-mobile-preview.html` — iframe 375×812 в тёмной рамке (iPhone 14)
- `composed-previews-index.html` — единый HTML с JS-переключателем: 📱 375, 📲 768, 💻 1280, 🖥 1920

Все три файла подгружают `composed.html` через `<iframe>`, не копируя его содержимое.

## Связанные концепты

- [[block-composer]] — создаёт `composed.html`, который скрипт оборачивает в preview
- [[07b-composed]] — этап, на котором появляется исходный `composed.html`
- [[landing-compose]] — команда, запускающая этап 07b и создающая composed.html

## Источник

- `scripts/generate-previews.sh`