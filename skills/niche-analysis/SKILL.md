---
name: niche-analysis
description: Stage 01a — automatic niche and competitor research. Invoked by /landing-niche command. Hands off to niche-analyst agent. Outputs three artifacts in 01a_АНАЛИЗ_НИШИ/. Zero-touch.
---

# niche-analysis skill

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill niche-analysis --stage 01a
```

Обёртка вокруг агента `niche-analyst` для запуска через slash-команду `/landing-niche`.

## Что делает skill

1. Проверяет, что текущая папка — это проект-лендинг (`.landing-state.yaml` существует).
2. Проверяет, что этап `00_brief` имеет статус `approved`.
3. Помечает `01a_niche_analysis` как `in_progress` через `scripts/gate-state.sh`.
4. Делегирует работу агенту `niche-analyst`.
5. После завершения работы агента запускает валидатор schema и `gate-check.sh`.

## Файлы

- `scripts/validate-competitors.py` — валидатор схемы YAML

## См. также

- Агент: `agents/niche-analyst.md`
- Spec: `docs/superpowers/specs/2026-05-06-niche-analysis-design.md`
