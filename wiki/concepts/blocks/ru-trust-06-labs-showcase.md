---
type: block
name: ru-trust-06-labs-showcase
sources: ["block-library/trust/ru-trust-06-labs-showcase/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["trust", "portfolio", "cases", "grid", "ru-market", "b2c", "services", "local", "editorial", "opendesign"]
---

# Витрина проектов — сетка 5 кейсов с тегами

## Что делает

Показывает портфолио из 5 кейсов в редакционном стиле: карточки с нумерацией Nº, тегами-пилюлями по категориям и кратким описанием каждого проекта. Помогает клиентам быстро оценить опыт компании ещё до звонка.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** и **07b (Compose)**. Подходит для лендингов услуг (b2c, local-бизнес), где нужно показать портфолио без перехода на отдельную страницу. Вставляется агентами [[ux-composer]] и [[block-composer]] в секцию доверия (trust). Рекомендован при стилях **Editorial & Magazine** и **Minimalism & Swiss Style**.

## Что на вход / на выход

**Вход (слоты meta.yaml):**
- `kicker` — надзаголовок (до 50 символов, опционально)
- `headline` — главный заголовок секции (до 80 символов, обязателен)
- `tag-1` … `tag-4` — декоративные теги-пилюли (до 20 символов каждый, опционально)
- `lab-1-type` … `lab-5-type` — тип кейса (Дизайн / Разработка / Маркетинг и т.п.)
- `lab-1-title` … `lab-5-title` — заголовок кейса (до 50 символов, обязателен)
- `lab-1-desc` … `lab-5-desc` — краткое описание кейса (до 120 символов, обязателен)
- `lab-1-year` … `lab-5-year` — год выполнения (опционально)

**Выход:**
- HTML-блок с сеткой: 5 карточек в ряд (desktop) или 2×2 + 1 (mobile)
- Теги-пилюли носят декоративный характер — JS не требуется
- Нумерация Nº в редакционном стиле

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки на этапе wireframe
- [[block-composer]] — инжектирует design-tokens и prototype-тексты в composed.html
- [[wireframe-rendering]] — скилл рендеринга wireframe.html с этим блоком
- [[block-composition]] — скилл сборки composed.html, куда попадает блок
- [[block-library-management]] — управление каталогом блоков, включая этот

## Источник

- `block-library/trust/ru-trust-06-labs-showcase/meta.yaml`
- Основан на `open-design-landing` от [nexu-io/open-design](https://github.com/nexu-io/open-design) (Apache-2.0). Attribution: `THIRD_PARTY_NOTICES.md`.