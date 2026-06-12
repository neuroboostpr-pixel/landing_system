---
slug: 12-seo
type: stage
name: "12_SEO — SEO-финализация"
stage: "12"
tags: [seo, auto, final, pipeline]
triggers: []
inputs: []
outputs: [12_SEO/seo-meta.md, 12_SEO/sitemap.xml, 12_SEO/robots.txt]
gates: [seo_meta_complete, sitemap_valid, robots_txt_present]
pre_reqs: [landing-qa]
related: [seo-optimizer, seo-tech-audit, landing-final-check, landing-deploy]
sources: ["template/12_SEO/README.md"]
updated: 2026-05-26
confidence: {gates: low, inputs: low}
---

# 12_SEO — SEO-финализация

## Что делает

Завершающий этап конвейера: агент `seo-optimizer` собирает финальный пакет SEO-артефактов лендинга. Генерируется файл метаданных `seo-meta.md` с title, description и OG-тегами, а также технические файлы `sitemap.xml` и `robots.txt`. Этап полностью автоматический (без user-gate) и завершает production-pipeline.

## Когда вызывается

Запускается автоматически оркестратором (`landing-orchestrator`) после успешного прохождения этапа QA (11). Никакого ручного ввода не требуется: `landing-orchestrator` диспатчит этап в рамках `/landing-go` после того, как все предыдущие этапы закрыты.

## Вход → выход

**Вход:** задеплоенный и прошедший QA лендинг (этап 09 + 11); данные ниши и бренда из этапов 01a, 04; контент из этапа 07.

**Выход:**
- `12_SEO/seo-meta.md` — title, meta description, Open Graph теги
- `12_SEO/sitemap.xml` — карта сайта
- `12_SEO/robots.txt` — правила для поисковых роботов

## Чем закрывается этап (gates)

- `seo_meta_complete` — файл `seo-meta.md` присутствует и содержит непустые поля title, description, OG
- `sitemap_valid` — `sitemap.xml` валиден и содержит URL задеплоенного сайта
- `robots_txt_present` — `robots.txt` создан и не блокирует индексацию полностью

## Failure modes

- `seo-meta.md` не генерируется, если агент не получил данные о нише или бренде (этапы 01a/04 не закрыты)
- `sitemap.xml` может содержать устаревшие URL если деплой (этап 09) завершился с ошибкой или домен изменился
- `robots.txt` может заблокировать индексацию при неверном базовом URL (опечатка в домене)
- Этап считается пройденным без реального HTTP-аудита — нужен отдельный прогон `/landing-audit`
- На multisite-проектах артефакты создаются только для основного сайта; поддомены требуют отдельного прогона

## Related

- [[seo-optimizer]] — агент, который генерирует все три артефакта этапа
- [[seo-tech-audit]] — 43-проверочный HTTP-аудит задеплоенного сайта (этап 11)
- [[landing-final-check]] — финальная проверка перед закрытием проекта
- [[landing-deploy]] — деплой на Бегет (этап 09), обязательный pre-req