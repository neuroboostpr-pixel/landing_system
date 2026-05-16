---
type: block
name: features-editorial-stacked-romanmelnikov-tilda-2
sources: ["block-library/features/features-editorial-stacked-romanmelnikov-tilda-2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "editorial", "stacked", "ru-market", "b2b-saas", "education", "services"]
---

# Плотный вводный блок с тезисом и текстовыми колонками

## Что делает

Отображает раздел «Преимущества» в редакционном стиле: широкая горизонтальная плашка, крупный тезис-заголовок и несколько коротких текстовых колонок под ним. Блок создаёт плотную, информационно насыщенную секцию без анимаций — читается быстро, выглядит профессионально.

## Когда вызывать / в каком этапе

Используется на **этапе 07a (wireframe)** при выборе варианта блока «features» для проектов в нишах услуг, образования или b2b-saas. Подключается автоматически агентом [[ux-composer]], когда прототип содержит секцию с перечислением преимуществ или ключевых тезисов. На **этапе 07b (compose)** наполняется реальным текстом из `prototype.yaml` агентом [[block-composer]].

Подходит для российского рынка (`ru_market: true`). Анимаций нет — хорошо работает там, где нужна сдержанная деловая подача без отвлекающих эффектов.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип: `text`) — крупный тезис, главная мысль блока
- Дополнительные текстовые колонки берутся из контентных слотов прототипа (описание коротких выгод или пунктов)
- Токены дизайн-системы из `tokens.json` (цвета, шрифты) — подставляются на этапе 07b

**Выход:**
- HTML-фрагмент блока внутри `wireframe.html` (этап 07a) как один из вариантов для выбора
- Готовый HTML-фрагмент в `composed.html` (этап 07b) с токенами и реальным текстом

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe.html
- [[block-composer]] — наполняет блок токенами и текстом прототипа на этапе 07b
- [[wireframe-rendering]] — скилл, управляющий рендером интерактивного wireframe
- [[block-composition]] — скилл, управляющий сборкой composed.html
- [[block-library-management]] — управляет всей библиотекой блоков, включая этот

## Источник

- `block-library/features/features-editorial-stacked-romanmelnikov-tilda-2/meta.yaml`
- Импортирован с: https://romanmelnikov.tilda.ws/ (2026-05-16, метод: codex-block-generation)