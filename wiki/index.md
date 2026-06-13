# Landing-System Wiki — главный индекс

> Авто-сгенерированный индекс. Обновляется при `python -m scripts.wiki.compile --source-mode=system`.

**Концептов всего:** 108
**Категории:** agent, catalog, command, rule, skill, stage, unknown

**Известные ограничения:**
- Блоки из `block-library/` ещё не в wiki — отдельная задача.
- Часть `[[wikilinks]]` ссылается на скрипты/конфиги вне wiki — это норма.

## 📋 Этапы pipeline

- [[00-brif]] — 00 — Бриф проекта
- [[01-kontekst]] — 01 — Контекст проекта
- [[01a-analiz-nishi]] — 01a. Анализ ниши
- [[02-materialy-klienta]] — Сбор материалов клиента (02)
- [[03-referensy]] — Этап 03: Референсы
- [[04-brend]] — 04 — Сборка бренд-кита
- [[05-dizayn-sistema]] — Этап 05: Генерация дизайн-системы
- [[06-stek]] — Стек технологий
- [[07-kontent]] — 07 — Написание контента
- [[07-prototip]] — 07 Прототип — импорт источника правды
- [[07b-composed]] — 07b — Composed HTML
- [[07c-photos]] — 07c — Фото клиента и Photo Pipeline
- [[07d-visuals]] — 07d — Иконки и инфографика
- [[08-kod]] — 08_КОД — WordPress-код лендинга
- [[09-deploy]] — 09 Деплой
- [[10-qa]] — QA-аудит
- [[11-analitika]] — 11 — Аналитика
- [[12-seo]] — 12_SEO — SEO-финализация
- [[13-segmenty-tsa]] — 13_СЕГМЕНТЫ_ЦА — Сегменты целевой аудитории

## 🤖 Агенты

- [[analytics-engineer]] — Инженер аналитики
- [[block-composer]] — Block Composer (Сборка composed.html)
- [[brand-architect]] — Brand Architect
- [[client-assets-collector]] — Сборщик клиентских материалов
- [[content-writer]] — Контент-райтер
- [[design-system-generator]] — Генератор дизайн-системы
- [[frontend-builder]] — Frontend Builder — CSS и PHP шаблоны блоков
- [[icon-generator]] — Генератор иконок
- [[infographic-builder]] — Infographic Builder
- [[integrations-engineer]] — integrations-engineer
- [[landing-onboarding-wizard]] — Онбординг-визард нового проекта
- [[lifecycle-keeper]] — Lifecycle Keeper — Хранитель версий
- [[moodboard-composer]] — Moodboard Composer
- [[niche-analyst]] — Аналитик ниши (Stage 01a)
- [[onboarding-guide]] — Проводник по онбордингу
- [[photo-classifier]] — Классификатор фото
- [[photo-matcher]] — Агент сопоставления фото со слотами
- [[photo-preview-board]] — Photo Preview Board — обработка слотов и рендер превью
- [[photo-stylist]] — Photo Stylist
- [[prototype-importer]] — Импортёр прототипа
- [[qa-auditor]] — QA-аудитор
- [[references-curator]] — Куратор референсов
- [[scene-director]] — Режиссёр сцен (Cinematic Premium)
- [[seo-optimizer]] — SEO-оптимизатор
- [[stack-planner]] — Планировщик стека (Stack Planner)
- [[style-extractor]] — Style Extractor
- [[system-setup]] — Настройщик системы
- [[visual-curator]] — Куратор визуалов
- [[wp-builder]] — WP-сборщик (Lazy Blocks)
- [[wp-deployer]] — WP Deployer — Деплой-инженер

## 🛠 Скиллы

- [[block-composition]] — Block Composition — сборка composed.html
- [[brand-kit-build]] — Построение бренд-кита
- [[client-assets-collection]] — Сбор материалов клиента
- [[design-tokens-generation]] — Генерация дизайн-токенов
- [[gpt5-prompting-engine]] — GPT-5 Prompting Engine
- [[landing-from-context]] — Создание лендинга из контекста агентства
- [[landing-onboarding]] — Онбординг landing-system
- [[landing-project-init]] — Инициализация нового проекта лендинга
- [[landing-versioning-and-cloning]] — Версионирование и клонирование лендингов (legacy)
- [[niche-analysis]] — Анализ ниши и конкурентов
- [[photo-curation]] — Конвейер обработки клиентских фото (Photo Curation)
- [[photo-styling]] — Стилизация фото
- [[prototype-import]] — Импорт прототипа
- [[references-collection]] — Управление индексом референсов
- [[seo-tech-audit]] — SEO Tech Audit
- [[style-decomposition]] — Декомпозиция стиля (Style Decomposition)
- [[visual-generation]] — Генерация визуалов (иконки и инфографика)
- [[visual-qa]] — Visual QA — автоматический визуальный контроль
- [[wiki-routing-observability]] — Wiki Routing Observability
- [[wp-cli-deployer]] — WP-CLI Deployer
- [[wp-landing-config]] — WP Landing Config — mu-plugin для настройки лендинга
- [[wp-multisite]] — WP Multisite — управление Multisite-сетью на Beget
- [[wp-theme-assembler]] — Сборщик WordPress-темы

## ⚡ Команды

- [[landing-brand]] — /landing-brand — Построить бренд-кит
- [[landing-build]] — /landing-build — Сборка WordPress-темы
- [[landing-clone]] — Клонирование лендинга
- [[landing-compose]] — /landing-compose — Сборка composed.html
- [[landing-content]] — Контент-адаптация прототипа (Stage 07)
- [[landing-deploy]] — Деплой лендинга на Бегет (/landing-deploy)
- [[landing-design]] — Генерация дизайн-системы (этап 05)
- [[landing-final-check]] — Финальная проверка лендинга
- [[landing-from-context]] — Создать лендинг из контекста агентства
- [[landing-go]] — /landing-go — Главная команда оркестратора
- [[landing-help]] — Справка по командам системы
- [[landing-moodboard]] — Команда /landing-moodboard
- [[landing-new]] — /landing-new — создать новый проект лендинга
- [[landing-niche]] — Анализ ниши /landing-niche
- [[landing-onboarding]] — Команда первичной настройки /landing-onboarding
- [[landing-photos]] — /landing-photos — Конвейер клиентских фото (stage 07c)
- [[landing-previews]] — /landing-previews — Превью на устройствах
- [[landing-prototype]] — /landing-prototype — Импорт прототипа
- [[landing-qa]] — /landing-qa — Визуальный QA лендинга
- [[landing-references]] — Сбор визуальных референсов
- [[landing-rollback]] — Откат лендинга к предыдущей версии
- [[landing-setup]] — Инициализация системы (/landing-setup)
- [[landing-stack]] — Планирование стека WordPress (этап 06)
- [[landing-start]] — /landing-start — Онбординг-визард
- [[landing-status]] — Статус системы и проекта
- [[landing-style]] — /landing-style — CSS и block.php для этапа 08b
- [[landing-visuals]] — /landing-visuals — Генерация визуальных ассетов

## 📐 Правила (стандарты качества)

- [[premium-07b-checklist]] — PREMIUM 07b — Чек-лист сборки composed.html
- [[stage-08-spec-lint]] — Stage-08 Composed ↔ block-spec Lint
- [[stage-agent-preamble]] — Stage Agent Preamble (канонический блок)
- [[stage-execution-protocol]] — Протокол выполнения этапов (обязательный)
- [[wiki-audit-checklist]] — Wiki Audit Checklist

## ❓ Прочее

- [[landing-orchestrator]] — landing-orchestrator
