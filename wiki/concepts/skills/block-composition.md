---
slug: block-composition
type: skill
name: "Block Composition (пост-обработка макета)"
stage: "07b"
tags: [compose, placeholders, photos, visuals, mood, tokens, rerender]
triggers: []
inputs: [07b-composed, 07c-photos, 07d-visuals]
outputs: [07b-composed]
pre_reqs: [07b-composed, 07c-photos, 07d-visuals]
related: [landing-compose, landing-photos, landing-visuals, block-composer, block-library]
sources: ["skills/block-composition/SKILL.md"]
updated: 2026-06-19
confidence: {triggers: low, stage: low}
---

# Block Composition (пост-обработка макета)

## Что делает

Скилл отвечает за пост-обработку готового `composed.html` — макета, который агент `block-composer` уже нарисовал по прототипу и референсу. Выполняет три операции: заменяет placeholder-слоты реальными активами (фото и визуалами), инжектирует mood-палитру из `block-library/_styles/` для переключения цветовой темы на уровне сайта, а также предоставляет библиотечную функцию `inject_block()` для photo/visual-пайплайнов (PR-B/PR-C). Машинная склейка блоков из библиотеки перенесена в архив: система перешла на reference-driven flow, где агент рисует макет сам.

## Когда вызывается

Вызывается программно после завершения этапов 07c (фото) и 07d (визуалы): `landing-orchestrator` запускает `rerender-composed.py`, чтобы подставить реальные ассеты вместо `[SLOT: name]` / `data-slot="name"` placeholders. `inject-tokens.py` вызывается при переключении mood-палитры (плагин `lp-preview-panel`). Прямого slash-триггера нет — скилл используется внутри других этапов.

## Вход → выход

**Вход:** готовый `07b_COMPOSED/composed.html` с placeholder-слотами; `07c_PHOTOS/selections.yaml` с выбранными фото (processed); активы из `07d_VISUALS/icons/` и `07d_VISUALS/infographics/`; `tokens.json` с mood-палитрой.

**Выход:** обновлённый `composed.html` с подставленными реальными фото и визуалами вместо placeholders; резервная копия `composed.html.bak`; опционально — макет с инжектированной mood-палитрой.

## Failure modes

- `selections.yaml` отсутствует или не прошёл `photo-board` — слоты фото остаются незаменёнными, скрипт падает без бэкапа.
- Имя слота в `composed.html` не совпадает с ключом в `selections.yaml` — placeholder остаётся в финальном HTML незаметно.
- `inject-tokens.py` применяет палитру поверх прямых цветов (не токенов) — переключатель mood не работает, нарушение правила 100% токенизации.
- Файлы `07d_VISUALS/` отсутствуют (PR-C не запускался) — иконки/инфографика остаются как `[SLOT: ...]` в вёрстке.
- Архивные скрипты (`compose-blocks.py`, `validate-selections.py`) случайно подтягиваются живым кодом — блокируется guard-тестом `pytest tests/archive/`.

## Related

- [[landing-compose]] — создаёт исходный `composed.html`, который этот скилл дополняет
- [[landing-photos]] — поставляет `selections.yaml` и обработанные фото для подстановки
- [[landing-visuals]] — поставляет иконки и инфографику для слотов
- [[block-composer]] — агент, рисующий макет; block-composition лишь постпроцессит его результат
- [[block-library]] — источник mood-палитр (`_styles/`) для `inject-tokens.py`
- [[07b-composed]] — этап, в рамках которого скилл завершает работу с макетом
- [[07c-photos]] — этап-поставщик фото-ассетов
- [[07d-visuals]] — этап-поставщик визуальных ассетов