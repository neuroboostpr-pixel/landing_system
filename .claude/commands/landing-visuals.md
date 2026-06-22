---
description: Stage 07e — генерация визуалов и DS asset-pack для composed.html. Требует approved 07c composed + mood asset plan.
---

# /landing-visuals

Генерирует визуалы для `composed.html` и проверяет DS asset-pack: промпты,
preview desktop/mobile, слои, Canvas/Canva-файл и правила обработки исходников.
Stage 07e.

## Использование

```
/landing-visuals [--project <slug>] [--type icons|infographics] [--force] [--slot <name>]
```

**Флаги:**
- `--project <slug>` — папка проекта (по умолчанию текущая).
- `--type icons` — только иконки (пропустить инфографику).
- `--type infographics` — только инфографика (пропустить иконки).
- `--force` — обойти кэш, перегенерить всё.
- `--slot <name>` — только один конкретный слот по имени.

## Гейты (что должно быть готово до запуска)

1. `<project>/.landing-state.yaml:stages.07c_composed.status == approved` — иначе:
   > Сначала утверди черновой макет (`07b_COMPOSED/composed.html`) — без него нельзя понять реальные визуальные слоты.

2. `<project>/07b_COMPOSED/composed.html` существует — иначе:
   > Сначала запусти `/landing-compose` (PR-A).

3. В выбранном mood есть DS asset-pack plan:
   ```bash
   python experimental/ds-engine-v2/engine/verify_ds_asset_pack.py --project <project> --mode plan
   ```
   Если не проходит — сгенерируй отчёт:
   ```bash
   python experimental/ds-engine-v2/engine/gen_assets_report.py grooming --project <project>
   ```

## Что происходит

Команда вызывает `visual-curator` агента, который:
1. Проверяет DS asset-pack plan по `docs/standards/ds-asset-pack.md`.
2. Сканирует `composed.html` на визуальные слоты (`slot-scanner.py`).
3. Для каждого слота — cache lookup по hash(hint+style+brand_color+niche). Если cache hit — copy без вызова генератора.
4. Если cache miss — диспатчит генерацию иконок/инфографики или использует mood asset-pack.
5. После всех генераций — re-render composed.html через `rerender-composed.py` (читает `07d_VISUALS/`, подставляет placeholders).

См. [`agents/visual-curator.md`](../agents/visual-curator.md) для деталей.

## Артефакты

В `<project>/07d_VISUALS/`:
- `_slots.yaml` — найденные слоты (auto)
- `icons/<slot-name>.png` — иконки (auto)
- `infographics/<slot-name>.png` — инфографика (auto)
- `.cache/<hash>.png` — кэш (auto, не удаляй, экономит API)
- `prompts.yaml` — лог промптов с attribution (auto)
- `STATE.yaml` — статусы этапов (auto)
- `.logs/` — codex prompts + responses (auto)

В `<project>/05_ДИЗАЙН-СИСТЕМА/moods/<mood>/`:
- `ASSETS-TODO.md` — список файлов для генерации с готовыми промптами
- `asset-pack.yaml` — машинный контракт ожидаемых файлов
- `assets/previews/preview-desktop.png` и `preview-mobile.png` — preview с реальным текстом
- `assets/layers/` — вектор/слои
- `assets/canvas/canvas-file.*` — Canvas/Canva-файл, экспорт или ссылка
- `assets/source-rules.md` — правила: исходники клиента не перерисовывать, только адаптировать под стиль лендинга

## После выполнения

`07b_COMPOSED/composed.html` перерендерится — placeholders заменятся на реальные
визуалы. Перед `07f_composed_final` дополнительно проходит ready-проверка:

```bash
python experimental/ds-engine-v2/engine/verify_ds_asset_pack.py --project <project> --mode ready
```

Если desktop/mobile preview, слои, Canvas/Canva-файл или обязательные ассеты
отсутствуют, финальный макет не закрывается.

## Запуск

Автоматически через `/landing-go` (рекомендуется) или вручную этой командой. Этап интегрирован в `landing-orchestrator` и `config/stage-gates.yaml`.

См. [spec](../docs/superpowers/specs/2026-05-13-visual-generation-design.md) и [plan](../docs/superpowers/plans/2026-05-13-visual-generation-plan.md).
