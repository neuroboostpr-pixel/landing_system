---
type: stage
name: pr-i-a-photo-pipeline
sources: ["docs/superpowers/specs/2026-05-15-pr-i-a-photo-pipeline-design.md"]
updated: 2026-05-15
triggers: []
stage: "07c"
uses:
  - photo-curator
  - photo-curation
  - visual-generation
  - landing-photos
  - stage-gates
  - block-composer
tags: [photos, codex, identity-safe, pipeline, 07c]
---

# PR-I.a — Photo Pipeline (размер + codex + identity)

## Что делает

Устраняет три главных проблемы при работе с фотографиями: агент больше не оставляет SVG-заглушки вместо реальных фото, обязательно прогоняет каждую фотку через codex в соответствии с бренд-параметрами, и подгоняет результат под точный размер и пропорцию слота.

## Когда вызывать / в каком этапе

Этап **07c** (photo-curation). Активируется командой `/landing-photos --interactive` или автоматически оркестратором при входе на этап 07c_photos. HARD GATE на этапах 07c_composed и 07f_composed_final — закрытие блокируется скриптом `verify-photo-pipeline.sh`, пока все слоты не заполнены реальными обработанными jpg.

## Что на вход / на выход

**Вход:**
- Фотографии клиента в `07c_PHOTOS/inbox/`
- `tokens.json` с цветами бренда (этап 05)
- `market-profile.md` с нишей, регионом, mood (этап 01a)
- `composed.html` с photo-слотами (этап 07b)

**Выход:**
- `07c_PHOTOS/processed/<slot-name>.jpg` — обработанные фото десктоп
- `07c_PHOTOS/processed/<slot-name>.mobile.jpg` — мобильный вариант
- `07c_PHOTOS/processed/manifest.json` — метаданные каждого обработанного фото
- `07c_PHOTOS/.cache/<sha256>.jpg` — hash-кэш для повторных прогонов
- Обновлённый `composed.html` — placeholders заменены на `<img>` с реальными путями

**Новые файлы (скрипты/шаблоны):**
- `skills/photo-curation/scripts/codex-process-photo.sh`
- `skills/photo-curation/scripts/photo-pipeline.py`
- `skills/photo-curation/scripts/interactive-slot-fill.py`
- `skills/photo-curation/scripts/identity-check.py`
- `scripts/verify-photo-pipeline.sh`
- `skills/photo-curation/templates/codex-photo-prompt.md`

**Тесты:** 4 bats-файла в `tests/pr-i-a/`.

**Изменяемые файлы:**
- `config/stage-gates.yaml` — новый hard_check `photo_pipeline_valid`
- `skills/photo-curation/SKILL.md`
- `commands/landing-photos.md` (новый флаг `--interactive`)
- `agents/photo-curator.md`

## Ключевые правила pipeline

1. **9 шагов на одно фото:** intake → classify → slot-match → validate-ratio → codex-post → identity-check → resize → cache → save.
2. **Codex-промпт** содержит цвет бренда, mood и регион из `market-profile.md`; объект (лицо/машина/товар) обязан сохраниться.
3. **Identity-safe:** для слотов `portrait/team/car/product` — perceptual hash сравнивает оригинал и обработку; расхождение > 10 (Hamming) → revert + warning.
4. **Кэш по ключу:** `hash(orig_photo + brand_primary + niche + region + slot_ratio)` — повторный прогон не тратит codex API.
5. **Ratio-mismatch:** расхождение ≤ 5% → auto crop_center; > 5% → флаг пользователю.

## Связанные концепты

- [[photo-curator]] — агент-оркестратор этапа 07c, получает усиленный промпт об обязательном codex шаге
- [[photo-curation]] — скилл с IDENTITY_SAFE правилами, переиспользуется без изменений
- [[visual-generation]] — источник паттерна codex-обёртки с hash-кэшем (PR-C)
- [[landing-photos]] — команда, получает новый флаг `--interactive`
- [[stage-gates]] — принимает новый hard_check `photo_pipeline_valid` для 07c и 07f
- [[block-composer]] — создаёт composed.html с photo-слотами, куда pipeline подставляет реальные img

## Источник

- `docs/superpowers/specs/2026-05-15-pr-i-a-photo-pipeline-design.md`