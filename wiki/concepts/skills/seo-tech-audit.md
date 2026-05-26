---
slug: seo-tech-audit
type: skill
name: "SEO Tech Audit"
stage: "11"
tags: [seo, audit, qa, python, multisite, stage-gate]
triggers: [landing-audit]
inputs: [.landing-state.yaml, project-url]
outputs: [11_QA/audit-report.md, 11_QA/audit-report.json, 11_QA/per-site/]
gates: [seo_audit_pass]
pre_reqs: [wp-deployer]
related: [qa-auditor, seo-optimizer, landing-orchestrator]
sources: ["skills/seo-tech-audit/SKILL.md"]
updated: 2026-05-26
---

# SEO Tech Audit

## Что делает

Автоматически проверяет задеплоенный лендинг по 43 критериям трёх групп: HTML on-page (25 проверок — title, meta-description, h1, canonical, lang, alt у изображений и др.), Network/Infra (13 — SSL срок, редиректы, robots.txt, sitemap, мягкие 404, security-headers, Whois), Schema/Microdata (5 — Open Graph, Twitter Card, JSON-LD, favicon). Работает на чистом Python без Lighthouse и Node.js. Поддерживает multisite: автоматически обнаруживает поддомены из `.landing-state.yaml::audience_segments` и прогоняет каждый поддомен отдельно со сводным отчётом.

## Когда вызывается

Запускается вручную через `/landing-audit <slug>` или автоматически orchestrator'ом на этапе 11 (QA) как hard-gate `seo_audit_pass`. Этап 11 не закрывается, пока хотя бы один hard-gate провален на любом поддомене. Может вызываться ad-hoc для любого URL без привязки к проекту.

## Вход → выход

**Вход:** задеплоенный сайт (URL или slug проекта), опционально `.landing-state.yaml` с перечнем поддоменов аудитории.

**Выход:** `11_QA/audit-report.md` (сводный отчёт по всем поддоменам), `11_QA/audit-report.json` (машиночитаемый для CI/orchestrator), `11_QA/per-site/<host>.{md,json}` (детали по каждому поддомену). Exit code `0` — все hard-gates прошли; `1` — есть провалы; `2` — системная ошибка.

## Failure modes

- Сайт недоступен по сети — exit code `2`, аудит не запускается; нужно проверить деплой.
- SSL-сертификат истёк или истекает менее чем через 7 дней — hard-gate fail, этап 11 не закроется до продления.
- robots.txt или sitemap.xml отсутствуют — hard-gate fail; нужно добавить через wp-cli или плагин.
- Multisite: `.landing-state.yaml` не содержит `audience_segments` — аудит прогоняется только по главному домену, поддомены пропускаются молча.
- Мягкая 404 (сервер отдаёт 200 на несуществующую страницу) — hard-gate fail, требует настройки `.htaccess` или permalink'ов WordPress.

## Related

- [[qa-auditor]] — агент, который интерпретирует результаты аудита и формирует задачи на исправление
- [[seo-optimizer]] — работает с SEO-атрибутами на этапе контента; результаты его работы проверяет этот скилл
- [[landing-orchestrator]] — вызывает скилл как часть stage-11 gate-check
- [[wp-deployer]] — должен завершиться до запуска аудита (сайт обязан быть доступен)