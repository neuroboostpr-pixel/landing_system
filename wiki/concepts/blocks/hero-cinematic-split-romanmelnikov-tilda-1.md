---
type: block
name: hero-cinematic-split-romanmelnikov-tilda-1
sources: ["block-library/hero/hero-cinematic-split-romanmelnikov-tilda-1/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["hero", "cinematic", "split", "luxury", "services", "education", "ru-market"]
---

# Крупный первый экран с контрастным заголовком (Cinematic Split)

## Что делает
Формирует первый экран лендинга: крупный контрастный заголовок слева, текстовый блок справа и монохромная сцена внизу. Создаёт кинематографичное, «премиальное» первое впечатление без лишней анимации.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** и **07b (Compose)**. Агент [[ux-composer]] выбирает этот блок из библиотеки, когда в `prototype.yaml` есть секция `hero` с настроением `cinematic` или `split`. Подходит для ниш: **услуги**, **люкс**, **образование**. Оптимален для российского рынка (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — контент для слота `heading` (обязательный текстовый слот)
- `tokens.json` — дизайн-токены (цвета, шрифты) из этапа 05
- `selections.yaml` — выбор пользователя из вариантов wireframe (этап 07a)

**Выход:**
- HTML-фрагмент блока в `wireframe.html` (этап 07a)
- Встроенный блок в `07b_COMPOSED/composed.html` с подставленными токенами и текстом из прототипа (этап 07b)
- Слот `[PHOTO: hero-bg]` остаётся placeholder'ом до этапа 07c ([[photo-curator]])

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки и рендерит wireframe.html
- [[block-composer]] — вставляет блок в composed.html с токенами и текстами
- [[wireframe-rendering]] — скилл рендеринга wireframe на этапе 07a
- [[block-composition]] — скилл сборки composed.html на этапе 07b
- [[photo-curator]] — заполняет фото-слоты этого блока на этапе 07c
- [[block-library-management]] — скилл управления библиотекой блоков, откуда взят этот блок

## Источник
- `block-library/hero/hero-cinematic-split-romanmelnikov-tilda-1/meta.yaml`
- Импортирован с: https://romanmelnikov.tilda.ws/ (2026-05-16, метод: codex-block-generation)