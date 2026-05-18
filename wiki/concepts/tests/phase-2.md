Давай дополнительно проверю содержимое самих тест-файлов, чтобы дать точные описания каждого из них.---
type: rule
name: phase-2
sources: ["tests/phase-2/README.md", "tests/phase-2/test-agents-frontmatter.bats", "tests/phase-2/test-commands-phase2.bats", "tests/phase-2/test-deps.bats", "tests/phase-2/test-orchestrator-phase2.bats"]
updated: 2026-05-18
triggers: []
stage: ""
uses:
  - client-assets-collector
  - photo-stylist
  - references-curator
  - moodboard-composer
  - style-extractor
  - landing-orchestrator
  - landing-references
  - landing-moodboard
tags: ["tests", "bats", "phase-2", "ci"]
---

# Тест-группа phase-2

## Что делает
Набор bats-тестов, проверяющих целостность агентов, команд и зависимостей, введённых в Phase 2 системы (сбор клиентских материалов, референсы, мудборд, стиль-декомпозиция). Гарантирует, что все файлы на месте, frontmatter корректен, а окружение исполняемо.

## Когда вызывать / в каком этапе
Запускается вручную или в CI после любых изменений в агентах, командах или зависимостях Phase 2. Не привязан к конкретному pipeline-этапу — это сквозная проверка работоспособности инфраструктуры.

```bash
# Bats-тесты
bats tests/phase-2/

# Pytest (если есть test_*.py)
pytest tests/phase-2/
```

## Что на вход / на выход

**Вход:** исходники системы в `$LANDING_SYSTEM_ROOT` (агенты, команды, `requirements.txt`).

**Выход:** pass/fail отчёт bats. При падении тест указывает, какой файл отсутствует или какое поле frontmatter пропущено.

### Покрытие по файлам

| Файл | Что проверяет |
|---|---|
| `test-agents-frontmatter.bats` | Наличие и корректный frontmatter (`name:`, `description:`) агентов: `client-assets-collector`, `photo-stylist`, `references-curator`, `moodboard-composer` (и другие Phase 2 агенты) |
| `test-commands-phase2.bats` | Наличие файлов команд `landing-references` и `landing-moodboard`, их frontmatter, упоминание связанных агентов и артефактов (`moodboard.html`) |
| `test-deps.bats` | Python ≥ 3.10, наличие `requirements.txt` с ключевыми пакетами (`Pillow`, `colorthief`, `Jinja2`, `trafilatura`, `playwright`, `beautifulsoup4`), установленность Playwright Chromium |
| `test-orchestrator-phase2.bats` | В `landing-orchestrator.md` присутствует секция `Phase 2 Scope` и упомянуты все Phase 2 агенты (`client-assets-collector`, `photo-stylist`, `references-curator`, `moodboard-composer`, `style-extractor`) |

## Связанные концепты
- [[client-assets-collector]] — агент сбора фото/видео клиента, проверяется наличие и frontmatter
- [[photo-stylist]] — агент обработки фоток, проверяется наличие и frontmatter
- [[references-curator]] — агент референсов, проверяется frontmatter и связь с командой
- [[moodboard-composer]] — агент мудборда, проверяется в командах и оркестраторе
- [[style-extractor]] — агент декомпозиции стиля, проверяется упоминание в оркестраторе
- [[landing-orchestrator]] — главный оркестратор, проверяется наличие Phase 2 Scope и всех агентов
- [[landing-references]] — команда `/landing-references`, проверяется frontmatter и содержимое
- [[landing-moodboard]] — команда `/landing-moodboard`, проверяется frontmatter и содержимое

## Источник
- `tests/phase-2/README.md`
- `tests/phase-2/test-agents-frontmatter.bats`
- `tests/phase-2/test-commands-phase2.bats`
- `tests/phase-2/test-deps.bats`
- `tests/phase-2/test-orchestrator-phase2.bats`