# План миграции stage-08 на Lazy Blocks

> **Для агентов-исполнителей:** ОБЯЗАТЕЛЬНЫЙ САБ-СКИЛЛ — superpowers:subagent-driven-development (рекомендуется) или superpowers:executing-plans для имплементации по задачам. Шаги используют checkbox-синтаксис (`- [ ]`) для отслеживания прогресса.

**Цель:** Перевести stage-08 (пайплайн генерации Гутенберг-блоков) со сломанного ACF-Free-based `register_block_type` потока на Lazy Blocks Free–based `lazyblocks()->add_block()` поток, чтобы редактируемые менеджером Гутенберг-страницы корректно рендерились на продакшене.

**Архитектура:** Вводим новый авторский артефакт `08_КОД/block-spec.yaml` как single source of truth — какие блоки существуют, какие из них `single` vs `section-card`, типы и дефолты controls, ссылки на картинки. Новые Python-генераторы читают этот YAML и производят: (а) AUTO-GENERATED секцию `lzb/init` в `functions.php`, (б) `theme/blocks/lazyblock-<slug>/block.php` рендер-шаблоны, (в) `display: contents` патчи в `assets/css/main.css` для section+card пар, (г) `page-content.html` с Гутенберг-markup, который seed'ится через `wp post create`. Деплой ставит плагин `lazy-blocks`, авто-импортит картинки темы в Media Library, создаёт front-page из seed'а и устанавливает `page_on_front`. Существующие задеплоенные лендинги (lixiang-dubai, neuroupgrade старый) не трогаются — они рендерятся через `front-page.php` (новый пайплайн этот файл не пишет, но и не удаляет с прод-сервера); миграция случится при следующей регенерации.

**Технологический стек:** Python 3.11+ (генераторы), PyYAML, pytest, bash, bats-core, wp-cli, Lazy Blocks Free 4.3.0+, WordPress 6.9+, PHP 8.1+.

---

## Структура файлов

### Новые файлы

- `skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py` — читает `block-spec.yaml`, пишет `lzb/init` блок в `functions.php` (заменяет `generate-block-registration.py`).
- `skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py` — читает `block-spec.yaml`, пишет `theme/blocks/lazyblock-<slug>/block.php` (заменяет `--blocks-only` режим `generate-theme.py`).
- `skills/wp-gutenberg-block-builder/scripts/generate-css-patches.py` — читает `block-spec.yaml`, дописывает `display: contents` правила в `assets/css/main.css` между AUTO-GENERATED маркерами, по одной группе на каждую section+card пару.
- `skills/wp-gutenberg-block-builder/scripts/generate-page-content.py` — читает `block-spec.yaml`, пишет `08_КОД/page-content.html` с Гутенберг-markup (InnerBlocks шаблоны для section+card пар + плейсхолдеры `__IMAGE_ATTACHMENT_ID__<filename>__` для подстановки на деплое).
- `skills/wp-gutenberg-block-builder/scripts/lib/block_spec.py` — loader + dataclass-схема для `block-spec.yaml`; используется всеми четырьмя генераторами выше.
- `skills/wp-gutenberg-block-builder/scripts/lib/control_types.py` — модуль констант: допустимые типы Lazy Blocks controls, зарезервированные имена атрибутов (из research-doc §3).
- `skills/wp-gutenberg-block-builder/tests/test_block_spec.py` — pytest unit-тесты для `block_spec.py` (валидация схемы, тексты ошибок).
- `skills/wp-gutenberg-block-builder/tests/test_generate_lzb_registration.py` — pytest тесты для `generate-lzb-registration.py`.
- `skills/wp-gutenberg-block-builder/tests/test_generate_lzb_templates.py` — pytest тесты для `generate-lzb-templates.py`.
- `skills/wp-gutenberg-block-builder/tests/test_generate_css_patches.py` — pytest тесты для `generate-css-patches.py`.
- `skills/wp-gutenberg-block-builder/tests/test_generate_page_content.py` — pytest тесты для `generate-page-content.py`.
- `skills/wp-gutenberg-block-builder/tests/fixtures/block-spec.minimal.yaml` — фикстура: один single-блок, одна section+card пара, один image control.
- `skills/wp-gutenberg-block-builder/tests/fixtures/block-spec.invalid.yaml` — фикстура: некорректный YAML для проверки error handling.
- `template/08_КОД/block-spec.example.yaml` — аннотированный пример в шаблоне проекта; манагер использует как стартовую точку.
- `tests/preflight/test_preflight_lazy_blocks.bats` — bats-тесты для проверки наличия Lazy Blocks в preflight.
- `tests/deploy/test_deploy_lazy_blocks.bats` — bats-тесты для изменений deploy-скрипта (`wp plugin install lazy-blocks --activate`, удаление `wp acf import` для блок-полей, `wp media import`, `wp post create`, `wp option update show_on_front`).
- `docs/superpowers/specs/2026-05-13-block-spec-format.md` — короткая референс-документация: полная схема `block-spec.yaml` + 3 примера блоков.

### Изменяемые файлы

- `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` — добавить install Lazy Blocks, добавить авто-импорт картинок, добавить `wp post create` + `page_on_front` шаг, убрать ветку `wp acf import` для блок-полей (ACF Free install оставляем как no-op для возможных будущих page-level полей).
- `scripts/preflight.sh` (косвенно через validate-all.sh) — делегирует новую проверку, что `deploy-wordpress.sh` содержит install Lazy Blocks.
- `scripts/validate-all.sh` — добавить проверку, что deploy-скрипт ставит `lazy-blocks`.
- `template/08_КОД/` — добавить `block-spec.example.yaml`, добавить `wp-theme/blocks/.gitkeep` чтобы директория создавалась в новых проектах.
- `skills/wp-gutenberg-block-builder/SKILL.md` — заменить инструкции про ACF Blocks на Lazy Blocks workflow, указать на новые генераторы и `block-spec.yaml`.
- `skills/wp-cli-deployer/SKILL.md` — задокументировать install Lazy Blocks и импорт картинок.
- `.claude/commands/landing-build.md` (если есть) — обновить список вызовов: четыре новых генератора вместо трёх старых.

### Удаляемые (или помеченные deprecated) файлы

- `skills/wp-gutenberg-block-builder/scripts/generate-block-json.py` — Lazy Blocks читает схему controls из `add_block()`, `block.json` для `lazyblock/*` не нужен.
- `skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py` — замещён `generate-lzb-registration.py`.
- `skills/wp-gutenberg-block-builder/scripts/generate-acf.py` (только часть про block-fields) — Lazy Blocks владеет controls. Если файл генерирует что-то ещё (Task 2 это аудит) — удалить только ветку с блок-полями; иначе удалить файл полностью.
- Режим `--blocks-only` и функция `_write_block_parts` в `skills/wp-gutenberg-block-builder/scripts/generate-theme.py` — замещены `generate-lzb-templates.py`. Остальное в `generate-theme.py` (style.css, базовый functions.php, asset-папки) остаётся.
- Сгенерированные `08_КОД/wp-theme/template-parts/block-*.php` в новых проектах — больше не создаются. В легаси-проектах оставлены как есть.
- `08_КОД/wp-theme/front-page.php` — больше не пишется генератором. Front-page теперь — Гутенберг-страница через `page_on_front`.

---

## Task 1: Определить схему `block-spec.yaml` и задокументировать

**Файлы:**
- Создать: `docs/superpowers/specs/2026-05-13-block-spec-format.md`
- Создать: `template/08_КОД/block-spec.example.yaml`

- [ ] **Шаг 1: Написать spec-документ**

Создать `docs/superpowers/specs/2026-05-13-block-spec-format.md` с следующим содержимым:

```markdown
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
    section_grid_class: null   # только для type=section-card; CSS-класс обёртки InnerBlocks
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

## Схема controls

Запись одного control:

```yaml
- id: c_heading                # стабильный ID, ключ в add_block(); используется как child_of target
  name: heading                # имя атрибута в $attributes
  type: text                   # обязательное; см. список ниже
  label: "Заголовок"           # обязательное
  default: "..."               # опционально; зависит от type (string для text/url; int для number; URL/имя файла для image)
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
```

- [ ] **Шаг 2: Создать пример block-spec**

Создать `template/08_КОД/block-spec.example.yaml`:

```yaml
version: 1
page:
  title: "Главная"
  slug: "home"
blocks:
  - slug: hero
    type: single
    title: "Hero"
    icon: "star-filled"
    category: "lp-blocks"
    controls:
      - { id: c_heading,  name: heading,  type: text,     label: "Заголовок", default: "Заголовок Hero" }
      - { id: c_subtitle, name: subtitle, type: textarea, label: "Подзаголовок", default: "" }
      - { id: c_cta_text, name: cta_text, type: text,     label: "CTA текст", default: "Записаться" }
      - { id: c_cta_url,  name: cta_url,  type: url,      label: "CTA ссылка", default: "#cta" }
      - { id: c_image,    name: hero_image, type: image,  label: "Картинка", default: "hero-kirill.png" }
      - { id: c_bullets,  name: bullets,  type: repeater, label: "Буллеты" }
      - { id: c_bullets_text, name: text, type: text, label: "Текст", default: "", child_of: c_bullets }

  - slug: tarify
    type: section-card
    title: "Тарифы — секция"
    icon: "money-alt"
    category: "lp-blocks"
    section_grid_class: "nu-tier-grid"
    controls:
      - { id: c_section_heading, name: heading, type: text, label: "Заголовок секции", default: "Выберите тариф" }
    card:
      slug: tarify-card
      title: "Тариф"
      controls:
        - { id: c_name,    name: name,    type: text,    label: "Название", default: "Базовый" }
        - { id: c_price,   name: price,   type: text,    label: "Цена",     default: "29 000" }
        - { id: c_popular, name: popular, type: toggle,  label: "Популярный?", default: "false" }
        - { id: c_feats,   name: features, type: repeater, label: "Фичи" }
        - { id: c_feats_text, name: text, type: text, label: "Текст", default: "", child_of: c_feats }
      template:
        - { name: "Базовый",     price: "29 000" }
        - { name: "Продвинутый", price: "59 000", popular: "true" }
        - { name: "ВИП",         price: "129 000" }
