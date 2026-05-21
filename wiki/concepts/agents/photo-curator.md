---
type: agent
name: photo-curator
sources: ["agents/photo-curator.md"]
updated: 2026-05-20
triggers: ["обработать фотографии клиента", "расставить фото по слотам", "запустить фото-пайплайн", "/landing-photos"]
stage: "07c"
uses: ["photo-classifier", "photo-matcher", "photo-preview-board", "block-composition", "landing-photos", "ux-composer", "design-system-generator"]
tags: ["photos", "pipeline", "stage-07c", "identity-safe", "orchestrator"]
---

# photo-curator — Оркестратор фото-пайплайна (этап 07c)

## Что делает
Принимает клиентские фотографии, автоматически классифицирует их через AI, подбирает к слотам wireframe-а, показывает галерею для ручной расстановки, обрабатывает утверждённые фото через codex и встраивает их в `composed.html` вместо placeholder-ов.

## Когда вызывать / в каком этапе
Вызывается командой `/landing-photos` на этапе **07c**. Запускается вручную после того, как утверждены этапы **05 (design-system)** и **07a (wireframe)**. Требует наличия фотографий в `07c_PHOTOS/inbox/`.

## Что на вход / на выход

**Вход:**
- Фотографии клиента в `07c_PHOTOS/inbox/` (7 подпапок по типу: портреты, процесс, объекты и т.д.)
- Опционально: фото из `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` (обратная совместимость)
- `07_ПРОТОТИП/prototype.yaml` — список слотов
- `07a_WIREFRAME/selections.yaml` — выбранные блоки
- `tokens.json` и `market-profile.md` — параметры бренда и ниши для codex-обработки

**Выход:**
- `07c_PHOTOS/catalog.yaml` — каталог всех фото с тегами
- `07c_PHOTOS/selections.draft.yaml` — авто-подбор фото к слотам
- `07c_PHOTOS/photo-board.html` — интерактивная галерея для ручного drag-drop расстановки
- `07c_PHOTOS/photo-preview.html` — превью как фото лягут в макет
- `07c_PHOTOS/processed/<slot>.jpg` — обработанные фото (desktop + mobile)
- Обновлённый `07b_COMPOSED/composed.html` с реальными фото вместо placeholder-ов
- `07c_PHOTOS/STATE.yaml` — статус всех подэтапов

**Два HARD GATE:**
1. После рендера `photo-board.html` — ждёт, пока пользователь расставит фото и положит `selections.yaml`
2. После рендера `photo-preview.html` — ждёт явного approve перед финальным перерендером

## Identity-safe правила
Клиентские фото **никогда не репеинтятся** через AI. Codex-постобработка меняет только фон/стиль окружения, но не объект (лицо, автомобиль, товар). AI-генерация лиц в слотах testimonial/expert/team требует явного флага `ai_approved_by_user`. Нарушение ловит `verify-photo-pipeline.sh` на HARD GATE.

## Связанные концепты
- [[photo-classifier]] — диспатчится пакетами по 5 фото, классифицирует через codex CLI `--image`
- [[photo-matcher]] — подбирает лучшие фото к каждому слоту, пишет `selections.draft.yaml`
- [[photo-preview-board]] — обрабатывает утверждённые фото, рендерит `photo-preview.html`
- [[block-composition]] — используется для финального перерендера `composed.html` с реальными фото
- [[landing-photos]] — slash-команда, которая запускает этот агент
- [[ux-composer]] — формирует wireframe и `selections.yaml`, которые photo-curator читает как prerequisite
- [[design-system-generator]] — его выход (`tokens.json`) нужен для codex-постобработки фото

## Источник
- `agents/photo-curator.md`