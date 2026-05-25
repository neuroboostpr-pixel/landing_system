---
type: stage
name: 12-seo
sources: ["template/12_SEO/README.md"]
updated: 2026-05-25
triggers: []
stage: "12"
uses: ["seo-optimizer", "landing-orchestrator"]
tags: ["seo", "meta", "sitemap", "robots", "auto"]
---

# 12_SEO — SEO-финализация лендинга

## Что делает
Финальный этап pipeline: генерирует SEO-метаданные, карту сайта и файл robots.txt для готового лендинга. Всё происходит автоматически — без ручного вмешательства.

## Когда вызывать / в каком этапе
Этап 12 — последний в pipeline, запускается автоматически через `landing-orchestrator` после деплоя (этап 09) и QA (этапы 10–11). Пользователь не вызывает его напрямую.

## Что на вход / на выход

**Вход:**
- Задеплоенный и проверенный лендинг (этапы 09–11 завершены)
- Данные из `DESIGN.md`, brand-kit и market-profile (заголовок, описание, ниша)

**Выход:**
- `seo-meta.md` — title, description, Open Graph теги
- `sitemap.xml` — карта сайта
- `robots.txt` — директивы для поисковых роботов

## Связанные концепты
- [[seo-optimizer]] — агент, который создаёт все артефакты этого этапа
- [[landing-orchestrator]] — диспатчит этап 12 как финал pipeline

## Источник
- `template/12_SEO/README.md`