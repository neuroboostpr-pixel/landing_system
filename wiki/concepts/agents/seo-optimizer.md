---
slug: seo-optimizer
type: agent
name: "SEO-оптимизатор"
stage: "12"
tags: [seo, meta-tags, schema-org, robots, sitemap, wp-theme]
triggers: []
inputs: [07-kontent, 00-brif, 01a-analiz-nishi, 08-kod]
outputs: [12-seo, 08-kod]
gates: [seo_meta_approved]
pre_reqs: [analytics-engineer, 11-analitika, 08-kod, 07-kontent]
related: [analytics-engineer, seo-tech-audit, landing-build, landing-deploy, 12-seo, 08-kod, 07-kontent]
sources: ["agents/seo-optimizer.md"]
updated: 2026-06-19
confidence: {triggers: low, stage: low}
---

# SEO-оптимизатор

## Что делает

Закрывает этап 12_SEO: добавляет мета-теги и Schema.org в `functions.php` темы, генерирует файловые артефакты (`meta-tags.yaml`, `structured-data.json`, `robots.txt`, `keywords.md`, `sitemap.xml`) и размещает их в папке `12_SEO/`. Читает SEO-копирайт из контентного этапа и ключевые сообщения конкурентов из анализа ниши, чтобы title и description соответствовали семантике и не выходили за лимиты (50–60 / 140–160 символов). Тип Schema.org выбирается по нише: LocalBusiness, Course или Organization.

## Когда вызывается

Вызывается оркестратором на этапе `12_seo`, строго после `analytics-engineer`. Перед запуском агент проверяет `.landing-state.yaml` — если `current_stage != 12_seo`, выполнение останавливается. Физический harness-hook `enforce_stage_gate.py` блокирует запись, пока предшественники не закрыты.

## Вход → выход

**Вход:**
- `07_КОНТЕНТ/seo-copy.md` — варианты title, description, h1
- `00_БРИФ/brief.md` — ниша, гео, CTA, ключевые слова
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — поле `key_messages` для семантики
- `08_КОД/wp-theme/functions.php` — тема с маркером `// [SEO_META]`

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен функциями `lp_seo_meta()` и `lp_schema_org()`
- `12_SEO/meta-tags.yaml` — title / description / og-теги
- `12_SEO/structured-data.json` — Schema.org объект
- `12_SEO/robots.txt` — запрет служебных путей WP + директива `Sitemap:`
- `12_SEO/keywords.md` — ключевые слова проекта
- `12_SEO/sitemap.xml` — главная + `/policy` + `/consent`

## Чем закрывается этап (gates)

- `seo_meta_approved` — агент показывает `meta-tags.yaml` и `structured-data.json`, ждёт явного утверждения пользователем перед тем как выполнять запись в `functions.php` и финализировать артефакты

## Failure modes

- `current_stage` в `.landing-state.yaml` не равен `12_seo` — агент останавливается; нужно закрыть предшественников через `gate-state.sh`
- `seo-copy.md` отсутствует или пуст — title/description генерируются по брифу «на угад», качество низкое; перед запуском должен быть пройден этап 07-kontent
- Маркер `// [SEO_META]` отсутствует в `functions.php` — вставка SEO-функций провалится или задублирует хуки; нужна ручная правка файла темы
- `robots.txt` не содержит директиву `Sitemap:` — поисковик не найдёт карту сайта; скрипт генерации sitemap должен запускаться до финального gate
- Schema.org тип не соответствует нише (например, `LocalBusiness` вместо `Course`) — снижает релевантность в поиске; нужно явно проверять поле `niche` в брифе перед генерацией

## Related

- [[analytics-engineer]] — предшественник; SEO-оптимизатор вызывается строго после него
- [[seo-tech-audit]] — аудитор этапа 11; проверяет уже задеплоенный сайт по 43 HTTP-проверкам, включая теги и Schema.org
- [[landing-build]] — этап 08, где `functions.php` создаётся впервые; SEO-оптимизатор дополняет его
- [[landing-deploy]] — этап 09; после деплоя `sitemap.xml` копируется в корень сайта через `scp`
- [[07-kontent]] — источник SEO-текстов (seo-copy.md)
- [[12-seo]] — папка-адресат всех выходных артефактов этапа