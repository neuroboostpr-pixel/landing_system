---
description: SEO/Tech аудит лендинга — 43 HTTP-проверки (HTML+Network+Schema). Multisite-aware. Stage-11 hard-gate.
---

# /landing-audit

Запускает `skills/seo-tech-audit/scripts/run-audit.py` для проверки задеплоенного лендинга.

## Использование

```
/landing-audit                                  # audit текущего проекта (cwd)
/landing-audit <project-slug>                   # audit любого проекта по slug в ~/Lendings/
/landing-audit <url>                            # ad-hoc URL (без проекта)
/landing-audit <project-slug> --site <host>     # один поддомен мультисайта
```

## Что делает

1. Определяет режим:
   - URL начинается с `http(s)://` → `--url` (ad-hoc)
   - Иначе → ищет `~/Lendings/<arg>` или текущий cwd → `--project`
2. Запускает `run-audit.py` с обнаруженными аргументами.
3. Пишет отчёт в `<project>/11_QA/audit-report.{md,json}` + `per-site/<host>.{md,json}`.
4. Возвращает exit-code 0 (все hard-gates ✓) / 1 (есть fails) / 2 (system error).
5. Печатает в чат сводку: какие сайты прошли, какие — нет, краткий список failed hard-gates.

## Покрытие (E1)

43 проверки за один прогон по каждому поддомену:
- HTML on-page (25): title/meta/h1/canonical/lang/img-alt/anchors
- Network/Infra (13): SSL, redirects, robots.txt, sitemap.xml, 404, Whois
- Schema (5): Open Graph, Twitter Card, JSON-LD, favicon

Не включено в E1 (будет в E2-E4): Lighthouse Web Vitals (LCP/CLS/INP), crawler битых ссылок, content metrics RU (тошнота/Flesch), AI readiness, auto-fix loop.

## Stage-11 gate

`config/stage-gates.yaml::11_qa.hard_checks::seo_audit_pass` — этот же скрипт.
Stage-11 не закрывается пока есть hard-gate failures.

## Зависимости

- Python 3.10+, `requests`, `beautifulsoup4`, `lxml`, `PyYAML`, `python-whois` (опционально, для N13)
