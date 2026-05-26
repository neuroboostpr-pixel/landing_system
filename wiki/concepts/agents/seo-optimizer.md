---
type: agent
name: seo-optimizer
sources: ["agents/seo-optimizer.md"]
updated: 2026-05-26
triggers: []
stage: "12_seo"
uses:
  - stage-execution-protocol
  - landing-orchestrator
  - analytics-engineer
tags: ["seo", "meta-tags", "schema-org", "wordpress", "stage-12"]
---

# SEO-оптимизатор

## Что делает

Добавляет в готовый WordPress-лендинг всё необходимое для продвижения в поисковиках: мета-теги, Open Graph, Schema.org разметку, robots.txt и список ключевых слов. Работает автоматически по материалам из предыдущих этапов — маркетологу не нужно разбираться в технических тонкостях SEO.

## Когда вызывать / в каком этапе

Запускается на этапе **12_seo** — после `analytics-engineer` (этап 11), когда тема WordPress уже задеплоена. Вызывается через `landing-orchestrator` в рамках общего pipeline. Обязательное предусловие: `.landing-state.yaml` должен содержать `current_stage == 12_seo`, иначе агент останавливается.

Перед началом работы агент:
1. Читает `.landing-state.yaml` и показывает Mermaid-карту pipeline.
2. Запускает `gate-check.sh --stage 12_seo` — продолжает только при exit 0.
3. Формирует TodoWrite со всеми оставшимися этапами.

## Что на вход / на выход

**Вход:**
- `07_КОНТЕНТ/seo-copy.md` — SEO-варианты заголовков, descriptions, h1
- `00_БРИФ/brief.md` — ниша, гео, целевая аудитория, CTA
- `08_КОД/wp-theme/functions.php` — уже существующий файл темы (с маркером `// [SEO_META]`)
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — поле `key_messages` как источник семантики

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-функциями `lp_seo_meta()` и `lp_schema_org()`
- `12_SEO/meta-tags.yaml` — title / description / og-теги по правилам длины
- `12_SEO/structured-data.json` — Schema.org объект (LocalBusiness / Course / Organization)
- `12_SEO/robots.txt` — запрет служебных страниц WP, Allow: /
- `12_SEO/keywords.md` — ключевые слова из брифа

**HARD GATE:** перед финальной записью агент показывает `meta-tags.yaml` и `structured-data.json` и ждёт явного утверждения пользователем.

## Правила SEO

- **Title:** 50–60 символов, ключевое слово стоит первым
- **Description:** 140–160 символов, содержит призыв к действию
- **h1:** один на странице, тема совпадает с title
- **Schema.org тип:** `LocalBusiness` (услуги), `Course` (обучение) или `Organization`

## Связанные концепты

- [[stage-execution-protocol]] — обязательный протокол, который агент исполняет перед любым Write/Edit
- [[landing-orchestrator]] — вызывает агента в рамках общего pipeline на этапе 12
- [[analytics-engineer]] — предшествующий агент, чья работа является предусловием

## Источник

- `agents/seo-optimizer.md`