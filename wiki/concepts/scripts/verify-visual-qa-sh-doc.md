---
type: rule
name: verify-visual-qa
sources: ["scripts/verify-visual-qa.sh", "scripts/verify_visual_qa.py"]
updated: 2026-05-18
triggers: []
stage: "10"
uses: ["qa-auditor", "visual-qa", "landing-qa", "stage-gates"]
tags: ["script", "qa", "soft-check", "stage-gates", "visual-qa"]
---

# verify-visual-qa.sh — мягкая проверка Visual QA

## Что делает

Проверяет, что в проекте создан отчёт Visual QA и в нём нет критических проблем. Это **мягкая (soft) проверка** — провал не блокирует сборку, но фиксируется в финальном чеклисте.

## Когда вызывать / в каком этапе

Вызывается автоматически скриптом `landing-final-check.sh` как часть итогового контроля качества (stage 10). Также можно запустить вручную:

```bash
bash scripts/verify-visual-qa.sh ~/Lendings/<slug>
```

Ожидает, что к этому моменту уже был запущен `/landing-qa`, который создаёт файл `10_QA/visual-qa-report.md`.

## Что на вход / на выход

**Вход:**
- `$1` — путь к папке проекта (обязательный аргумент)
- `<project>/10_QA/visual-qa-report.md` — отчёт, созданный командой `/landing-qa`

**Выход (exit-коды):**
| Код | Смысл |
|-----|-------|
| `0` | Отчёт есть, критических проблем нет — всё ОК |
| `1` | В отчёте обнаружены `### CRITICAL` или `CRITICAL (` — есть критические замечания |
| `2` | Файл отчёта отсутствует — Visual QA ни разу не запускался |

При exit 2 в stderr выводится подсказка: `Запусти: /landing-qa <project>`.

**Внутренняя реализация:** bash-обёртка, делегирующая всю логику Python-скрипту `scripts/verify_visual_qa.py`. Python-скрипт читает отчёт и ищет ключевые слова критических ошибок простым `in`-поиском по тексту.

## Место в финальном чеклисте

Скрипт зарегистрирован в `landing-final-check.sh` как **необязательная** проверка (`required = no`). Это значит, что при падении в финальном отчёте появится `WARN`, но общий exit-код `landing-final-check.sh` не станет ненулевым. В отличие от обязательных проверок (`composed-premium`, `photo-pipeline`, `identity-preserved`), провал здесь не блокирует деплой.

## Связанные концепты

- [[qa-auditor]] — агент, запускающий visual QA и создающий `visual-qa-report.md`
- [[visual-qa]] — скилл визуальной проверки качества лендинга
- [[landing-qa]] — команда, инициирующая создание отчёта
- [[stage-gates]] — система контрольных точек между этапами; этот скрипт — один из soft-checks

## Источник

- `scripts/verify-visual-qa.sh`
- `scripts/verify_visual_qa.py`