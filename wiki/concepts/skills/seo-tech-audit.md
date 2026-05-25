---
type: skill
name: seo-tech-audit
sources: ["skills/seo-tech-audit/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: "11"
uses: ["landing-audit", "landing-orchestrator", "stage-gates"]
tags: ["seo", "audit", "qa", "python", "multisite"]
---

# SEO Tech Audit — автоматический аудит задеплоенного лендинга

## Что делает

Запускает 43 автоматические HTTP-проверки задеплоенного лендинга: проверяет HTML-разметку, сетевую инфраструктуру и микроразметку (Schema/OG). Формирует отчёт в Markdown и JSON, который становится жёстким гейтом перед закрытием этапа 11 (QA).

## Когда вызывать / в каком этапе

Вызывается на **этапе 11 (QA)** — после деплоя лендинга на Бегет. Активируется двумя способами:

- Команда `/landing-audit <slug>` из Claude Code;
- Напрямую через Python: `python skills/seo-tech-audit/scripts/run-audit.py --project ~/Lendings/<slug>`.

`landing-orchestrator` не закроет этап 11, пока `seo_audit_pass` из `config/stage-gates.yaml` не вернёт `exit 0`. В мультисайт-режиме аудит автоматически обходит все поддомены, перечисленные в `.landing-state.yaml::audience_segments`.

## Что на вход / на выход

**Вход:**
- Путь до папки проекта (`--project`) или прямой URL (`--url`);
- `.landing-state.yaml` (для auto-discovery поддоменов в multisite);
- Опциональный флаг `--json` для CI/orchestrator.

**Выход** — артефакты в `<project>/11_QA/`:

| Файл | Назначение |
|---|---|
| `audit-report.md` | Сводный отчёт по всем поддоменам |
| `audit-report.json` | Машино-читаемый результат |
| `per-site/<host>.md` | Детализация по каждому поддомену |
| `per-site/<host>.json` | То же в JSON |

**Exit-коды:** `0` — все hard-гейты пройдены; `1` — есть хотя бы одна критическая ошибка; `2` — системная ошибка (проект не найден, нет сети).

**Что проверяется (E1, 43 чека):**
- **HTML on-page (25):** title, meta-description, H1, canonical, lang, img-alt, внутренние ссылки и др.
- **Network/Infra (13):** SSL-сертификат (≥7 дней), www→non-www редирект, robots.txt, sitemap.xml, мягкие 404, security headers.
- **Schema/Microdata (5):** Open Graph (5 свойств), Twitter Card, JSON-LD, favicon.

**За рамками E1 (будущие фазы):**
- Lighthouse Web Vitals (LCP/CLS/INP) — E2;
- Crawler битых ссылок — E2;
- Контент-метрики (тошнота, Flesch) — E3;
- AI readiness + auto-fix loop — E4.

**Зависимости:** только стандартный Python (`requests`, `beautifulsoup4`, `lxml`, `python-whois`). Node.js / Lighthouse не требуется.

## Связанные концепты

- [[landing-audit]] — slash-команда, которая вызывает этот скилл
- [[landing-orchestrator]] — использует exit-код как hard-gate этапа 11
- [[stage-gates]] — конфиг `config/stage-gates.yaml`, содержащий `seo_audit_pass`
- [[landing-deploy]] — этап 09, после которого запускается аудит

## Источник

- `skills/seo-tech-audit/SKILL.md`