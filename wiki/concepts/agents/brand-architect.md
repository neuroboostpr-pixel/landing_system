---
slug: brand-architect
type: agent
name: "Архитектор бренд-кита"
stage: "04"
tags: [brand, design-tokens, provenance, legal, typography]
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
gates: [brand_kit_approved]
pre_reqs: [03-referensy, 01a-analiz-nishi, style-extractor]
related:
  - brand-kit-build
  - style-extractor
  - landing-brand
  - 04-brend
  - 05-dizayn-sistema
  - design-system-generator
  - stage-execution-protocol
sources: ["agents/brand-architect.md"]
updated: 2026-06-19
confidence: {gates: low}
---

# Архитектор бренд-кита

## Что делает

Агент этапа 04. Синтезирует единый бренд-кит (`brand-kit.md`) из всех извлечённых стилевых данных — палитры, шрифтов, иконок, сетки и motion-токенов. Каждый токен сопровождается ссылкой на источник (провенанс). Параллельно собирает юридические реквизиты Оператора ПД для выполнения требований 152-ФЗ и рендерит HTML-превью для согласования с менеджером. Правки делит на концептуальные (→ redirect на `visual-concept.yaml`) и локальные (принимает сразу). Фиксирует самостоятельно принятые решения в `.stage-decisions/04_brand.md`.

## Когда вызывается

Запускается скиллом `/landing-brand` после того, как `style-extractor` завершил работу и в `03b_КОНЦЕПТ/` появился утверждённый `visual-concept.yaml`. Если файл концепта отсутствует — агент прекращает работу и просит сначала закрыть этап 03b.

## Вход → выход

**Вход:** утверждённый `visual-concept.yaml` (03b), пять артефактов extraction (палитра, шрифты, иконки, сетка, motion), индекс референсов (03), файлы позиционирования и профиля ниши (01a).

**Выход:** `04_БРЕНД/brand-kit.md` — канонический бренд-кит с провенансом; `04_БРЕНД/brand-kit.html` — визуальное превью (свотчи, шрифтовые образцы, иконки); `04_БРЕНД/extracted/legal.yaml` — реквизиты Оператора ПД.

## Чем закрывается этап (gates)

- `brand_kit_approved` — пользователь явно подтвердил `brand-kit.html`; без этого этап 05 не открывается.

## Failure modes

- `visual-concept.yaml` отсутствует или устарел — агент останавливается, Pipeline уходит в дедлок этапа 04.
- Не все пять extracted-файлов присутствуют в `04_БРЕНД/extracted/` — `build.py` падает с ошибкой, brand-kit не генерируется.
- Менеджер вносит концептуальную правку (смена цвета, mood) напрямую в brand-kit вместо `visual-concept.yaml` — агент принимает её как локальную; при следующем прогоне правка перезатирается.
- Legal-данные не получены и поле остаётся `TODO_LEGAL` — лендинг не может выйти в продакшен в РФ без заполнения `legal.yaml` до `/landing-deploy`.
- `gate-check.sh` для этапа 04 возвращает exit != 0 (не закрыты предшественники) — `PreToolUse`-хук физически блокирует запись файлов.

## Related

- [[brand-kit-build]] — скилл, владеющий агентом и Python-скриптами `build.py` / `render-html.py`
- [[style-extractor]] — предшественник: извлекает palette/fonts/icons/grid/motion в `04_БРЕНД/extracted/`
- [[landing-brand]] — команда-триггер этапа 04
- [[04-brend]] — папка-этап в шаблоне проекта
- [[05-dizayn-sistema]] — следующий этап; открывается только после `brand_kit_approved`
- [[design-system-generator]] — агент этапа 05, потребляет brand-kit.md как вход
- [[stage-execution-protocol]] — обязательный протокол pre-flight для всех агентов