---
type: command
name: landing-final-check
sources: ["commands/landing-final-check 2.md"]
updated: 2026-05-19
triggers:
  - "финальная проверка лендинга"
  - "проверить перед деплоем"
  - "запустить все проверки качества"
  - "bundle verify перед публикацией"
stage: "10"
uses:
  - landing-deploy
  - wp-deployer
  - qa-auditor
  - visual-qa
tags: [command, qa, verify, deploy, checklist]
---

# /landing-final-check — Финальная авто-проверка перед деплоем

## Что делает
Запускает все verify-скрипты системы одним пакетом и формирует итоговый отчёт о готовности лендинга к публикации. Если хотя бы одна обязательная проверка провалилась — деплой блокируется.

## Когда вызывать / в каком этапе
Вызывается вручную на этапе **10 QA** — после того как завершены этапы 07b (composed), 07c (фото), 07d (визуал) и 08 (сборка). Обязательный шаг перед `/landing-deploy`.

## Что на вход / на выход

**Вход:**
- `<project>` — путь к папке проекта (kebab-case slug)
- Наличие артефактов предыдущих этапов: `composed.html`, `processed/` фото, `tokens.json`, `manifest.yaml`

**Выход:**
- **stdout** — краткая сводка по каждой проверке (pass / fail)
- **`<project>/10_QA/final-check-report.md`** — детальный отчёт с описанием каждого нарушения
- **exit 0** — все обязательные проверки прошли; **exit 1** — есть провалы

**Пакет проверок:**

| Проверка | Обязательность |
|---|---|
| Wiki sync | опциональная |
| Composed premium (13 фич) | обязательная |
| Content preserved (текст прототипа) | обязательная |
| Photo pipeline (processed/, no placeholders, hero no-crop) | обязательная |
| Identity preserved (manifest без violations) | обязательная |
| Visual QA | опциональная |

## Связанные концепты
- [[qa-auditor]] — агент этапа 10, проверяет живой сайт после деплоя
- [[landing-deploy]] — следующий шаг после успешного final-check
- [[wp-deployer]] — деплоит тему на Бегет
- [[visual-qa]] — один из verify-скриптов пакета (опциональный)
- [[block-composer]] — должен исправить composed.html, если HARD GATE 07b не пройден

## Источник
- `commands/landing-final-check 2.md`