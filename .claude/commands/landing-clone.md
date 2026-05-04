---
description: Create an independent A/B copy of a landing on a new subdomain. Run within a landing project folder.
allowed-tools: Bash, Read
---

# /landing-clone

## Usage

```
/landing-clone <new-slug>
```

## What I do

1. Run `clone-landing.sh <project-dir> <new-slug>`
2. Update `BEGET_PATH` for new subdomain in cloned project `.env`
3. Run `/landing-deploy` in cloned project
4. Report new URL
