````markdown
# Формат block-spec.yaml (входной артефакт stage-08)

**Owner:** Манагер (заполняется на ревью /landing-content) или скилл /landing-content.
**Читается:** generate-lzb-registration.py, generate-lzb-templates.py, generate-css-patches.py, generate-page-content.py.
**Расположение:** `<project>/08_КОД/block-spec.yaml`.

## Верхнеуровневая структура

```yaml
version: 1
page:
  title: "NeuroUpgrade 3.0 — главная"
  slug: "home"             # WP post slug для front-page
blocks:
  - slug: hero             # без префикса 'lazyblock/'; namespace добавляется генераторами
    type: single           # single | section-card
    title: "Hero"
    icon: "star-filled"    # имя dashicon
    category: "lp-blocks"
    controls: [...]        # см. ниже
  - slug: tarify
    type: section-card
    title: "Тарифы — секция"
    icon: "money-alt"
    category: "lp-blocks"
    controls:
      - { id: c_heading, name: heading, type: text, label: "Заголовок секции", default: "Наши тарифы" }
    section_grid_class: "nu-tier-grid"   # используется generate-css-patches для display:contents
    card:
      slug: tarify-card
      title: "Тариф (карточка)"
      controls: [...]
      template:                       # что Гутенберг-страница seed'ится при деплое
        - {}                          # одна пустая карточка с дефолтами
        - { name: "Продвинутый", popular: true }
        - { name: "ВИП" }
```

**Inheritance:** Внутри `card:` поля `icon` и `category` не задаются — генератор регистрации (`generate-lzb-registration.py`) копирует их из родительской section.

## Схема controls

Запись одного control:

```yaml
- id: c_heading                # стабильный ID, ключ в add_block(); используется как child_of target
  name: heading                # имя атрибута в $attributes
  type: text                   # обязательное; см. список ниже
  label: "Заголовок"           # обязательное
  default: "..."               # опционально; зависит от type (string для text/url; int для number; bool для toggle/checkbox; URL/имя файла для image)
  child_of: c_parent           # опционально; ID родительского repeater control (только для nested)
  options:                     # опционально; type-specific extras (например select choices)
    choices: ["a", "b"]
```

Допустимые значения `type` (Lazy Blocks Free, из research-doc):
`text`, `textarea`, `rich-text`, `classic-editor`, `code-editor`, `number`, `range`, `url`, `email`, `password`, `image`, `gallery`, `file`, `inner-blocks`, `select`, `radio`, `checkbox`, `toggle`, `color`, `date-time`, `repeater`.

Зарезервированные имена (которые НЕЛЬЗЯ использовать — выставляются Lazy Blocks автоматически):
`anchor`, `lazyblock`, `className`, `blockId`, `blockUniqueClass`, `ghostkitSpacings`, `ghostkitSR`.

## Ссылки на картинки

Для `type: image` controls `default` — путь относительно `08_КОД/wp-theme/assets/img/` (например `default: hero-kirill.png`). На деплое файл авто-импортится в Media Library, его attachment ID подставляется в seed-markup страницы.

## Правила валидации

1. `version` должен быть `1`.
2. Каждый `slug` блока уникален; lowercase ASCII kebab-case.
3. `type` ∈ {`single`, `section-card`}.
4. Если `type: section-card`, у блока ОБЯЗАТЕЛЬНО `card:` под-объект и `section_grid_class` (непустая строка).
5. Если `type: single`, `card:` и `section_grid_class` ДОЛЖНЫ отсутствовать.
6. Каждый `id` control'а уникален внутри своего блока.
7. Каждое `name` control'а не в reserved-списке.
8. `child_of` (если задан) ссылается на существующий control `id` в том же блоке с `type: repeater`.
9. Lazy Blocks НЕ поддерживает nested repeaters — если у repeater'а ребёнок сам `repeater`, валидация ПАДАЕТ с подсказкой разбить на section+card.
10. `type` в допустимом списке.

Образец с тремя архетипами — `template/08_КОД/block-spec.example.yaml`.
````
