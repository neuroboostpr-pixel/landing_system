---
slug: brand-architect
type: agent
name: "Brand Architect — синтез бренд-кита"
stage: "04"
tags: [brand, typography, palette, provenance, legal]
triggers: [landing-brand]
inputs:
  - 03b_КОНЦЕПТ/visual-concept.yaml
  - 04_БРЕНД/extracted/palette.yaml
  - 04_БРЕНД/extracted/fonts.yaml
  - 04_БРЕНД/extracted/icons.yaml
  - 04_БРЕНД/extracted/grid.md
  - 04_БРЕНД/extracted/motion.md
  - 03_РЕФЕРЕНСЫ/index.yaml
  - 01a_АНАЛИЗ_НИШИ/positioning.md
  - 01a_АНАЛИЗ_НИШИ/market-profile.md
  - 01a_АНАЛИЗ_НИШИ/landing-structure.md
outputs:
  - 04_БРЕНД/brand-kit.md
  - 04_БРЕНД/brand-kit.html
  - 04_БРЕНД/extracted/legal.yaml
gates: [brand_kit_html_approved]
pre_reqs: [03-referensy, 01a-analiz-nishi, style-extractor]
related: [brand-kit-build, landing-brand, style-extractor, design-system-generator, 04-brend, stage-execution-protocol, niche-analyst]
sources: ["agents/brand-architect.md"]
updated: 2026-06-19
confidence: {gates: low}
---

# Brand Architect — синтез бренд-кита

## Что делает

Агент этапа 04: собирает все данные, извлечённые на предшествующих шагах (палитра, шрифты, иконки, сетка, анимации), и синтезирует единый `brand-kit.md` с полной провенансой — каждый токен трассируется к источнику. Реализует визуальный концепт из `03b_КОНЦЕПТ/visual-concept.yaml`, не изобретая палитру самостоятельно. Дополнительно собирает legal-реквизиты Оператора ПД (152-ФЗ) и рендерит HTML-превью бренд-кита для согласования с клиентом.

## Когда вызывается

Запускается командой `/landing-brand` после завершения этапа 03 (референсы одобрены, `visual-concept.yaml` присутствует). Не стартует без утверждённого visual-concept: при отсутствии файла останавливается и просит запустить `/landing-visual-concept`.

## Вход → выход

**Вход:** утверждённый `visual-concept.yaml`; пять извлечённых артефактов из `04_БРЕНД/extracted/` (палитра, шрифты, иконки, сетка, motion); `03_РЕФЕРЕНСЫ/index.yaml`; три файла ниши из `01a_АНАЛИЗ_НИШИ/` (positioning, market-profile, landing-structure).

**Выход:** `04_БРЕНД/brand-kit.md` — канонический бренд-кит с провенансой; `04_БРЕНД/brand-kit.html` — визуальный превью (свотчи, образцы шрифтов, иконки); `04_БРЕНД/extracted/legal.yaml` — юридические реквизиты клиента.

## Чем закрывается этап (gates)

- `brand_kit_html_approved` — пользователь явно одобрил `brand-kit.html` перед переходом к этапу 05

## Failure modes

- **Отсутствует `visual-concept.yaml`** — агент останавливается; этап 03b не завершён, дальнейшая работа заблокирована.
- **Концептуальная правка после показа превью** (другой цвет, другой mood) — без перезаписи `visual-concept.yaml` агент отклоняет правку и просит сначала обновить файл концепта.
- **Неполный набор extracted-артефактов** — HARD GATE не пропускает генерацию, если хоть один из пяти файлов отсутствует.
- **Legal-реквизиты не заполнены** — pipeline не блокируется, но деплой в РФ невозможен; секция Legal в brand-kit остаётся с метками `TODO_LEGAL`.
- **Предшественник (03-referensy) не закрыт** — PreToolUse-хук физически блокирует Write/Edit к файлам этапа 04.

## Related

- [[brand-kit-build]] — скилл-владелец; содержит Python-скрипты `build.py` и `render-html.py`
- [[landing-brand]] — slash-команда, которая диспатчит этого агента
- [[style-extractor]] — производит все extracted/*.yaml, необходимые на входе
- [[design-system-generator]] — следующий этап (05), использует brand-kit.md как базу
- [[04-brend]] — каталог этапа, в котором агент работает
- [[stage-execution-protocol]] — обязательный протокол pre-flight перед любым Write
- [[niche-analyst]] — производит positioning.md и market-profile.md, влияющие на типографику и палитру