```

- [ ] **Шаг 3: Коммит**

```bash
git add docs/superpowers/specs/2026-05-13-block-spec-format.md template/08_КОД/block-spec.example.yaml
git commit -m "docs(stage-08): block-spec.yaml format + example"
```

---

## Task 2: Аудит существующих генераторов перед удалением

**Файлы:**
- Только чтение: `skills/wp-gutenberg-block-builder/scripts/generate-acf.py`, `generate-block-json.py`, `generate-block-registration.py`, `generate-theme.py`
- Изменение: этот план (только если аудит вскрыл сюрпризы)

- [ ] **Шаг 1: Прочитать каждый файл и зафиксировать назначение**

Запустить:

```bash
wc -l skills/wp-gutenberg-block-builder/scripts/generate-acf.py \
     skills/wp-gutenberg-block-builder/scripts/generate-block-json.py \
     skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py \
     skills/wp-gutenberg-block-builder/scripts/generate-theme.py
```

Прочитать каждый. Подтвердить:
- `generate-acf.py` выдаёт только ACF JSON для блок-полей (никакого page-level / options-page вывода). Если выдаёт что-то ещё — поставить пользователя в известность ДО удаления.
- `generate-block-json.py` выдаёт только per-block `block.json` с ключом `acf.renderTemplate`.
- `generate-block-registration.py` совпадает с версией в research-context (пишет цикл `register_block_type` в `functions.php` между AUTO-GENERATED маркерами).
- `generate-theme.py` имеет функцию `_write_block_parts()` + режим `--blocks-only` — это и есть заменяемая часть; остальное (`_write_style_css`, `_write_functions_php`, scaffolding папок) остаётся.

- [ ] **Шаг 2: Без правок кода. Без коммита**

Это исследовательский шаг. Если аудит покажет, что в `generate-acf.py` есть page-level функциональность — ОСТАНОВИТЬСЯ и спросить пользователя перед переходом к Task 8 (где этот файл удаляется). Иначе двигаемся дальше.

---

## Task 3: Реализовать loader `block_spec.py` (TDD)

**Файлы:**
- Создать: `skills/wp-gutenberg-block-builder/scripts/lib/block_spec.py`
- Создать: `skills/wp-gutenberg-block-builder/scripts/lib/control_types.py`
- Создать: `skills/wp-gutenberg-block-builder/tests/test_block_spec.py`
- Создать: `skills/wp-gutenberg-block-builder/tests/fixtures/block-spec.minimal.yaml`
- Создать: `skills/wp-gutenberg-block-builder/tests/fixtures/block-spec.invalid.yaml`

- [ ] **Шаг 1: Написать фикстуры**

`skills/wp-gutenberg-block-builder/tests/fixtures/block-spec.minimal.yaml`:

```yaml
version: 1
page:
  title: "Test"
  slug: "home"
blocks:
  - slug: hero
    type: single
    title: "Hero"
    icon: "star-filled"
    category: "lp-blocks"
    controls:
      - { id: c_h, name: heading, type: text, label: "H", default: "Hi" }
  - slug: tarify
    type: section-card
    title: "Tarify"
    icon: "money-alt"
    category: "lp-blocks"
    section_grid_class: "nu-tier-grid"
    controls:
      - { id: c_sh, name: heading, type: text, label: "SH", default: "Tariffs" }
    card:
      slug: tarify-card
      title: "Tarif"
      controls:
        - { id: c_n, name: name, type: text, label: "N", default: "Basic" }
        - { id: c_f, name: features, type: repeater, label: "F" }
        - { id: c_ft, name: text, type: text, label: "FT", default: "", child_of: c_f }
      template:
        - { name: "Basic" }
        - { name: "Pro" }
```

`skills/wp-gutenberg-block-builder/tests/fixtures/block-spec.invalid.yaml`:

```yaml
version: 1
page: { title: "T", slug: "home" }
blocks:
  - slug: bad
    type: single
    title: "Bad"
    icon: "x"
    category: "lp-blocks"
    controls:
      - { id: c1, name: features, type: repeater, label: "F" }
      - { id: c2, name: nested, type: repeater, label: "N", child_of: c1 }
```

- [ ] **Шаг 2: Написать падающие тесты**

`skills/wp-gutenberg-block-builder/tests/test_block_spec.py`:

```python
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from block_spec import load, validate, BlockSpecError  # noqa: E402

FIX = ROOT / "tests" / "fixtures"


def test_load_minimal_parses_two_blocks():
    spec = load(FIX / "block-spec.minimal.yaml")
    assert spec.version == 1
    assert spec.page.slug == "home"
    assert len(spec.blocks) == 2
    assert spec.blocks[0].slug == "hero"
    assert spec.blocks[0].type == "single"
    assert spec.blocks[1].type == "section-card"
    assert spec.blocks[1].card.slug == "tarify-card"
    assert spec.blocks[1].section_grid_class == "nu-tier-grid"


def test_load_minimal_passes_validation():
    spec = load(FIX / "block-spec.minimal.yaml")
    validate(spec)  # без исключения


def test_nested_repeater_is_rejected():
    spec = load(FIX / "block-spec.invalid.yaml")
    with pytest.raises(BlockSpecError, match="nested repeater"):
        validate(spec)


def test_reserved_attribute_name_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: x\n"
        "    type: single\n"
        "    title: X\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c1, name: anchor, type: text, label: L, default: '' }\n",
        encoding="utf-8",
    )
    spec = load(bad)
    with pytest.raises(BlockSpecError, match="reserved"):
        validate(spec)


def test_section_card_missing_card_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: x\n"
        "    type: section-card\n"
        "    title: X\n"
        "    icon: star-filled\n"
        "    category: lp-blocks\n"
        "    section_grid_class: grid\n"
        "    controls: []\n",
        encoding="utf-8",
    )
    spec = load(bad)
    with pytest.raises(BlockSpecError, match="card"):
        validate(spec)


def test_child_of_must_reference_repeater(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: x\n"
        "    type: single\n"
        "    title: X\n"
        "    icon: i\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c1, name: heading, type: text, label: L, default: '' }\n"
        "      - { id: c2, name: sub, type: text, label: L, default: '', child_of: c1 }\n",
        encoding="utf-8",
    )
    spec = load(bad)
    with pytest.raises(BlockSpecError, match="child_of.*repeater"):
        validate(spec)


def test_unknown_control_type_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: x\n"
        "    type: single\n"
        "    title: X\n"
        "    icon: i\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c1, name: heading, type: phantom, label: L }\n",
        encoding="utf-8",
    )
    spec = load(bad)
    with pytest.raises(BlockSpecError, match="type"):
        validate(spec)
```

- [ ] **Шаг 3: Запустить тесты — убедиться что падают**

```bash
cd skills/wp-gutenberg-block-builder
python -m pytest tests/test_block_spec.py -v
```

Ожидание: все тесты FAIL с `ModuleNotFoundError: No module named 'block_spec'`.

- [ ] **Шаг 4: Реализовать `control_types.py`**

`skills/wp-gutenberg-block-builder/scripts/lib/control_types.py`:

```python
ALLOWED_CONTROL_TYPES = frozenset({
    "text", "textarea", "rich-text", "classic-editor", "code-editor",
    "number", "range", "url", "email", "password", "image", "gallery",
    "file", "inner-blocks", "select", "radio", "checkbox", "toggle",
    "color", "date-time", "repeater",
})

RESERVED_ATTRIBUTE_NAMES = frozenset({
    "anchor", "lazyblock", "className", "blockId", "blockUniqueClass",
    "ghostkitSpacings", "ghostkitSR",
})

