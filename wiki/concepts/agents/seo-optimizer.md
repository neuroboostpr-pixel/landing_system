---
type: agent
name: seo-optimizer
sources: ["agents/seo-optimizer.md"]
updated: 2026-05-15
triggers: ["оптимизировать SEO", "добавить мета-теги", "настроить Schema.org", "создать robots.txt", "ключевые слова для лендинга"]
stage: "08"
uses: ["analytics-engineer", "content-writer", "niche-analyst", "wp-builder"]
tags: ["seo", "meta-tags", "schema-org", "robots-txt", "wordpress", "stage-08"]
---

# seo-optimizer — SEO-оптимизатор лендинга

## Что делает

Подключает лендинг к поисковым системам: прописывает мета-теги, Open Graph, Schema.org и robots.txt на основе готового SEO-текста и данных брифа. Делает страницу видимой и правильно отображаемой в Google и Яндексе.

## Когда вызывать / в каком этапе

Запускается на **этапе 08** — строго после `analytics-engineer`. Вызывается агентом `landing-orchestrator` в рамках команды `/landing-build` или `/landing-go`. Вручную не вызывается. Перед запуском обязательны: утверждённый SEO-текст (`07_КОНТЕНТ/seo-copy.md`), бриф (`00_БРИФ/approved-design-brief.md`) и существующий `functions.php` от `wp-builder`.

## Что на вход / на выход

**Вход:**
- `07_КОНТЕНТ/seo-copy.md` — title, description, h1 варианты от `content-writer`
- `00_БРИФ/approved-design-brief.md` — ниша, гео, CTA, ключевые слова
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — ключевые сообщения конкурентов для расширения семантики
- `08_КОД/wp-theme/functions.php` — WordPress-файл с маркером `// [SEO_META]`

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен функциями `lp_seo_meta()` и `lp_schema_org()`
- `12_SEO/meta-tags.yaml` — title / description / og-поля
- `12_SEO/structured-data.json` — Schema.org объект (LocalBusiness / Course / Organization)
- `12_SEO/robots.txt` — запрет служебных страниц WP, Allow: /
- `12_SEO/keywords.md` — список ключевых слов из брифа

**HARD GATE:** после генерации агент показывает `meta-tags.yaml` и `structured-data.json` и ждёт явного утверждения пользователем перед завершением этапа.

## SEO-правила агента

- Title: 50–60 символов, ключевое слово стоит первым
- Description: 140–160 символов, содержит призыв к действию
- h1 — один на странице, совпадает с тематикой title
- Schema.org тип выбирается по нише: `LocalBusiness` (услуги), `Course` (обучение), `Organization` (бренд)

## Связанные концепты

- [[analytics-engineer]] — должен завершиться перед запуском seo-optimizer (добавляет Яндекс.Метрику)
- [[content-writer]] — поставляет `seo-copy.md` с вариантами SEO-текста
- [[niche-analyst]] — поставляет `competitors.yaml` с ключевыми сообщениями ниши
- [[wp-builder]] — создаёт `functions.php`, в который агент вписывает SEO-функции
- [[landing-orchestrator]] — вызывает агента в нужный момент этапа 08

## Источник

- `agents/seo-optimizer.md`