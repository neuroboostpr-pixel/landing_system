---
type: agent
name: client-assets-collector
sources: ["agents/client-assets-collector.md"]
updated: 2026-05-20
triggers: []
stage: "02"
uses: ["photo-stylist", "landing-orchestrator", "stage-execution-protocol", "client-assets-collection", "niche-analyst"]
tags: ["stage-02", "assets", "scraping", "reviews", "photos"]
---

# Client Assets Collector — сбор материалов клиента

## Что делает

Собирает все материалы клиента: фотографии, видео и отзывы с публичных площадок (Яндекс Карты, 2ГИС, Otzovik). Без API-ключей — только бесплатный локальный скрапинг через trafilatura и Playwright. Итог — галерея `assets-gallery.html` для проверки и файл `assets-manifest.yaml` со списком всего собранного.

## Когда вызывать / в каком этапе

Запускается на этапе **02 — Материалы клиента**. Условие активации: `current_stage == 02_assets` в `.landing-state.yaml`. До запуска агент обязан проверить gate через `gate-check.sh` и показать Mermaid-карту pipeline. Диспатчит [[landing-orchestrator]] после завершения этапа 01a нишевого анализа.

## Что на вход / на выход

**Вход:**
- Файлы клиента (фото, видео) — пользователь кладёт вручную в `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` и `videos/`
- URL-адреса страниц с отзывами (Яндекс Карты, 2ГИС, Otzovik, Flamp)
- `00_БРИФ/brief.md` — нишевые сигналы
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — разделы 1–4, 6: какие фото нужны, а какие — нет (red flags)

**Выход:**
- `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/*.{jpg,png,webp}` — исходные фото без обработки
- `02_МАТЕРИАЛЫ_КЛИЕНТА/videos/*.{mp4,mov}` — видео с пометкой длительности
- `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/<source>/*.json` — распарсенные отзывы
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml` — реестр всех файлов с плановым использованием (hero / about / proof)
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-gallery.html` — визуальный превью для одобрения клиентом

## Связанные концепты

- [[photo-stylist]] — владеет обработкой фото (cutout, стилизация); `client-assets-collector` только копирует оригиналы, не трогает пиксели
- [[niche-analyst]] — поставляет `visual-requirements.md`, который определяет, что запрашивать у клиента
- [[client-assets-collection]] — скилл с Python-скриптом `parse-reviews.py` для скрапинга отзывов
- [[landing-orchestrator]] — диспатчит агента и ждёт HARD GATE перед переходом к этапу 03
- [[stage-execution-protocol]] — обязательный протокол проверки gate-check перед любым Write/Edit действием

## Источник

- `agents/client-assets-collector.md`