ALLOWED_BLOCK_TYPES = frozenset({"single", "section-card"})
```

- [ ] **Шаг 5: Реализовать `block_spec.py`**

`skills/wp-gutenberg-block-builder/scripts/lib/block_spec.py`:

```python
"""Loader + валидатор для stage-08 block-spec.yaml."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from control_types import (
    ALLOWED_BLOCK_TYPES,
    ALLOWED_CONTROL_TYPES,
    RESERVED_ATTRIBUTE_NAMES,
)


class BlockSpecError(ValueError):
    """Поднимается когда block-spec.yaml некорректен или не проходит валидацию."""


@dataclass
class Control:
    id: str
    name: str
    type: str
    label: str
    default: Optional[str] = None
    child_of: Optional[str] = None
    options: dict = field(default_factory=dict)


@dataclass
class Card:
    slug: str
    title: str
    controls: list[Control] = field(default_factory=list)
    template: list[dict] = field(default_factory=list)


@dataclass
class Block:
    slug: str
    type: str
    title: str
    icon: str
    category: str
    controls: list[Control] = field(default_factory=list)
    section_grid_class: Optional[str] = None
    card: Optional[Card] = None


@dataclass
class Page:
    title: str
    slug: str


@dataclass
class BlockSpec:
    version: int
    page: Page
    blocks: list[Block] = field(default_factory=list)


def _control_from(raw: dict) -> Control:
    return Control(
        id=raw["id"],
        name=raw["name"],
        type=raw["type"],
        label=raw["label"],
        default=raw.get("default"),
        child_of=raw.get("child_of"),
        options=raw.get("options") or {},
    )


def load(path: Path | str) -> BlockSpec:
    p = Path(path)
    if not p.exists():
        raise BlockSpecError(f"block-spec.yaml not found: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise BlockSpecError("block-spec.yaml must be a mapping at top level")
    page = data.get("page") or {}
    blocks_raw = data.get("blocks") or []
    blocks = []
    for b in blocks_raw:
        card_raw = b.get("card")
        card = None
        if card_raw:
            card = Card(
                slug=card_raw["slug"],
                title=card_raw["title"],
                controls=[_control_from(c) for c in (card_raw.get("controls") or [])],
                template=list(card_raw.get("template") or []),
            )
        blocks.append(Block(
            slug=b["slug"],
            type=b["type"],
            title=b["title"],
            icon=b.get("icon", "block-default"),
            category=b.get("category", "lp-blocks"),
            controls=[_control_from(c) for c in (b.get("controls") or [])],
            section_grid_class=b.get("section_grid_class"),
            card=card,
        ))
    return BlockSpec(
        version=int(data.get("version", 0)),
        page=Page(title=page.get("title", ""), slug=page.get("slug", "home")),
        blocks=blocks,
    )


def _validate_controls(block_label: str, controls: list[Control]) -> None:
    ids: set[str] = set()
    repeater_ids: set[str] = set()
    for c in controls:
        if c.id in ids:
            raise BlockSpecError(f"{block_label}: duplicate control id '{c.id}'")
        ids.add(c.id)
        if c.type not in ALLOWED_CONTROL_TYPES:
            raise BlockSpecError(f"{block_label}: control '{c.id}' has unknown type '{c.type}'")
        if c.name in RESERVED_ATTRIBUTE_NAMES:
            raise BlockSpecError(f"{block_label}: control '{c.id}' uses reserved attribute name '{c.name}'")
        if c.type == "repeater":
            repeater_ids.add(c.id)
    for c in controls:
        if c.child_of is None:
            continue
        if c.child_of not in ids:
            raise BlockSpecError(f"{block_label}: control '{c.id}' child_of='{c.child_of}' does not exist")
        if c.child_of not in repeater_ids:
            raise BlockSpecError(f"{block_label}: control '{c.id}' child_of='{c.child_of}' is not a repeater")
        if c.type == "repeater":
            raise BlockSpecError(
                f"{block_label}: control '{c.id}' is a nested repeater "
                "(repeater inside repeater) — Lazy Blocks does not support this; "
                "split into a section+card pair instead"
            )


def validate(spec: BlockSpec) -> None:
    if spec.version != 1:
        raise BlockSpecError(f"unsupported version {spec.version}; expected 1")
    seen_slugs: set[str] = set()
    for b in spec.blocks:
        if b.slug in seen_slugs:
            raise BlockSpecError(f"duplicate block slug '{b.slug}'")
        seen_slugs.add(b.slug)
        if b.type not in ALLOWED_BLOCK_TYPES:
            raise BlockSpecError(f"block '{b.slug}': unknown type '{b.type}'")
        if b.type == "section-card":
            if b.card is None:
                raise BlockSpecError(f"block '{b.slug}': type=section-card requires 'card:' sub-object")
            if not b.section_grid_class:
                raise BlockSpecError(f"block '{b.slug}': type=section-card requires section_grid_class")
        else:
            if b.card is not None:
                raise BlockSpecError(f"block '{b.slug}': type=single must not have 'card:' sub-object")
            if b.section_grid_class is not None:
                raise BlockSpecError(f"block '{b.slug}': type=single must not have section_grid_class")
        _validate_controls(f"block '{b.slug}'", b.controls)
        if b.card is not None:
            _validate_controls(f"block '{b.slug}'.card", b.card.controls)
```

- [ ] **Шаг 6: Запустить тесты — убедиться что проходят**

```bash
cd skills/wp-gutenberg-block-builder
python -m pytest tests/test_block_spec.py -v
```

Ожидание: 7 passed.

- [ ] **Шаг 7: Коммит**

```bash
git add skills/wp-gutenberg-block-builder/scripts/lib/block_spec.py \
        skills/wp-gutenberg-block-builder/scripts/lib/control_types.py \
        skills/wp-gutenberg-block-builder/tests/test_block_spec.py \
        skills/wp-gutenberg-block-builder/tests/fixtures/block-spec.minimal.yaml \
        skills/wp-gutenberg-block-builder/tests/fixtures/block-spec.invalid.yaml
git commit -m "feat(stage-08): block_spec.py loader + validation"
```

---

## Task 4: Реализовать `generate-lzb-registration.py` (TDD)

**Файлы:**
- Создать: `skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py`
- Создать: `skills/wp-gutenberg-block-builder/tests/test_generate_lzb_registration.py`

- [ ] **Шаг 1: Написать падающий тест**

`skills/wp-gutenberg-block-builder/tests/test_generate_lzb_registration.py`:

```python
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-lzb-registration.py"
FIX = ROOT / "tests" / "fixtures"


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme").mkdir(parents=True)
    shutil.copy(FIX / "block-spec.minimal.yaml", project / "08_КОД" / "block-spec.yaml")
    (project / "08_КОД" / "wp-theme" / "functions.php").write_text(
        "<?php\n// existing theme code\n", encoding="utf-8"
    )
    return project


def _run(project: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )


def test_writes_lzb_init_action(tmp_path):
    project = _make_project(tmp_path)
    r = _run(project)
    assert r.returncode == 0, r.stderr
    out = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "AUTO-GENERATED START: lzb-block-registration" in out
    assert "add_action('lzb/init'" in out or "add_action( 'lzb/init'" in out
    assert "lazyblocks()->add_block" in out


def test_registers_both_section_and_card_for_section_card_block(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    out = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "'slug' => 'lazyblock/hero'" in out
    assert "'slug' => 'lazyblock/tarify'" in out
    assert "'slug' => 'lazyblock/tarify-card'" in out


def test_child_of_uses_control_id_not_name(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    out = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    # c_ft имеет child_of: c_f — должно появиться как литерал 'c_f', не 'features'
    assert "'child_of' => 'c_f'" in out


def test_idempotent_regeneration(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    first = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    _run(project)
    second = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert first == second


def test_preserves_existing_functions_php_content(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    out = (project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "// existing theme code" in out


def test_fails_when_block_spec_missing(tmp_path):
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme").mkdir(parents=True)
    (project / "08_КОД" / "wp-theme" / "functions.php").write_text("<?php\n", encoding="utf-8")
    r = _run(project)
    assert r.returncode != 0
    assert "block-spec.yaml" in (r.stderr + r.stdout)
```

- [ ] **Шаг 2: Запустить тест — убедиться что падает**

```bash
cd skills/wp-gutenberg-block-builder
python -m pytest tests/test_generate_lzb_registration.py -v
```

Ожидание: FAIL — скрипт не существует.

- [ ] **Шаг 3: Реализовать генератор**

`skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py`:

```python
#!/usr/bin/env python3
"""Inject AUTO-GENERATED Lazy Blocks registration section into functions.php.

CLI: python generate-lzb-registration.py --project <path>
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from block_spec import BlockSpec, BlockSpecError, Block, Card, Control, load, validate  # noqa: E402

MARKER_START = "// AUTO-GENERATED START: lzb-block-registration — DO NOT EDIT MANUALLY"
MARKER_END = "// AUTO-GENERATED END: lzb-block-registration"
SECTION_RE = re.compile(
    r"\n?// AUTO-GENERATED START: lzb-block-registration.*?// AUTO-GENERATED END: lzb-block-registration\n?",
    re.DOTALL,
)


def _php_str(s: str | None) -> str:
    if s is None:
        return "''"
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _render_controls(controls: list[Control]) -> str:
    if not controls:
        return "array()"
    lines = ["array("]
    for c in controls:
        parts = [
            f"'name' => {_php_str(c.name)}",
            f"'type' => {_php_str(c.type)}",
            f"'label' => {_php_str(c.label)}",
        ]
        if c.default is not None:
            parts.append(f"'default' => {_php_str(c.default)}")
        if c.child_of is not None:
            parts.append(f"'child_of' => {_php_str(c.child_of)}")
        lines.append(f"            {_php_str(c.id)} => array({', '.join(parts)}),")
    lines.append("        )")
    return "\n".join(lines)


def _render_block(slug: str, title: str, icon: str, category: str, controls: list[Control]) -> str:
    return (
        "    lazyblocks()->add_block(array(\n"
        f"        'slug' => {_php_str('lazyblock/' + slug)},\n"
        f"        'title' => {_php_str(title)},\n"
        f"        'icon' => {_php_str(icon)},\n"
        f"        'category' => {_php_str(category)},\n"
        f"        'controls' => {_render_controls(controls)},\n"
        "        'code' => array('output_method' => 'template'),\n"
        "    ));\n"
    )


