---
type: agent
name: photo-matcher
sources: ["agents/photo-matcher.md"]
updated: 2026-05-26
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-curation", "landing-photos"]
tags: ["фото", "ранжирование", "codex", "07c", "identity-safe"]
---

# Photo Matcher — ранжирование фото по слотам

## Что делает
Принимает каталог клиентских фотографий и список слотов из wireframe, затем через codex подбирает топ-3 кандидата на каждый слот и выставляет флаги: нужен ли AI-фоллбек и требуется ли явное согласие пользователя для «чувствительных» слотов (портреты, команда, эксперты).

## Когда вызывать / в каком этапе
Вызывается **только** родительским агентом `photo-curator` в рамках этапа **07c** (Photo Pipeline). Прямой вызов не предусмотрен: агент не владеет этапом самостоятельно и не читает `.landing-state.yaml`.

## Что на вход / на выход

**Вход:**
- `<project_dir>` — путь к папке проекта
- `07_ПРОТОТИП/prototype.yaml` — список всех слотов прототипа
- `07a_WIREFRAME/selections.yaml` — выбранные пользователем варианты блоков
- `07c_PHOTOS/catalog.yaml` — каталог классифицированных фотографий

**Выход:**
- `07c_PHOTOS/selections.draft.yaml` — черновик подбора: для каждого слота типа `photo` — до 3 кандидатов, флаг `ai_fallback_needed` (если кандидатов нет) и флаг `required_user_approval` (для identity-safe слотов — портреты/команда/эксперты/отзывы)

## Процесс

1. Строит `_slots-input.yaml` — фильтрует слоты прототипа по выбранным вариантам wireframe, оставляя только слоты типа `photo`.
2. Запускает `skills/photo-curation/scripts/codex-match.sh` с каталогом и отфильтрованными слотами.
3. Валидирует, что вывод — корректный YAML со структурой `slots: [...]`. При ошибке — 2 повторные попытки; после третьей неудачи прерывает работу и просит пользователя проверить лог codex.

**Identity-safe правило:** промпт для codex явно инструктирует выставить `required_user_approval: true` для слотов testimonial / expert / team. Валидатор (`selections-validator.py`) и интерфейс `photo-board.html` принудительно соблюдают это условие на следующих шагах.

## Связанные концепты
- [[photo-curator]] — родительский агент, который диспатчит photo-matcher
- [[landing-photos]] — slash-команда, запускающая весь Photo Pipeline (07c)
- [[photo-curation]] — скилл, содержащий скрипты `codex-match.sh` и `selections-validator.py`

## Источник
- `agents/photo-matcher.md`