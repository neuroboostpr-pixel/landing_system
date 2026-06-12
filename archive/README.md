# Архив блочного трека

Сюда перенесено наследие «блочного» способа производства лендингов
(подбор готовых блоков из библиотеки + wireframe-выбор вариантов).

**Почему:** система переведена на reference-driven флоу — агент рисует макет
сам по прототипу и референсу клиента. Канон:
`docs/superpowers/specs/2026-06-12-reference-driven-flow-spec.md`, раздел 6.

**Что здесь лежит:**
- `block-library/` — ~178 готовых блоков, каталог, таксономия, галерея
- `skills/` — wireframe-rendering, landing-import-blocks, block-library-management
- `commands/` — /landing-wireframe, /landing-import-blocks
- `agents/` — ux-composer
- `scripts/` — генераторы каталога/галереи, нормализаторы блоков
- `tests/` — тесты блочного трека
- `template/` — папка 07a_WIREFRAME из шаблона проекта

**НЕ здесь (переиспользуется новым флоу, лежит на старых местах):**
`block-library/_styles/`, `_shapes/`, `_patterns/`, `_assets/`,
slot-формат `{{slot:name}}`, Lazy Blocks, плагин lp-preview-panel, фото-пайплайн.

Код в архиве не поддерживается и не запускается. Не импортировать из live-кода —
это проверяет `tests/archive/test_no_block_track_refs.py`.
