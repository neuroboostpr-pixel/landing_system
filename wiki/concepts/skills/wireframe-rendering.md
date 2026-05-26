---
slug: wireframe-rendering
type: skill
name: "Рендеринг интерактивного Wireframe (07a)"
stage: "07a"
tags: [wireframe, block-library, prototype, css-only, ux]
triggers: [landing-wireframe]
inputs:
  - 07_ПРОТОТИП/prototype.yaml
  - block-library/catalog.yaml
  - block-library/<category>/<block-id>/assets/template.html
outputs:
  - 07a_WIREFRAME/wireframe.html
  - 07a_WIREFRAME/candidates.yaml
gates: []
pre_reqs:
  - prototype-importer
  - block-library-management
related:
  - ux-composer
  - block-composer
  - block-library-management
  - prototype-importer
  - design-system-generator
sources:
  - skills/wireframe-rendering/SKILL.md
updated: 2026-05-26
confidence: {gates: low}
---

# Рендеринг интерактивного Wireframe (07a)

## Что делает

Скилл генерирует `wireframe.html` — интерактивный браузерный preview, в котором каждый блок прототипа отображается в 2–3 вариантах компоновки, подобранных из `block-library/`. Переключение между вариантами реализовано на чистом CSS (`:checked` selector) — без JavaScript-фреймворков и шага сборки. Вдобавок записывает `candidates.yaml` со списком выбранных кандидатов для downstream-скиллов.

## Когда вызывается

Вызывается вручную командой `/landing-wireframe` после того, как `prototype.yaml` подготовлен скиллом `prototype-importer`. Также может быть вызван агентом `ux-composer` в рамках пайплайна оркестратора (PR-D).

## Вход → выход

**Вход:** `07_ПРОТОТИП/prototype.yaml` (список блоков прототипа), `block-library/catalog.yaml` (каталог всех блоков), HTML-шаблоны блоков (`template.html` и `template-mobile.html`) из `block-library/`.

**Выход:** `07a_WIREFRAME/wireframe.html` — готовый интерактивный файл с radio-кнопками для выбора варианта каждого блока; `07a_WIREFRAME/candidates.yaml` — список отобранных кандидатов с метаданными, который затем используется `/landing-compose`.

## Failure modes

- `prototype.yaml` отсутствует или не прошёл валидацию — `match-candidates.py` падает с ошибкой отсутствия входных данных.
- В `block-library/catalog.yaml` нет подходящего блока для какого-то типа секции — кандидат не найден, блок пропускается без предупреждения.
- `template.html` или `template-mobile.html` отсутствует у конкретного блока — рендерер генерирует заглушку вместо реального превью.
- При открытии `wireframe.html` через `file://` iframe sandbox может блокировать ресурсы — нужно запустить `scripts/serve-preview.sh`.
- `selections.yaml`, скачанный пользователем после подтверждения вариантов, не положен обратно в `07a_WIREFRAME/` — следующий скилл `block-composer` не найдёт выбор.

## Related

- [[prototype-importer]] — подготавливает `prototype.yaml`, который является обязательным входом
- [[ux-composer]] — агент, способный вызывать этот скилл в рамках оркестратора
- [[block-composer]] — потребляет `candidates.yaml` и `selections.yaml` на этапе 07b
- [[block-library-management]] — поддерживает каталог и шаблоны блоков
- [[design-system-generator]] — поставляет дизайн-токены, используемые в итоговом compose