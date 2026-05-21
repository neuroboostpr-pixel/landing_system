---
type: agent
name: photo-preview-board
sources: ["agents/photo-preview-board.md"]
updated: 2026-05-20
triggers: []
stage: "07c"
uses: ["photo-curator", "photo-stylist", "selections-validator", "identity-safe"]
tags: ["photos", "preview", "processing", "identity-safe"]
---

# photo-preview-board — рендер превью фотографий

## Что делает

Берёт утверждённый пользователем файл `selections.yaml` и обрабатывает каждый фото-слот: кадрирует клиентские снимки, генерирует изображения через codex или ставит SVG-заглушку. После обработки рендерит `photo-preview.html` для финального визуального контроля.

## Когда вызывать / в каком этапе

Агент работает на этапе **07c (Photos)** и вызывается **только через `photo-curator`** — прямой вызов не предусмотрен. `photo-curator` диспатчит его после того, как пользователь утвердил расстановку фото в `photo-board.html` и положил `selections.yaml` в `07c_PHOTOS/`.

## Что на вход / на выход

**Вход:**
- `<project>/07c_PHOTOS/selections.yaml` — канонический файл с выбором пользователя (стратегия per-слот: `bring-your-own`, `generate` или `placeholder`)

**Выход:**
- `<project>/07c_PHOTOS/processed/<slot_id>/desktop.jpg` — обрезанный/ресайзнутый снимок под десктоп
- `<project>/07c_PHOTOS/processed/<slot_id>/mobile.jpg` — мобильная версия (если у блока задан `mobile_ratio`)
- `<project>/07c_PHOTOS/photo-preview.html` — HTML-превью для финального approve

**Логика стратегий:**
- `bring-your-own` — берёт клиентское фото из `intake/`, обрезает под нужный ratio через `style.py`
- `generate` — генерирует через `codex-generate-fallback.sh`; но если слот identity-safe (`testimonial`, `expert`, `team-member`, `avatar`) и `ai_approved_by_user == false` — автоматически деградирует до `placeholder` без уведомления
- `placeholder` — рисует SVG-заглушку с брендовым цветом и хинтом слота

**Identity-safe gate** — ключевое правило: AI-генерация людей (лица, команда, отзывы) запрещена без явного разрешения пользователя. Это единственная точка принудительного применения правила в pipeline.

## Связанные концепты

- [[photo-curator]] — родительский агент-оркестратор, единственный кто вызывает photo-preview-board
- [[photo-stylist]] — используется для обрезки/ресайза клиентских фото (`style.py`)
- [[photo-matcher]] — формирует черновик `selections.yaml`, который пользователь затем утверждает
- [[photo-classifier]] — классифицирует фото на этапе intake до того, как попасть в selections

## Источник

- `agents/photo-preview-board.md`