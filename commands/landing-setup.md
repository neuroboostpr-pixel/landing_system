---
description: One-time system initialization. Runs preflight checks, configures .env and config/system.yaml, reports what integrations are ready. Run once before creating any landing projects.
allowed-tools: Bash, Read, Write, Edit
---

# /landing-setup

Одноразовая настройка системы. Запускается один раз при установке.

## What I do

1. Run `scripts/preflight.sh` — check Python, bats, wp-cli, .env
2. If any checks fail — show fix instructions, wait, re-run
3. Configure `.env` — collect API keys for Firecrawl, CRM, deploy
4. Configure `config/system.yaml` — select integrations (CRM, analytics, libraries)
5. Show readiness report

## Usage

```
/landing-setup
```

## Output

- `.env` — filled with API keys (gitignored)
- `config/system.yaml` — integration settings (committed)
- Readiness report showing what's connected

## After setup

```
/landing-new <slug>   — create a new landing project
```
