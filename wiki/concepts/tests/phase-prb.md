Читаю исходник перед написанием wiki-страницы.Посмотрю на содержимое тестовых файлов, чтобы точнее описать что именно они проверяют.---
type: rule
name: phase-prb-tests
sources: ["tests/phase-prb/README.md", "tests/phase-prb/test-agents-frontmatter.bats", "tests/phase-prb/test-codex-wrappers.bats", "tests/phase-prb/test-landing-photos-gate.bats", "tests/phase-prb/test-template-07c.bats"]
updated: 2026-05-18
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-classifier", "photo-matcher", "photo-preview-board", "landing-photos", "photo-curation"]
tags: ["tests", "bats", "photo-pipeline", "pr-b", "07c"]
---

# Тест-группа PR-B (фото-пайплайн, этап 07c)

## Что делает

Набор автоматизированных bats-тестов, которые проверяют корректность реализации фото-пайплайна (PR-B): наличие и содержимое агентов, команды `/landing-photos`, скриптов-обёрток над codex, а также структуру шаблона папки `07c_PHOTOS`.

## Когда вызывать / в каком этапе

Тесты запускаются в CI-паттерне и вручную разработчиком после внесения изменений в любой из компонентов PR-B. Применяются к этапу **07c** (обработка клиентских фотографий) перед закрытием HARD GATE.

```bash
bats tests/phase-prb/
```

## Что на вход / на выход

**Вход:**
- Файлы агентов: `agents/photo-curator.md`, `agents/photo-classifier.md`, `agents/photo-matcher.md`, `agents/photo-preview-board.md`
- Команда: `commands/landing-photos.md`
- Скрипты: `skills/photo-curation/scripts/codex-classify.sh`, `codex-match.sh`
- Шаблон: `template/07c_PHOTOS/` с 7 подпапками inbox

**Выход:**
- Результат bats: pass / fail по каждому тесту
- При успехе — подтверждение, что структура PR-B консистентна

## Покрытие по файлам

| Файл | Что проверяет |
|---|---|
| `test-agents-frontmatter.bats` | Frontmatter всех 4 photo-агентов, наличие ссылки на `IDENTITY_SAFE.md`, связи `photo-curator` → суб-агенты + `/landing-photos` |
| `test-codex-wrappers.bats` | `codex-classify.sh` пишет `catalog.yaml`; `codex-match.sh` генерит `selections.draft.yaml`; все обёртки пишут логи в `07c_PHOTOS/.logs/` |
| `test-landing-photos-gate.bats` | Команда `/landing-photos` существует, упоминает `photo-curator`, флаги `--force-stage` и `--all-ai`, stage-gates 05 и 07a |
| `test-template-07c.bats` | `template/07c_PHOTOS` содержит 7 inbox-подпапок с README, `_свалка` имеет `.gitkeep`, основной README на русском упоминает `/landing-photos` |

## Связанные концепты

- [[photo-curator]] — главный агент этапа 07c, фронтматтер которого тестируется
- [[photo-classifier]] — суб-агент, его файл проверяется на наличие и корректный frontmatter
- [[photo-matcher]] — суб-агент, аналогично
- [[photo-preview-board]] — суб-агент, аналогично
- [[landing-photos]] — команда, gate-условия которой покрыты тестами
- [[photo-curation]] — скилл, содержащий скрипты `codex-classify.sh` и `codex-match.sh`
- [[07c-photos]] — этап pipeline, для которого написана вся тест-группа

## Источник

- `tests/phase-prb/README.md`
- `tests/phase-prb/test-agents-frontmatter.bats`
- `tests/phase-prb/test-codex-wrappers.bats`
- `tests/phase-prb/test-landing-photos-gate.bats`
- `tests/phase-prb/test-template-07c.bats`