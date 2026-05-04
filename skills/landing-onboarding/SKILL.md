---
name: landing-onboarding
description: First-time setup of landing-system on a new machine. Validates local deps, MCP servers, superpowers plugin, and all API keys.
---

# landing-onboarding

## Mission

Настроить landing-system на новой машине: зависимости, плагины, MCP, API.

## Scripts

- `scripts/wizard.sh` — interactive flow
- `scripts/validate-all.sh` — runs all 15 API validators
- `scripts/setup-flag.sh` — manages `~/.landing-system/setup_complete`

## Used by

- `/landing-onboarding` slash command
- Auto-redirected from any `/landing-*` if setup_complete missing

## What it produces

`~/.landing-system/setup_complete` — flag with ISO timestamp. Other commands check this file before proceeding.
