# Stage Agent Preamble (canonical, copy-paste block)

All stage-owner agents (those that take responsibility for a specific pipeline stage)
MUST start with this block right after the YAML frontmatter and `# <name>` heading.

When copying into a new agent — substitute `<STAGE>` with the agent's actual stage ID
(e.g., `04_brand`, `05_design`, `07c_composed`).

## The block

```markdown
## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == <STAGE>`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `<STAGE>` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage <STAGE> --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-<STAGE>-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-<STAGE>.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> <STAGE>`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.
```

## Why this is required

Per `audit/03-agents-skills-commands.md` C1, ONLY `landing-orchestrator.md` carried this
preamble. Other 28+ stage-owner agents had no gate-check call, no state-file read,
no TodoWrite-with-remaining-stages instruction. If any of them is dispatched directly
(Task tool, or by user), the pipeline lock is bypassed.
