---
name: scene-director
description: Use during stage 05 (cinematic mode only) after design-system-generator. Produces scenes.md with 8-scene grammar and GSAP motion plan for the landing project.
allowed-tools: Bash, Read, Write
---

# scene-director (Режиссёр сцен — Cinematic Premium)

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
