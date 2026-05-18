---
type: rule
name: check-wiki-sync
sources: ["scripts/check-wiki-sync.sh"]
updated: 2026-05-18
triggers: ["проверить синхрон wiki", "wiki устарела", "wiki не в синхроне", "проверить кэш wiki"]
stage: ""
uses: ["wiki", "landing-orchestrator"]
tags: ["wiki", "sync", "ci", "bash", "cache"]
---

# check-wiki-sync.sh — проверка синхрона wiki с источниками

## Что делает
Сравнивает SHA-256 хэши всех файлов-источников системы с записями в `wiki/.cache.json`. Если хоть один источник изменился и wiki не пересобрана — выводит список расхождений и завершается с exit 1.

## Когда вызывать / в каком этапе
Используется в pre-commit проверках и CI, а также вручную после любого изменения в `agents/`, `skills/`, `commands/`, `template/` или `docs/standards/`. Рекомендуется запускать перед коммитом, если хук `post-commit` недоступен или упал.

```bash
bash scripts/check-wiki-sync.sh
# exit 0 — синхрон
# exit 1 — wiki устарела, нужно пересобрать
```

## Что на вход / на выход

**Вход:**
- `wiki/.cache.json` — файл с хэшами, созданный компилятором wiki
- Файлы-источники по 21 glob-паттерну: `agents/*.md`, `skills/*/SKILL.md`, `commands/*.md`, `template/*/README.md`, `docs/standards/*.md`, `block-library/*/*/meta.yaml`, `config/*.yaml`, `docs/superpowers/specs/*.md`, `scripts/**/*.doc.md` и др.

**Выход:**
- `exit 0` + сообщение `✅ Wiki в синхроне с источниками.`
- `exit 1` + список файлов с расхождением + команда для исправления:
  ```
  python3 -m scripts.wiki.compile --source-mode=system
  git add wiki/ && git commit -m 'chore(wiki): manual resync'
  ```

## Связанные концепты
- [[wiki]] — правило обязательной синхронности wiki в каждом коммите
- [[landing-orchestrator]] — оркестратор, который зависит от актуальности wiki-индекса

## Источник
- `scripts/check-wiki-sync.sh`