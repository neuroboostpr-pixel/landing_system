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

# seo-optimizer — SEO-оптимизатор

## Что делает
Добавляет поисковую оптимизацию на готовый лендинг: прописывает мета-теги, генерирует Schema.org разметку и robots.txt. Вся SEO-конфигурация сохраняется в папке `12_SEO/` и внедряется в WordPress-тему через `functions.php`.

## Когда вызывать / в каком этапе
Запускается на **этапе 12 (12_seo)** после того, как отработал [[analytics-engineer]]. Вызывается агентом [[landing-orchestrator]] автоматически в рамках `stage 08`–`12` финальной сборки. Перед стартом агент проверяет `.landing-state.yaml`: текущий этап должен быть `12_seo`, иначе он останавливается и сообщает об ошибке.

## Что на вход / на выход

**Вход:**
- `07_КОНТЕНТ/seo-copy.md` — title, description, h1-варианты от [[content-writer]]
- `00_БРИФ/brief.md` — ниша, гео, целевая аудитория, ключевые слова
- `08_КОД/wp-theme/functions.php` — уже существующий файл темы с placeholder `// [SEO_META]`
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — поле `key_messages` как источник семантики (генерируется [[niche-analyst]])

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-функциями `lp_seo_meta()` и `lp_schema_org()`
- `12_SEO/meta-tags.yaml` — title, description, og-теги в структурированном формате
- `12_SEO/structured-data.json` — Schema.org объект (LocalBusiness / Course / Organization)
- `12_SEO/robots.txt` — запрет служебных страниц WordPress, Allow `/`
- `12_SEO/keywords.md` — список ключевых слов из брифа

**HARD GATE:** перед записью файлов агент показывает `meta-tags.yaml` и `structured-data.json` и ждёт явного утверждения пользователя.

## Ключевые правила SEO
- Title: 50–60 символов, ключевое слово стоит первым
- Description: 140–160 символов с призывом к действию
- H1: один на странице, тема совпадает с title
- Schema.org тип выбирается по нише: `LocalBusiness` для услуг, `Course` для обучения, `Organization` в остальных случаях

## Связанные концепты
- [[analytics-engineer]] — предшествующий агент; должен завершиться до запуска seo-optimizer
- [[content-writer]] — поставляет `seo-copy.md` с вариантами заголовков и описаний
- [[niche-analyst]] — поставляет `competitors.yaml` с семантикой конкурентов
- [[landing-orchestrator]] — диспатчит агента в нужный момент pipeline
- [[wp-builder]] — создаёт `functions.php`, в который seo-optimizer вписывает SEO-функции

## Источник
- `agents/seo-optimizer.md`