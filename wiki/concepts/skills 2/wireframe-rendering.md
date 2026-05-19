---
type: skill
name: wireframe-rendering
sources: ["skills/wireframe-rendering/SKILL.md"]
updated: 2026-05-15
triggers: ["/landing-wireframe", "нарисуй wireframe", "покажи варианты блоков", "составь wireframe"]
stage: "07a"
uses: ["ux-composer", "prototype-import", "block-library-management", "block-composition"]
tags: ["wireframe", "html", "css-only", "block-library", "preview"]
---

# Wireframe Rendering — интерактивный прототип блоков

## Что делает

Строит `wireframe.html` — интерактивную страницу-предпросмотр, где для каждого блока прототипа показаны 2–3 варианта композиции из библиотеки блоков. Переключение между вариантами работает на чистом CSS (без JS-фреймворков), а каждый блок отображается сразу в двух видах: desktop и mobile.

## Когда вызывать / в каком этапе

Этап **07a**. Вызывается командой `/landing-wireframe` или агентом `ux-composer` после того, как импортирован прототип (этап 07 — `prototype-import`). Предшествует команде `/landing-compose` (этап 07b).

## Что на вход / на выход

**Входные артефакты:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — машиночитаемый прототип, подготовленный скиллом `prototype-import`
- `block-library/catalog.yaml` — каталог всех доступных блоков системы
- `block-library/<category>/<block-id>/assets/template.html` и `template-mobile.html` — HTML-шаблоны блоков для desktop и mobile

**Выходные артефакты:**
- `<project>/07a_WIREFRAME/wireframe.html` — интерактивный wireframe с CSS-переключением вариантов
- `<project>/07a_WIREFRAME/candidates.yaml` — список подобранных кандидатов (до 3-х) для каждого слота прототипа

**Вспомогательные скрипты:**
- `scripts/match-candidates.py` — подбирает кандидатов из каталога для каждого блока прототипа
- `scripts/render-wireframe.py` — собирает `wireframe.html` из оболочки + кандидатов
- `scripts/serve-preview.sh` — локальный `http.server` на случай, если `file://` ломает iframe sandbox

**Шаблоны:**
- `templates/wireframe-shell.html` — HTML-оболочка с radio-кнопками и CSS-логикой переключения

## Связанные концепты

- [[prototype-import]] — поставляет `prototype.yaml`, который служит основным входом
- [[block-library-management]] — каталог `block-library/catalog.yaml`, из которого подбираются кандидаты
- [[ux-composer]] — агент, который вызывает этот скилл для рендеринга wireframe
- [[block-composition]] — следующий этап (07b): принимает выбранные в wireframe варианты и формирует `composed.html`

## Источник

- `skills/wireframe-rendering/SKILL.md`