---
slug: block-library-management
type: catalog
name: "Библиотека wireframe-блоков"
tags: [block-library, wireframe, catalog, scaffolding]
triggers: [landing-wireframe, landing-compose, landing-import-blocks]
inputs: []
outputs: [block-library/catalog.yaml]
related: [landing-wireframe, landing-compose, landing-import-blocks, block-composition, block-composer, wp-gutenberg-block-builder]
sources: ["block-library/README.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# Библиотека wireframe-блоков

## Что делает

Хранит общую коллекцию переиспользуемых wireframe-блоков для всех проектов landing-system. Каждый блок — самодостаточная единица: HTML-шаблон (desktop + mobile), `meta.yaml` со схемой и `SKILL.md` с инструкцией по применению. Библиотека охватывает 9 категорий (hero, features, social-proof, process, pricing, trust, cta, faq, quiz) и индексируется через `catalog.yaml`. Блоки разрабатываются один раз и применяются повторно на этапе wireframe и compose.

## Когда вызывается

Обращение к библиотеке происходит во время этапов 07a (wireframe) и 07b (compose), когда `block-composer` или `landing-wireframe` подбирают варианты блоков для прототипа. Новые блоки добавляются вручную через скаффолдер — после решения команды, что для ниши нужен новый паттерн.

## Вход → выход

**Вход:** slug нового блока (через скаффолдер) или поиск по категории/нише при сборке wireframe.

**Выход:** папка блока со структурой `template.html`, `template-mobile.html`, `SKILL.md`, `meta.yaml`; обновлённый `catalog.yaml`.

## Failure modes

- Нарушение naming convention — блок не находится валидатором, `catalog.yaml` расходится с реальными папками.
- Редактирование существующего блока вместо создания `-v2` — нарушает иммутабельность и ломает проекты, которые уже используют оригинальный блок.
- Невалидный `meta.yaml` — `validate-meta.py` вернёт ошибку, блок не попадёт в wireframe.
- Скаффолдер не обновил `catalog.yaml` — блок создан, но недоступен для поиска.
- Отсутствие `template-mobile.html` — compose генерирует только desktop-вариант, мобильная вёрстка ломается.

## Related

- [[landing-wireframe]] — использует библиотеку для предложения 2–3 вариантов блоков на выбор
- [[landing-compose]] — берёт выбранные блоки и собирает `composed.html`
- [[landing-import-blocks]] — команда ручного импорта блоков в проект
- [[block-composition]] — процесс сборки страницы из блоков библиотеки
- [[block-composer]] — агент, подбирающий блоки под структуру прототипа
- [[wp-gutenberg-block-builder]] — финальная кодогенерация блоков для WordPress на этапе 08