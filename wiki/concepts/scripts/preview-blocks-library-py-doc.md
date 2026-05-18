---
type: script
name: preview-blocks-library
sources: ["scripts/preview-blocks-library.py"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["block-library-management", "ux-composer", "block-composer"]
tags: ["blocks", "preview", "gallery", "html", "utility"]
---

# preview-blocks-library — галерея всех блоков библиотеки

## Что делает
Скрипт обходит папку `block-library/` и рендерит все найденные блоки в единый HTML-файл-галерею, чтобы дизайнер или маркетолог мог быстро просмотреть весь ассортимент визуально прямо в браузере.

## Когда вызывать / в каком этапе
Вызывается вручную в любой момент — когда нужно быстро найти подходящий блок по виду, сравнить варианты или убедиться, что импорт новых блоков прошёл корректно. Особенно полезен на этапах 07a (wireframe) и 07b (compose), когда [[ux-composer]] или [[block-composer]] подбирают блоки из библиотеки.

Запуск:
```bash
python3 scripts/preview-blocks-library.py
```

## Что на вход / на выход

**Вход:**
- `block-library/` — директория со всеми блоками. Поддерживает два формата:
  - **Новый (imported/scaffolded):** `<block>/index.html` + `<block>/styles.css`, текстовые слоты через `{{slot:NAME}}`
  - **Легаси (ru-*):** `<block>/assets/template.html`, самодостаточный HTML с `<style>` и атрибутами `data-slot`

**Выход:**
- `/tmp/block-library-gallery.html` — одна HTML-страница со всеми блоками

**Особенности вывода:**
- Липкая навигация вверху страницы с категориями и радиофильтром
- Три режима фильтрации: «Все», «Только новые импортированные», «Только legacy ru-*»
- Слоты заполняются dummy-контентом для визуального смысла превью

## Связанные концепты
- [[block-library-management]] — управление библиотекой блоков, из которой читает скрипт
- [[ux-composer]] — агент этапа 07a, подбирает блоки для wireframe; галерея помогает в выборе
- [[block-composer]] — агент этапа 07b, собирает composed.html из тех же блоков

## Источник
- `scripts/preview-blocks-library.py`