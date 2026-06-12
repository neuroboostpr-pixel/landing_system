# Block Library

Общая библиотека wireframe-блоков для всех проектов landing-system.

## Структура одного блока

```
hero/ru-hero-01-services-calc/
  SKILL.md              ← когда применять, slots, conversion-notes
  assets/
    template.html       ← desktop wireframe (ч/б), CSS внутри <style>
    template-mobile.html
  meta.yaml             ← schema: см. skills/block-library-management/scripts/validate-meta.py
```

## Категории

- `hero/`, `features/`, `social-proof/`, `process/`, `pricing/`, `trust/`, `cta/`, `faq/`, `quiz/`

## Naming convention

`<market>-<category>-<NN>-<descriptor>` в kebab-case. Примеры:
- `ru-hero-01-services-calc`
- `ru-quiz-01-step-card`

**Иммутабельность:** существующие блоки НЕ редактируются. Изменение = новый id с суффиксом `-v2`, например `ru-hero-01-services-calc-v2`.

## Добавить новый блок

```bash
python skills/block-library-management/scripts/scaffold-block.py \
    --id ru-hero-04-something --category hero
```

Скаффолдер создаст папку, копирует `vendor/opendesign-extracts/skill-block-template/`, обновит `catalog.yaml`.

## Валидация

```bash
python skills/block-library-management/scripts/validate-catalog.py block-library/catalog.yaml
python skills/block-library-management/scripts/validate-meta.py block-library/hero/ru-hero-01-services-calc/meta.yaml
```

## Атрибуция

Формат блоков заимствован у OpenDesign (Apache-2.0). См. `THIRD_PARTY_NOTICES.md`.
