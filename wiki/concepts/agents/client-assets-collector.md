---
type: agent
name: client-assets-collector
sources: ["agents/client-assets-collector.md"]
updated: 2026-05-26
triggers: []
stage: "02"
uses: ["landing-orchestrator", "stage-execution-protocol", "gate-check"]
tags: ["stage-02", "assets", "scraping", "reviews", "photos"]
---

# Client Assets Collector — Сборщик материалов клиента

## Что делает
Собирает все клиентские материалы (фото, видео) и автоматически скрейпит публичные отзывы с Яндекс Карт, 2ГИС, Отзовика и Flamp. Формирует структурированный каталог файлов с галереей для проверки клиентом — без API-ключей, только бесплатные инструменты.

## Когда вызывать / в каком этапе
Этап **02_assets** — сразу после закрытия этапа анализа ниши (01a). Агент активируется через `landing-orchestrator`, когда `.landing-state.yaml` фиксирует `current_stage == 02_assets`. Если этап не соответствует — агент останавливается и сообщает об ошибке.

Перед началом работы обязательно:
1. Читает `.landing-state.yaml` и показывает Mermaid-карту pipeline через `render-pipeline-map.sh`.
2. Создаёт TodoWrite-список всех оставшихся этапов.
3. Прогоняет `gate-check.sh --stage 02_assets` — продолжает только при exit 0.

## Что на вход / на выход

**Входы:**
- Файлы от клиента (фото/видео) — пользователь помещает в `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` и `videos/`.
- URL-адреса публичных отзывников (Яндекс Карты, 2ГИС, Отзовик, Flamp).
- `00_БРИФ/brief.md` — сигналы о нише.
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — определяет, какие фото нужны, а какие категорически не подходят (red flags, Section 6).

**Выходы:**
- `photos/original/*.{jpg,png,webp}` — исходные фото без обработки.
- `videos/*.{mp4,mov}` — видеофайлы с пометкой длительности.
- `testimonials/<source>/*.json` — распарсенные отзывы по источникам.
- `assets-manifest.yaml` — реестр всех файлов с плановым назначением (hero / about / proof).
- `assets-gallery.html` — HTML-галерея для ревью пользователем.

## HARD GATE
Переход к этапу 03 (Референсы) заблокирован до тех пор, пока пользователь не просмотрел `assets-gallery.html` и не дал явное подтверждение. Если парсинг отзывов падает по сети — агент выводит ошибку и спрашивает: повторить или пропустить.

## Связанные концепты
- [[landing-orchestrator]] — диспатчит этот агент в нужный момент pipeline
- [[stage-execution-protocol]] — обязательный протокол для любого этапа: карта → todo → gate → verify
- [[gate-check]] — скрипт-страж, физически блокирует Write/Edit при незакрытом предшественнике

## Источник
- `agents/client-assets-collector.md`