---
type: rule
name: verify-composed-premium
sources: ["scripts/verify-composed-premium.sh", "scripts/verify-composed-premium.sh.doc.md"]
updated: 2026-05-18
triggers: ["проверить composed.html", "запустить verify", "HARD GATE 07b", "premium checklist"]
stage: "07b"
uses: ["premium-07b-checklist", "block-composer", "landing-build"]
tags: ["qa", "gate", "bash", "07b", "composed"]
---

# verify-composed-premium.sh — проверка premium-стандарта composed.html

## Что делает

Bash-скрипт автоматически проверяет `composed.html` на соответствие стандарту из `premium-07b-checklist.md`. Сканирует файл на наличие всех обязательных интерактивных и визуальных фич — и выдаёт exit-код: всё ок или чего-то не хватает.

## Когда вызывать / в каком этапе

Вызывается на этапе **07b (Block Compose)** как HARD GATE перед тем, как закрыть этап и двигаться дальше. `landing-orchestrator` не пропустит на этап 08 (build), пока скрипт не вернёт exit 0. Если `block-composer` сгенерировал `composed.html` — запускай этот скрипт немедленно.

```bash
bash scripts/verify-composed-premium.sh <путь/к/composed.html>
```

## Что на вход / на выход

**Вход:**
- `composed.html` — финальный скомпозированный HTML-файл (обычно `07b_COMPOSED/composed.html`)

**Выход (exit-коды):**
| Код | Смысл |
|-----|-------|
| `0` | Все premium-фичи найдены — этап закрыт |
| `1` | Одна или несколько фич отсутствуют — `block-composer` обязан доработать |
| `2` | Файл не найден по указанному пути |

Скрипт выводит список: какие фичи из чеклиста найдены, а какие отсутствуют — чтобы агент точно знал, что именно доработать.

## Связанные концепты

- [[premium-07b-checklist]] — полный перечень 13 обязательных premium-фич, которые скрипт ищет в HTML
- [[block-composer]] — агент, генерирующий `composed.html`; обязан переработать файл если exit 1
- [[07b-composed]] — этап pipeline, на котором живёт этот gate
- [[landing-build]] — следующий этап (08), куда нельзя перейти без exit 0
- [[landing-orchestrator]] — вызывает скрипт как часть проверки HARD GATE

## Источник

- `scripts/verify-composed-premium.sh`
- `scripts/verify-composed-premium.sh.doc.md`