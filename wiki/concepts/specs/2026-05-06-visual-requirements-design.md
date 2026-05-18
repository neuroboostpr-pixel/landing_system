---
type: rule
name: visual-requirements
sources: ["docs/superpowers/specs/2026-05-06-visual-requirements-design.md"]
updated: 2026-05-18
triggers: []
stage: "01a"
uses: ["niche-analyst", "niche-visual-rules", "client-assets-collector", "moodboard-composer", "references-curator", "wp-builder", "stage-gates"]
tags: ["visual", "niche", "artifact", "spec"]
---

# Visual Requirements — артефакт визуальных требований

## Что делает

Фиксирует визуальный язык лендинга ещё на этапе анализа ниши: что должно быть в Hero, какой стиль фотографии использовать, каких визуальных «ловушек» избегать. Превращает неформальное «выглядит дёшево» в конкретный письменный контракт, который все downstream-агенты обязаны соблюдать.

## Когда вызывать / в каком этапе

Артефакт `visual-requirements.md` создаётся автоматически агентом [[niche-analyst]] в шаге 9 — последнем шаге анализа ниши (этап `01a`). Ручного запуска не требуется: файл появляется вместе с `market-profile.md`, `competitors.yaml` и другими артефактами этапа. Начиная с версии этого спека, `gate-check.sh` для этапа 01a проверяет наличие файла как обязательный hard-check.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — бриф клиента
- `01_КОНТЕКСТ/context.md` — контекстные данные
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — данные по конкурентам (поле `visual_notes`)
- `config/niche-visual-rules.yaml` — встроенный справочник категорий (5 категорий: `premium_automotive`, `local_services`, `professional_services`, `b2c_consumer`, `default`)

**Выход:**
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — 250–400 слов, 7 разделов:
  1. Hero focal point (что в центре первого экрана)
  2. Photography style (studio / lifestyle / documentary)
  3. People in frame (да / нет / optional)
  4. Product treatment в каталоге
  5. Background palette (допустимые и запрещённые фоны)
  6. Red flags (≥3 запретов ❌ + ≥3 предпочтений ✅ с обоснованиями)
  7. Источники правил (ссылки на справочник и конкретных конкурентов)

**Новые файлы системы:**
- `config/niche-visual-rules.yaml` — справочник визуальных категорий ниш
- `tests/phase-niche/test-visual-rules.bats` — тесты валидации справочника

## Связанные концепты

- [[niche-analyst]] — пишет артефакт (шаг 9 в алгоритме); читает `niche-visual-rules.yaml`
- [[niche-visual-rules]] — конфиг-справочник категорий, из которого берутся базовые правила
- [[client-assets-collector]] — читает секции 1–4 и 6, чтобы правильно запрашивать фото у клиента
- [[moodboard-composer]] — читает секции 1–3, 5, 6, чтобы не сохранять запрещённые референсы
- [[references-curator]] — сверяет предложенные референсы с секцией 6 (Red flags)
- [[wp-builder]] — sanity-check ассетов перед сборкой темы по секциям 1, 4, 5
- [[stage-gates]] — новый hard-check `visual_requirements_md` в конфиге этапа `01a_niche_analysis`
- [[01a-analiz-nishi]] — этап, в котором живёт артефакт

## Источник

- `docs/superpowers/specs/2026-05-06-visual-requirements-design.md`