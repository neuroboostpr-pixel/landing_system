Вот структурированная wiki-страница:

---
type: rule
name: landing-final-check
sources: ["scripts/landing-final-check.sh"]
updated: 2026-05-18
triggers: ["финальная проверка проекта", "запустить все verify-скрипты", "проверить проект перед деплоем"]
stage: "10"
uses: ["verify-composed-premium", "verify-content-preserved", "verify-photo-pipeline", "verify-identity-preserved", "check-wiki-sync", "verify-visual-qa", "qa-auditor"]
tags: ["qa", "verification", "gate", "bash", "script"]
---

# landing-final-check — финальная проверка проекта

## Что делает

Запускает все verify-скрипты системы одним вызовом и формирует сводный отчёт в `10_QA/final-check-report.md`. Это единая точка входа для итогового контроля качества перед деплоем.

## Когда вызывать / в каком этапе

Используется на этапе **10 (QA)** — после сборки WordPress-темы (этап 08) и перед деплоем на Бегет (этап 09). Вызывается вручную:

```bash
bash scripts/landing-final-check.sh ~/Lendings/<project-slug>
```

## Что на вход / на выход

**Вход:**
- Путь к папке проекта (`$1`, обязательный аргумент)
- Наличие артефактов этапов: `07b_COMPOSED/composed.html`, `07c_PHOTOS/`, `04_БРЕНД/`

**Выход:**
- `10_QA/final-check-report.md` — сводный markdown-отчёт с секцией на каждую проверку (первые 20 строк вывода + статус)
- Exit code `0` — все обязательные проверки прошли; `1` — есть хотя бы одна провальная обязательная проверка
- Вывод в stderr: прогресс каждой проверки; итоговая строка `✅ Final check: PASS` или `❌ Final check: FAIL (N)`

**Проверки (в порядке выполнения):**

| Имя | Скрипт | Обязательная |
|-----|--------|-------------|
| wiki-sync | `check-wiki-sync.sh` | нет (WARN) |
| composed-premium | `verify-composed-premium.sh` | **да** |
| content-preserved | `verify-content-preserved.sh` | **да** |
| photo-pipeline | `verify-photo-pipeline.sh` | **да** |
| identity-preserved | `verify-identity-preserved.sh` | **да** |
| visual-qa | `verify-visual-qa.sh` | нет (WARN) |

Необязательные проверки при провале дают статус `⚠️ WARN` и не блокируют итоговый exit 0.

## Связанные концепты

- [[qa-auditor]] — агент этапа 10, проверяет живой сайт после деплоя; `landing-final-check` проверяет артефакты до деплоя
- [[premium-07b-checklist]] — стандарт, который проверяет `verify-composed-premium.sh`
- [[10-qa]] — этап pipeline, в котором используется этот скрипт
- [[landing-final-check]] — slash-команда (`/landing-final-check`), которая вызывает этот скрипт через skill
- [[verify-photo-pipeline]] — проверка идентичности и корректности photo-pipeline (PR-B)
- [[photo-curator]] — агент, чьи артефакты проверяет `verify-photo-pipeline`

## Источник

- `scripts/landing-final-check.sh`