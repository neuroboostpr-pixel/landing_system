---
type: skill
name: wireframe-rendering
sources: ["skills/wireframe-rendering/SKILL.md"]
updated: 2026-05-26
triggers: []
stage: "07a"
uses: ["landing-wireframe", "ux-composer", "landing-prototype", "block-library"]
tags: ["wireframe", "html", "preview", "block-library", "css-only"]
---

# Wireframe Rendering — Интерактивный вайрфрейм блоков

## Что делает

Генерирует интерактивный HTML-файл, в котором для каждого блока лендинга показано 2–3 варианта компоновки из библиотеки блоков. Маркетолог или дизайнер выбирает понравившийся вариант прямо в браузере — без кода и сборки.

## Когда вызывать / в каком этапе

Этап **07a**. Вызывается командой `/landing-wireframe` или агентом `ux-composer` после того, как этап 07 (прототип) завершён и файл `prototype.yaml` готов. Предшествует этапу 07b (compose).

## Что на вход / на выход

**Входные артефакты:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — структура блоков прототипа
- `block-library/catalog.yaml` — каталог всех блоков библиотеки
- `block-library/<category>/<block-id>/assets/template.html` — desktop-шаблон блока
- `block-library/<category>/<block-id>/assets/template-mobile.html` — mobile-шаблон блока

**Выходные артефакты:**
- `<project>/07a_WIREFRAME/wireframe.html` — интерактивный вайрфрейм с CSS-only переключением вариантов
- `<project>/07a_WIREFRAME/candidates.yaml` — машинный список выбранных кандидатов

**Внутренние скрипты:**
- `scripts/match-candidates.py` — подбирает кандидатов из каталога под каждый блок прототипа
- `scripts/render-wireframe.py` — собирает итоговый `wireframe.html` из шаблона и кандидатов
- `scripts/serve-preview.sh` — запускает `python -m http.server` если `file://` ломает iframe sandbox

**Шаблон оболочки:**
- `templates/wireframe-shell.html` — HTML-оболочка с radio-кнопками и CSS-переключателями (`:checked` selector, без JS-фреймворков)

## Связанные концепты

- [[landing-wireframe]] — slash-команда, которая вызывает этот скилл
- [[ux-composer]] — агент, использующий скилл в рамках оркестрации
- [[landing-prototype]] — предыдущий этап, формирует `prototype.yaml` на входе
- [[landing-compose]] — следующий этап (07b), потребляет `selections.yaml` из вайрфрейма
- [[block-library]] — источник HTML-шаблонов кандидатов для каждого блока

## Источник

- `skills/wireframe-rendering/SKILL.md`