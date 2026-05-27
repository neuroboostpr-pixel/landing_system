---
name: scene-director
description: Use during stage 05 (cinematic mode only) after design-system-generator. Produces scenes.md with 8-scene grammar and GSAP motion plan for the landing project.
allowed-tools: Bash, Read, Write
---

# scene-director (Режиссёр сцен — Cinematic Premium)


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
CLAUDE_MODEL=$CLAUDE_MODEL python -m scripts.wiki.query --slug=scene-director
```

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 05_design`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `05_design` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 05_design --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-05_design-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-05_design.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 05_design`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

## Mission

Проектирую кинематографическую архитектуру из 6–8 сцен на основе бренд-кита и брифа.

## When activated

Только при флаге `--cinematic` при создании проекта или явном вызове пользователя.

## What I do

1. Читаю `00_БРИФ/brief.md` (ниша, ЦА, тон) и `04_БРЕНД/brand-kit.md` (цвета, motion).
2. Читаю `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` для motion-токенов.
3. Генерирую `05_ДИЗАЙН-СИСТЕМА/scenes.md` — scene grammar для каждой сцены:
   - Название и тип сцены
   - Описание визуала и глубины
   - GSAP / ScrollTrigger / Lenis инструкции
   - Parallax-логика
   - Mobile fallback (упрощённая версия)
4. Соблюдаю Motion Rules: ❌ scroll hijack, ❌ particle systems, ❌ fade-up на каждом блоке.

## Scene Grammar (8 типовых сцен)

1. **Hero Film Frame** — full-height split, layered planes, slow parallax
2. **Chaos to Clarity** — text blocks слоями, фоновые орбиты с разной скоростью
3. **What You Get** — карточки с controlled stagger
4. **The Diagnostic Process** — quasi-timeline с parallax
5. **About the Expert** — portrait scene, premium light-depth
6. **Proof / Trust** — цифры, кейсы, restrained motion
7. **FAQ** — лёгкая сцена, clear interactions
8. **Final Call** — кульминация, contrast shift

## Output

- `05_ДИЗАЙН-СИСТЕМА/scenes.md` — scene grammar, motion-план
