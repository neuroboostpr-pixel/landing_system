Теперь у меня достаточно контекста для составления wiki-страницы.

---
type: unknown
name: pr-n-detect-region-tests
sources: ["tests/pr-n/README.md", "tests/pr-n/test_detect_region.bats"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["photo-curation", "photo-curator"]
tags: ["tests", "bats", "detect-region", "photo-pipeline", "pr-n"]
---

# PR-N: Тесты detect-region

## Что делает

Группа bats-тестов, проверяющая скрипт `detect-region.py` — утилиту, которая автоматически определяет географический регион проекта (Dubai, Moscow, global и др.) из файлов `market-profile.md` или `brief.md`. Результат используется в фото-пайплайне для адаптации атмосферы генерируемых фото под локацию сайта.

## Когда вызывать / в каком этапе

Тесты запускаются при разработке и CI-проверках, связанных с `photo-curation`. Относятся к PR-N — набору улучшений фото-пайплайна (регион-адаптация). Сами по себе не являются этапом workflow, но защищают логику этапа **07c photos**.

Запуск вручную:
```bash
bats tests/pr-n/
```

## Что на вход / на выход

**Вход:**
- Тестовый проект с файлами:
  - `01a_АНАЛИЗ_НИШИ/market-profile.md` (поле `**Geo:**`)
  - `00_БРИФ/brief.md` (поле `Region:`)
  - Либо пустой проект (без файлов)

**Выход:**
- `bats` report: PASS / FAIL по 4 сценариям:
  1. Парсинг `**Geo:** Dubai` из `market-profile.md` → `"Dubai"`
  2. Парсинг `Region: Moscow` из `brief.md` → `"Moscow"`
  3. Пустой проект → `"global"`
  4. Приоритет `market-profile.md` над `brief.md` при наличии обоих

## Связанные концепты

- [[photo-curation]] — скрипт `detect-region.py` входит в `skills/photo-curation/scripts/`; тесты защищают эту логику
- [[photo-curator]] — агент 07c, использует регион для prompt-адаптации при генерации фото-фонов
- [[niche-analyst]] — создаёт `market-profile.md` с полем `**Geo:**`, которое читает detect-region

## Источник

- `tests/pr-n/README.md`
- `tests/pr-n/test_detect_region.bats`