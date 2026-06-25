---
slug: client-assets-collector
type: agent
name: "Сборщик материалов клиента"
stage: "02"
tags: [scraping, photos, videos, reviews, assets, stage-02]
triggers: []
inputs:
  - 00_БРИФ/brief.md
  - 01a_АНАЛИЗ_НИШИ/visual-requirements.md
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/videos/
outputs:
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/videos/
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/style-report.md
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/assets-gallery.html
gates:
  - assets_gallery_approved
pre_reqs:
  - 00-brif
  - 01a-analiz-nishi
related:
  - client-assets-collection
  - photo-stylist
  - photo-curator
  - 02-materialy-klienta
  - niche-analyst
  - landing-orchestrator
sources: ["agents/client-assets-collector.md"]
updated: 2026-06-19
confidence:
  triggers: low
---

# Сборщик материалов клиента

## Что делает

Агент этапа 02 собирает всё исходное сырьё клиента в единое место: фотографии, видео и публичные отзывы с Яндекс Карт, 2GIS, Otzovik, Flamp. Использует бесплатный локальный скрейпинг (trafilatura + Playwright) без API-ключей. После сбора автоматически анализирует качество и однородность фото через Pillow, выставляет вердикт «готово / нужна обработка / не хватает» и формирует HTML-галерею для визуальной проверки маркетологом.

## Когда вызывается

Запускается на этапе `02_assets`, когда `.landing-state.yaml::current_stage == 02_assets`. Вызывается оркестратором после закрытия этапа 01a (анализ ниши). Перед запросом материалов обязательно читает `01a_АНАЛИЗ_НИШИ/visual-requirements.md` (секции 1–4, 6) — это определяет, какие фото нужны, а какие red flags клиенту нельзя передавать.

## Вход → выход

**Вход:** бриф (`brief.md`), требования к визуалу из нишевого анализа, пользовательские файлы (фото/видео), URL публичных страниц с отзывами.

**Выход:** рассортированные фото в `photos/original/`, видео в `videos/`, разобранные отзывы в `testimonials/<source>/*.json`, сводный манифест `assets-manifest.yaml` с плановым использованием каждого файла (hero / about / proof), отчёт `style-report.md` об анализе фото-стиля, интерактивная галерея `assets-gallery.html`.

## Чем закрывается этап (gates)

- `assets_gallery_approved` — пользователь просмотрел `assets-gallery.html` и явно подтвердил переход к этапу 03; агент не идёт дальше без этого одобрения.

## Failure modes

- Скрейпинг падает (сетевая ошибка, блокировка) — агент сообщает об ошибке и спрашивает: повторить или пропустить источник.
- Фото-анализ возвращает вердикт «не хватает» (менее 3–5 фото) — агент останавливается и запрашивает у клиента дополнительные материалы.
- `current_stage != 02_assets` — агент полностью останавливается, не делая никаких записей, и сообщает о несоответствии.
- PreToolUse хук блокирует Write/Edit если предшественник не закрыт — не обходить, закрывать предшественника.
- `assets-manifest.yaml` не сгенерирован (ошибка скрипта) — gate-check упадёт с exit != 0, этап не откроется.

## Related

- [[client-assets-collection]] — Python-скилл с конкретными скриптами `parse-reviews.py` и `analyze-photo-style.py`, которые вызывает агент
- [[photo-stylist]] — следующий владелец собранных фото (обработка / ретушь)
- [[photo-curator]] — занимается подбором фото к слотам на этапе 07c
- [[01a-analiz-nishi]] — обязательный предшественник; его `visual-requirements.md` определяет, что запрашивать
- [[02-materialy-klienta]] — папка-этап, которую агент наполняет
- [[niche-analyst]] — агент, создавший `visual-requirements.md` на этапе 01a