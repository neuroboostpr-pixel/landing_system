---
name: references-collection
description: Maintains 03_РЕФЕРЕНСЫ/index.yaml — tracks reference URLs, files, and statuses (candidate/approved/rejected). Owned by references-curator agent.
---

# references-collection

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill references-collection --stage 03
```

## What I do

CRUD on a YAML index of references with statuses. Subcommands:
- `add <refs-dir> <ref> [--type url|file] [--status candidate|approved|rejected]`
- `update <refs-dir> <ref-id> --status <new>`
- `list <refs-dir> [--status <filter>]`
- `show <refs-dir> <ref-id>`
- `remove <refs-dir> <ref-id>`

See [scripts/index.py](scripts/index.py).

## Референс = скриншот от клиента (A3, обязательное правило)

Источник того, как сайт должен выглядеть, — **скриншот и/или текстовое
описание ОТ КЛИЕНТА**. Ссылка на живой сайт — только подсказка, никогда
единственный источник (спека reference-driven flow §2.3):

1. На этапе сбора у клиента **запрашиваются скриншоты** (вход первого класса,
   наравне с прототипом).
2. Ссылка недоступна (бот-защита/403/гео/авторизация) → агент **обязан
   запросить у клиента скриншот**. Молча пропустить референс или выдумать
   стиль — дефект. Реальный провал: Mercedes за CloudFront → 403, текстовый
   пересказ наврал про «белый/без засечек», по скриншоту — чёрный фон, serif,
   синие кнопки-пилюли.
3. **Палитра и шрифты снимаются с пикселей скриншота** (extract-palette →
   refs-palette.html), не с текстового пересказа и не «на глаз».
4. Если клиент дал референс на конкретный блок с пометкой «бери раскладку» —
   зафиксируй в index.yaml поле `take: design|layout|both`
   (см. docs/standards/reference-driven-rules.md §3).

