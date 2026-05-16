---
type: block
name: header-luxury-split-romanmelnikov-tilda-0
sources: ["block-library/header/header-luxury-split-romanmelnikov-tilda-0/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-library-management", "wireframe-rendering"]
tags: ["header", "luxury", "split", "dark", "ru-market", "no-animation"]
---

# Узкая навигационная шапка: тёмный фон, тёплый акцент (luxury-split)

## Что делает

Рендерит узкую горизонтальную шапку сайта на тёмном фоне с мелкими навигационными ссылками и тёплым акцентным цветом. Подходит для премиального, делового и образовательного сегментов.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** — когда `ux-composer` подбирает блок-шапку для лендинга с luxury- или services-нишей. Блок выбирается автоматически из библиотеки или вручную через `/landing-wireframe`, если прототип указывает на сдержанный, «дорогой» заголовочный стиль без анимации.

Условия применения:
- Ниша: `services`, `luxury`, `education`
- Настроение стиля: `luxury`
- Паттерн расположения: `split` (логотип слева / навигация справа)
- Анимация не нужна (`has_animation: false`)
- Проект ориентирован на российский рынок (`ru_market: true`)

## Что на вход / на выход

**Вход:**
- Слот `heading` (тип `text`, обязательный) — название бренда или сайта, которое отображается в шапке
- Цветовые токены из `tokens.json` (тёмный фон, тёплый акцент)

**Выход:**
- HTML-блок шапки, встроенный в `wireframe.html` (этап 07a) и далее в `composed.html` (этап 07b)
- Placeholder для текста и навигационных ссылок до финального наполнения контентом

## Мета-информация

| Поле | Значение |
|------|----------|
| Категория | `header` |
| Layout | `split` |
| Настроение | `luxury` |
| Анимация | нет |
| Источник | [romanmelnikov.tilda.ws](https://romanmelnikov.tilda.ws/) |
| Метод импорта | `codex-block-generation` |
| Дата импорта | 2026-05-16 |

## Связанные концепты

- [[ux-composer]] — использует этот блок при построении wireframe.html на этапе 07a
- [[block-library-management]] — скилл управления библиотекой, отвечает за регистрацию и индексирование блока
- [[wireframe-rendering]] — скилл, рендерящий интерактивный wireframe с вариантами блоков
- [[block-composition]] — скилл этапа 07b, подставляет токены и тексты в выбранный блок

## Источник

- `block-library/header/header-luxury-split-romanmelnikov-tilda-0/meta.yaml`