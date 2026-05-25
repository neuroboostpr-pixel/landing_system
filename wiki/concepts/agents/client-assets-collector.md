---
type: agent
name: client-assets-collector
sources: ["agents/client-assets-collector.md"]
updated: 2026-05-25
triggers: []
stage: "02"
uses: ["landing-orchestrator", "stage-execution-protocol", "gate-check"]
tags: ["stage-02", "assets", "scraping", "reviews", "photos"]
---

# Client Assets Collector — Сборщик материалов клиента

## Что делает
Собирает все клиентские материалы на этапе 02: фотографии, видео и публичные отзывы с Яндекс.Карт, 2GIS, Отзовика. Без API-ключей — только локальный скрейпинг. Результат — структурированная папка `02_МАТЕРИАЛЫ_КЛИЕНТА/` с манифестом и HTML-галереей для проверки.

## Когда вызывать / в каком этапе
Активируется на **этапе 02 (02_assets)** pipeline. Запускается агентом `landing-orchestrator` после закрытия этапа 01. Перед запуском проверяет `.landing-state.yaml` — `current_stage` обязан быть `02_assets`, иначе агент останавливается.

## Что на вход / на выход

**Входные данные:**
- Файлы от клиента (фото, видео) — пользователь кладёт в `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` и `videos/`
- URL публичных профилей с отзывами (Яндекс.Карты, 2GIS, Отзовик, Flamp)
- `00_БРИФ/brief.md` — для понимания ниши
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — определяет, какие фото нужны (секции 1–4, 6), а какие — явно не подходят (red flags секция 6)

**Результаты:**
- `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/*.{jpg,png,webp}`
- `02_МАТЕРИАЛЫ_КЛИЕНТА/videos/*.{mp4,mov}`
- `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/<source>/*.json` — распаршенные отзывы
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml` — реестр всех файлов с указанием планируемого использования (hero / about / proof)
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-gallery.html` — HTML-галерея для просмотра и утверждения

## Как работает
1. Уточняет у пользователя, какие материалы уже есть.
2. Копирует фото в `photos/original/` без изменений — обработка в зоне ответственности `photo-stylist`.
3. Для каждого URL запускает `python3 skills/client-assets-collection/scripts/parse-reviews.py`.
4. Генерирует `assets-manifest.yaml` и `assets-gallery.html`.
5. Ждёт явного утверждения от пользователя через галерею — **HARD GATE**, этап 03 не начинается без approve.
6. По завершении: запускает `scripts/verify-02_assets.sh` и закрывает этап через `scripts/gate-state.sh approve`.

Если скрейпинг упал — сообщает об ошибке и спрашивает: повторить или пропустить.

## Связанные концепты
- [[landing-orchestrator]] — диспатчит агента на этап 02
- [[stage-execution-protocol]] — обязательный протокол проверки перед любым действием
- [[landing-photos]] — следующий этап работы с фото (07c), использует собранные материалы
- [[landing-niche]] — анализ ниши (01a), чьи visual-requirements читаются перед запросом материалов

## Источник
- `agents/client-assets-collector.md`