---
type: block
name: hero-brutalist-split-sskrusgun-ru-1
sources: ["block-library/hero/hero-brutalist-split-sskrusgun-ru-1/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["hero", "brutalist", "split", "ru-market", "ecommerce", "services", "education"]
---

# Hero: Брутальный сплит с крупным фото (sskrusgun)

## Что делает
Первый экран лендинга с крупным предметным фото слева/справа, мощным жирным заголовком и жёстким красно-белым контрастом в брутальном стиле. Сразу захватывает внимание за счёт графической смелости и минимализма без украшений.

## Когда вызывать / в каком этапе
Используется на этапе **07a (UX Wireframe)** — `ux-composer` выбирает этот блок из библиотеки при подборе варианта hero-секции. На этапе **07b (Compose)** `block-composer` инжектирует токены бренда и текст из прототипа в слоты блока. Подходит, если клиент работает в нише услуг, образования или e-commerce и хочет выглядеть уверенно и жёстко — без «корпоративной мягкости».

## Что на вход / на выход

**Вход:**
- `tokens.json` — цвета и шрифты бренда (красный/белый контраст из brand-kit)
- `prototype.yaml` — текст заголовка (`heading`, обязательный слот)
- Фото товара или команды (photo-слот, заполняется на этапе 07c через `photo-curator`)

**Выход:**
- HTML-фрагмент hero-блока в составе `wireframe.html` (07a) или `composed.html` (07b)
- Слот `heading` подставляется из прототипа; фото остаётся placeholder до этапа PR-B

## Особенности блока
- **Стиль:** brutalist — грубые границы, нет скруглений, контрастные цвета
- **Раскладка:** split — контент делится на две половины (текст + фото)
- **Анимация:** отсутствует (`has_animation: false`)
- **Рынок:** адаптирован под RU-аудиторию (`ru_market: true`)
- **Ниши:** услуги, образование, e-commerce
- **Источник:** импортирован с [sskrusgun.ru](https://sskrusgun.ru/) методом codex-block-generation

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe.html
- [[block-composer]] — инжектирует токены и тексты в слоты на этапе 07b
- [[wireframe-rendering]] — скилл рендеринга, в котором живёт этот блок
- [[block-composition]] — скилл сборки composed.html с подстановкой контента
- [[photo-curator]] — заполняет фото-слот блока на этапе 07c
- [[block-library-management]] — управляет реестром, в котором зарегистрирован блок

## Источник
- `block-library/hero/hero-brutalist-split-sskrusgun-ru-1/meta.yaml`