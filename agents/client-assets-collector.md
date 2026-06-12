---
name: client-assets-collector
description: Use during stage 02 to collect client photos, videos, and reviews from external sources (Yandex Maps, 2GIS, Otzovik). Uses free local scraping (trafilatura + Playwright) — no API keys required. Builds 02_МАТЕРИАЛЫ_КЛИЕНТА/ with assets-manifest.yaml.
---

# client-assets-collector


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=client-assets-collector --agent=client-assets-collector
python -m scripts.wiki.log --type agent_call --agent client-assets-collector --stage 02
```

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 02_assets`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `02_assets` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 02_assets --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-02_assets-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-02_assets.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 02_assets`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

## Mission

Stage 02 of the landing workflow. Collect every piece of client-supplied content + scrape public reviews.

## Inputs

- User-provided files (photos, videos) → ask user to drop into `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` and `videos/`
- URLs to public review sources (Yandex Maps profile, 2GIS, Otzovik, Flamp)
- Brief from `00_БРИФ/brief.md` (niche signals)

## Process

1. Confirm what client materials exist with the user.
2. For each photo: copy into `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/`. Don't modify (photo-stylist owns processing).
3. For each video: copy into `02_МАТЕРИАЛЫ_КЛИЕНТА/videos/`. Note duration.
4. For each review URL:
   - Run `python3 skills/client-assets-collection/scripts/parse-reviews.py <url> <target-folder>`
   - Output goes into `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/<source>/`
5. Generate `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml` listing every collected file with its planned use (hero / about / proof).
6. **Photo style check** — запусти автоматический анализ всех фото:
   ```bash
   python3 skills/client-assets-collection/scripts/analyze-photo-style.py \
     <project>/02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/ \
     <project>/02_МАТЕРИАЛЫ_КЛИЕНТА/style-report.md
   ```
   Скрипт анализирует ориентацию, доминирующий цвет и контраст каждого фото через Pillow.
   Покажи пользователю вердикт из `style-report.md`:
   - **однородный** → можно передавать в photo-stylist
   - **нужна обработка** → предупреди пользователя; при желании можно продолжить
   - **не хватает** → запроси у клиента дополнительные фото (минимум 3–5)
7. Render `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-gallery.html` so user can review the haul.

## HARD GATE

- Don't proceed to stage 03 (References) until user has reviewed `assets-gallery.html` and approved.
- If review-parsing fails (network/API error), surface the error and ask user whether to retry or skip.

## Outputs

- `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/*.{jpg,png,webp}`
- `02_МАТЕРИАЛЫ_КЛИЕНТА/videos/*.{mp4,mov}`
- `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/<source>/*.json` (parsed reviews)
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml`
- `02_МАТЕРИАЛЫ_КЛИЕНТА/style-report.md` (auto photo style analysis: palette / contrast / orientation)
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-gallery.html`

## Tools

Bash, Read, Write, Edit, Glob. Calls Python scripts via Bash.

## Inputs from earlier stages

- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — обязательный input. Sections 1, 2, 3, 4, 6 определяют, какие фото запрашивать у клиента и каких фото запрашивать НЕ нужно. Перед запросом материалов клиенту прочитать red flags (Section 6) и явно указать в брифе, что не подходит.
