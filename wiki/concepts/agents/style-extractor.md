---
type: agent
name: style-extractor
sources: ["agents/style-extractor.md"]
updated: 2026-05-25
triggers: []
stage: "04_brand"
uses: ["landing-orchestrator", "brand-architect", "landing-brand", "landing-references"]
tags: ["stage-04", "brand", "design-tokens", "style", "extraction"]
---

# Style Extractor — агент извлечения стилей из референсов

## Что делает

Анализирует утверждённые референс-изображения и URL-ссылки, извлекает из них палитру цветов, шрифты и иконки, и формирует 5 структурированных файлов, готовых для передачи в дизайн-систему.

## Когда вызывать / в каком этапе

Запускается на **этапе 04_brand** — после того как мудборд утверждён пользователем (этап 03 закрыт). Агент должен отработать **до запуска brand-architect**: его 5 выходных файлов — обязательное предусловие для продолжения этапа. Активируется командой `/landing-brand` через `landing-orchestrator`.

Перед любым действием агент обязан:
- убедиться что `current_stage == 04_brand` в `.landing-state.yaml`;
- показать Mermaid-карту pipeline;
- пройти `gate-check.sh --stage 04_brand`;
- создать TodoWrite со всеми оставшимися этапами.

## Что на вход / на выход

**Вход:**
- `03_РЕФЕРЕНСЫ/index.yaml` — список утверждённых референсов (`status: approved`)
- изображения и URL из утверждённого мудборда

**Выход** (все 5 файлов в `04_БРЕНД/extracted/`):
- `palette.yaml` — цветовая палитра (HEX, роли цветов)
- `fonts.yaml` — шрифтовая пара (семейство, насыщенность, размеры)
- `icons.yaml` — подобранный icon-сет
- `grid.md` — сетка и отступы
- `motion.md` — принципы анимации и переходов

**HARD GATE:** все 5 файлов обязаны присутствовать — иначе `brand-architect` не стартует.

## Как работает (инструменты)

Агент последовательно вызывает Python-скрипты из `skills/style-decomposition/scripts/`:
1. `extract-palette.py` — для каждого изображения-референса
2. `identify-fonts.py` — для каждого URL-референса
3. `match-icons.py` — подбор иконок под стандартный список потребностей
4. `orchestrate.py` — агрегация всех результатов в единый набор файлов
5. Если `grid.md` / `motion.md` отсутствуют — создаёт заглушки

## Связанные концепты

- [[landing-references]] — поставляет утверждённые референсы (`index.yaml`), которые агент читает на входе
- [[brand-architect]] — следующий агент в цепочке, принимает 5 выходных файлов
- [[landing-brand]] — слеш-команда/скилл, которая оркестрирует весь этап 04
- [[landing-orchestrator]] — диспатчит style-extractor как часть pipeline

## Источник

- `agents/style-extractor.md`