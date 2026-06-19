---
slug: content-writer
type: agent
name: "Контент-райтер"
stage: "07"
tags: [content, extraction, prototype, gutenberg, copy]
triggers: [landing-content]
inputs: [07_ПРОТОТИП/prototype.md, 07_ПРОТОТИП/prototype.yaml, 01a_АНАЛИЗ_НИШИ/positioning.md, 01a_АНАЛИЗ_НИШИ/competitors.yaml]
outputs: [07_КОНТЕНТ/content.md, 07_КОНТЕНТ/extraction-log.md]
gates: [content_md_exists, content_no_lorem, content_sections_match, extraction_log_passed]
pre_reqs: [07-prototip, 06-stek, 05-dizayn-sistema]
related: [landing-content, prototype-importer, block-composer, landing-compose, prototype-import]
sources: ["agents/content-writer.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Контент-райтер

## Что делает

Извлекает реальные тексты из прототипа лендинга и структурирует их по блокам будущей страницы. Главный принцип — никакой выдумки: каждое слово в `content.md` должно быть взято из `prototype.md` или `prototype.yaml`, а не сочинено агентом. После извлечения валидирует результат на отсутствие шаблонных заглушек (Lorem ipsum, «описание здесь» и т.д.) и фиксирует итог в лог-файле.

## Когда вызывается

Запускается командой `/landing-content` на этапе 07, когда прототип уже импортирован (`07-prototip` закрыт) и дизайн-система одобрена (`05-dizayn-sistema`). Перед первым Write-действием агент обязан убедиться, что `.landing-state.yaml` показывает `current_stage == 07_content`, и пройти `gate-check.sh --stage 07_content`.

## Вход → выход

**Вход:** `07_ПРОТОТИП/prototype.md` (канон, обязателен) + опционально `prototype.yaml` (машинная структура блоков). Дополнительно: `01a_АНАЛИЗ_НИШИ/positioning.md` и `competitors.yaml` для тонального контекста.

**Выход:** `07_КОНТЕНТ/content.md` — тексты, структурированные по секциям (H2) и блокам (H3) прототипа. `07_КОНТЕНТ/extraction-log.md` — лог с числом извлечённых блоков, предупреждениями и статусом валидации.

## Чем закрывается этап (gates)

- `content_md_exists` — файл `content.md` физически создан в `07_КОНТЕНТ/`
- `content_no_lorem` — в файле нет шаблонных заглушек (Lorem ipsum, placeholder-фраз)
- `content_sections_match` — число секций в `content.md` совпадает с числом секций в прототипе
- `extraction_log_passed` — `extraction-log.md` существует и содержит статус ✅ PASSED

## Failure modes

- **Текст не найден в yaml и md** — агент помечает блок `[TEXT NOT FOUND IN PROTOTYPE]` вместо выдуманного текста; это приводит к падению gate `content_no_lorem`, если не устранить.
- **prototype.md не существует** — агент останавливается с FAIL ещё до начала извлечения; нужно сначала запустить `/landing-prototype`.
- **Число секций расходится** — если yaml содержит устаревшую схему (`sections` вместо `blocks`), нормализатор может пропустить часть структуры.
- **Stage gate enforcement** — хук `enforce_stage_gate.py` физически блокирует запись, если предшественник (например `07-prototip`) не закрыт; обход невозможен.
- **Выдуманный контент** — самый критичный дефект; агент обязан провалить валидацию, а не тихо записать сочинённый текст.

## Related

- [[landing-content]] — слеш-команда, которая вызывает этот агент
- [[prototype-importer]] — создаёт `prototype.md` и `prototype.yaml`, обязательный предшественник
- [[block-composer]] — потребляет `content.md` на этапе 07c для сборки `composed.html`
- [[landing-compose]] — следующий этап, где тексты из `content.md` встраиваются в макет
- [[stage-execution-protocol]] — обязательный протокол pre-flight для всех этапов