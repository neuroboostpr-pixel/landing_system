---
type: agent
name: photo-curator
sources: ["agents/photo-curator.md"]
updated: 2026-05-15
triggers: ["/landing-photos", "обработать фотки клиента", "фото-пайплайн", "загрузить фотографии на лендинг"]
stage: "07c"
uses: ["photo-classifier", "photo-matcher", "photo-preview-board", "block-composition", "landing-orchestrator"]
tags: ["photo", "PR-B", "stage-07c", "identity-safe"]
---

# photo-curator — оркестратор фото-пайплайна (этап 07c)

## Что делает
Управляет полным процессом работы с клиентскими фотографиями: принимает фотки из папки `inbox/`, классифицирует их через AI, подбирает лучшие фото к каждому блоку лендинга, показывает галерею на подтверждение и в конце обновляет `composed.html` — заменяя заглушки на реальные изображения.

## Когда вызывать / в каком этапе
Вызывается командой `/landing-photos` на **этапе 07c**. Запуск возможен только после того, как утверждены:
- этап `05_design` (дизайн-система) — статус `approved` в `.landing-state.yaml`
- этап `07a_wireframe` (выбраны варианты блоков, существует `selections.yaml`)

Если хотя бы одно условие не выполнено — агент выходит с ошибкой на русском языке.

## Что на вход / на выход

**На вход:**
- Фотографии клиента в `<project>/07c_PHOTOS/inbox/` (7 подпапок по типу: портреты, процесс, объекты, интерьер, до/после, документы, свалка)
- Обратная совместимость: также сканирует `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/`
- `07_ПРОТОТИП/prototype.yaml` — список слотов для фото
- `07a_WIREFRAME/selections.yaml` — выбранные варианты блоков

**На выход:**
- `07c_PHOTOS/catalog.yaml` — каталог классифицированных фото
- `07c_PHOTOS/selections.draft.yaml` — черновик подбора фото к слотам
- `07c_PHOTOS/photo-board.html` — интерактивная галерея для ручной расстановки
- `07c_PHOTOS/selections.yaml` — утверждённый подбор (загружает пользователь)
- `07c_PHOTOS/photo-preview.html` — предпросмотр фото в макете
- `07c_PHOTOS/STATE.yaml` — трекинг прогресса (intake → classify → match → approval → process)
- Обновлённый `07b_COMPOSED/composed.html` с реальными фото вместо заглушек

## Алгоритм работы
Агент проходит 12 шагов: подготовка папок → импорт → классификация (батчами по 5 через `photo-classifier`) → матчинг (`photo-matcher`) → рендер галереи → **HARD GATE** (пользователь расставляет фото) → валидация → обработка (`photo-preview-board`) → **HARD GATE** (пользователь проверяет превью) → перерендер `composed.html`. При перезапуске читает `STATE.yaml` и продолжает с первого незавершённого шага.

**Identity-safe:** клиентские фото никогда не перерисовываются AI. AI-генерация лиц для слотов testimonial/team требует явной галочки `ai_approved_by_user`.

## Связанные концепты
- [[photo-classifier]] — классифицирует каждое фото через codex CLI (теги, тип, контент)
- [[photo-matcher]] — подбирает лучшие фото к каждому слоту wireframe
- [[photo-preview-board]] — обрабатывает фото (кроп/ресайз) и рендерит `photo-preview.html`
- [[block-composition]] — скрипт `compose-blocks.py`, который перерендерит `composed.html` с реальными фото
- [[landing-orchestrator]] — вызывает photo-curator как часть stage 07c в общем workflow

## Источник
- `agents/photo-curator.md`