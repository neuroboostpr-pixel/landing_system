---
slug: gen-images
type: skill
name: "Генерация изображений (иконки и фото)"
stage: "07c"
tags: [icons, svg, photos, cutout, image-generation, codex, vtracer, rembg]
triggers: [landing-compose, landing-visuals, landing-photos]
inputs:
  - 07b_COMPOSED/build-spec.md
  - 07b_COMPOSED/composed.html
  - 07c_PHOTOS/inbox
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - market-profile.md
outputs:
  - 07d_VISUALS/icons/*.svg
  - 07c_PHOTOS/processed/*.png
gates: []
pre_reqs: [07b-composed, 05-dizayn-sistema, 07-prototip]
related:
  - 07c-photos
  - 07d-visuals
  - landing-visuals
  - landing-photos
  - landing-compose
  - icon-generator
  - visual-generation
  - rembg
sources: ["skills/gen-images/SKILL.md"]
updated: 2026-06-22
confidence: {triggers: low, stage: low}
---

# Генерация изображений (иконки и фото)

## Что делает

Скилл закрывает все визуальные слоты макета `composed.html` до финализации этапа: генерирует иконки в виде inline-SVG и вырезает клиентские фото из фона. Работает в двух параллельных пайплайнах: **A — иконки** (Lucide-готовые или codex image_gen → нарезка → vtracer SVG) и **B — фото** (rembg вырез + feather-размытие края + autocrop). Все иконки красятся токенами дизайн-системы через `currentColor` / `var(--lp-accent)` — сама генерация ч/б. Макет с пустыми placeholder-слотами считается незакрытым этапом.

## Когда вызывается

Вызывается из `gen-html` **до** закрытия макета, если выполнено хотя бы одно из пяти детерминированных условий:

- **T1** — в `07c_PHOTOS/inbox/` есть фото и в макете есть роль `figure-cutout` / `avatar` / `case-card`.
- **T2** — в прототипе или HTML есть иконо-роли (`feature`, `cta-note`, `trust-item`, `process-step`) без `<svg>`.
- **T3** — роль `section-bg` требует фонового изображения.
- **T4** — нужны SVG-фигуры-декор (`diamond-decor`, волны, блобы).
- **T5** — гейт `verify_html_vs_ds.py` нашёл пустой placeholder (принудительный).

Также вызывается вручную: «сгенерируй иконки для блока X».

## Вход → выход

**Вход:** `build-spec.md` / `composed.html` (слоты иконок и роли), `07c_PHOTOS/inbox/*` (клиентские фото), `tokens.json` и `market-profile.md` (бренд-контекст и ниша).

**Выход:** `07d_VISUALS/icons/*.svg` + inline-SVG подставлены в слоты `composed.html`; `07c_PHOTOS/processed/*.png` (RGBA, с feathered-краем) готовы для вёрстки.

## Failure modes

- **codex кладёт PNG не туда** — файл уходит в `~/.codex/generated_images/<session>/`, а не в указанную папку; нужно брать путь из stdout или через `find ... -newermt @<метка старта>`, иначе подберётся старая генерация.
- **Иконки по стилю, не по смыслу** — нарушение правила «иконка по концепции текста»; слайсер назначает по порядку, если промт собран из неверных концепций — соответствие сломано.
- **Пропуск feather** — rembg даёт резкий край с каймой фона; без эрозии+порог+blur вырез выглядит «вырезанным» и не вписывается в макет.
- **Иконки не токенизированы** — если SVG содержит хардкод цвета вместо `currentColor`, при смене мода иконка не перекрасится.
- **Несовпадение `--expect N`** — если слайсер получил не то количество bbox-ов, что концепций, manifest.json выдаёт неверное сопоставление.

## Related

- [[07c-photos]] — этап фото-пайплайна, куда уходят processed-файлы
- [[07d-visuals]] — этап генерации иконок/инфографики
- [[landing-visuals]] — slash-команда, запускающая этот скилл вручную
- [[landing-photos]] — slash-команда photo-пайплайна
- [[landing-compose]] — команда, вызывающая gen-images внутри gen-html
- [[icon-generator]] — роль агента-генератора иконок
- [[visual-generation]] — концепт пайплайна визуальной генерации
- [[rembg]] — инструмент вырезки фона (пайплайн B)