---
slug: landing-audit
type: command
name: "SEO/Tech Аудит Лендинга"
stage: "11"
tags: [seo, audit, qa, http-checks, multisite]
triggers: [/landing-audit]
inputs: []
outputs: [11_QA/audit-report.md, 11_QA/audit-report.json, 11_QA/per-site]
pre_reqs: [09-deploy]
related: [seo-tech-audit, 10-qa, 11-analitika, 12-seo, landing-qa]
sources: ["commands/landing-audit.md"]
updated: 2026-06-22
---

# /landing-audit — SEO/Tech Аудит Лендинга

## Что делает

Запускает автоматическую проверку задеплоенного лендинга через 43 HTTP-теста: HTML on-page (title, meta, h1, canonical, lang, img-alt, anchors), сетевая инфраструктура (SSL, редиректы, robots.txt, sitemap.xml, 404-поведение, security headers, Whois), схема разметки (Open Graph, Twitter Card, JSON-LD, favicon). Multisite-aware: автоматически обнаруживает поддомены из `.landing-state.yaml::audience_segments` и аудирует каждый. Является hard-gate для закрытия этапа 11 — пока есть провальные проверки, этап не закрывается.

## Когда вызывается

Вызывается вручную командой `/landing-audit` после деплоя (этап 09) — когда сайт уже доступен в интернете. Можно передать slug проекта, прямой URL или запустить без аргументов из папки проекта. Также вызывается gate-checker'ом при попытке закрыть этап 11.

## Вход → выход

**Вход:** задеплоенный лендинг с доступным доменом; опционально — slug проекта (`~/Lendings/<slug>`) или прямой URL (`https://...`); Python 3.10+ с зависимостями (`requests`, `beautifulsoup4`, `lxml`, `PyYAML`).

**Выход:** отчёты `<project>/11_QA/audit-report.{md,json}` (сводный по всем поддоменам) и `per-site/<host>.{md,json}` (детальный по каждому). Exit-code 0 — все hard-gates прошли, 1 — есть провалы, 2 — системная ошибка. В чат выводится краткая сводка: какие сайты прошли, какие нет, список failed checks.

## Failure modes

- **SSL истекает / невалиден** — проверка N1 сразу падает, остальные network-тесты могут не запуститься.
- **Сайт ещё не задеплоен** — скрипт получает connection error, возвращает exit-code 2 вместо 1.
- **`python-whois` не установлен** — проверка N13 (Whois) пропускается без ошибки, итоговое покрытие ≠ 43.
- **Multisite: поддомены не прописаны в `.landing-state.yaml`** — аудит запускается только для главного домена, сегменты не проверяются.
- **robots.txt запрещает весь сайт** — HTML-тесты частично валятся из-за 403, отчёт некорректен.

## Related

- [[seo-tech-audit]] — Python-скрипт `run-audit.py`, который реально выполняет все 43 проверки
- [[10-qa]] — предшествующий QA-этап (функциональный), аудит дополняет его SEO-метриками
- [[11-analitika]] — этап, для которого `seo_audit_pass` является hard-gate
- [[12-seo]] — финальный SEO-этап, использует результаты аудита
- [[landing-qa]] — смежная команда ручного QA перед аудитом