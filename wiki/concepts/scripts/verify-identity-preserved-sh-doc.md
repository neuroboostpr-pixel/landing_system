---
type: rule
name: verify-identity-preserved
sources: ["scripts/verify-identity-preserved.sh", "scripts/verify-identity-preserved.sh.doc.md"]
updated: 2026-05-18
triggers: []
stage: "07f"
uses: ["photo-curator", "photo-preview-board", "stage-gates"]
tags: ["identity-safe", "photo-pipeline", "hard-check", "gate"]
---

# verify-identity-preserved — проверка сохранения идентичности на фото

## Что делает

Проверяет, что клиентские фотографии не были искажены AI-обработкой: лица, возраст и пропорции людей остались нетронутыми. Если хотя бы один слот нарушает порог сходства — скрипт падает с ошибкой и блокирует переход на следующий этап.

## Когда вызывать / в каком этапе

Запускается автоматически как `hard_check` в stage-gate **07f** (финальная сборка composed.html с реальными фото). Без прохождения этой проверки оркестратор не пропускает проект дальше. Вызывается через `scripts/gate-check.sh`.

## Что на вход / на выход

**Вход:**
- `$1` — путь к папке проекта (обязательный аргумент)
- `<project>/07c_PHOTOS/processed/manifest.json` — манифест обработанных фото; каждая запись может содержать флаг `identity_violation`, `distance` и `threshold`

**Выход:**
- `exit 0` + сообщение `✅ Identity сохранён` — все слоты чисты (или манифест отсутствует)
- `exit 1` + список нарушений в stderr с указанием слота, расстояния и порога — gate провален

**Пример нарушения в stderr:**
```
❌ Identity violations (2):
  - hero-portrait: distance=0.42 > threshold=0.25
  - team-member-2: distance=0.38 > threshold=0.25
```

## Связанные концепты

- [[photo-curator]] — оркестрирует этап 07c, формирует `manifest.json` с флагами обработки
- [[photo-preview-board]] — финальная обработка фото (crop/resize/AI fallback), которая может создать нарушения
- [[stage-gates]] — конфиг hard/soft проверок по этапам; этот скрипт является `hard_check` для 07f
- [[photo-stylist]] — identity-safe стилизация; не должна нарушать пороги этого скрипта

## Источник

- `scripts/verify-identity-preserved.sh`
- `scripts/verify-identity-preserved.sh.doc.md`