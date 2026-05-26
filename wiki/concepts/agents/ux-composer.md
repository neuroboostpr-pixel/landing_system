---
type: agent
name: ux-composer
sources: ["agents/ux-composer.md"]
updated: 2026-05-26
triggers: []
stage: "07a"
uses: ["landing-wireframe", "prototype-import", "wireframe-rendering", "block-library-management", "landing-orchestrator", "ui-ux-pro-max"]
tags: ["wireframe", "ux", "stage-07a", "block-library", "prototype"]
---

# UX Composer — интерактивный wireframe из прототипа

## Что делает
Берёт утверждённый прототип лендинга и собирает интерактивную HTML-страницу с 2–3 вариантами вёрстки на каждый блок. Пользователь кликает radio-кнопками, выбирает лучший вариант и скачивает файл с выбором.

## Когда вызывать / в каком этапе
Этап **07a (UX Wireframe)**. Агент активируется командой `/landing-wireframe` после того, как в `07_ПРОТОТИП/source/` появился и прошёл валидацию файл `prototype.yaml`. Текущий статус проекта в `.landing-state.yaml` должен быть `07b_wireframe` — иначе агент останавливается.

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — структура блоков прототипа
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены
- `<project>/04_БРЕНД/brand-kit.md` — бренд-кит
- `block-library/catalog.yaml` — каталог доступных блоков
- 6 CSV-файлов из скилла `ui-ux-pro-max` (UX-паттерны, правила, палитры, шрифты, стили, web-interface)

**Выход:**
- `07a_WIREFRAME/wireframe.html` — интерактивная страница с вариантами блоков
- `07a_WIREFRAME/candidates.yaml` — список блоков-кандидатов от библиотеки
- `07a_WIREFRAME/selections.yaml` — файл выбора пользователя (создаётся пользователем после просмотра)

## Ключевые ограничения
- **Агент НИКОГДА не придумывает блоки самостоятельно.** Все варианты — исключительно из `block-library`. Если подходящего блока нет → флаг `needs_new_block: true` и предложение запустить `scaffold-block.py`.
- **HARD GATE:** пока `selections.yaml` не создан — этапы 07b и далее недоступны.
- Если скилл `ui-ux-pro-max` не установлен — агент останавливается с инструкцией по установке.

## Порядок работы
1. Проверить `.landing-state.yaml`, показать Mermaid-карту pipeline.
2. Создать TodoWrite со всеми оставшимися этапами.
3. Запустить `gate-check.sh` — при ошибке остановиться.
4. Провалидировать `prototype.yaml` скриптом.
5. Запустить `render-wireframe.py` — получить `wireframe.html`.
6. Проверить `candidates.yaml` на пустые блоки — сообщить если есть.
7. Попросить пользователя открыть HTML, выбрать варианты и положить `selections.yaml`.

## Связанные концепты
- [[landing-wireframe]] — slash-команда, которая вызывает этого агента
- [[landing-compose]] — следующий этап (07b), использует результат selections.yaml
- [[prototype-import]] — предшествующий этап, создаёт prototype.yaml
- [[wireframe-rendering]] — скилл с render-wireframe.py и шаблоном
- [[block-library-management]] — скилл для создания новых блоков через scaffold-block.py
- [[landing-orchestrator]] — оркестратор, который диспатчит этот этап в рамках /landing-go
- [[ui-ux-pro-max]] — внешний скилл с CSV-данными по UX-паттернам и стилям (обязательная зависимость)

## Источник
- `agents/ux-composer.md`