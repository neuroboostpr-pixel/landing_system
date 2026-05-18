Теперь у меня достаточно контекста для составления wiki-страницы.

---
type: unknown
name: tests-pr-p
sources: ["tests/pr-p/README.md"]
updated: 2026-05-18
triggers: []
stage: "07b"
uses: ["premium-07b-checklist", "block-composition", "block-composer"]
tags: ["tests", "bats", "premium", "patterns", "07b"]
---

# Тесты PR-P — премиум-эффекты и библиотека паттернов

## Что делает
Группа bats-тестов, проверяющих инфраструктуру премиум-стилистики лендингов: корректность извлечения CSS-паттернов из живых сайтов, сборку библиотеки паттернов `_patterns/`, а также расширенный чеклист из 20 premium-проверок для этапа 07b.

## Когда вызывать / в каком этапе
Запускается при изменениях в `scripts/extract-effects/` или `docs/standards/premium-07b-checklist.md`. Привязан к этапу **07b (Compose)** — HARD GATE 07b закрывается только если `verify-composed-premium.sh` проходит все 20 проверок, часть которых тестируется именно здесь.

## Что на вход / на выход

**Вход:**
- Скрипты `scripts/extract-effects/extract-patterns.py` и `build-patterns-library.py`
- `docs/standards/premium-07b-checklist.md` (20 пунктов §1–§20)
- `scripts/verify-composed-premium.sh` (усиленная версия с +5 grep-паттернами)

**Выход:**
- Результаты прогона трёх bats-тестов:
  - `test_build_patterns_library.bats` — проверяет, что скрипт корректно создаёт `_patterns/` с `index.html`, `styles.css`, `meta.yaml`
  - `test_extract_patterns.bats` — проверяет 12 regex-паттернов извлечения (keyframes, transitions, hover, backdrop-filter, clip-path, gradient-complex и др.)
  - `test_premium_checklist_extended.bats` — проверяет, что `verify-composed-premium.sh` корректно проверяет новые пункты §14–§20 (scroll-driven анимации, glassmorphism, gradient-mesh, mix-blend-mode, prefers-reduced-motion, clip-path)

## Связанные концепты
- [[premium-07b-checklist]] — расширенный чеклист из 20 пунктов, именно его логику покрывают тесты
- [[block-composition]] — этап 07b, для которого проверяется корректность premium-фич
- [[block-composer]] — агент, обязанный выдавать composed.html, проходящий все 20 проверок

## Источник
- `tests/pr-p/README.md`