---
type: unknown
name: generate-palette-css
sources: ["scripts/generate-palette-css.py", "scripts/generate-palette-css.py.doc.md"]
updated: 2026-05-18
triggers: []
stage: "05"
uses: ["design-tokens-generation", "brand-architect", "wp-theme-assembler"]
tags: ["script", "python", "css", "palette", "tokens"]
---

# generate-palette-css — генератор CSS-блоков палитр

## Что делает
Читает файл `04_БРЕНД/palettes.yaml` текущего проекта и генерирует CSS-блоки вида `body.theme-<id> { ... }` — по одному блоку на каждую цветовую схему. Это позволяет лендингу переключаться между темами через один CSS-класс на `body`.

## Когда вызывать / в каком этапе
Используется на этапе **05 (Design System)** и **08 (Build)** — после того как `brand-architect` сформировал `brand-kit.md` и `design-system-generator` зафиксировал палитры в `palettes.yaml`. Обычно вызывается автоматически в рамках сборки темы или вручную при обновлении палитры:

```bash
python scripts/generate-palette-css.py <project-path>
```

## Что на вход / на выход

**Вход:**
- `<project>/04_БРЕНД/palettes.yaml` — YAML-файл с описанием именованных цветовых палитр (id, набор CSS-переменных или hex-значений).

**Выход:**
- CSS-фрагмент (или файл) с блоками `body.theme-<id> { --color-primary: ...; --color-bg: ...; ... }` для каждой палитры из yaml.
- Результат интегрируется в WordPress-тему через `wp-theme-assembler` или `frontend-builder`.

## Связанные концепты
- [[brand-architect]] — создаёт `brand-kit.md`, из которого выводится `palettes.yaml`
- [[design-tokens-generation]] — скилл, управляющий генерацией токенов; палитры — часть токенов
- [[design-system-generator]] — агент, запускающий генерацию дизайн-системы на этапе 05
- [[wp-theme-assembler]] — скилл сборки WordPress-темы, потребляет сгенерированный CSS
- [[05-dizayn-sistema]] — этап, к которому относится этот скрипт

## Источник
- `scripts/generate-palette-css.py`