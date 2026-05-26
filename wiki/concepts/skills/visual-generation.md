---
type: skill
name: visual-generation
sources: ["skills/visual-generation/SKILL.md"]
updated: 2026-05-26
triggers: ["/landing-visuals", "сгенерировать иконки", "сгенерировать инфографику", "визуалы для лендинга"]
stage: "07d"
uses: ["landing-visuals", "landing-compose", "landing-design", "landing-orchestrator"]
tags: ["icons", "infographics", "codex", "image-gen", "stage-07d", "PR-C"]
---

# visual-generation — Генерация иконок и инфографики

## Что делает
Автоматически создаёт иконки и инфографику для всех визуальных слотов лендинга: сканирует `composed.html`, генерирует PNG через codex image_gen с учётом бренда и ниши, подставляет результат обратно в HTML вместо плейсхолдеров.

## Когда вызывать / в каком этапе
Этап **07d** (PR-C). Запускается командой `/landing-visuals` после:
- утверждённого этапа 05 (`design-system` с `tokens.json`),
- существующего `07b_COMPOSED/composed.html` (PR-A).

Можно запустить частично через флаги:
- `--type icons` или `--type infographics` — только один вид визуалов,
- `--force` — игнорировать кэш,
- `--slot <name>` — обработать один конкретный слот.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — собранный HTML с плейсхолдерами `[SLOT: feature-1-icon]` и аналогичными,
- `tokens.json` — цвета и дизайн-токены бренда,
- `market-profile.md` — ниша проекта (влияет на стиль генерации).

**Выход:**
- `07d_VISUALS/_slots.yaml` — список всех найденных слотов (результат сканирования),
- `07d_VISUALS/<slot-name>.png` — сгенерированные PNG-файлы,
- `07d_VISUALS/.cache/<hash>.png` — кэш по hash(hint + style + brand_color + niche),
- `07d_VISUALS/STATE.yaml` — статус прогона (scan / generate / inject),
- обновлённый `composed.html` — плейсхолдеры заменены на `<img class="lp-icon">`.

**Три шага конвейера:**
1. `slot-scanner.py` — парсинг слотов из HTML,
2. `codex-generate-icon.sh` / `codex-generate-infographic.sh` — генерация с кэш-проверкой,
3. `inject-content.py` — подстановка PNG в HTML.

**Prompt waterfall:**
- Иконки: совпадение по `icons.csv` → generic template,
- Инфографика: совпадение по тегам/категориям OpenDesign JSON → generic template.

**Identity-safe не применяется** — в иконках и чартах нет людей, ограничения на лица не действуют.

## Связанные концепты
- [[landing-visuals]] — slash-команда, которая вызывает этот скилл
- [[landing-compose]] — поставляет `composed.html` со слотами на вход
- [[landing-design]] — поставляет `tokens.json` с брендовыми цветами
- [[landing-orchestrator]] — диспатчит этап 07d в pipeline PR-D
- [[landing-photos]] — параллельный этап 07c (фото), выполняется одновременно с 07d

## Источник
- `skills/visual-generation/SKILL.md`