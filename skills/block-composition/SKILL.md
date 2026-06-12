---
name: block-composition
description: Stage 07b/07f — re-render готового composed.html (подстановка фото/иконок/инфографики в placeholders) и инъекция mood-палитр. Машинная склейка блоков из библиотеки — в архиве (reference-driven flow).
---

# block-composition (reference-driven)

Макет `composed.html` РИСУЕТ агент block-composer (правила:
`docs/standards/reference-driven-rules.md`, `design-elements-rules.md`).
Этот скилл оставляет только пост-обработку готового макета:

- `scripts/rerender-composed.py --project <dir>` — заменяет `[SLOT: name]`
  и `data-slot="name"` placeholders на реальные фото (07c_PHOTOS/selections.yaml,
  processed) и визуалы (07d_VISUALS/icons|infographics). Бэкап в composed.html.bak.
- `scripts/inject-tokens.py` — инъекция mood-палитры из `block-library/_styles/`
  (переключатель палитры, спека §2.5).
- `scripts/inject-content.py` — библиотека inject_block() для photo/visual
  пайплайнов (PR-B/PR-C тесты).

Архив: compose-blocks.py, validate-selections.py → archive/skills/block-composition/.
