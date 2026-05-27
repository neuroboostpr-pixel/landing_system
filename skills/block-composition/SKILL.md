---
name: block-composition
description: Stage 07b — compose chosen blocks with design-tokens injected and prototype content substituted. Used by /landing-compose command and block-composer agent.
---

# block-composition

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill block-composition --stage 07b
```

Сборка composed.html из утверждённых блоков и tokens.json.

## Scripts

- `scripts/validate-selections.py` — проверить `selections.yaml`
- `scripts/inject-tokens.py` — заменить CSS-переменные в template.html на значения из tokens.json
- `scripts/inject-content.py` — подставить тексты/заголовки/CTA из prototype.yaml
- `scripts/compose-blocks.py` — собрать composed.html (desktop) + composed-mobile.html

## Inputs

- `<project>/07_ПРОТОТИП/prototype.yaml`
- `<project>/07a_WIREFRAME/selections.yaml`
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json`
- `block-library/` (общая)

## Outputs

- `<project>/07b_COMPOSED/composed.html`
- `<project>/07b_COMPOSED/composed-mobile.html`
- `<project>/07b_COMPOSED/block-injection-log.md`