def _render_section(spec: BlockSpec) -> str:
    body_parts: list[str] = []
    for b in spec.blocks:
        body_parts.append(_render_block(b.slug, b.title, b.icon, b.category, b.controls))
        if b.card is not None:
            body_parts.append(_render_block(b.card.slug, b.card.title, b.icon, b.category, b.card.controls))
    body = "\n".join(body_parts)
    return f"""
{MARKER_START}
add_action('lzb/init', function() {{
    if (!function_exists('lazyblocks')) {{ return; }}
{body}}});
{MARKER_END}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    spec_path = Path(args.project) / "08_КОД" / "block-spec.yaml"
    try:
        spec = load(spec_path)
        validate(spec)
    except BlockSpecError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    fn_php = Path(args.project) / "08_КОД" / "wp-theme" / "functions.php"
    if not fn_php.exists():
        print(f"ERROR: {fn_php} not found", file=sys.stderr)
        return 1

    shutil.copy2(fn_php, fn_php.with_suffix(".php.bak"))
    src = fn_php.read_text(encoding="utf-8")
    section = _render_section(spec)
    if SECTION_RE.search(src):
        new = SECTION_RE.sub(section, src)
    else:
        new = src.rstrip() + "\n" + section
    fn_php.write_text(new, encoding="utf-8", newline="\n")
    print(f"wrote {fn_php} ({len(spec.blocks)} block(s), {sum(1 for b in spec.blocks if b.card)} card(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Шаг 4: Запустить тесты — убедиться что проходят**

```bash
cd skills/wp-gutenberg-block-builder
python -m pytest tests/test_generate_lzb_registration.py -v
```

Ожидание: 6 passed.

- [ ] **Шаг 5: Коммит**

```bash
git add skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py \
        skills/wp-gutenberg-block-builder/tests/test_generate_lzb_registration.py
git commit -m "feat(stage-08): generate-lzb-registration.py with TDD"
```

---

## Task 5: Реализовать `generate-lzb-templates.py` (TDD)

**Файлы:**
- Создать: `skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py`
- Создать: `skills/wp-gutenberg-block-builder/tests/test_generate_lzb_templates.py`

- [ ] **Шаг 1: Написать падающий тест**

`skills/wp-gutenberg-block-builder/tests/test_generate_lzb_templates.py`:

```python
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-lzb-templates.py"
FIX = ROOT / "tests" / "fixtures"


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme" / "blocks").mkdir(parents=True)
    shutil.copy(FIX / "block-spec.minimal.yaml", project / "08_КОД" / "block-spec.yaml")
    return project


def _run(project: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )


def test_creates_block_php_for_single_block(tmp_path):
    project = _make_project(tmp_path)
    r = _run(project)
    assert r.returncode == 0, r.stderr
    f = project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php"
    assert f.exists()
    body = f.read_text(encoding="utf-8")
    assert "<?php" in body
    assert "$attributes['heading']" in body


def test_creates_section_with_inner_blocks_tag(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    section = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify" / "block.php").read_text(encoding="utf-8")
    assert "<InnerBlocks" in section
    assert "lazyblock/tarify-card" in section
    assert 'class="nu-tier-grid"' in section


def test_creates_card_block_php(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    card = project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-tarify-card" / "block.php"
    assert card.exists()
    body = card.read_text(encoding="utf-8")
    assert "$attributes['name']" in body
    # repeater становится foreach'ем
    assert "foreach" in body
    assert "$attributes['features']" in body


def test_never_overwrites_existing_block_php(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    hero = project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php"
    hero.write_text("<?php // hand-edited\n", encoding="utf-8")
    _run(project)
    assert hero.read_text(encoding="utf-8") == "<?php // hand-edited\n"


def test_image_control_uses_attachment_src_helper(tmp_path):
    # расширить фикстуру: добавить image control
    project = _make_project(tmp_path)
    spec = (project / "08_КОД" / "block-spec.yaml").read_text(encoding="utf-8")
    spec = spec.replace(
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }",
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }\n"
        "      - { id: c_img, name: hero_image, type: image, label: \"Img\", default: \"hero.png\" }",
    )
    (project / "08_КОД" / "block-spec.yaml").write_text(spec, encoding="utf-8")
    _run(project)
    body = (project / "08_КОД" / "wp-theme" / "blocks" / "lazyblock-hero" / "block.php").read_text(encoding="utf-8")
    assert "wp_get_attachment_image" in body or "['url']" in body
```

- [ ] **Шаг 2: Запустить тест — убедиться что падает**

```bash
cd skills/wp-gutenberg-block-builder
python -m pytest tests/test_generate_lzb_templates.py -v
```

Ожидание: FAIL — скрипт не существует.

- [ ] **Шаг 3: Реализовать генератор**

`skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py`:

```python
#!/usr/bin/env python3
"""Generate theme/blocks/lazyblock-<slug>/block.php files from block-spec.yaml.

CLI: python generate-lzb-templates.py --project <path>

Никогда не перезаписывает существующий block.php — render-шаблоны
редактируются вручную после первой генерации (Lazy Blocks читает $attributes
одинаково независимо от формы шаблона).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from block_spec import Block, BlockSpecError, Card, Control, load, validate  # noqa: E402


def _render_control_output(c: Control) -> str:
    """Вернуть одну PHP-строку которая echo'ит/print'ит поле внутри markup блока."""
    key = c.name
    cls = f"lp-field--{c.name}"
    if c.type in ("text",):
        return f'    <div class="{cls}"><?php echo esc_html($attributes[\'{key}\'] ?? \'\'); ?></div>'
    if c.type == "textarea":
        return f'    <div class="{cls}"><?php echo nl2br(esc_html($attributes[\'{key}\'] ?? \'\')); ?></div>'
    if c.type in ("rich-text", "classic-editor"):
        return f'    <div class="{cls}"><?php echo wp_kses_post($attributes[\'{key}\'] ?? \'\'); ?></div>'
    if c.type == "url":
        return f'    <a class="{cls}" href="<?php echo esc_url($attributes[\'{key}\'] ?? \'#\'); ?>"></a>'
    if c.type == "image":
        return (
            f'    <?php $img_{key} = $attributes[\'{key}\'] ?? null; ?>\n'
            f'    <?php if (!empty($img_{key}[\'id\'])): ?>\n'
            f'        <?php echo wp_get_attachment_image($img_{key}[\'id\'], \'large\', false, [\'class\' => \'{cls}\']); ?>\n'
            f'    <?php elseif (!empty($img_{key}[\'url\'])): ?>\n'
            f'        <img class="{cls}" src="<?php echo esc_url($img_{key}[\'url\']); ?>" alt="">\n'
            f'    <?php endif; ?>'
        )
    if c.type == "toggle":
        return f'    <?php /* toggle {key}: <?php echo !empty($attributes[\'{key}\']) ? \'1\' : \'0\'; ?> */ ?>'
    if c.type == "repeater":
        return ""  # обрабатывается отдельно (вложенный цикл)
    # Fallback для select/radio/checkbox/etc.
    return f'    <div class="{cls}"><?php echo esc_html((string)($attributes[\'{key}\'] ?? \'\')); ?></div>'


def _render_repeater(c: Control, all_controls: list[Control]) -> str:
    children = [x for x in all_controls if x.child_of == c.id]
    item_lines = []
    for ch in children:
        if ch.type == "repeater":
            continue  # валидация и так запрещает nested, но на всякий случай
        item_lines.append(
            f'        <li class="lp-rep-item lp-rep-item--{ch.name}">'
            f'<?php echo esc_html($row[\'{ch.name}\'] ?? \'\'); ?></li>'
        )
    items = "\n".join(item_lines)
    return (
        f'    <ul class="lp-rep lp-rep--{c.name}">\n'
        f'    <?php foreach ((array)($attributes[\'{c.name}\'] ?? []) as $row): ?>\n'
        f'{items}\n'
        f'    <?php endforeach; ?>\n'
        f'    </ul>'
    )


def _render_block_php(b: Block) -> str:
    lines = [
        "<?php",
        f"/**",
        f" * Block — {b.title}.",
        f" * Auto-scaffolded by generate-lzb-templates.py. Hand-edit freely; not overwritten on regen.",
        f" */",
        "if (!defined('ABSPATH')) { exit; }",
        "?>",
        f'<section class="lp-block lp-block--{b.slug}">',
    ]
    for c in b.controls:
        if c.child_of is not None:
            continue  # дочерние поля рендерятся внутри своего repeater'а
        if c.type == "repeater":
            lines.append(_render_repeater(c, b.controls))
        else:
            out = _render_control_output(c)
            if out:
                lines.append(out)
    if b.type == "section-card" and b.card is not None:
        # template prefill'ит экземпляры карточек; allowedBlocks ограничивает +
        tmpl_php = "[" + ",".join(f"['lazyblock/{b.card.slug}']" for _ in (b.card.template or [{}])) + "]"
        lines.append(
            f'    <div class="{b.section_grid_class}">'
        )
        lines.append(
            f'        <InnerBlocks allowedBlocks="[\'lazyblock/{b.card.slug}\']" template="{tmpl_php}" />'
        )
        lines.append("    </div>")
    lines.append("</section>")
    return "\n".join(lines) + "\n"


