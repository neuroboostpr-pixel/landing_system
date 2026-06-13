---
type: script
name: enforce_stage_gate
language: python
sources: ["scripts/hooks/enforce_stage_gate.py"]
updated: 2026-05-18
---

# enforce_stage_gate.py

PreToolUse hook — блокирует Write/Edit/MultiEdit к файлам стадии,
которая ещё не достигла статуса in_progress/approved.

Запускается из .claude/settings.json:

  {
    "hooks": {
      "PreToolUse": [{
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [{"type": "command",
                   "command": "python3 $CLAUDE_PROJECT_DIR/scripts/hooks/enforce_stage_gate.py"}]
      }]
    }
  }

Контракт PreToolUse hook (Anthropic Claude Code):
- stdin: JSON {"tool_name": str, "tool_input": {...}}
- exit 0: allow
- exit != 0 + stderr: block + show stderr to model

## Источник

- `scripts/hooks/enforce_stage_gate.py`
