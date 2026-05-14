---
name: wireframe-rendering
description: Stage 07a — render interactive wireframe.html (desktop+mobile per block with CSS-only radio toggles between 2-3 candidates) from prototype.yaml + block-library. Used by /landing-wireframe and ux-composer agent.
---

# wireframe-rendering

## Что делает

Рендерит `<project>/07a_WIREFRAME/wireframe.html` — интерактивный preview, где для каждого блока прототипа показано 2-3 варианта композиции из `block-library/`. Переключение между вариантами — CSS-only (`:checked` selector), без сборки/JS-фреймворков.

## Scripts

- `scripts/match-candidates.py` — выбрать кандидатов из catalog
- `scripts/render-wireframe.py` — собрать wireframe.html из шаблона + кандидатов
- `scripts/serve-preview.sh` — опциональный `python -m http.server` для случаев, когда `file://` ломает iframe sandbox

## Templates

- `templates/wireframe-shell.html` — оболочка с radio-кнопками и CSS

## Inputs

- `<project>/07_ПРОТОТИП/prototype.yaml`
- `block-library/catalog.yaml`
- `block-library/<category>/<block-id>/assets/template.html|template-mobile.html`

## Outputs

- `<project>/07a_WIREFRAME/wireframe.html`
- `<project>/07a_WIREFRAME/candidates.yaml`
