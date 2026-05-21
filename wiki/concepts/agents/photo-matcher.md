---
type: agent
name: photo-matcher
sources: ["agents/photo-matcher.md"]
updated: 2026-05-20
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-curation", "photo-classifier", "photo-preview-board"]
tags: ["photo", "matching", "identity-safe", "codex"]
---

# Photo Matcher — ранжирование фото по слотам

## Что делает
Сопоставляет загруженные фотографии клиента с визуальными слотами на лендинге. Для каждого слота выбирает три лучших кандидата и помечает, нужна ли AI-генерация или обязательное согласие пользователя.

## Когда вызывать / в каком этапе
Вспомогательный агент этапа **07c** (Photos). Вызывается исключительно агентом `photo-curator` — напрямую не запускать. Запускается после того, как `photo-classifier` заполнил `catalog.yaml` тегами.

## Что на вход / на выход

**Вход:**
- `<project_dir>` — корневая папка проекта
- `07c_PHOTOS/catalog.yaml` — каталог с тегами всех загруженных фото (создаётся `photo-classifier`)
- `07a_WIREFRAME/selections.yaml` — утверждённые варианты блоков (только выбранные варианты, только слоты типа `photo`)
- `07_ПРОТОТИП/prototype.yaml` — список слотов из прототипа

**Выход:**
- `07c_PHOTOS/selections.draft.yaml` — YAML с топ-3 кандидатами на каждый слот, флагами `ai_fallback_needed` и `required_user_approval`

## Процесс

1. Строит `_slots-input.yaml` из `prototype.yaml`, фильтруя по `selections.yaml` (только активные варианты, только photo-слоты).
2. Запускает `skills/photo-curation/scripts/codex-match.sh` — codex получает полный каталог и список слотов, возвращает ранжированные кандидаты.
3. Валидирует YAML-вывод. При невалидном YAML — две попытки повтора. Если после двух попыток ошибка сохраняется — прерывает работу и просит пользователя проверить лог codex.
4. Пустой список кандидатов для слота → `ai_fallback_needed: true` (штатная ситуация, не ошибка).

## Правило identity-safe

Для слотов типа testimonial / expert / team codex обязан выставить `required_user_approval: true`. Это правило прописано в `IDENTITY_SAFE.md` и проверяется downstream: `selections-validator.py` и UI `photo-board.html` не дают пройти дальше без явного согласия пользователя.

## Связанные концепты
- [[photo-curator]] — родительский агент, который диспатчит photo-matcher и управляет всем этапом 07c
- [[photo-classifier]] — предшественник: тегирует фото и заполняет catalog.yaml, который читает этот агент
- [[photo-preview-board]] — следующий шаг: использует selections.yaml для рендера превью и финального подтверждения
- [[photo-curation]] — скилл-оркестратор этапа 07c, владеет скриптами и IDENTITY_SAFE правилами

## Источник
- `agents/photo-matcher.md`