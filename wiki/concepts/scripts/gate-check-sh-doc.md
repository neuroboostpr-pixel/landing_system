---
type: rule
name: gate-check
sources: ["scripts/gate-check.sh", "scripts/gate-check.sh.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["stage-gates", "landing-orchestrator"]
tags: ["bash", "gate", "quality", "automation"]
---

# gate-check — проверка шлюзов между этапами

## Что делает
Запускает проверки качества перед переходом на следующий этап лендинга. Читает конфиг `config/stage-gates.yaml`, выполняет жёсткие (`hard_checks`) и мягкие (`soft_checks`) проверки для указанного этапа проекта.

## Когда вызывать / в каком этапе
Вызывается автоматически агентом [[landing-orchestrator]] перед закрытием каждого этапа (00–12). Также можно запустить вручную, чтобы убедиться, что текущий этап пройден корректно, прежде чем двигаться дальше.

```bash
# Ручной запуск
bash scripts/gate-check.sh --stage 07b --project ~/Lendings/my-project

# С флагом авто-подтверждения мягких проверок
bash scripts/gate-check.sh --stage 07b --project ~/Lendings/my-project --approve

# Полностью неинтерактивный режим
bash scripts/gate-check.sh --stage 07b --project ~/Lendings/my-project --auto
```

## Что на вход / на выход

**Вход:**
- `--stage <id>` — номер этапа (например `07b`, `08`, `10`)
- `--project <dir>` — путь до папки проекта
- `--approve` (опционально) — автоматически подтверждать soft-проверки
- `--auto` (опционально) — полностью неинтерактивный режим (CI/CD)
- `config/stage-gates.yaml` — список hard и soft проверок для каждого этапа

**Выход:**
- `exit 0` — гейт пройден, можно двигаться дальше
- `exit 1` — гейт не пройден, переход заблокирован
- Вывод в консоль: список прошедших/упавших проверок

## Поведение проверок

- **hard_checks** — обязательные условия. Если хотя бы одно не выполнено — скрипт завершается с `exit 1`, этап не закрывается.
- **soft_checks** — рекомендательные. Выводятся как предупреждения; при `--approve` принимаются автоматически; без флага — запрашивают подтверждение у пользователя.

## Связанные концепты
- [[stage-gates]] — конфиг с описанием всех проверок для каждого этапа
- [[landing-orchestrator]] — мастер-агент, который вызывает gate-check между этапами
- [[landing-go]] — команда single entry point, которая через оркестратор запускает gate-check

## Источник
- `scripts/gate-check.sh`
- `scripts/gate-check.sh.doc.md`