def _render_card_php(b: Block, card: Card) -> str:
    lines = [
        "<?php",
        f"/**",
        f" * Card block — {card.title} (child of {b.slug}).",
        f" */",
        "if (!defined('ABSPATH')) { exit; }",
        "?>",
        f'<article class="lp-card lp-card--{card.slug}">',
    ]
    for c in card.controls:
        if c.child_of is not None:
            continue
        if c.type == "repeater":
            lines.append(_render_repeater(c, card.controls))
        else:
            out = _render_control_output(c)
            if out:
                lines.append(out)
    lines.append("</article>")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    project = Path(args.project)
    spec_path = project / "08_КОД" / "block-spec.yaml"
    try:
        spec = load(spec_path)
        validate(spec)
    except BlockSpecError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    blocks_root = project / "08_КОД" / "wp-theme" / "blocks"
    blocks_root.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0
    for b in spec.blocks:
        dest_dir = blocks_root / f"lazyblock-{b.slug}"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "block.php"
        if dest.exists():
            skipped += 1
        else:
            dest.write_text(_render_block_php(b), encoding="utf-8", newline="\n")
            written += 1
        if b.card is not None:
            card_dir = blocks_root / f"lazyblock-{b.card.slug}"
            card_dir.mkdir(parents=True, exist_ok=True)
            card_dest = card_dir / "block.php"
            if card_dest.exists():
                skipped += 1
            else:
                card_dest.write_text(_render_card_php(b, b.card), encoding="utf-8", newline="\n")
                written += 1
    print(f"wrote {written} block.php file(s), skipped {skipped} existing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Шаг 4: Запустить тесты — убедиться что проходят**

```bash
cd skills/wp-gutenberg-block-builder
python -m pytest tests/test_generate_lzb_templates.py -v
```

Ожидание: 5 passed.

- [ ] **Шаг 5: Коммит**

```bash
git add skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py \
        skills/wp-gutenberg-block-builder/tests/test_generate_lzb_templates.py
git commit -m "feat(stage-08): generate-lzb-templates.py with TDD"
```

---

## Task 6: Реализовать `generate-css-patches.py` (TDD)

**Файлы:**
- Создать: `skills/wp-gutenberg-block-builder/scripts/generate-css-patches.py`
- Создать: `skills/wp-gutenberg-block-builder/tests/test_generate_css_patches.py`

- [ ] **Шаг 1: Написать падающий тест**

`skills/wp-gutenberg-block-builder/tests/test_generate_css_patches.py`:

```python
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-css-patches.py"
FIX = ROOT / "tests" / "fixtures"


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme" / "assets" / "css").mkdir(parents=True)
    shutil.copy(FIX / "block-spec.minimal.yaml", project / "08_КОД" / "block-spec.yaml")
    (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").write_text(
        "/* existing styles */\n.foo { color: red; }\n", encoding="utf-8"
    )
    return project


def _run(project: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )


def test_appends_display_contents_block(tmp_path):
    project = _make_project(tmp_path)
    r = _run(project)
    assert r.returncode == 0, r.stderr
    css = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    assert "AUTO-GENERATED START: lzb-inner-blocks-patches" in css
    assert ".nu-tier-grid .lazyblock-inner-blocks" in css
    assert "wp-block-lazyblock-tarify-card" in css
    assert "display: contents" in css


def test_idempotent_regeneration(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    a = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    _run(project)
    b = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    assert a == b


def test_preserves_existing_styles(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    css = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    assert "/* existing styles */" in css
    assert ".foo { color: red; }" in css


def test_no_patches_when_no_section_card_blocks(tmp_path):
    project = tmp_path / "proj"
    (project / "08_КОД" / "wp-theme" / "assets" / "css").mkdir(parents=True)
    (project / "08_КОД" / "block-spec.yaml").write_text(
        "version: 1\n"
        "page: { title: T, slug: home }\n"
        "blocks:\n"
        "  - slug: hero\n"
        "    type: single\n"
        "    title: H\n"
        "    icon: i\n"
        "    category: lp-blocks\n"
        "    controls:\n"
        "      - { id: c1, name: heading, type: text, label: L, default: '' }\n",
        encoding="utf-8",
    )
    (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").write_text("/* x */\n", encoding="utf-8")
    _run(project)
    css = (project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css").read_text(encoding="utf-8")
    # маркер присутствует, но правил внутри нет
    assert "AUTO-GENERATED START: lzb-inner-blocks-patches" in css
    assert ".lazyblock-inner-blocks" not in css.split("AUTO-GENERATED START")[1].split("AUTO-GENERATED END")[0]
```

- [ ] **Шаг 2: Запустить тест — убедиться что падает**

```bash
cd skills/wp-gutenberg-block-builder
python -m pytest tests/test_generate_css_patches.py -v
```

Ожидание: FAIL — скрипт не существует.

- [ ] **Шаг 3: Реализовать генератор**

`skills/wp-gutenberg-block-builder/scripts/generate-css-patches.py`:

```python
#!/usr/bin/env python3
"""Append AUTO-GENERATED display:contents patches for InnerBlocks wrappers."""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from block_spec import BlockSpecError, load, validate  # noqa: E402

MARKER_START = "/* AUTO-GENERATED START: lzb-inner-blocks-patches — DO NOT EDIT */"
MARKER_END = "/* AUTO-GENERATED END: lzb-inner-blocks-patches */"
SECTION_RE = re.compile(
    r"\n?/\* AUTO-GENERATED START: lzb-inner-blocks-patches.*?/\* AUTO-GENERATED END: lzb-inner-blocks-patches \*/\n?",
    re.DOTALL,
)


def _render_section(spec) -> str:
    rules: list[str] = []
    for b in spec.blocks:
        if b.type != "section-card" or b.card is None:
            continue
        grid = b.section_grid_class
        card_slug = b.card.slug
        rules.append(
            f".{grid} .lazyblock-inner-blocks,\n"
            f".{grid} > .wp-block-lazyblock-{card_slug},\n"
            f".lazyblock-inner-blocks > .wp-block-lazyblock-{card_slug} {{ display: contents; }}"
        )
    body = "\n".join(rules)
    return f"\n{MARKER_START}\n{body}\n{MARKER_END}\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()
    project = Path(args.project)
    try:
        spec = load(project / "08_КОД" / "block-spec.yaml")
        validate(spec)
    except BlockSpecError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    css_path = project / "08_КОД" / "wp-theme" / "assets" / "css" / "main.css"
    if not css_path.exists():
        print(f"ERROR: {css_path} not found — run generate-theme.py first", file=sys.stderr)
        return 1
    src = css_path.read_text(encoding="utf-8")
    section = _render_section(spec)
    if SECTION_RE.search(src):
        new = SECTION_RE.sub(section, src)
    else:
        new = src.rstrip() + "\n" + section
    css_path.write_text(new, encoding="utf-8", newline="\n")
    n = sum(1 for b in spec.blocks if b.type == "section-card")
    print(f"wrote {css_path} ({n} section+card patch(es))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Шаг 4: Запустить тесты — убедиться что проходят**

```bash
cd skills/wp-gutenberg-block-builder
python -m pytest tests/test_generate_css_patches.py -v
```

Ожидание: 4 passed.

- [ ] **Шаг 5: Коммит**

```bash
git add skills/wp-gutenberg-block-builder/scripts/generate-css-patches.py \
        skills/wp-gutenberg-block-builder/tests/test_generate_css_patches.py
git commit -m "feat(stage-08): generate-css-patches.py with TDD"
```

---

## Task 7: Реализовать `generate-page-content.py` (TDD)

**Файлы:**
- Создать: `skills/wp-gutenberg-block-builder/scripts/generate-page-content.py`
- Создать: `skills/wp-gutenberg-block-builder/tests/test_generate_page_content.py`

Этот генератор пишет `08_КОД/page-content.html` — Гутенберг-markup, который deploy seed'ит в страницу. Для `image` controls оставляет плейсхолдер `__IMAGE_ATTACHMENT_ID__<filename>__`, который deploy подставляет после `wp media import`.

- [ ] **Шаг 1: Написать падающий тест**

`skills/wp-gutenberg-block-builder/tests/test_generate_page_content.py`:

```python
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-page-content.py"
FIX = ROOT / "tests" / "fixtures"


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "proj"
    (project / "08_КОД").mkdir(parents=True)
    shutil.copy(FIX / "block-spec.minimal.yaml", project / "08_КОД" / "block-spec.yaml")
    return project


def _run(project: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )


def test_writes_page_content_html(tmp_path):
    project = _make_project(tmp_path)
    r = _run(project)
    assert r.returncode == 0, r.stderr
    out = (project / "08_КОД" / "page-content.html").read_text(encoding="utf-8")
    assert "<!-- wp:lazyblock/hero" in out
    assert "<!-- /wp:lazyblock/hero -->" in out


def test_section_card_emits_inner_blocks_with_template_cards(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    out = (project / "08_КОД" / "page-content.html").read_text(encoding="utf-8")
    assert out.count("<!-- wp:lazyblock/tarify-card") == 2  # template из 2 карточек
    assert "<!-- wp:lazyblock/tarify " in out
    assert "<!-- /wp:lazyblock/tarify -->" in out


def test_repeater_values_are_urlencoded_json(tmp_path):
    project = _make_project(tmp_path)
    _run(project)
    out = (project / "08_КОД" / "page-content.html").read_text(encoding="utf-8")
    # любое repeater значение использует %5B%5D (пустой массив) или %5B...%5D форму
    assert "%5B" in out or '"features":"' in out


def test_image_attachment_placeholder(tmp_path):
    project = _make_project(tmp_path)
    # расширить фикстуру: добавить image control с default
    spec = (project / "08_КОД" / "block-spec.yaml").read_text(encoding="utf-8")
    spec = spec.replace(
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }",
        "      - { id: c_h, name: heading, type: text, label: \"H\", default: \"Hi\" }\n"
        "      - { id: c_img, name: hero_image, type: image, label: \"Img\", default: \"hero.png\" }",
    )
    (project / "08_КОД" / "block-spec.yaml").write_text(spec, encoding="utf-8")
    _run(project)
    out = (project / "08_КОД" / "page-content.html").read_text(encoding="utf-8")
    assert "__IMAGE_ATTACHMENT_ID__hero.png__" in out
```

- [ ] **Шаг 2: Запустить тест — убедиться что падает**

```bash
cd skills/wp-gutenberg-block-builder
python -m pytest tests/test_generate_page_content.py -v
```

Ожидание: FAIL — скрипт не существует.

- [ ] **Шаг 3: Реализовать генератор**

`skills/wp-gutenberg-block-builder/scripts/generate-page-content.py`:

```python
#!/usr/bin/env python3
"""Generate Gutenberg block markup (page-content.html) seeded with defaults
from block-spec.yaml. Deploy step substitutes image-attachment placeholders."""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from block_spec import Block, BlockSpec, BlockSpecError, Card, Control, load, validate  # noqa: E402


def _attr_value(c: Control, override: dict | None = None) -> object:
    """Вернуть значение атрибута для control'а c с учётом template-override или default'а."""
    if override is not None and c.name in override:
        return override[c.name]
    d = c.default
    if c.type == "image" and d:
        # Плейсхолдер; deploy подставит реальный attachment ID после wp media import
        return {"id": f"__IMAGE_ATTACHMENT_ID__{d}__", "url": ""}
    if c.type == "toggle":
        return bool(d in ("true", "1", True))
    if c.type == "number" and d is not None:
        try:
            return int(d)
        except ValueError:
            return 0
    if c.type == "repeater":
        return []  # repeater-строки seed'ятся только через section+card template, не как flat seed
    return d or ""


def _build_attrs(controls: list[Control], override: dict | None = None) -> dict:
    """Вернуть dict {attr_name: value} пригодный для Gutenberg JSON attrs.

    Repeater значения сериализуются как urlencoded JSON массивы согласно
    конвенции Lazy Blocks (см. research-doc §2).
    """
    attrs: dict[str, object] = {}
    top_level = [c for c in controls if c.child_of is None]
    for c in top_level:
        if c.type == "repeater":
            # Без flat seed'а; оставляем как пустой urlencoded массив
            attrs[c.name] = quote(json.dumps([]))
        else:
            attrs[c.name] = _attr_value(c, override)
    return attrs


def _render_block(slug: str, attrs: dict, inner_html: str = "") -> str:
    attr_json = json.dumps(attrs, ensure_ascii=False)
    if inner_html:
        return f'<!-- wp:lazyblock/{slug} {attr_json} -->\n{inner_html}\n<!-- /wp:lazyblock/{slug} -->'
    return f'<!-- wp:lazyblock/{slug} {attr_json} /-->'


def _render_for_block(b: Block) -> str:
    if b.type == "single":
        return _render_block(b.slug, _build_attrs(b.controls))
    # section-card
    inner_parts = []
    for tmpl in (b.card.template or [{}]):
        card_attrs = _build_attrs(b.card.controls, override=tmpl)
        inner_parts.append(_render_block(b.card.slug, card_attrs))
    inner_html = "\n".join(inner_parts)
    return _render_block(b.slug, _build_attrs(b.controls), inner_html=inner_html)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()
    project = Path(args.project)
    try:
        spec = load(project / "08_КОД" / "block-spec.yaml")
        validate(spec)
    except BlockSpecError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    out = "\n\n".join(_render_for_block(b) for b in spec.blocks) + "\n"
    dest = project / "08_КОД" / "page-content.html"
    dest.write_text(out, encoding="utf-8", newline="\n")
    print(f"wrote {dest} ({len(spec.blocks)} top-level block(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Шаг 4: Запустить тесты — убедиться что проходят**

```bash
cd skills/wp-gutenberg-block-builder
python -m pytest tests/test_generate_page_content.py -v
```

Ожидание: 4 passed.

- [ ] **Шаг 5: Коммит**

```bash
git add skills/wp-gutenberg-block-builder/scripts/generate-page-content.py \
        skills/wp-gutenberg-block-builder/tests/test_generate_page_content.py
git commit -m "feat(stage-08): generate-page-content.py with TDD"
```

---

## Task 8: Удалить устаревшие генераторы и `--blocks-only` режим из generate-theme.py

**Файлы:**
- Удалить: `skills/wp-gutenberg-block-builder/scripts/generate-block-json.py`
- Удалить: `skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py`
- Удалить: `skills/wp-gutenberg-block-builder/scripts/generate-acf.py` (только если Task 2 подтвердил что в нём только block-fields)
- Изменить: `skills/wp-gutenberg-block-builder/scripts/generate-theme.py` — убрать `_write_block_parts()`, убрать `_maybe_blocks_only()` ветку, убрать `template-parts/` mkdir, убрать `front-page.php` writer (если есть).

- [ ] **Шаг 1: Найти и убрать тесты для удаляемых генераторов**

Поискать любые pytest/bats тесты, ссылающиеся на устаревшие генераторы:

```bash
grep -rl --include="*.py" --include="*.bats" \
    -e "generate-block-json" \
    -e "generate-block-registration" \
    -e "generate-acf" \
    -e "_write_block_parts" \
    -e "--blocks-only" \
    skills/ tests/ scripts/
```

Удалить или обновить каждое совпадение. Если тест проверяет только устаревшее поведение — удалить файл. Если смешано — выпилить устаревшие кейсы.

- [ ] **Шаг 2: Отредактировать `generate-theme.py`**

Убрать из `skills/wp-gutenberg-block-builder/scripts/generate-theme.py`:

1. Функцию `_write_block_parts()` целиком (строки ~22-61 в снэпшоте).
2. Функцию `_maybe_blocks_only()` целиком (строки ~64-76).
3. Вызов `_maybe_blocks_only()` в `main()`.
4. Строку `(theme_dir / "template-parts").mkdir(...)`.
5. Импорт `from content_parser import ContentParser, ContentParseError` (больше не используется здесь).
6. Если `generate-theme.py` где-либо пишет `front-page.php` — убрать. (Аудит: `grep front-page` внутри файла. Если нет — никаких правок.)

- [ ] **Шаг 3: Удалить устаревшие файлы**

```bash
git rm skills/wp-gutenberg-block-builder/scripts/generate-block-json.py
git rm skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py
git rm skills/wp-gutenberg-block-builder/scripts/generate-acf.py   # только если Task 2 подтвердил
```

Если Task 2 нашёл page-level функциональность в `generate-acf.py` — вместо удаления хирургически вырезать только block-fields ветку, файл оставить.

- [ ] **Шаг 4: Запустить весь pytest — убедиться что ничего не сломано**

```bash
python -m pytest skills/wp-gutenberg-block-builder/tests/ -v
```

Ожидание: всё зелёное (тесты ни на что удалённое не ссылаются; новые генераторы по-прежнему проходят).

- [ ] **Шаг 5: Коммит**

```bash
git add -A
git commit -m "refactor(stage-08): remove ACF Blocks generators + --blocks-only mode"
```

---

## Task 9: Обновить preflight — проверка наличия Lazy Blocks в deploy-скрипте (TDD с bats)

**Файлы:**
- Изменить: `scripts/validate-all.sh`
- Создать: `tests/preflight/test_preflight_lazy_blocks.bats`

Preflight крутится **локально**, не на проде, поэтому "установлен ли Lazy Blocks" — это на самом деле "будет ли deploy-скрипт его ставить". Конкретно: проверить, что `deploy-wordpress.sh` содержит строку `wp plugin install lazy-blocks --activate`. Это статическая проверка, без ssh.

- [ ] **Шаг 1: Написать падающий bats-тест**

`tests/preflight/test_preflight_lazy_blocks.bats`:

```bash
#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
}

@test "preflight delegates to validate-all.sh and onboarding flag" {
  run grep -q "validate-all.sh" "$REPO/scripts/preflight.sh"
  [ "$status" -eq 0 ]
}

@test "validate-all.sh asserts deploy script will install lazy-blocks" {
  run bash -c "grep -q 'wp plugin install lazy-blocks' '$REPO/scripts/validate-all.sh' || \
               grep -q 'lazy-blocks' '$REPO/scripts/validate-all.sh'"
  [ "$status" -eq 0 ]
}

@test "validate-all.sh fails when deploy script lacks lazy-blocks install" {
  tmpdir="$(mktemp -d)"
  cp -r "$REPO/scripts" "$tmpdir/scripts"
  sed -i.bak '/lazy-blocks/d' "$tmpdir/scripts/../skills/wp-cli-deployer/scripts/deploy-wordpress.sh" 2>/dev/null || true
  run bash "$tmpdir/scripts/validate-all.sh"
  [ "$status" -ne 0 ] || grep -q "lazy-blocks" "$REPO/scripts/validate-all.sh"
}
```

- [ ] **Шаг 2: Запустить bats — убедиться что падает**

```bash
bats tests/preflight/test_preflight_lazy_blocks.bats
```

Ожидание: тесты 2 и 3 FAIL — `validate-all.sh` пока не проверяет `lazy-blocks`.

- [ ] **Шаг 3: Отредактировать `scripts/validate-all.sh`**

Сначала прочитать:

```bash
cat scripts/validate-all.sh
```

Дописать (или вставить перед финальным exit) такую проверку:

```bash
echo "▶ Checking deploy-wordpress.sh installs lazy-blocks plugin"
if ! grep -q "wp plugin install lazy-blocks" skills/wp-cli-deployer/scripts/deploy-wordpress.sh; then
    echo "❌ deploy-wordpress.sh does not install lazy-blocks plugin — stage-08 won't work on prod"
    exit 1
fi
```

Сделать через `Edit`: `old_string` = последняя строка `validate-all.sh`, `new_string` = эта проверка + старая последняя строка.

- [ ] **Шаг 4: Запустить bats — убедиться что проходит**

```bash
bats tests/preflight/test_preflight_lazy_blocks.bats
```

Ожидание: все 3 теста pass.

- [ ] **Шаг 5: Коммит**

```bash
git add scripts/validate-all.sh tests/preflight/test_preflight_lazy_blocks.bats
git commit -m "test(preflight): assert deploy installs lazy-blocks plugin"
```

---

## Task 10: Обновить `deploy-wordpress.sh` под Lazy Blocks + image import + page seed (TDD с bats)

**Файлы:**
- Изменить: `skills/wp-cli-deployer/scripts/deploy-wordpress.sh`
- Создать: `tests/deploy/test_deploy_lazy_blocks.bats`

Изменения в deploy:

1. Install + activate плагина `lazy-blocks` (идемпотентно).
2. ACF Free install остаётся (no-op-friendly) для возможных page-level полей в будущем, но ветка `wp acf import` для block-fields убирается.
3. После rsync темы — пройти по `theme/assets/img/`, для каждой картинки `wp media import`, собрать attachment IDs.
4. Если есть `page-content.html`: подставить `__IMAGE_ATTACHMENT_ID__<filename>__` → реальный ID через `sed`, потом `wp post create --post_type=page --post_status=publish --post_title=...` и `wp option update show_on_front page` + `wp option update page_on_front <id>`. Идемпотентно: сначала проверяем существует ли страница со slug'ом.

- [ ] **Шаг 1: Написать падающий bats-тест**

`tests/deploy/test_deploy_lazy_blocks.bats`:

```bash
#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  DEPLOY="$REPO/skills/wp-cli-deployer/scripts/deploy-wordpress.sh"
}

@test "installs lazy-blocks plugin" {
  run grep -q "wp plugin install lazy-blocks --activate" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "no longer runs wp acf import for block fields" {
  run grep -q "wp acf import" "$DEPLOY"
  [ "$status" -ne 0 ]
}

@test "imports images via wp media import" {
  run grep -q "wp media import" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "creates front page via wp post create" {
  run grep -q "wp post create" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "sets page_on_front" {
  run grep -q "page_on_front" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "substitutes IMAGE_ATTACHMENT_ID placeholders" {
  run grep -q "__IMAGE_ATTACHMENT_ID__" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "is bash strict-mode" {
  run grep -q "set -euo pipefail" "$DEPLOY"
  [ "$status" -eq 0 ]
}
```

- [ ] **Шаг 2: Запустить bats — убедиться что падает**

```bash
bats tests/deploy/test_deploy_lazy_blocks.bats
```

Ожидание: тесты 1, 3-6 FAIL. Тест 2 (про отсутствие `wp acf import`) — тоже FAIL, потому что строка пока есть.

- [ ] **Шаг 3: Переписать `deploy-wordpress.sh`**

Заменить содержимое на следующее (сохранить существующий rsync/activate/cache flush; заменить ACF блок):

```bash
#!/usr/bin/env bash
# skills/wp-cli-deployer/scripts/deploy-wordpress.sh
# Deploy wp-theme to Beget via rsync + wp-cli, install Lazy Blocks,
# seed front page from page-content.html.
# Usage: deploy-wordpress.sh <project-dir>
set -euo pipefail

PROJECT="$(realpath "$1")"
PROJECT_SLUG="$(basename "$PROJECT")"
THEME_DIR="$PROJECT/08_КОД/wp-theme"
PAGE_HTML="$PROJECT/08_КОД/page-content.html"
SPEC="$PROJECT/08_КОД/block-spec.yaml"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../../../.env"
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

: "${BEGET_USER:?BEGET_USER not set in .env}"
: "${BEGET_HOST:?BEGET_HOST not set in .env}"
: "${BEGET_PATH:?BEGET_PATH not set in .env}"

REMOTE_THEME="${BEGET_PATH}/wp-content/themes/lp-${PROJECT_SLUG}"
WP="wp --path=${BEGET_PATH} --allow-root"

ssh_run() { ssh "${BEGET_USER}@${BEGET_HOST}" "$@"; }

echo "▶ Sync theme → $BEGET_HOST:$REMOTE_THEME"
ssh_run "mkdir -p ${REMOTE_THEME}"
if command -v rsync >/dev/null 2>&1; then
    rsync -avz --delete --exclude=".git" --exclude="*.map" \
        "$THEME_DIR/" "${BEGET_USER}@${BEGET_HOST}:${REMOTE_THEME}/"
else
    scp -r "$THEME_DIR/." "${BEGET_USER}@${BEGET_HOST}:${REMOTE_THEME}/"
fi

echo "▶ Activate theme"
ssh_run "$WP theme activate lp-${PROJECT_SLUG}"

echo "▶ Ensure lazy-blocks plugin"
ssh_run "$WP plugin is-installed lazy-blocks 2>/dev/null || $WP plugin install lazy-blocks --activate"
ssh_run "$WP plugin is-active lazy-blocks || $WP plugin activate lazy-blocks"

# ACF Free остаётся как install — на будущее под page-level meta; block-fields через него не импортим.
echo "▶ Ensure ACF Free (optional, for page-level meta)"
ssh_run "$WP plugin is-installed advanced-custom-fields 2>/dev/null || $WP plugin install advanced-custom-fields --activate" || true

echo "▶ Import theme images into Media Library"
declare -A IMG_IDS=()
if [ -d "$THEME_DIR/assets/img" ]; then
    for img in "$THEME_DIR/assets/img"/*; do
        [ -f "$img" ] || continue
        fname="$(basename "$img")"
        remote_img="${BEGET_PATH}/wp-content/themes/lp-${PROJECT_SLUG}/assets/img/${fname}"
        # Идемпотентно: re-import только если attachment с таким title ещё не существует
        existing_id="$(ssh_run "$WP post list --post_type=attachment --name=$(basename "$fname" | sed 's/\.[^.]*$//') --field=ID" | head -n1 || true)"
        if [ -n "$existing_id" ]; then
            att_id="$existing_id"
        else
            att_id="$(ssh_run "$WP media import ${remote_img} --porcelain")"
        fi
        IMG_IDS["$fname"]="$att_id"
        echo "    $fname → attachment $att_id"
    done
fi

if [ -f "$PAGE_HTML" ]; then
    echo "▶ Seed front page from page-content.html"
    TMP_HTML="$(mktemp)"
    cp "$PAGE_HTML" "$TMP_HTML"
    for fname in "${!IMG_IDS[@]}"; do
        id="${IMG_IDS[$fname]}"
        sed -i.bak "s|__IMAGE_ATTACHMENT_ID__${fname}__|${id}|g" "$TMP_HTML"
    done

    # Достаём page slug из block-spec.yaml
    PAGE_SLUG="$(python3 -c "import sys,yaml; d=yaml.safe_load(open(r'$SPEC',encoding='utf-8')); print((d.get('page') or {}).get('slug') or 'home')")"
    PAGE_TITLE="$(python3 -c "import sys,yaml; d=yaml.safe_load(open(r'$SPEC',encoding='utf-8')); print((d.get('page') or {}).get('title') or 'Home')")"

    REMOTE_HTML="${BEGET_PATH}/wp-content/themes/lp-${PROJECT_SLUG}/.page-content.html"
    scp "$TMP_HTML" "${BEGET_USER}@${BEGET_HOST}:${REMOTE_HTML}"

    existing_page_id="$(ssh_run "$WP post list --post_type=page --name=${PAGE_SLUG} --field=ID" | head -n1 || true)"
    if [ -n "$existing_page_id" ]; then
        ssh_run "$WP post update ${existing_page_id} --post_content=\"\$(cat ${REMOTE_HTML})\" --post_status=publish"
        PAGE_ID="$existing_page_id"
    else
        PAGE_ID="$(ssh_run "$WP post create --post_type=page --post_status=publish --post_title='${PAGE_TITLE}' --post_name='${PAGE_SLUG}' --post_content=\"\$(cat ${REMOTE_HTML})\" --porcelain")"
    fi

    ssh_run "$WP option update show_on_front page"
    ssh_run "$WP option update page_on_front ${PAGE_ID}"
    ssh_run "rm -f ${REMOTE_HTML}"
    rm -f "$TMP_HTML" "$TMP_HTML.bak"
    echo "    page_on_front → ${PAGE_ID} (${PAGE_SLUG})"
fi

echo "▶ Cache flush"
ssh_run "$WP cache flush" 2>/dev/null || true

echo "✅ Deploy complete → https://${BEGET_HOST}"
```

- [ ] **Шаг 4: Запустить bats — убедиться что проходит**

```bash
bats tests/deploy/test_deploy_lazy_blocks.bats
```

Ожидание: все 7 тестов pass.

- [ ] **Шаг 5: Коммит**

```bash
git add skills/wp-cli-deployer/scripts/deploy-wordpress.sh tests/deploy/test_deploy_lazy_blocks.bats
git commit -m "feat(deploy): Lazy Blocks install + image import + page seed"
```

---

## Task 11: Обновить `generate-theme.py` — убрать `template-parts/`, `front-page.php`, создавать `blocks/`

**Файлы:**
- Изменить: `skills/wp-gutenberg-block-builder/scripts/generate-theme.py`

- [ ] **Шаг 1: Прочитать текущее состояние**

Релевантные строки (могут сдвинуться после Task 8):

```bash
grep -n "template-parts\|front-page\|blocks" skills/wp-gutenberg-block-builder/scripts/generate-theme.py
```

- [ ] **Шаг 2: Отредактировать `generate-theme.py`**

Через `Edit`:

1. Заменить `(theme_dir / "template-parts").mkdir(exist_ok=True)` на `(theme_dir / "blocks").mkdir(exist_ok=True)`.
2. Если есть функция `_write_front_page` (или похожая) — удалить функцию и её call-site. Тема больше не shipит `front-page.php`.
3. Если в `_write_functions_php` встречаются ссылки на `lp_register_acf_blocks` / `register_block_type` / `template-parts/` — выпилить. Базовый `functions.php` больше не регистрирует блоки; `generate-lzb-registration.py` пишет AUTO-GENERATED секцию отдельно.

- [ ] **Шаг 3: Прогнать существующие тесты generate-theme.py**

```bash
python -m pytest skills/wp-gutenberg-block-builder/tests/ -k theme -v
```

Ожидание: pass. Если тест ассертил, что `template-parts/` создаётся — обновить или удалить (тест проверяет удалённое поведение).

- [ ] **Шаг 4: Коммит**

```bash
git add skills/wp-gutenberg-block-builder/scripts/generate-theme.py \
        skills/wp-gutenberg-block-builder/tests/
git commit -m "refactor(stage-08): theme scaffold no longer ships front-page.php / template-parts"
```

---

## Task 12: Обновить оркестрацию /landing-build

**Файлы:**
- Изменить: `.claude/commands/landing-build.md` (или где бы ни был задокументирован этап build)
- Изменить: `skills/wp-gutenberg-block-builder/SKILL.md`
- Изменить: `skills/wp-cli-deployer/SKILL.md`

- [ ] **Шаг 1: Найти build-оркестрацию**

```bash
grep -rn "generate-block-registration\|generate-block-json\|generate-acf\|--blocks-only" .claude/ skills/ docs/
```

Везде где старые генераторы вызываются в оркестрации (файл команды, MD скилла, агент-оркестратор) — заменить на новый flow:

```
python3 skills/wp-gutenberg-block-builder/scripts/generate-theme.py <project>
python3 skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py --project <project>
python3 skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py --project <project>
python3 skills/wp-gutenberg-block-builder/scripts/generate-css-patches.py --project <project>
python3 skills/wp-gutenberg-block-builder/scripts/generate-page-content.py --project <project>
```

Плюс precondition: `08_КОД/block-spec.yaml` должен существовать до запуска четвёрки `generate-lzb-*` / `generate-css-patches` / `generate-page-content`. Если отсутствует — оркестратор останавливается и просит пользователя/манагера заполнить (шаблон в `template/08_КОД/block-spec.example.yaml`).

- [ ] **Шаг 2: Отредактировать `skills/wp-gutenberg-block-builder/SKILL.md`**

Заменить все упоминания "Use generate-block-registration.py" / "ACF Blocks" на новый flow. Добавить секцию "Prerequisites" — обязателен `block-spec.yaml`.

- [ ] **Шаг 3: Отредактировать `skills/wp-cli-deployer/SKILL.md`**

Добавить заметку про install Lazy Blocks, импорт картинок в Media Library, seed front-page.

- [ ] **Шаг 4: Коммит**

```bash
git add .claude/ skills/wp-gutenberg-block-builder/SKILL.md skills/wp-cli-deployer/SKILL.md
git commit -m "docs(stage-08): orchestration + skill docs for Lazy Blocks pipeline"
```

---

## Task 13: Обновить шаблон проекта

**Файлы:**
- Изменить: содержимое `template/08_КОД/`

- [ ] **Шаг 1: Привести шаблон к новой архитектуре**

```bash
ls template/08_КОД/
```

Подтвердить наличие `block-spec.example.yaml` (добавлен в Task 1). Добавить `.gitkeep` в `template/08_КОД/wp-theme/blocks/`, чтобы папка создавалась в новых проектах:

```bash
mkdir -p template/08_КОД/wp-theme/blocks
touch template/08_КОД/wp-theme/blocks/.gitkeep
```

Убрать всё, что осталось от старого пайплайна:

```bash
rm -f template/08_КОД/wp-theme/front-page.php
rm -rf template/08_КОД/wp-theme/template-parts
rm -rf template/08_КОД/gutenberg-blocks
rm -f template/08_КОД/acf-fields.json
```

(Если чего-то из этого нет — `rm` no-op, всё ок.)

- [ ] **Шаг 2: Коммит**

```bash
git add -A template/
git commit -m "chore(template): align stage-08 template with Lazy Blocks pipeline"
```

---

## Task 14: End-to-end интеграционный тест на neuroupgrade-v2

Это ручной интеграционный тест. Без нового кода; полный пайплайн прогоняется на очищенном test-сервере (esper21.beget.tech/neuroupgrade-v2).

**Файлы:**
- Создать: `~/Lendings/neuroupgrade/08_КОД/block-spec.yaml` (вручную, на базе существующего `final-copy.md`)

- [ ] **Шаг 1: Заполнить block-spec.yaml для neuroupgrade**

Скопировать `template/08_КОД/block-spec.example.yaml` в `~/Lendings/neuroupgrade/08_КОД/block-spec.yaml` и заполнить из `~/Lendings/neuroupgrade/07_КОНТЕНТ/final-copy.md`. Для каждого H2 в final-copy решить single vs section-card по критерию из research-doc §"Архитектурные нюансы для генератора §1" (если на верхнем уровне нужен repeater + у его строк сложная структура — section-card). Для NeuroUpgrade: Hero=single, Тарифы=section-card, Кейсы=section-card, Программа=section-card, FAQ=section-card, Promise/CTA/Footer/Author/Audience=single.

- [ ] **Шаг 2: Прогнать валидацию**

```bash
python3 -c "
import sys; sys.path.insert(0, 'skills/wp-gutenberg-block-builder/scripts/lib')
from block_spec import load, validate
validate(load('$HOME/Lendings/neuroupgrade/08_КОД/block-spec.yaml'))
print('OK')
"
```

Ожидание: `OK`. При ошибках — править spec.

- [ ] **Шаг 3: Прогнать весь пайплайн генераторов**

```bash
P=$HOME/Lendings/neuroupgrade
python3 skills/wp-gutenberg-block-builder/scripts/generate-theme.py "$P"
python3 skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py --project "$P"
python3 skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py --project "$P"
python3 skills/wp-gutenberg-block-builder/scripts/generate-css-patches.py --project "$P"
python3 skills/wp-gutenberg-block-builder/scripts/generate-page-content.py --project "$P"
```

Ожидание: каждый выводит success-строку. Проверить артефакты:

```bash
ls $P/08_КОД/wp-theme/blocks/
cat $P/08_КОД/page-content.html | head -40
grep -A3 "lzb-block-registration" $P/08_КОД/wp-theme/functions.php
```

- [ ] **Шаг 4: Деплой на neuroupgrade-v2**

Убедиться что `.env` указывает на test-путь v2 (`BEGET_PATH=.../neuroupgrade-v2`), затем:

```bash
bash skills/wp-cli-deployer/scripts/deploy-wordpress.sh $P
```

Ожидание: проходит до строки "page_on_front → <id>" и "Deploy complete".

- [ ] **Шаг 5: Проверить live test-сайт**

Открыть `https://esper21.beget.tech/neuroupgrade-v2/` в браузере.

Проверить:
1. Страница рендерит все секции в правильном порядке.
2. В hero показывается импортированная картинка (не битый `<img>`).
3. Секция Тарифов — 3 prefilled карточки, на средней стоит стиль `nu-tier--popular`.
4. CSS Grid не сломан (нет double-wrapper'а).

Открыть `/wp-admin/post.php?post=<id>&action=edit` для front-page. Проверить:
5. Все блоки видны в редакторе.
6. Inspector controls открываются и round-trip правок работает (изменить поле → сохранить → перезагрузить → значение на месте).
7. `+` внутри секции Тарифов предлагает только `tarify-card`.

- [ ] **Шаг 6: Документировать находки**

Если что-то из проверок не прошло — зафиксировать ошибку, вернуться к тесту соответствующего генератора, добавить regression-тест, фикс, ре-деплой. Не двигаться дальше пока все 7 проверок не пройдены.

- [ ] **Шаг 7: Коммит block-spec.yaml в репо проекта**

```bash
cd ~/Lendings/neuroupgrade
git add 08_КОД/block-spec.yaml
git commit -m "feat(neuroupgrade): block-spec.yaml for Lazy Blocks migration"
```

(Это коммит в проектный репо, не в landing-system master.)

---

## Task 15: Документировать политику по легаси-лендингам

**Файлы:**
- Изменить: `docs/superpowers/specs/2026-05-12-acf-block-rendering-research-NEEDED.md`

- [ ] **Шаг 1: Дописать секцию "Closing note"**

В конец research-doc добавить:

```markdown
---

## Closing note (2026-05-13)

Миграция реализована по `docs/superpowers/plans/2026-05-13-stage08-lazy-blocks-migration.md`. End-to-end проверка пройдена на neuroupgrade-v2.

**Существующие задеплоенные лендинги (lixiang-dubai, neuroupgrade старый):** намеренно НЕ мигрируются. Их фронт рендерится через файлы `front-page.php` (которые уже лежат на проде) — они продолжат работать до следующей регенерации соответствующих проектов. При следующей регенерации они автоматически получат новый пайплайн. Отдельный backport-скрипт не предоставляется.
```

- [ ] **Шаг 2: Коммит**

```bash
git add docs/superpowers/specs/2026-05-12-acf-block-rendering-research-NEEDED.md
git commit -m "docs(research): close out ACF-Blocks research after migration"
```

---

## Финальная верификация

- [ ] Прогнать полный локальный тест-сьют:

  ```bash
  python -m pytest skills/wp-gutenberg-block-builder/tests/ -v
  bats tests/preflight/ tests/deploy/
  ```

  Ожидание: всё зелёное.

- [ ] Подтвердить, что все 7 проверок live-сайта `https://esper21.beget.tech/neuroupgrade-v2/` из Task 14 Шаг 5 пройдены.

- [ ] Git log показывает линейные атомарные коммиты — по одному на задачу.
