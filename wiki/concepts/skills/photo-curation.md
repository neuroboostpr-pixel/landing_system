---
slug: photo-curation
type: skill
name: "Обработка фотографий (Photo Curation)"
stage: "07c"
tags: [photos, pipeline, codex, ai, intake, classify, match, identity-safe]
triggers: [landing-photos]
inputs: [07c_PHOTOS/inbox, 05-dizayn-sistema, 07b-composed]
outputs: [07c_PHOTOS/processed, photo-preview.html, selections.yaml, 07b-composed]
gates: []
pre_reqs: [05-dizayn-sistema, 07b-composed]
related: [photo-curator, photo-classifier, photo-matcher, photo-preview-board, photo-stylist, landing-photos, landing-compose, landing-visuals]
sources: ["skills/photo-curation/SKILL.md"]
updated: 2026-06-19
---

# Обработка фотографий (Photo Curation)

## Что делает

Скилл реализует семиэтапный конвейер превращения сырых клиентских фотографий в оптимизированные изображения, встроенные в `composed.html`. На входе — фотки из папки `07c_PHOTOS/inbox/`, на выходе — подрезанные под слоты изображения в `07c_PHOTOS/processed/` и обновлённый макет. Codex CLI выполняет AI-классификацию, матчинг к слотам и при необходимости генерирует фото-заглушки. Вся обработка кешируется по хешу параметров, чтобы повторный запуск не тратил API-вызовы на уже обработанное.

## Когда вызывается

Запускается командой `/landing-photos` вручную после того, как утверждены этапы 05 (design-system) и 07b (composed.html со слотами `data-slot`). Оркестратор не диспатчит этот скилл автоматически — вызов только ручной.

## Вход → выход

**Вход:** клиентские фото в `07c_PHOTOS/inbox/` (по подпапкам-типам), утверждённый `05_design` с токенами, `07b_COMPOSED/composed.html` с разметкой слотов.

**Выход:** обработанные изображения в `07c_PHOTOS/processed/` + `manifest.json`; интерактивная доска `photo-board.html`; `photo-preview.html` для финального approve; обновлённый `composed.html` с реальными `<img>` вместо плейсхолдеров; `07c_PHOTOS/STATE.yaml` с прогрессом.

## Failure modes

- **HEIC-конвертация не проходит** — нет нужных системных утилит; `intake.py` падает на первом шаге.
- **Codex возвращает невалидный YAML** — `codex-classify.sh` / `codex-match.sh` не могут распарсить ответ, пайплайн прерывается.
- **Нет кандидатов для слота** — все фото отфильтрованы по тегам; слот уходит на `generate-fallback`, что требует явного `ai_approved_by_user: true` если в кадре люди.
- **`selections.yaml` не возвращён в папку** — пользователь скачал файл из `photo-board.html`, но забыл положить обратно; `compose re-render` не запускается, плейсхолдеры остаются.
- **Identity-check ложно блокирует фото** — perceptual hash расходится после ресайза; требуется ручная проверка `IDENTITY_SAFE.md` и сброс кеша через `--force-stage process`.

## Related

- [[photo-curator]] — агент-владелец этого скилла, ведёт этап 07c
- [[photo-classifier]] — AI-классификация фото через codex (шаг 2)
- [[photo-matcher]] — ранжирование кандидатов по слотам (шаг 3)
- [[photo-preview-board]] — интерактивная доска approve (шаг 4)
- [[photo-stylist]] — стилизация фото под brand-токены
- [[landing-photos]] — slash-команда, которая вызывает этот скилл
- [[landing-compose]] — создаёт composed.html со слотами, которые этот скилл заполняет
- [[landing-visuals]] — параллельный этап 07d для иконок и инфографики