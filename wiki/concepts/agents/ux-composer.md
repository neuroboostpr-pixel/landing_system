---
type: agent
name: ux-composer
sources: ["agents/ux-composer.md"]
updated: 2026-05-20
triggers: []
stage: "07a"
uses: ["prototype-importer", "block-composer", "landing-wireframe", "wireframe-rendering", "block-library-management", "ui-ux-pro-max", "stage-execution-protocol"]
tags: ["wireframe", "07a", "block-library", "ux", "prototype"]
---

# ux-composer — Сборщик интерактивного wireframe

## Что делает
Берёт одобренный прототип (`prototype.yaml`) и для каждого блока подбирает 2–3 готовых варианта из block-library. Собирает `wireframe.html` с radio-переключателями, чтобы пользователь мог выбрать понравившийся вариант на каждый блок и скачать `selections.yaml`. **Никогда не придумывает блоки сам** — только выбирает из библиотеки.

## Когда вызывать / в каком этапе
Этап **07a (UX Wireframe)**. Запускается через команду `/landing-wireframe` или `landing-orchestrator` после того, как:
- этап `07_ПРОТОТИП` закрыт (существует `prototype.yaml` и он прошёл валидацию),
- `.landing-state.yaml` содержит `current_stage == 07b_wireframe`.

Если `.landing-state.yaml` не соответствует — агент останавливается и сообщает об ошибке.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/prototype.yaml` — список блоков с типами и текстами
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены
- `04_БРЕНД/brand-kit.md` — брендинг
- `block-library/catalog.yaml` — каталог доступных блоков
- CSV-файлы из `ui-ux-pro-max`: `landing.csv`, `ux-guidelines.csv`, `web-interface.csv`, `styles.csv`, `colors.csv`, `typography.csv` — UX-паттерны, стили, палитры, типографика

**Выход:**
- `07a_WIREFRAME/wireframe.html` — интерактивный wireframe с radio-вариантами на каждый блок
- `07a_WIREFRAME/candidates.yaml` — список кандидатов из library для каждого блока
- `07a_WIREFRAME/selections.yaml` — заполняется пользователем после выбора в браузере (скачивается кнопкой «Confirm»)

**HARD GATE:** пока `selections.yaml` не появился в папке — переход к этапу 07b (compose) заблокирован.

## Особые правила
- Если для блока прототипа `candidates: []` — агент не генерирует fallback, а сообщает пользователю и предлагает scaffoldить новый блок командой `scaffold-block.py`.
- Если `ui-ux-pro-max` не установлен — агент останавливается с инструкцией по установке.
- `PreToolUse` hook (`enforce_stage_gate.py`) физически блокирует Write/Edit, если предшественники этапа не закрыты — обходить нельзя.

## Связанные концепты
- [[prototype-importer]] — создаёт `prototype.yaml`, который ux-composer читает на вход
- [[block-composer]] — следующий этап (07b): принимает `selections.yaml` и собирает `composed.html`
- [[wireframe-rendering]] — скилл с шаблоном и скриптом `render-wireframe.py`
- [[block-library-management]] — скилл для создания новых блоков через `scaffold-block.py`
- [[landing-wireframe]] — slash-команда, запускающая этот агент
- [[stage-execution-protocol]] — обязательный протокол перед любым действием агента

## Источник
- `agents/ux-composer.md`