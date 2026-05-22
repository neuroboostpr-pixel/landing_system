---
name: seo-tech-audit
description: Аудит задеплоенного лендинга — 43 HTTP-проверки (HTML on-page, network/infra, schema/microdata). Multisite-aware (auto-discovers поддомены из .landing-state.yaml). Используется как stage-11 hard-gate. Pure Python, без Lighthouse/Node (E1 scope; Lighthouse Vitals = E2).
---

# seo-tech-audit

Скилл для автоматического аудита задеплоенного лендинга. Запускается через slash-команду `/landing-audit` или напрямую `python scripts/run-audit.py`.

**Что проверяет (E1, 43 check'а):**
- **HTML on-page (25):** title/meta/h1/canonical/lang/img-alt/internal links и т.д.
- **Network/Infra (13):** SSL, redirects, robots.txt, sitemap.xml, 404 page, Whois
- **Schema/Microdata (5):** Open Graph, Twitter Card, JSON-LD, favicon

**Что НЕ проверяет в E1 (отдельные фазы):**
- Lighthouse Web Vitals (LCP/CLS/INP) — E2
- Crawler битых ссылок — E2
- Content metrics RU (тошнота/Flesch) — E3
- AI readiness + auto-fix loop — E4

Spec: [docs/superpowers/specs/2026-05-15-s2e-seo-tech-audit-design.md](../../docs/superpowers/specs/2026-05-15-s2e-seo-tech-audit-design.md) (§13 — E1 scope)

## Использование

```bash
# Все поддомены проекта (auto-discover из .landing-state.yaml)
python skills/seo-tech-audit/scripts/run-audit.py --project ~/Lendings/dubai-avto-liza

# Конкретный URL (ad-hoc)
python skills/seo-tech-audit/scripts/run-audit.py --url https://dubai-avto-liza.ailexi.ru

# JSON output для CI/orchestrator
python skills/seo-tech-audit/scripts/run-audit.py --project <p> --json
```

Или slash-команда `/landing-audit dubai-avto-liza` из Claude Code.

## Output

```
11_QA/
├── audit-report.md       # Сводный отчёт (все поддомены)
├── audit-report.json     # Машино-читаемый
└── per-site/
    ├── <host1>.md
    ├── <host1>.json
    └── ...
```

## Exit codes

- `0` — все hard-gates ✓ на всех поддоменах
- `1` — хоть один hard-gate fail на любом поддомене
- `2` — system error (project not found, network unreachable)

## Stage-11 gate

`config/stage-gates.yaml::11_qa.hard_checks` включает `seo_audit_pass` который запускает run-audit.py. Stage-11 не закроется пока есть hard-gate failures.
