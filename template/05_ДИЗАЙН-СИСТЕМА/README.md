# 05_ДИЗАЙН-СИСТЕМА

## Что здесь будет

- `DESIGN.md` — единый источник истины токенов (цвета, шрифты, отступы)
- `tokens.json` — машиночитаемые токены
- `design-preview.html` — visual preview
- `moods/<mood>/recipes.yaml` — правила визуального характера
- `moods/<mood>/assets-manifest.yaml` — список нужных визуальных ассетов
- `moods/<mood>/ASSETS-TODO.md` — готовые промпты и список файлов для генерации
- `moods/<mood>/asset-pack.yaml` — машинный контракт ассетов для проверки
- `moods/<mood>/assets/` — готовые preview, слои, Canvas/Canva-файл, SVG/PNG/JPG

## Кто создаёт

`design-system-generator` агент на основе `04_БРЕНД/brand-kit.md`.

DS asset-pack создаётся на визуальном этапе:

```bash
python experimental/ds-engine-v2/engine/gen_assets_report.py grooming --project <project>
```

Проверка плана:

```bash
python experimental/ds-engine-v2/engine/verify_ds_asset_pack.py --project <project> --mode plan
```

Финальная проверка готовых файлов:

```bash
python experimental/ds-engine-v2/engine/verify_ds_asset_pack.py --project <project> --mode ready
```

## Этап

05_design + 07e_visuals/07f_composed_final.
