# DS Asset Pack Standard

Применяется к Stage 07e/07f, когда DS-Engine v2 или mood-рецепты готовят визуалы
для premium landing. Цель — чтобы верстка получала не одну картинку, а полный
управляемый набор материалов.

## Обязательный пакет

В выбранном mood:

`05_ДИЗАЙН-СИСТЕМА/moods/<mood>/`

должны быть:

- `recipes.yaml` — правила визуального характера mood.
- `assets-manifest.yaml` — список всех визуальных форм, снятых с референса или явно помеченных как `под-нишу`.
- `ASSETS-TODO.md` — человекочитаемый список файлов и готовых промптов.
- `asset-pack.yaml` — машинный контракт ожидаемых файлов.
- `assets/previews/preview-desktop.png` — preview блока/лендинга с реальным текстом прототипа.
- `assets/previews/preview-mobile.png` — mobile-preview с тем же текстом.
- `assets/layers/layers.svg` или `layers.json` — слои/вектор для верстки.
- `assets/canvas/canvas-file.*` — Canvas/Canva-файл, экспорт или ссылка на него.
- `assets/prompts.md` — промпты генерации.
- `assets/source-rules.md` — правила использования клиентских исходников.

## Жёсткие правила

1. Клиентские фото, люди, товары, техника и реальные объекты не перерисовываются как новые сущности. Их можно кадрировать, вырезать, чистить фон, улучшать свет и адаптировать под стиль.
2. Для каждого ключевого визуального блока нужен desktop и mobile preview с реальным текстом из прототипа. Если текст плохо читается, пакет не готов.
3. SVG-ассеты, которые перекрашиваются в верстке, не должны иметь вшитый бренд-цвет. Цвет задаётся CSS-токенами.
4. Каждый ассет в `to_generate` обязан иметь готовый промпт, который можно копировать в генератор без дописывания.
5. Обязательные не-CSS ассеты из `assets-manifest.yaml` должны иметь реальные файлы в `assets/`.

## Проверки

Plan-gate:

```bash
python experimental/ds-engine-v2/engine/verify_ds_asset_pack.py --project <project> --mode plan
```

Ready-gate:

```bash
python experimental/ds-engine-v2/engine/verify_ds_asset_pack.py --project <project> --mode ready
```

`plan` блокирует хаос в ТЗ на генерацию. `ready` блокирует финальную сборку без
реальных материалов.
