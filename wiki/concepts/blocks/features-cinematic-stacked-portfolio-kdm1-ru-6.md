---
type: block
name: features-cinematic-stacked-portfolio-kdm1-ru-6
sources: ["block-library/features/features-cinematic-stacked-portfolio-kdm1-ru-6/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "cinematic", "stacked", "education", "services", "ru-market"]
---

# Секция заданий с крупными иллюстрациями и двумя текстовыми зонами

## Что делает
Блок типа «features» в стиле cinematic: показывает задания или направления сервиса через крупные иллюстрации людей, сопровождённые двумя смысловыми текстовыми зонами. Подходит для визуального акцента на ключевых предложениях или шагах программы.

## Когда вызывать / в каком этапе
Используется на этапе **07a (UX Wireframe)** при выборе блоков для секции «features» (преимущества, задания, направления). `ux-composer` подбирает блок из библиотеки по нише и mood-стилю; `block-composer` применяет его на этапе **07b (Compose)** с инъекцией токенов дизайна и текстов прототипа.

Подходит для ниш:
- **education** — онлайн-школы, курсы, наставничество
- **services** — сервисные компании с несколькими направлениями

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции
- Иллюстрации людей — подставляются через photo-slots (PR-B)
- Токены дизайна из `tokens.json` (цвет, шрифт, отступы)

**Выход:**
- HTML-блок внутри `wireframe.html` (этап 07a) — интерактивный вариант для выбора
- HTML-блок внутри `composed.html` (этап 07b) — с реальным контентом и токенами
- Photo-слоты передаются в `photo-curator` (этап 07c) для подбора клиентских фото

## Связанные концепты
- [[ux-composer]] — выбирает этот блок при рендере wireframe.html
- [[block-composer]] — применяет блок в composed.html с инъекцией токенов
- [[wireframe-rendering]] — скилл рендера 07a, использует meta.yaml блоков
- [[block-composition]] — скилл сборки 07b, подставляет тексты и токены
- [[photo-curator]] — заполняет photo-слоты с иллюстрациями людей
- [[block-library-management]] — управляет реестром блоков, регистрирует этот блок

## Источник
- `block-library/features/features-cinematic-stacked-portfolio-kdm1-ru-6/meta.yaml`