# 07d_VISUALS — иконки и инфографика

Это папка для автоматически сгенерённых визуальных элементов лендинга: иконки и
инфографика. Полный mood asset-pack для верстки лежит в:

`05_ДИЗАЙН-СИСТЕМА/moods/<mood>/`

## Что произойдёт когда запустишь /landing-visuals

1. Система проверит DS asset-pack plan: `recipes.yaml`, `assets-manifest.yaml`, `ASSETS-TODO.md`, `asset-pack.yaml`.
2. Система просканирует `07b_COMPOSED/composed.html`, найдёт визуальные слоты.
3. Для каждого слота — сгенерит или возьмёт из asset-pack PNG/SVG под брендинг проекта.
4. PNG/SVG сохранится в `icons/`, `infographics/` или mood `assets/`.
5. `composed.html` перерендерится — placeholders `[SLOT: ...]` заменятся на реальные файлы.

## Кэш

`07d_VISUALS/.cache/<hash>.png` — кэшированные генерации по hash(hint + style + brand_color + niche).
- Перезапуск `/landing-visuals` НЕ зовёт codex второй раз для одних и тех же слотов — берёт из кэша.
- Чтобы перегенерить — `/landing-visuals --force`.
- Один слот — `/landing-visuals --slot feature-1-icon`.

## Артефакты

- `_slots.yaml` — найденные слоты в composed.html (auto)
- `icons/` — сгенерённые PNG иконки
- `infographics/` — сгенерённые PNG инфографики
- `.cache/` — кэш по hash (НЕ удаляй — экономит codex API)
- `prompts.yaml` — какой промпт → какой PNG (для аудита и attribution)
- `STATE.yaml` — статусы этапов
- `.logs/` — codex prompts + responses

## Mood asset-pack

В `05_ДИЗАЙН-СИСТЕМА/moods/<mood>/` должны быть:

- `ASSETS-TODO.md` — список файлов для генерации с готовыми промптами
- `asset-pack.yaml` — машинный контракт
- `assets/previews/preview-desktop.png`
- `assets/previews/preview-mobile.png`
- `assets/layers/layers.svg` или `layers.json`
- `assets/canvas/canvas-file.*`
- `assets/prompts.md`
- `assets/source-rules.md`

Если preview с реальным текстом плохо читается на desktop или mobile, пакет не готов.

## Что НЕ делать

- Не редактируй PNG в `icons/` или `infographics/` вручную — `--force` их перезапишет. Лучше отредактируй промпт-шаблон в `skills/visual-generation/templates/`.
- Не коммить `.cache/` в git — это локальный кеш.

## Перезапуск

```
/landing-visuals --force                 # перегенерить всё с нуля
/landing-visuals --type icons            # только иконки
/landing-visuals --slot feature-3-icon   # один конкретный слот
```

См. полную документацию: [`/landing-visuals`](../../commands/landing-visuals.md).
