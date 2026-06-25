---
slug: seo-tech-audit
type: skill
name: "SEO/Tech Аудит лендинга"
stage: "11"
tags: [seo, audit, qa, html, network, schema, multisite]
triggers: [landing-audit]
inputs: [09-deploy]
outputs: [10-qa]
gates: [seo_audit_pass]
pre_reqs: [09-deploy]
related: [landing-audit, landing-qa, landing-deploy, landing-orchestrator, 10-qa]
sources: ["skills/seo-tech-audit/SKILL.md"]
updated: 2026-06-19
confidence: {inputs: low, outputs: low}
---

# SEO/Tech Аудит лендинга

## Что делает

Автоматически проверяет задеплоенный лендинг по 43 параметрам качества: HTML on-page (title, meta, h1, canonical, lang, img-alt), сетевая инфраструктура (SSL, редиректы, robots.txt, sitemap, Whois), микроразметка (Open Graph, Twitter Card, JSON-LD, favicon). Работает на чистом Python без Lighthouse и Node.js. В мультисайт-режиме автоматически обнаруживает все поддомены из `.landing-state.yaml` и проверяет каждый отдельно. Используется как hard-gate этапа 11: стейдж не закрывается, пока хоть один критичный чек падает на любом поддомене.

## Когда вызывается

Запускается командой `/landing-audit <slug>` или напрямую через `python skills/seo-tech-audit/scripts/run-audit.py`. Вызывается после успешного деплоя (этап 09) как часть QA-цикла. Оркестратор запускает его автоматически при попытке закрыть gate `seo_audit_pass` в `config/stage-gates.yaml`.

## Вход → выход

**Вход:** задеплоенный лендинг (URL или slug проекта с `.landing-state.yaml`); доступность целевого домена по HTTPS.

**Выход:** отчёты в `<project>/11_QA/` — `audit-report.md` (сводный по всем поддоменам), `audit-report.json` (для CI/оркестратора), отдельные файлы `per-site/<host>.{md,json}` на каждый поддомен. Exit code 0 = все hard-gates ✓, 1 = есть failures, 2 = system error.

## Чем закрывается этап (gates)

- seo_audit_pass — run-audit.py возвращает exit 0 на всех поддоменах проекта; при multisite проверяются все записи из `audience_segments[]`

## Failure modes

- Домен недоступен или DNS не разрезолвился — exit code 2, аудит не запускается; нужно проверить деплой этапа 09.
- SSL-сертификат истекает менее чем через 7 дней — hard-gate блокирует закрытие этапа 11.
- robots.txt или sitemap.xml отсутствуют на сервере — чек падает; для Бегета нужно убедиться, что файлы задеплоены через wp-cli или rsync.
- В мультисайт-режиме один поддомен не отвечает — весь аудит считается failed, хотя остальные поддомены прошли.
- Lighthouse-метрики (LCP/CLS) не проверяются в E1 — если заказчик требует Web Vitals, нужна фаза E2.

## Related

- [[landing-audit]] — slash-команда, которая вызывает этот скилл
- [[landing-qa]] — общий QA-скилл этапа 10, предшествует аудиту
- [[landing-deploy]] — деплой (этап 09), обязательный pre-req
- [[landing-orchestrator]] — управляет gate-check и диспатчит аудит
- [[10-qa]] — этап, в папку которого пишутся отчёты