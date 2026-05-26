---
slug: brand-architect
type: agent
name: "Brand Architect"
stage: "04"
tags: [brand-kit, style, provenance, legal, 152-fz, palette, fonts, icons]
triggers: [landing-brand]
inputs:
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
gates: [brand-kit-approved]
pre_reqs: [style-extractor]
related:
  - landing-brand
  - landing-design
  - landing-niche
sources: ["agents/brand-architect.md"]
updated: 2026-05-26
confidence:
  triggers: low
---

# Brand Architect

## Что делает

Агент этапа 04. Синтезирует все извлечённые стилевые данные (палитра, шрифты, иконки, сетка, анимации) в единый `brand-kit.md` с полным указанием источника для каждого токена. Параллельно собирает legal-реквизиты Оператора ПД (для 152-ФЗ compliance) и записывает их в `legal.yaml`. На выходе рендерит HTML-превью `brand-kit.html` со свотчами, образцами шрифтов и иконками для визуального утверждения командой.

## Когда вызывается

Запускается командой `/landing-brand` после того, как `style-extractor` отработал и все пять файлов в `04_БРЕНД/extracted/` присутствуют. Агент читает `.landing-state.yaml` и убеждается, что `current_stage == 04_brand`; иначе отказывается действовать.

## Вход → выход

**Вход:** пять YAML/MD-артефактов от `style-extractor` (`palette.yaml`, `fonts.yaml`, `icons.yaml`, `grid.md`, `motion.md`) + одобренный список референсов `03_РЕФЕРЕНСЫ/index.yaml` + три обязательных документа ниши (`positioning.md`, `market-profile.md`, `landing-structure.md`).

**Выход:** `04_БРЕНД/brand-kit.md` — канонический бренд-кит с провенансом; `04_БРЕНД/brand-kit.html` — визуальный превью; `04_БРЕНД/extracted/legal.yaml` — реквизиты Оператора ПД (или заглушки `TODO_LEGAL`).

## Чем закрывается этап (gates)

- `brand-kit-approved` — пользователь явно утвердил `brand-kit.html` перед переходом на этап 05 (Design System).

## Failure modes

- Один из пяти `extracted/*.yaml` файлов отсутствует — агент останавливается с ошибкой hard gate; решение: перезапустить `style-extractor`.
- Файл `01a_АНАЛИЗ_НИШИ/positioning.md` не содержит поля `**Mode:**` — бренд-кит генерируется без mode-аугментации, тон и палитра могут не соответствовать нише.
- Пользователь пропускает сбор legal-данных — поля заполняются `TODO_LEGAL`; `landing-deploy` будет заблокирован до заполнения.
- `scripts/gate-check.sh --stage 04_brand` возвращает exit != 0 — `PreToolUse` hook блокирует все Write/Edit, нужно закрыть предшественника.
- `brand-kit.html` утверждён без проверки соответствия блокам из `landing-structure.md` — design-system на этапе 05 не покроет все `template-parts`.

## Related

- [[landing-brand]] — slash-команда, которая запускает этого агента
- [[landing-design]] — следующий этап (05), потребляет `brand-kit.md` как основной вход
- [[landing-niche]] — поставляет `positioning.md` и `market-profile.md` с описанием ниши и accessibility-tier