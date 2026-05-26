---
slug: style-extractor
type: agent
name: "Style Extractor"
stage: "04"
tags: [brand, style, palette, fonts, icons, extraction]
triggers: [landing-brand]
inputs: [03_РЕФЕРЕНСЫ/index.yaml]
outputs: [04_БРЕНД/extracted/palette.yaml, 04_БРЕНД/extracted/fonts.yaml, 04_БРЕНД/extracted/icons.yaml, 04_БРЕНД/extracted/grid.md, 04_БРЕНД/extracted/motion.md]
gates: [all_5_outputs_present]
pre_reqs: [moodboard-composer]
related: [brand-architect, moodboard-composer, design-system-generator]
sources: ["agents/style-extractor.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# Style Extractor

## Что делает

Агент извлекает конкретную, готовую к использованию в коде систему стилей из утверждённых референсных изображений и URL-адресов. Он читает список одобренных референсов из `03_РЕФЕРЕНСЫ/index.yaml`, запускает серию Python-скриптов для анализа палитры, шрифтов и иконок, агрегирует результаты и записывает пять структурированных файлов в папку `04_БРЕНД/extracted/`. Именно эти файлы станут основой для работы агента `brand-architect` на том же этапе 04.

## Когда вызывается

Вызывается командой `/landing-brand` после того, как мудборд проекта утверждён пользователем (этап 03 закрыт). До запуска агент проверяет, что `current_stage == 04_brand` в `.landing-state.yaml`, и запускает `gate-check.sh` — если предшествующий этап не закрыт, выполнение блокируется.

## Вход → выход

**Вход:** `03_РЕФЕРЕНСЫ/index.yaml` со списком референсов со статусом `approved`; изображения из папки референсов; URL-адреса сайтов для анализа шрифтов.

**Выход:** пять файлов в `04_БРЕНД/extracted/`:
- `palette.yaml` — цветовая палитра
- `fonts.yaml` — гарнитуры и их параметры
- `icons.yaml` — подобранные иконки
- `grid.md` — сеточная система
- `motion.md` — параметры анимаций

## Чем закрывается этап (gates)

- `all_5_outputs_present` — все пять файлов (`palette.yaml`, `fonts.yaml`, `icons.yaml`, `grid.md`, `motion.md`) записаны в `04_БРЕНД/extracted/`; `brand-architect` не запускается, пока хоть один из них отсутствует

## Failure modes

- Референсы в `03_РЕФЕРЕНСЫ/index.yaml` не помечены как `approved` — агент не найдёт материал для анализа и сформирует пустые выходные файлы
- Python-скрипты (`extract-palette.py`, `identify-fonts.py`, `match-icons.py`) недоступны или упали — `orchestrate.py` не завершится, gate не будет закрыт
- URL-референсы недоступны по сети — блок идентификации шрифтов завершится с ошибкой; остальные файлы могут быть неполными
- `grid.md` и `motion.md` создаются как плейсхолдеры — если агент не перезаписал их реальными данными, дизайн-система получит пустые значения
- Этап 03 не закрыт через `gate-state.sh` — `enforce_stage_gate.py` заблокирует запись файлов ещё до их создания

## Related

- [[moodboard-composer]] — должен завершить этап 03 с утверждёнными референсами, иначе агенту нечего анализировать
- [[brand-architect]] — использует все 5 выходных файлов style-extractor'а как входные данные для сборки бренд-кита
- [[design-system-generator]] — на этапе 05 потребляет бренд-кит, основанный на результатах этого агента