---
type: stage
name: pr-i-a-photo-pipeline-plan
sources: ["docs/superpowers/plans/2026-05-15-pr-i-a-photo-pipeline-plan.md"]
updated: 2026-05-15
triggers: []
stage: "07c"
uses:
  - photo-curator
  - photo-curation
  - visual-generation
  - stage-gates
  - landing-photos
  - 07c-photos
  - 07b-composed
tags: ["photo", "codex", "pipeline", "identity-safe", "hard-gate", "pr-i-a"]
---

# PR-I.a — План реализации Photo Pipeline

## Что делает

Описывает полный план реализации обязательного конвейера обработки клиентских фотографий: каждое фото до попадания в `composed.html` проходит через codex, проверку identity-safe и точный resize под размеры слота. Нереализованные плейсхолдеры теперь блокируют закрытие этапов 07c и 07f через HARD GATE.

## Когда вызывать / в каком этапе

Применяется в **этапе 07c** (`/landing-photos`) и фиксируется в **07f** (composed final). Реализация состоит из 8 задач:

1. **Task 1** — `codex-process-photo.sh`: bash-обёртка над codex CLI, аналог `codex-generate-icon.sh` из visual-generation. Принимает фото + параметры бренда, возвращает обработанное фото с сохранённым объектом (машина / лицо / товар не перерисовываются).
2. **Task 2** — `photo-pipeline.py`: главный Python-конвейер: validate ratio → codex → identity check → crop → resize → cache (hash) → save + `manifest.json`.
3. **Task 3** — `identity-check.py`: сравнение оригинала и обработанного через perceptual hash (`imagehash.phash`). Если Hamming distance > threshold → pipeline отказывается от codex-результата и берёт оригинал.
4. **Task 4–5** — `verify-photo-pipeline.sh` + Python-хелпер: hard\_check, который ловит SVG-плейсхолдеры и фото вне `processed/`. Подключается в `config/stage-gates.yaml` на 07c и 07f.
5. **Task 6** — 4 bats-теста: placeholder-детекция, crop ratio, cache-key детерминизм, interactive smoke.
6. **Task 7** — обновление промптов `photo-curator.md`, `landing-photos.md`, `SKILL.md`.
7. **Task 8** — регрессия всех тестов + отметка в `docs/ПЛАН-ДОРАБОТОК.md`.

## Что на вход / на выход

**Вход:**
- Клиентские фото в `07c_PHOTOS/inbox/`
- `07c_PHOTOS/selections.yaml` (от drag-drop UI или интерактивного режима)
- `04_БРЕНД/tokens.json` — `primary` цвет бренда
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — niche и region

**Выход:**
- `07c_PHOTOS/processed/<slot>.jpg` — обработанное и ресайзнутое фото
- `07c_PHOTOS/processed/manifest.json` — статус всех слотов
- `07c_PHOTOS/.cache/<hash>.jpg` — кэш для повторных прогонов
- Обновлённый `composed.html` — `<img src="processed/...">` вместо SVG-плейсхолдеров

**Что НЕ входит в PR-I.a:**
- Playwright Visual QA (→ PR-I.b)
- Генерация фото с нуля через codex (→ PR-I.c)
- Interactive-slot-fill UI (→ пропущен как `skip` в тестах, может войти в итерацию 2)

## Связанные концепты

- [[photo-curator]] — агент-оркестратор этапа 07c, усиливается обязательными правилами codex
- [[photo-curation]] — скилл, в котором живут все скрипты pipeline
- [[visual-generation]] — паттерн-референс (codex-generate-icon.sh → codex-process-photo.sh)
- [[stage-gates]] — HARD GATE 07c/07f подключает `verify-photo-pipeline.sh`
- [[landing-photos]] — команда, запускающая pipeline для пользователя
- [[07c-photos]] — этап, в котором план исполняется
- [[07b-composed]] — артефакт, который проверяется на плейсхолдеры

## Источник

- `docs/superpowers/plans/2026-05-15-pr-i-a-photo-pipeline-plan.md`