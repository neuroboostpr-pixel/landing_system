На основе исходника формирую wiki-страницу:

---
type: unknown
name: pr-k-tests
sources: ["tests/pr-k/README.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["photo-classifier", "photo-matcher", "photo-curator"]
tags: ["tests", "bats", "photo-pipeline", "pr-k"]
---

# Тест-группа PR-K: Photo Pipeline

## Что делает
Набор bats-тестов, проверяющих корректность работы трёх ключевых сценариев фото-пайплайна: кэширование классификации фото, защиту hero-слота от обрезки и жадный алгоритм матчинга фото к слотам.

## Когда вызывать / в каком этапе
Запускается после изменений в агентах `photo-classifier`, `photo-matcher` или `photo-curator` (этап 07c). Должен проходить до мёржа любого PR, затрагивающего photo-pipeline.

```bash
# Все bats-тесты группы
bats tests/pr-k/

# Python-тесты (если добавлены)
pytest tests/pr-k/
```

## Что на вход / на выход

**Вход:**
- Тестовые фикстуры фото и mock-окружение (ожидается рядом с `.bats`-файлами)

**Выход:**
- Результат bats: `ok` / `not ok` per test case
- exit 0 — все тесты прошли (GATE открыт)
- exit 1 — есть падение (GATE заблокирован)

**Покрытые сценарии:**

| Файл | Что проверяет |
|------|---------------|
| `test_classify_caches.bats` | Повторный вызов `photo-classifier` с теми же параметрами берётся из кэша, API не дёргается дважды |
| `test_hero_no_crop.bats` | Фото в `hero`-слоте не обрезается AI-инструментами; identity-safe правило соблюдается |
| `test_match_greedy.bats` | Алгоритм `photo-matcher` заполняет максимальное число слотов (жадный matching), не оставляет пустых при наличии кандидатов |

## Связанные концепты
- [[photo-classifier]] — агент классификации фото; `test_classify_caches.bats` верифицирует его хэш-кэш
- [[photo-matcher]] — агент матчинга; `test_match_greedy.bats` верифицирует жадный алгоритм
- [[photo-curator]] — оркестратор этапа 07c, использует оба агента выше
- [[photo-curation]] — скилл, описывающий полный photo-pipeline
- [[07c-photos]] — этап, для которого написана эта тест-группа

## Источник
- `tests/pr-k/README.md`