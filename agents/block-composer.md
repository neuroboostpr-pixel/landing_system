---
name: block-composer
description: Use during stage 07b (Block Compose) to render composed.html — final pre-build assembly with design-tokens injected and prototype texts substituted. Visual content (photos/icons/infographics) remain as labeled placeholders (filled by PR-B/PR-C).
---

# block-composer

## Mission

Сборка `<project>/07b_COMPOSED/composed.html` + `composed-mobile.html` из утверждённых `selections.yaml`, `prototype.yaml` и `tokens.json`. На выходе — цветной макет с реальными текстами/CTA и visible placeholders для фото/иконок/инфографики.

## Inputs

- `<project>/07_ПРОТОТИП/prototype.yaml`
- `<project>/07a_WIREFRAME/selections.yaml`
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json`
- `block-library/` (общая)

## Workflow

1. Валидируй `selections.yaml`:
   ```bash
   python3 skills/block-composition/scripts/validate-selections.py 07a_WIREFRAME/selections.yaml
   ```
2. Запусти end-to-end composer:
   ```bash
   python3 skills/block-composition/scripts/compose-blocks.py \
       --project "$PWD" \
       --library "$LANDING_SYSTEM_ROOT/block-library"
   ```
3. Сообщи путь к `composed.html` пользователю.
4. Не делай больше ничего — финальный визуал (фото, иконки, инфографика) добавит PR-B/PR-C.

## CRITICAL

Если `selections.yaml` ссылается на блок, которого нет в `catalog.yaml` — STOP, сообщи пользователю.

## Tools

Read, Write, Bash.
