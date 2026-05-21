---
type: agent
name: style-extractor
sources: ["agents/style-extractor.md"]
updated: 2026-05-20
triggers: []
stage: "04"
uses: ["moodboard-composer", "brand-architect", "references-curator", "style-decomposition", "landing-brand"]
tags: ["brand", "palette", "fonts", "icons", "stage-04"]
---

# style-extractor — извлечение стилей из референсов

## Что делает
Анализирует утверждённые референсы (картинки и URL-адреса) и вытаскивает из них готовую к использованию систему стилей: цветовую палитру, шрифты, иконки, сетку и правила анимации. Результат — пять YAML/MD-файлов, с которыми дальше работает [[brand-architect]].

## Когда вызывать / в каком этапе
Запускается на **этапе 04** (`04_brand`) — после того, как мудборд утверждён ([[moodboard-composer]] завершил работу и `03_РЕФЕРЕНСЫ/index.yaml` содержит записи со статусом `approved`). Вызывается командой `/landing-brand` или напрямую агентом [[landing-orchestrator]].

Перед стартом агент проверяет:
- `.landing-state.yaml` → `current_stage == 04_brand`
- `bash scripts/gate-check.sh --stage 04_brand` → exit 0
- Если предшественники не закрыты — STOP (hook `enforce_stage_gate.py` физически блокирует запись файлов).

## Что на вход / на выход

**Вход:**
- `03_РЕФЕРЕНСЫ/index.yaml` — список утверждённых референсов (status: `approved`)
- Файлы изображений и URL из папки `03_РЕФЕРЕНСЫ/`

**Выход (5 файлов в `04_БРЕНД/extracted/`):**
| Файл | Содержимое |
|---|---|
| `palette.yaml` | Цветовая палитра с hex-кодами |
| `fonts.yaml` | Шрифтовые пары и размеры |
| `icons.yaml` | Подобранный набор иконок |
| `grid.md` | Сеточная система (колонки, отступы) |
| `motion.md` | Принципы анимации |

**HARD GATE:** все 5 файлов обязаны существовать, иначе [[brand-architect]] не запустится.

## Как работает внутри
1. Читает `index.yaml`, отбирает только `approved`-референсы.
2. Для картинок запускает `skills/style-decomposition/scripts/extract-palette.py`.
3. Для URL запускает `scripts/identify-fonts.py`.
4. Прогоняет `scripts/match-icons.py` по стандартному списку потребностей.
5. Агрегирует всё через `scripts/orchestrate.py`.
6. Дописывает `grid.md` и `motion.md` если их ещё нет.

## Связанные концепты
- [[moodboard-composer]] — предшественник: формирует утверждённые референсы
- [[brand-architect]] — преемник: синтезирует `brand-kit.md` из 5 выходных файлов
- [[references-curator]] — управляет `index.yaml` со статусами референсов
- [[style-decomposition]] — скилл с Python-скриптами, которые вызывает агент
- [[landing-brand]] — команда, инициирующая этот этап

## Источник
- `agents/style-extractor.md`