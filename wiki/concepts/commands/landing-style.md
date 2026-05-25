---
type: command
name: landing-style
sources: ["commands/landing-style.md"]
updated: 2026-05-25
triggers:
  - "переведи wireframes в CSS"
  - "перепиши block.php шаблоны"
  - "сгенерируй стили для блоков"
  - "этап 08b"
  - "применить дизайн к коду"
stage: "08b"
uses:
  - frontend-builder
  - landing-build
  - landing-deploy
  - landing-design
tags: ["css", "block.php", "frontend", "lazy-blocks", "stage-08"]
---

# /landing-style — Генерация CSS и шаблонов блоков (этап 08b)

## Что делает

Переводит визуальные wireframes из DESIGN.md §5 в готовый CSS-код и PHP-шаблоны блоков. После выполнения каждый Lazy Blocks блок получает layout-aware разметку, а `main.css` пересобирается автоматически.

## Когда вызывать / в каком этапе

Вызывается на этапе **08b** — после того, как `/landing-build` завершён и утверждён (`08_build: approved` в `.landing-state.yaml`). Без одобрения 08_build команда останавливается с ошибкой.

Ручной вызов: `/landing-style` (все блоки) или `/landing-style --block <slug>` (один блок).

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — раздел §5 с заголовками `### Block N — Name` (wireframes)
- `08_КОД/block-spec.yaml` — список блоков для стилизации
- `08_КОД/wp-theme/blocks/lazyblock-*/block.php` — скелеты блоков после `/landing-build`
- brand-kit, design tokens из §2–§3

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` §5 — под каждым `### Block N` добавляется fenced ```css блок
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — перезаписывается с marker-заголовком и layout-aware разметкой
- `08_КОД/wp-theme/assets/css/main.css` — полностью регенерируется из обновлённого DESIGN.md

## Логика выполнения

1. **Pre-flight:** проверяет onboarding и stage-gate `08_build: approved`.
2. **Шаг 1:** диспатчит агент `frontend-builder` — он последовательно обрабатывает каждый блок из `block-spec.yaml`: составляет CSS с media-queries, добавляет его в DESIGN.md §5, перезаписывает `block.php`.
3. **Шаг 2:** запускает `extract-main-css.py` — регенерирует `assets/css/main.css`.
4. **Шаг 3 (hard gate авто):** `gate-check.sh --stage 08b_style` — 4 проверки: DESIGN.md существует, все `block.php` имеют marker, каждый `### Block N` в §5 содержит CSS, `main.css` присутствует.
5. **Шаг 4 (hard gate ручной):** визуальный approve в браузере (hero, pricing, FAQ, цвета, отсутствие PHP-fatal). После — `gate-check.sh --approve` → `08b_style: approved`.

## Связанные концепты

- [[frontend-builder]] — агент, выполняющий основную работу по генерации CSS и block.php
- [[landing-build]] — предыдущий этап (08), должен быть approved перед запуском
- [[landing-deploy]] — следующий этап (09), разблокируется после approve 08b_style
- [[landing-design]] — этап 05, источник токенов; сюда нужно идти, если токен отсутствует

## Источник

- `commands/landing-style.md`