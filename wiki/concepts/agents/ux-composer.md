---
type: agent
name: ux-composer
sources: ["agents/ux-composer.md"]
updated: 2026-05-20
triggers: []
stage: "07a"
uses: ["prototype-importer", "block-composer", "block-library-management", "landing-wireframe", "ui-ux-pro-max", "design-system-generator", "brand-architect"]
tags: ["wireframe", "stage-07a", "ux", "block-library"]
---

# UX Composer — интерактивный wireframe

## Что делает

Собирает `wireframe.html` с 2–3 вариантами вёрстки на каждый блок прототипа. Пользователь выбирает понравившийся вариант прямо в браузере, нажимает «Confirm» — и скачивается `selections.yaml`, который передаётся дальше в этап compose.

**Главное правило:** агент никогда не придумывает новые блоки — берёт только из `block-library/catalog.yaml`. Если подходящего блока нет — говорит об этом явно.

## Когда вызывать / в каком этапе

Этап **07a (UX Wireframe)**. Вызывается командой `/landing-wireframe` после того, как:
- Этап 07 завершён: `prototype.yaml` существует и валиден.
- Этап 05 завершён: `tokens.json` и `brand-kit.md` готовы.
- `.landing-state.yaml` фиксирует `current_stage == 07b_wireframe` (старый индекс — 07a/07b в этом агенте совмещены).

Перед любым действием агент проверяет `.landing-state.yaml`, строит Mermaid-карту pipeline и вызывает `gate-check.sh`.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/prototype.yaml` — структура блоков прототипа
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены
- `04_БРЕНД/brand-kit.md` — бренд-кит
- `block-library/catalog.yaml` — библиотека доступных блоков
- CSV-файлы из `ui-ux-pro-max` (UX-паттерны, правила, палитры, типографика, стили)
- Референсные DESIGN.md из `vendor/opendesign-extracts/`

**Выход:**
- `07a_WIREFRAME/candidates.yaml` — кандидаты блоков по слотам прототипа
- `07a_WIREFRAME/wireframe.html` — интерактивный HTML для выбора вариантов
- Ожидает от пользователя: `07a_WIREFRAME/selections.yaml` (скачивается из браузера)

**HARD GATE:** без `selections.yaml` этап 07b (compose) недоступен.

## Что происходит при отсутствии нужного блока

Агент возвращает `needs_new_block: true` с пояснением. Пользователь может добавить блок командой:
```bash
python3 skills/block-library-management/scripts/scaffold-block.py --id <new-id> --category <type>
```

## Связанные концепты

- [[prototype-importer]] — генерирует `prototype.yaml`, без которого wireframe невозможен
- [[block-composer]] — следующий этап: принимает `selections.yaml` и рендерит `composed.html`
- [[block-library-management]] — используется для добавления новых блоков, если кандидатов нет
- [[landing-wireframe]] — slash-команда, запускающая этот агент
- [[ui-ux-pro-max]] — обязательная зависимость: данные UX-паттернов, палитр и типографики
- [[design-system-generator]] — поставляет `tokens.json` на этапе 05
- [[brand-architect]] — поставляет `brand-kit.md` на этапе 04

## Источник

- `agents/ux-composer.md`