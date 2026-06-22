# moods

Здесь лежат mood-рецепты и asset-pack для визуального стиля лендинга.

Минимальная структура выбранного mood:

```text
<mood>/
  recipes.yaml
  assets-manifest.yaml
  ASSETS-TODO.md
  asset-pack.yaml
  assets/
    previews/
    layers/
    canvas/
    decor/
    icons/
    figures/
    bg/
    brand/
```

`ASSETS-TODO.md` и `asset-pack.yaml` можно создать командой:

```bash
python experimental/ds-engine-v2/engine/gen_assets_report.py grooming --project <project>
```
