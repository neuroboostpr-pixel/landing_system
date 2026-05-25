---
type: agent
name: seo-optimizer
sources: ["agents/seo-optimizer.md"]
updated: 2026-05-25
triggers: []
stage: "12"
uses: ["landing-orchestrator", "analytics-engineer", "stage-execution-protocol"]
tags: ["seo", "schema", "meta", "wordpress", "stage-12"]
---

# seo-optimizer — SEO-оптимизатор лендинга

## Что делает

Добавляет на лендинг всё необходимое для поисковых систем: мета-теги, Schema.org разметку, robots.txt и файл с ключевыми словами. Работает после того, как контент и WordPress-тема уже готовы.

## Когда вызывать / в каком этапе

Активируется на **этапе 12 (12_SEO)** после завершения работы `analytics-engineer`. Запускается через `landing-orchestrator` или вручную. Перед любыми изменениями агент проверяет, что `.landing-state.yaml` содержит `current_stage == 12_seo`, запускает `gate-check.sh` и показывает Mermaid-карту пайплайна. Если предшествующие этапы не закрыты — STOP.

## Что на вход / на выход

**Вход:**
- `07_КОНТЕНТ/seo-copy.md` — SEO-заголовки и descriptions, подготовленные контент-агентом
- `00_БРИФ/brief.md` — ниша, гео, ЦА, CTA
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — ключевые сообщения конкурентов (источник семантики)
- `08_КОД/wp-theme/functions.php` — должен существовать и содержать плейсхолдер `// [SEO_META]`

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-функциями `lp_seo_meta()` и `lp_schema_org()`
- `12_SEO/meta-tags.yaml` — title, description, og-поля
- `12_SEO/structured-data.json` — Schema.org объект (LocalBusiness / Course / Organization)
- `12_SEO/robots.txt` — запрет служебных страниц WP, Allow: /
- `12_SEO/keywords.md` — ключевые слова из брифа

**HARD GATE:** перед финальной записью агент показывает `meta-tags.yaml` и `structured-data.json` и ждёт явного утверждения от пользователя.

## Правила SEO

- Title: 50–60 символов, ключевое слово первым
- Description: 140–160 символов, включает призыв к действию
- H1 — один на странице, тематически совпадает с title
- Schema.org тип выбирается по нише: `LocalBusiness` (услуги), `Course` (обучение), `Organization`

## Связанные концепты

- [[landing-orchestrator]] — диспатчит агента на этапе 12
- [[analytics-engineer]] — предшествующий агент, после которого запускается seo-optimizer
- [[stage-execution-protocol]] — обязательный протокол проверки gate-check перед любым действием

## Источник

- `agents/seo-optimizer.md`