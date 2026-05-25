---
type: agent
name: ux-composer
sources: ["agents/ux-composer.md"]
updated: 2026-05-25
triggers: []
stage: "07a"
uses: ["landing-wireframe", "landing-compose", "landing-orchestrator", "prototype-import", "wireframe-rendering", "block-library-management", "ui-ux-pro-max"]
tags: ["wireframe", "ux", "stage-07a", "block-library", "pre-flight"]
---

# UX Composer — Агент сборки интерактивного вайрфрейма

## Что делает
Берёт структуру прототипа и библиотеку блоков, генерирует интерактивный HTML-файл с 2–3 вариантами дизайна на каждую секцию лендинга. Пользователь выбирает понравившиеся варианты, и результат сохраняется для дальнейшей сборки страницы. Никогда не придумывает блоки из головы — работает строго с утверждённой библиотекой.

## Когда вызывать / в каком этапе
Вызывается на **этапе 07a** (UX Wireframe) после того, как утверждён прототип (`07_ПРОТОТИП/prototype.yaml`). Запускается командой `/landing-wireframe` или через `landing-orchestrator`, когда `current_stage == 07b_wireframe` в `.landing-state.yaml`. До закрытия этого этапа (появления `selections.yaml`) этапы 07b и далее недоступны — стоит **HARD GATE**.

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — структура блоков прототипа
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — токены дизайна
- `<project>/04_БРЕНД/brand-kit.md` — бренд-кит проекта
- `block-library/catalog.yaml` — каталог доступных блоков
- CSV-файлы из `ui-ux-pro-max` (UX-паттерны, гайдлайны, стили, палитры, типографика) — **обязательная зависимость**

**Выход:**
- `07a_WIREFRAME/wireframe.html` — интерактивный вайрфрейм с radio-кнопками для выбора вариантов
- `07a_WIREFRAME/candidates.yaml` — кандидаты из библиотеки на каждый блок прототипа
- `07a_WIREFRAME/selections.yaml` — скачивается пользователем после выбора вариантов (вручную кладётся в папку)

**Если блок не найден:** агент возвращает `needs_new_block: true` с пояснением, пользователь добавляет новый блок через `scaffold-block.py`.

## Связанные концепты
- [[landing-wireframe]] — slash-команда, запускающая этого агента
- [[landing-compose]] — следующий этап (07b), потребляет `selections.yaml`
- [[landing-orchestrator]] — диспатчит агента в общем pipeline
- [[prototype-import]] — скилл импорта и валидации прототипа (предшественник)
- [[wireframe-rendering]] — скилл рендера `wireframe.html` через `render-wireframe.py`
- [[block-library-management]] — скилл добавления новых блоков если candidates пустые
- [[ui-ux-pro-max]] — внешний плагин с CSV UX-данными; без него агент не запустится

## Источник
- `agents/ux-composer.md`