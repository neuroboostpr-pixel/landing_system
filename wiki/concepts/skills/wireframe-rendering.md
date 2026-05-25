---
type: skill
name: wireframe-rendering
sources: ["skills/wireframe-rendering/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: "07a"
uses: ["landing-wireframe", "ux-composer", "landing-prototype"]
tags: ["wireframe", "html", "block-library", "prototype", "07a"]
---

# Wireframe Rendering — интерактивный wireframe на этапе 07a

## Что делает

Превращает структуру прототипа в интерактивный HTML-файл, где каждый блок страницы показан в 2–3 визуальных вариантах. Маркетолог или заказчик просто кликает по вариантам и выбирает понравившийся — никакого кода, никакой сборки.

## Когда вызывать / в каком этапе

Этап **07a** — после того как `landing-prototype` создал `prototype.yaml`. Вызывается командой `/landing-wireframe` или агентом `ux-composer`. Запускается вручную, не через `landing-orchestrator` (до PR-D).

## Что на вход / на выход

**Входные артефакты:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — структурированный прототип лендинга
- `block-library/catalog.yaml` — каталог всех доступных блоков
- `block-library/<category>/<block-id>/assets/template.html` — HTML-шаблоны блоков (десктоп)
- `block-library/<category>/<block-id>/assets/template-mobile.html` — мобильные варианты

**Выходные артефакты:**
- `<project>/07a_WIREFRAME/wireframe.html` — интерактивный wireframe с CSS-only переключением вариантов (`:checked` selector, без JS-фреймворков)
- `<project>/07a_WIREFRAME/candidates.yaml` — список подобранных кандидатов для каждого блока

**Скрипты:**
- `scripts/match-candidates.py` — подбирает 2–3 кандидата из `catalog.yaml` для каждого блока прототипа
- `scripts/render-wireframe.py` — собирает `wireframe.html` из шаблона оболочки и кандидатов
- `scripts/serve-preview.sh` — поднимает `python -m http.server` если `file://` ломает iframe sandbox

**Шаблоны:**
- `templates/wireframe-shell.html` — HTML-оболочка с radio-кнопками и CSS-логикой переключения

## Связанные концепты

- [[landing-wireframe]] — slash-команда, вызывающая этот скилл
- [[landing-prototype]] — предыдущий этап, создаёт `prototype.yaml` как входной артефакт
- [[landing-compose]] — следующий этап 07b, использует `selections.yaml` из wireframe
- [[ux-composer]] — агент, который диспатчит этот скилл в рамках оркестрации

## Источник

- `skills/wireframe-rendering/SKILL.md`