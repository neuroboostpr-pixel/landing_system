---
type: agent
name: client-assets-collector
sources: ["agents/client-assets-collector.md"]
updated: 2026-05-15
triggers: []
stage: "02"
uses: ["photo-stylist", "niche-analyst", "landing-orchestrator"]
tags: ["stage-02", "photos", "reviews", "scraping", "assets"]
---

# client-assets-collector — Сбор материалов клиента

## Что делает
Собирает все исходные материалы клиента: фотографии, видео и отзывы с публичных площадок (Яндекс Карты, 2GIS, Otzovik, Flamp). Работает без API-ключей — использует бесплатный локальный парсинг через trafilatura и Playwright. Результат — структурированная папка `02_МАТЕРИАЛЫ_КЛИЕНТА/` с манифестом и HTML-галереей для просмотра.

## Когда вызывать / в каком этапе
**Этап 02** — сразу после анализа ниши (`01a_АНАЛИЗ_НИШИ/`). Агент запускается оркестратором `landing-orchestrator` или вручную. Перед запуском обязательно должен существовать файл `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — он определяет, какие именно фото запрашивать у клиента и от каких материалов стоит отказаться (секции red flags).

## Что на вход / на выход

**Вход:**
- Пользовательские файлы (фото, видео) — клиент кладёт их в `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` и `videos/`
- Ссылки на профили в Яндекс Картах, 2GIS, Otzovik, Flamp
- `00_БРИФ/brief.md` — сигналы о нише
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — требования к визуалу (обязательно)

**Выход:**
- `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/*.{jpg,png,webp}` — оригинальные фото (без обработки)
- `02_МАТЕРИАЛЫ_КЛИЕНТА/videos/*.{mp4,mov}` — видео с указанием хронометража
- `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/<source>/*.json` — распарсенные отзывы по источникам
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml` — реестр всех файлов с плановым назначением (hero / about / proof)
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-gallery.html` — HTML-галерея для пользовательского просмотра

## Связанные концепты
- [[photo-stylist]] — обрабатывает фото из этого этапа (identity-safe cutout, edge cleanup), агент не трогает оригиналы
- [[niche-analyst]] — поставляет `visual-requirements.md`, который задаёт критерии отбора фото
- [[landing-orchestrator]] — диспатчит агента в нужный момент и держит HARD GATE до user approve
- [[client-assets-collection]] — скилл с Python-скриптами парсинга отзывов

## Источник
- `agents/client-assets-collector.md`