---
slug: client-assets-collector
type: agent
name: "Сборщик материалов клиента"
stage: "02"
tags: [stage-02, scraping, photos, reviews, assets, pillow, playwright]
triggers: [landing-orchestrator]
inputs: [00-brif, 01a-analiz-nishi]
outputs: [02-materialy-klienta]
gates: [assets_gallery_approved]
pre_reqs: [00-brif, 01a-analiz-nishi]
related: [client-assets-collection, photo-curator, photo-stylist, landing-orchestrator, 02-materialy-klienta]
sources: ["agents/client-assets-collector.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Сборщик материалов клиента

## Что делает

Агент этапа 02: собирает все клиентские материалы — фото и видео — и парсит публичные отзывы с Яндекс.Карт, 2GIS, Otzovik, Flamp через локальный скрейпинг (trafilatura + Playwright, без API-ключей). Анализирует стиль фотографий через Pillow и формирует `style-report.md` с вердиктом (однородный / нужна обработка / не хватает). Генерирует `assets-gallery.html` для просмотра и `assets-manifest.yaml` с плановым назначением каждого файла (hero / about / proof). Читает `01a_АНАЛИЗ_НИШИ/visual-requirements.md`, чтобы корректно сформировать запрос к клиенту и заранее обозначить red flags.

## Когда вызывается

Запускается оркестратором, когда `.landing-state.yaml` содержит `current_stage == 02_assets`. Предшественники (бриф и анализ ниши) должны быть закрыты — иначе harness PreToolUse hook физически блокирует запись. Перед любым действием агент выводит Mermaid-карту pipeline и создаёт TodoWrite-список оставшихся этапов.

## Вход → выход

**Вход:** файлы клиента (фото/видео), URL-адреса площадок с отзывами, `00_БРИФ/brief.md`, `01a_АНАЛИЗ_НИШИ/visual-requirements.md`.

**Выход:** `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` (оригинальные фото), `videos/` (видео), `testimonials/<source>/*.json` (отзывы), `assets-manifest.yaml`, `style-report.md`, `assets-gallery.html`.

## Чем закрывается этап (gates)

- `assets_gallery_approved` — пользователь просмотрел `assets-gallery.html` и подтвердил набор материалов перед переходом на этап 03 (References).

## Failure modes

- Парсинг отзывов падает по сети или блокировке сайта — агент сообщает об ошибке и спрашивает: повторить или пропустить источник.
- Фотографий меньше 3–5 штук — `style-report.md` возвращает «не хватает», агент запрашивает дополнительные материалы у клиента и не закрывает этап.
- `current_stage != 02_assets` в state-файле — агент останавливается сразу, не выполняет никаких Write/Edit действий.
- Отсутствует `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — нельзя корректно сформулировать запрос на нужные фото, агент должен остановиться.
- harness PreToolUse hook блокирует Write/Edit, если предшественник не закрыт — нельзя обходить, нужно закрыть предшественника.

## Related

- [[client-assets-collection]] — Python-скрипты парсинга отзывов и анализа стиля фото, которые вызывает этот агент
- [[01a-analiz-nishi]] — обязательный вход: задаёт требования к фото и red flags для запроса клиенту
- [[photo-curator]] — следующий в цепочке: принимает отобранные фото для дальнейшей обработки
- [[landing-orchestrator]] — диспатчит агента в рамках pipeline по состоянию `.landing-state.yaml`
- [[02-materialy-klienta]] — целевая папка-этап, которую агент наполняет артефактами