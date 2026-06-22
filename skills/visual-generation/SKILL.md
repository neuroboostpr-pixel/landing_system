---
name: visual-generation
description: Stage 07e — generate visuals and validate DS asset-pack for composed.html slots. Parameterized by tokens.json + niche. Hash-cache. Owned by visual-curator agent.
---

# visual-generation

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill visual-generation --stage 07e
```

Конвейер генерации визуалов (иконки, инфографика, mood asset-pack) для лендинга.
Запускается командой `/landing-visuals` после approved `07c_composed`.

Перед генерацией обязателен DS asset-pack plan:

```bash
python experimental/ds-engine-v2/engine/verify_ds_asset_pack.py --project <project> --mode plan
```

Если plan отсутствует, сначала создать отчёт и структуру:

```bash
python experimental/ds-engine-v2/engine/gen_assets_report.py grooming --project <project>
```

## Этапы

1. **asset-plan** — проверить `docs/standards/ds-asset-pack.md`: recipes, manifest, ASSETS-TODO, asset-pack.
2. **scan** — `scripts/slot-scanner.py` парсит `composed.html`, выдаёт списки icon/infographic слотов в `07d_VISUALS/_slots.yaml`.
3. **generate** — `scripts/codex-generate-icon.sh` / `-infographic.sh` или mood asset-pack для каждого слота. Перед вызовом генератора — кэш-lookup по hash(hint+style+brand_color+niche).
4. **inject** — `inject-content.py` (PR-A/PR-B расширенный) подставляет PNG/SVG в `composed.html` на месте placeholders.
5. **ready-gate before 07f** — перед финальным composed проверить:
   ```bash
   python experimental/ds-engine-v2/engine/verify_ds_asset_pack.py --project <project> --mode ready
   ```

## Identity-safe

Применяется всегда, когда asset-pack содержит людей, товары, технику, помещения,
объекты клиента или любые реальные исходники. Исходник нельзя перерисовывать как
новую сущность: разрешены кадрирование, маска, удаление фона, свет/контраст,
подготовка mobile-версии и композиционная раскладка. AI-сцены допустимы как фон
или окружение, но не как замена реального человека/объекта без явного approval.

## Cache

`07d_VISUALS/.cache/<hash>.png` — переиспользование сгенерированных изображений между прогонами. `FORCE=1` обходит кэш.

## Prompt-picker waterfall

- **icons:** icons.csv keyword match → generic template (skip OpenDesign — они не под иконки)
- **infographics:** OpenDesign 90 JSON tag/category match → generic template

## State management

`07d_VISUALS/STATE.yaml` отслеживает scan / generate / inject. Перезапуск продолжает с прерванного.

## Стандарт пайплайна картинок (D1, обязательный)

Каждое визуальное место обрабатывается по
[`docs/standards/image-pipeline.md`](../docs/standards/image-pipeline.md):
анализ места → цель → спецификация → референсы (число = составу композиции) →
генерация на вырезаемом фоне → rembg → вставка; адаптация под палитру —
полупрозрачным оверлеем акцента, не отдельной картинкой на каждый цвет.

## DS asset-pack стандарт

См. [`docs/standards/ds-asset-pack.md`](../docs/standards/ds-asset-pack.md).
Финальный визуальный пакет должен содержать preview desktop/mobile с реальным
текстом прототипа, слои/вектор, Canvas/Canva-файл или экспорт, промпты и правила
использования исходников.
