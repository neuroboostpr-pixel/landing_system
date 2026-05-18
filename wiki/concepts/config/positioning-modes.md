---
type: rule
name: positioning-modes
sources: ["config/positioning-modes.yaml"]
updated: 2026-05-18
triggers: []
stage: "01a"
uses: ["niche-analyst", "niche-analysis"]
tags: ["positioning", "niche", "config", "registry"]
---

# Positioning Modes — реестр режимов позиционирования

## Что делает
Хранит три канонических режима позиционирования лендинга (rational, emotional_aspiration, trust_authority) и матрицу автоматического выбора режима по параметрам ниши. Агент `niche-analyst` читает этот файл на шаге 7 анализа и назначает проекту один режим (или гибрид двух).

## Когда вызывать / в каком этапе
Файл читается автоматически агентом [[niche-analyst]] во время этапа **01a (Анализ ниши)**. Ручного вызова не требует — вся логика инкапсулирована внутри скилла [[niche-analysis]].

## Что на вход / на выход

**Вход (читает из брифа/контекста):**
- `accessibility_tier` — ценовой уровень продукта (utility_essential → ultra_luxury)
- `regulated` — регулируется ли ниша (медицина, финансы, юриспруденция)
- `emotional_load` — высокая / низкая эмоциональная нагрузка
- `brief_indicators` — ключевые слова из брифа (экономия, премиум, сертификат и т.д.)

**Выход (что пишется в артефакты 01a):**
- Назначенный режим позиционирования: `rational` | `emotional_aspiration` | `trust_authority` | гибрид
- Список шаблонных секций (template_sections) для выбранного режима — структура нарратива лендинга

## Три режима

| Режим | Суть | Типичные ниши |
|---|---|---|
| `rational` | Продажа через факты, ROI, метрики | B2B SaaS, утилиты, commodity |
| `emotional_aspiration` | Продажа через статус и identity | Luxury, lifestyle, premium авто |
| `trust_authority` | Продажа через доверие и снятие риска | Медицина, юридия, финансы |

Матрица `mode_prediction_matrix` сопоставляет комбинацию (tier + regulated + emotional_load) с конкретным режимом или гибридом. Гибрид записывается через `+`, например `hybrid:emotional_aspiration+trust_authority`.

## Связанные концепты
- [[niche-analyst]] — агент, который читает этот реестр и применяет матрицу
- [[niche-analysis]] — скилл, реализующий логику классификации ниши
- [[01a-analiz-nishi]] — этап pipeline, в котором происходит выбор режима

## Источник
- `config/positioning-modes.yaml`