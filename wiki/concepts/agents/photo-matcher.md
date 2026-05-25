---
type: agent
name: photo-matcher
sources: ["agents/photo-matcher.md"]
updated: 2026-05-25
triggers: []
stage: "07c"
uses:
  - photo-curator
  - photo-curation
tags: [photos, matching, codex, stage-07c]
---

# Photo Matcher — ранжирование фото по слотам

## Что делает
Подбирает топ-3 фотографии из каталога для каждого слота-заглушки в wireframe. Помечает слоты, где фото клиента отсутствуют (`ai_fallback_needed`), и ставит флаг обязательного согласия пользователя для личных фото (персоны, эксперты, команда).

## Когда вызывать / в каком этапе
Вспомогательный агент этапа **07c (Фото)**. Вызывается **только** родительским агентом `photo-curator` — не напрямую пользователем. Stage Execution Protocol отслеживает родитель, не этот агент.

## Что на вход / на выход

**Вход:**
- `<project_dir>` — путь к папке проекта
- `07_ПРОТОТИП/prototype.yaml` — полный список слотов прототипа
- `07a_WIREFRAME/selections.yaml` — выбранные пользователем варианты wireframe (только `type: photo` слоты)
- `07c_PHOTOS/catalog.yaml` — каталог загруженных фотографий

**Выход:**
- `07c_PHOTOS/selections.draft.yaml` — черновик с топ-3 кандидатами на каждый слот, флагом `ai_fallback_needed` и флагом `required_user_approval` для identity-safe слотов

## Как работает

1. Строит `_slots-input.yaml` из прототипа, фильтруя только активные photo-слоты по `wireframe/selections.yaml`.
2. Запускает codex через `skills/photo-curation/scripts/codex-match.sh` с каталогом и списком слотов.
3. Проверяет, что ответ codex — валидный YAML со структурой `slots: [...]`. При ошибке повторяет дважды; если снова невалидно — прерывает работу и просит пользователя проверить лог codex.
4. Пустой список кандидатов для слота → `ai_fallback_needed: true` (штатная ситуация).
5. Слоты типа testimonial / expert / team → `required_user_approval: true` согласно политике `IDENTITY_SAFE.md`. Эту метку enforс-ят downstream: `selections-validator.py` и UI `photo-board.html`.

## Связанные концепты
- [[photo-curator]] — родительский агент, который диспатчит photo-matcher
- [[photo-curation]] — скилл с codex-match.sh и логикой identity-safe
- [[landing-photos]] — команда, запускающая весь pipeline этапа 07c

## Источник
- `agents/photo-matcher.md`