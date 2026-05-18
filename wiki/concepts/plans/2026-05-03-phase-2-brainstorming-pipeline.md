---
type: rule
name: phase-2-brainstorming-pipeline
sources: ["docs/superpowers/plans/2026-05-03-phase-2-brainstorming-pipeline.md"]
updated: 2026-05-18
triggers: []
stage: "02–04"
uses:
  - client-assets-collector
  - photo-stylist
  - references-curator
  - moodboard-composer
  - style-extractor
  - brand-architect
  - client-assets-collection
  - photo-styling
  - references-collection
  - moodboard-creation
  - style-decomposition
  - brand-kit-build
  - landing-references
  - landing-moodboard
  - landing-brand
  - landing-orchestrator
  - 02-materialy-klienta
  - 03-referensy
  - 04-brend
tags: [plan, phase-2, python, pipeline, brainstorming, free-stack]
---

# Phase 2 — Brainstorming Pipeline (план реализации)

## Что делает

Описывает как реализовать первые пять этапов производства лендинга (00 Бриф → 01 Контекст → 02 Материалы → 03 Референсы → 04 Бренд) через шесть специализированных агентов и набор Python/Bash инструментов. На выходе каждого этапа — HTML-превью для согласования с клиентом и `brand-kit.md` с полной трассировкой источников.

Ключевой принцип: **0 ₽ навсегда, без API-ключей**. Всё работает сразу после распаковки ZIP — регистрация нигде не нужна. Вместо платных API используются: trafilatura (парсинг статики), Playwright + headless Chromium (парсинг динамических страниц — Я.Карты, 2GIS, Otzovik), Claude Vision (распознавание шрифтов по скриншоту), Iconify HTTP API (иконки, open-access), Google Fonts через Bunny CDN (шрифты).

## Когда вызывать / в каком этапе

Это план реализации, а не запускаемый агент. Описывает 30 задач в 6 блоках:

- **Block A** (задачи 0–5) — Python-инфраструктура: `requirements.txt`, `tools/env.py`, `tools/logger.py`, web_scraper адаптер, Iconify адаптер, font_downloader, Jinja2 базовый движок
- **Block B** (задачи 6–10) — Этап 02: `client-assets-collector`, `photo-stylist`, скрипты `collect.py` и `parse-reviews.py`
- **Block C** (задачи 11–15) — Этап 03: `references-curator`, `moodboard-composer`, скрипты `index.py` и `render.py`
- **Block D** (задачи 16–22) — Переход 03→04: `style-extractor`, скрипты `extract-palette.py`, `identify-fonts.py`, `match-icons.py`, `download-fonts.py`
- **Block E** (задачи 23–26) — Этап 04: `brand-architect`, `build.py`, `render-html.py`
- **Block F** (задачи 27–30) — Оркестратор, слеш-команды `/landing-references`, `/landing-moodboard`, `/landing-brand`, интеграционные тесты

Каждая задача следует TDD-циклу: failing test → реализация → passing test → коммит.

## Что на вход / на выход

**Вход:** Клиентские фото, видео, URL с отзывами (Я.Карты / 2GIS / Otzovik), ссылки на визуальные референсы, `00_БРИФ/brief.md`.

**Выход на каждом этапе:**
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-gallery.html` + `assets-manifest.yaml`
- `03_РЕФЕРЕНСЫ/moodboard.html` + `index.yaml`
- `04_БРЕНД/extracted/*.yaml` (палитра, шрифты, иконки)
- `04_БРЕНД/brand-kit.md` с провенансом + `brand-kit.html`

## Связанные концепты

- [[client-assets-collector]] — агент этапа 02, собирает фото и разбирает отзывы
- [[photo-stylist]] — агент этапа 02, identity-safe обработка клиентских фото
- [[references-curator]] — агент этапа 03 (первая половина), ведёт index.yaml
- [[moodboard-composer]] — агент этапа 03 (вторая половина), рендерит moodboard.html
- [[style-extractor]] — агент перехода 03→04, извлекает палитру / шрифты / иконки
- [[brand-architect]] — агент этапа 04, синтезирует brand-kit.md с трассировкой
- [[landing-orchestrator]] — расширяется в Task 27 для диспатча всех шести агентов
- [[brand-kit-build]] — скилл, владеющий `build.py` и `render-html.py`
- [[style-decomposition]] — скилл, владеющий скриптами palette / fonts / icons / download

## Источник

- `docs/superpowers/plans/2026-05-03-phase-2-brainstorming-pipeline.md`