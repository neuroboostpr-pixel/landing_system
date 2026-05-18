---
type: rule
name: block-loader
sources: ["scripts/block-loader.py.doc.md", "scripts/block-loader.py"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["block-library-management", "wireframe-rendering", "block-composition"]
tags: ["python", "script", "block-library", "loader"]
---

# block-loader — загрузчик блоков из библиотеки

## Что делает

Python-модуль, который умеет читать HTML/CSS-блоки из `block-library/` и возвращать их содержимое в виде словаря. Поддерживает оба формата хранения блоков — старый и новый — так что агентам не нужно знать, в каком формате лежит конкретный блок.

## Когда вызывать / в каком этапе

Используется внутренне любым агентом или скриптом, которому нужно прочитать HTML-шаблон блока из библиотеки. Особенно актуален на этапах **07a (wireframe)** и **07b (compose)**, когда `ux-composer` и `block-composer` собирают финальные HTML-файлы из отдельных блоков.

## Что на вход / на выход

**Вход:**
- Путь к блоку внутри `block-library/` в виде строки, например `"hero/ru-hero-01-services-calc"`.

**Выход:**
- Словарь с ключами:
  - `html` — десктопный HTML-шаблон блока
  - `css` — стили блока (если есть отдельный файл `styles.css`)
  - `mobile_html` — мобильный вариант HTML (если есть)
  - `meta` — содержимое `meta.yaml` блока

**Поддерживаемые форматы блоков:**
- **Старый формат:** `assets/template.html` + `assets/template-mobile.html`
- **Новый формат:** `index.html` + `styles.css`

Если мобильного файла нет, `mobile_html` возвращается как `None`.

## Пример использования

```python
from scripts.block_loader import load_block

block = load_block("hero/ru-hero-01-services-calc")
# → {"html": "...", "css": "...", "mobile_html": "...", "meta": {...}}
```

## Связанные концепты

- [[block-library-management]] — управление библиотекой блоков, которую loader читает
- [[wireframe-rendering]] — этап 07a, использует loader для сборки wireframe.html
- [[block-composition]] — этап 07b, использует loader для сборки composed.html
- [[ux-composer]] — агент, вызывающий loader при рендере wireframe
- [[block-composer]] — агент, вызывающий loader при сборке composed.html

## Источник

- `scripts/block-loader.py`
- `scripts/block-loader.py.doc.md`