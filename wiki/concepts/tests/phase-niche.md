Файлов `.bats` ещё нет на диске — ориентируюсь на README и имена файлов как источники семантики.

---
type: unknown
name: phase-niche-tests
sources: ["tests/phase-niche/README.md"]
updated: 2026-05-18
triggers: []
stage: "01a"
uses: ["niche-analyst", "niche-analysis", "positioning-modes", "niche-visual-rules"]
tags: ["tests", "bats", "pytest", "phase-niche"]
---

# Тесты phase-niche — автотесты анализа ниши и позиционирования

## Что делает
Группа автотестов, которая проверяет корректность этапа анализа ниши (01a): работу оркестратора с нишевыми данными, правила позиционирования и визуальные нормы для разных типов ниш.

## Когда вызывать / в каком этапе
Запускается вручную или через CI после любых изменений в агенте `niche-analyst`, скилле `niche-analysis`, конфигах `positioning-modes` и `niche-visual-rules`. Этап 01a pipeline.

## Что на вход / на выход

**Вход:**
- Тестовые fixtures (бриф, `market-profile.md`, `.landing-state.yaml`)
- Код агента `niche-analyst` и связанных скриллов

**Выход:**
- Результат bats/pytest с pass/fail по каждому тест-кейсу
- Покрывает 5 сценариев:
  - `test-e2e-skip-prevention` — проверка, что этап 01a нельзя пропустить (hard gate)
  - `test-migrate-niche-to-v2` — миграция старых нишевых данных в формат v2
  - `test-niche-stage` — корректность артефактов этапа (market-profile, brand-type, mode)
  - `test-positioning-modes` — логика выбора одного из 3 режимов позиционирования
  - `test-visual-rules` — соответствие визуальных норм типу ниши

## Связанные концепты
- [[niche-analyst]] — агент, чья работа тестируется в `test-niche-stage`
- [[niche-analysis]] — скилл, реализующий логику анализа
- [[positioning-modes]] — правило выбора режима (rational / emotional / trust), тестируется в `test-positioning-modes`
- [[niche-visual-rules]] — стандарт визуала по нише, тестируется в `test-visual-rules`
- [[stage-gates]] — hard gate 01a проверяется в `test-e2e-skip-prevention`
- [[01a-analiz-nishi]] — соответствующий этап pipeline

## Источник
- `tests/phase-niche/README.md`