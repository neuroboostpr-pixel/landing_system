---
type: stage
name: 07a-wireframe
sources: ["template/07a_WIREFRAME/README.md"]
updated: 2026-05-25
triggers: []
stage: "07a"
uses: ["landing-wireframe", "ux-composer", "landing-compose"]
tags: ["wireframe", "ux", "preview", "блоки"]
---

# 07a Wireframe — интерактивный выбор вариантов блоков

## Что делает
Показывает маркетологу интерактивный HTML-превью лендинга, где для каждого блока предлагается 2–3 варианта композиции. Пользователь выбирает подходящий вариант через radio-кнопки и подтверждает выбор — система сохраняет решение в файл.

## Когда вызывать / в каком этапе
Этап 07a запускается командой `/landing-wireframe` после того, как утверждён прототип (этап 07, `prototype.md`). Входит в цепочку PR-A: prototype → wireframe → compose. Вызывается вручную, не через оркестратор.

## Что на вход / на выход

**Вход:**
- `prototype.md` / `prototype.yaml` — разобранный прототип из этапа 07
- `candidates.yaml` — 2–3 кандидата на блок, генерируется агентом `ux-composer`

**Выход:**
- `wireframe.html` — интерактивный desktop+mobile превью с radio-кнопками для каждого блока
- `selections.yaml` — финальный выбор пользователя (скачивается после нажатия «Confirm selections»)

**Как использовать:**
1. Открыть `wireframe.html` двойным кликом (работает на `file://`)
2. Если iframe-превью не рендерится — запустить:
   ```bash
   bash skills/wireframe-rendering/scripts/serve-preview.sh 07a_WIREFRAME/
   ```
3. Выбрать вариант блока для каждой секции, нажать «Confirm selections»
4. Сохранить скачанный `selections.yaml` обратно в `07a_WIREFRAME/`

## Связанные концепты
- [[landing-wireframe]] — slash-команда, которая запускает этот этап и генерирует `wireframe.html`
- [[ux-composer]] — агент, генерирующий `candidates.yaml` (2–3 варианта на блок)
- [[landing-compose]] — следующий этап (07b): собирает `composed.html` на основе `selections.yaml`
- [[landing-prototype]] — предыдущий этап: разбирает PDF/MD прототип в `prototype.md`

## Источник
- `template/07a_WIREFRAME/README.md`