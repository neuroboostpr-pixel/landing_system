---
slug: moodboard-composer
type: agent
name: "Moodboard Composer"
stage: "03"
tags: [moodboard, references, visual-direction, stage-03]
triggers: [landing-moodboard]
inputs: [03-referensy, 01a-analiz-nishi]
outputs: [03-referensy]
gates: [moodboard_approved]
pre_reqs: [03-referensy, 01a-analiz-nishi]
related: [references-curator, style-extractor, landing-references, moodboard-creation, visual-curator, niche-analysis]
sources: ["agents/moodboard-composer.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Moodboard Composer

## Что делает

Агент синтезирует визуальное направление проекта на основе одобренных референсов. Он читает `03_РЕФЕРЕНСЫ/index.yaml`, собирает теги (split-screen, warm-palette, premium-typography и т.д.) по каждому референсу, затем формирует два артефакта: текстовый нарратив `moodboard.md` (что берём из визуального языка, что отвергаем, характер палитры, типографики, движения) и визуальную HTML-доску `moodboard.html` с карточками референсов. Также учитывает `niche-analysis.md` и `visual-requirements.md` для исключения red-flag решений.

## Когда вызывается

Вызывается на этапе 03 после того как все нужные референсы собраны и имеют статус `approved` в `index.yaml`. Типичный триггер — завершение скилла `/landing-references` и готовность пользователя утвердить визуальное направление перед переходом к brand-kit.

## Вход → выход

**Вход:** `03_РЕФЕРЕНСЫ/index.yaml` со списком одобренных референсов; `01a_АНАЛИЗ_НИШИ/niche-analysis.md` (секция 6 — что брать в следующие этапы); `01a_АНАЛИЗ_НИШИ/visual-requirements.md` (секции 1–3, 5–6 — red-flag-паттерны, которые не сохранять).

**Выход:** `03_РЕФЕРЕНСЫ/moodboard.md` — текстовый нарратив визуального направления; `03_РЕФЕРЕНСЫ/moodboard.html` — визуальная доска с карточками референсов, генерируется через `render.py`. Этап помечается `approved` только после явного согласования пользователем.

## Чем закрывается этап (gates)

- moodboard_approved — пользователь открыл `moodboard.html`, просмотрел визуальную доску и явно подтвердил выбранное направление. Без этого gate `style-extractor` не запускается.

## Failure modes

- Референс с red-flag из `visual-requirements.md` §6 попал в moodboard — агент должен был отфильтровать его ещё при сборке тегов.
- `render.py` не найден или упал с ошибкой — `moodboard.html` не создаётся, этап зависает.
- `index.yaml` не содержит ни одного `approved`-референса — агент запустился преждевременно, до завершения этапа сбора.
- Пользователь не дал явного подтверждения `moodboard.html` — hard gate не закрыт, `style-extractor` заблокирован.
- Предшественник (например `01a-analiz-nishi`) не закрыт — `enforce_stage_gate.py` hook физически блокирует Write-операции.

## Related

- [[references-curator]] — собирает и фильтрует референсы, которые затем обрабатывает этот агент
- [[style-extractor]] — следующий агент в цепочке, берёт на вход результат moodboard
- [[moodboard-creation]] — скилл с `render.py` для генерации HTML-доски
- [[niche-analysis]] — определяет допустимый визуальный язык и red-flag паттерны
- [[visual-curator]] — курирует визуальные решения на последующих этапах
- [[landing-references]] — slash-команда, запускающая сбор референсов (предшественник)