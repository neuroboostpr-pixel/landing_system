---
type: rule
name: pr-a-prototype-block-library-ux-composer-design
sources: ["docs/superpowers/specs/2026-05-12-prototype-block-library-ux-composer-design.md"]
updated: 2026-05-18
triggers:
  - "что такое PR-A"
  - "как работает block library"
  - "архитектура прототип + wireframe + compose"
  - "зачем нужен ux-composer"
stage: "07–07b"
uses:
  - prototype-importer
  - ux-composer
  - block-composer
  - prototype-import
  - block-library-management
  - wireframe-rendering
  - block-composition
  - landing-prototype
  - landing-wireframe
  - landing-compose
  - 07-prototip
  - 07a-wireframe
  - 07b-composed
  - design-tokens-generation
tags: [spec, pr-a, prototype, block-library, wireframe, compose, architecture]
---

# PR-A: Прототип + Block Library + ux-composer — дизайн-спецификация

## Что делает

Описывает архитектуру трёх новых этапов (07 Прототип → 07a Wireframe → 07b Compose), которые закрывают разрыв между DESIGN.md и кодом. Вводит общую библиотеку переиспользуемых блоков и агентов для их оркестрации.

## Когда вызывать / в каком этапе

Спецификация применяется при планировании или доработке компонентов PR-A. Этапы 07–07b вызываются вручную через `/landing-prototype` → `/landing-wireframe` → `/landing-compose` (интеграция в `landing-orchestrator` — задача PR-D).

## Что на вход / на выход

**Вход:**
- Пользовательский прототип (`prototype.pdf` или `.md`) в `07_ПРОТОТИП/source/`
- Токены дизайн-системы (`tokens.json`, `DESIGN.md`) из этапа 05
- Подтверждённый выбор вариантов блоков (`selections.yaml`) из wireframe-этапа

**Выход:**
- `prototype.md` + `prototype.yaml` — нормализованный источник правды по контенту
- `wireframe.html` — интерактивный preview с radio-переключателями вариантов (CSS-only, 2–3 варианта на блок, desktop + mobile рядом)
- `selections.yaml` — подтверждённый пользователем выбор композиций
- `composed.html` — цветной макет с инжектированными tokens, текстами из прототипа и плейсхолдерами для визуала (PR-B/PR-C)
- `landing-system/block-library/` — каталог из 17 seed-блоков (12 базовых + 5 quiz), каждый с `template.html`, `template-mobile.html`, `meta.yaml`, `SKILL.md`

**Ключевые решения (decisions log):**
- Прототип — гибрид MD+YAML: человек редактирует MD, YAML автогенерится
- Блоки — чистый HTML + inline CSS, без фреймворков, открываются двойным кликом
- `ux-composer` НИКОГДА не придумывает блоки — только выбирает из библиотеки; при отсутствии подходящего — `needs_new_block: true`
- Wireframe использует 30 строк inline JS только для сохранения выбора (clipboard / скачивание `selections.yaml`)
- OpenDesign (Apache-2.0) подключён copy-only с атрибуцией в `THIRD_PARTY_NOTICES.md`

## Связанные концепты

- [[prototype-importer]] — агент импорта PDF/MD → `prototype.{md,yaml}`
- [[ux-composer]] — агент подбора блоков и рендера `wireframe.html`
- [[block-composer]] — агент сборки `composed.html` из выбранных блоков
- [[prototype-import]] — скилл парсинга PDF через `anthropic-skills:pdf`
- [[block-library-management]] — скилл управления каталогом библиотеки
- [[wireframe-rendering]] — скилл рендера интерактивного wireframe
- [[block-composition]] — скилл инжекта токенов и текстов в шаблон блока
- [[landing-prototype]] — команда запуска импорта прототипа
- [[landing-wireframe]] — команда запуска ux-composer
- [[landing-compose]] — команда запуска block-composer
- [[design-tokens-generation]] — скилл обновляется под 9-секционную структуру DESIGN.md (D12)

## Источник

- `docs/superpowers/specs/2026-05-12-prototype-block-library-ux-composer-design.md`