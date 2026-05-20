---
type: agent
name: seo-optimizer
sources: ["agents/seo-optimizer.md"]
updated: 2026-05-20
triggers: []
stage: "12"
uses: ["analytics-engineer", "content-writer", "niche-analyst", "landing-orchestrator"]
tags: ["seo", "meta-tags", "schema-org", "wordpress", "stage-12"]
---

# seo-optimizer — SEO-оптимизатор лендинга

## Что делает
Добавляет мета-теги, Open Graph, Schema.org, robots.txt и список ключевых слов к готовому WordPress-лендингу. Превращает технически работающий сайт в сайт, понятный поисковым системам.

## Когда вызывать / в каком этапе
Запускается на **этапе 12 (12_SEO)** после того, как отработал [[analytics-engineer]] (этап 11). Агент проверяет `current_stage == 12_seo` в `.landing-state.yaml` и не начинает работу, пока предшествующие этапы не закрыты gate-check'ом.

Прямой вызов через [[landing-orchestrator]] или вручную в рамках шага `/landing-build`.

## Что на вход / на выход

**Вход:**
- `07_КОНТЕНТ/seo-copy.md` — SEO-варианты заголовков и description'ов (создаёт [[content-writer]])
- `08_КОД/wp-theme/functions.php` — уже существующий файл темы с маркером `// [SEO_META]`
- `00_БРИФ/brief.md` — ниша, гео, целевая аудитория, ключевые слова
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — поле `key_messages` как источник семантики (создаёт [[niche-analyst]])

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-функциями `lp_seo_meta()` и `lp_schema_org()`
- `12_SEO/meta-tags.yaml` — title, description, og-теги по правилам (50–60 / 140–160 символов)
- `12_SEO/structured-data.json` — Schema.org объект (LocalBusiness / Course / Organization)
- `12_SEO/robots.txt` — закрывает служебные страницы WP, открывает корень
- `12_SEO/keywords.md` — список ключевых слов из брифа

После генерации — **HARD GATE**: показывает `meta-tags.yaml` + `structured-data.json` и ждёт явного утверждения пользователя.

## Правила SEO внутри агента
- Title: 50–60 символов, ключевое слово первым
- Description: 140–160 символов, призыв к действию
- Один `h1` на странице, тематически совпадающий с title
- Канонический URL и Open Graph добавляются всегда
- Тип Schema.org выбирается по нише: `LocalBusiness` (услуги), `Course` (обучение), `Organization` (бренд)

## Связанные концепты
- [[analytics-engineer]] — должен отработать перед seo-optimizer (этап 11)
- [[content-writer]] — создаёт `seo-copy.md`, который агент использует как основу мета-текстов
- [[niche-analyst]] — создаёт `competitors.yaml` с семантикой конкурентов
- [[landing-orchestrator]] — диспатчит агента в рамках общего pipeline
- [[wp-builder]] — создаёт `functions.php`, куда агент дописывает SEO-функции

## Источник
- `agents/seo-optimizer.md`