---
description: First-time setup wizard. Validates all dependencies and API keys.
---

Run the onboarding wizard for landing-system.

Steps:
1. Read `docs/SETUP.md` to brief the user on what the system does.
2. Dispatch the `onboarding-guide` agent.
3. The agent runs `bash scripts/wizard.sh` and walks the user through each section interactively.
4. After all required validators pass, the agent runs `bash scripts/setup-flag.sh mark_complete`.
5. Report final status: "Onboarding complete" or list what's still missing.

If `~/.landing-system/setup_complete` already exists, ask whether to re-run anyway (e.g. to add new keys).
