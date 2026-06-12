---
slug: moodboard-composer
type: agent
name: "Moodboard Composer"
stage: "03"
tags: [moodboard, references, visual-direction, stage-03]
triggers: [landing-references]
inputs:
  - 03_РЕФЕРЕНСЫ/index.yaml
  - 01a_АНАЛИЗ_НИШИ/niche-analysis.md
  - 01a_АНАЛИЗ_НИШИ/visual-requirements.md
outputs:
  - 03_РЕФЕРЕНСЫ/moodboard.md
  - 03_РЕФЕРЕНСЫ/moodboard.html
gates: [moodboard-approved]
pre_reqs: [landing-references, landing-niche]
related: [landing-brand, landing-design, landing-moodboard]
sources: ["agents/moodboard-composer.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# Moodboard Composer

## Что делает

Агент синтезирует визуальный мудборд из одобренных референсов этапа 03. На выходе — два файла: `moodboard.md` с текстовым нарративом о выбранном визуальном направлении (палитра, типографика, моушен, что берём и что отвергаем) и `moodboard.html` — визуальная доска с карточками референсов. Агент опирается на анализ ниши и визуальные требования, сформулированные на этапе 01a, чтобы мудборд соответствовал целевому рынку.

## Когда вызывается

Запускается после того, как пользователь утвердил набор референсов (статус `approved` в `index.yaml`) на этапе 03. Вызывается через команду `/landing-references` или оркестратором после закрытия этапа 03. Обязательное предусловие — `current_stage == 03_references` в `.landing-state.yaml`.

## Вход → выход

**Вход:** одобренные референсы в `03_РЕФЕРЕНСЫ/index.yaml`; секция 6 «Что брать с собой» из `niche-analysis.md`; разделы 1–3, 5–6 `visual-requirements.md` (включая red flags — референсы из них не сохраняются).

**Выход:** `moodboard.md` — текстовый нарратив визуального направления; `moodboard.html` — визуальная доска, сгенерированная через `skills/moodboard-creation/scripts/render.py`. После HARD GATE (пользователь открывает `.html` и подтверждает) — этап переходит к `style-extractor`.

## Чем закрывается этап (gates)

- moodboard-approved — пользователь открывает `moodboard.html` и явно подтверждает визуальное направление. Без подтверждения следующий этап (04 бренд) не открывается.

## Failure modes

- `current_stage` не соответствует `03_references` — агент останавливается, не пишет файлы.
- `gate-check.sh` возвращает ненулевой код — нерешённые предшественники блокируют выполнение (harness `PreToolUse` hook физически запрещает Write/Edit).
- Референс из red flag (`visual-requirements.md` секция 6) попал в `index.yaml` со статусом `approved` — такой референс не должен включаться в мудборд, но агент может пропустить проверку при неполном чтении.
- `render.py` падает из-за отсутствующих изображений в папке референсов — HTML не генерируется, этап не закрывается.
- Пользователь одобряет мудборд устно, не через `gate-state.sh approve` — состояние `.landing-state.yaml` не обновляется, оркестратор считает этап незакрытым.

## Related

- [[landing-references]] — предшествующий этап: собирает и утверждает референсы, результат которых читает этот агент
- [[landing-brand]] — следующий этап (04): принимает нарратив мудборда как основу для бренд-кита
- [[landing-moodboard]] — slash-команда, предположительно вызывающая этого агента напрямую
- [[landing-design]] — этап 05: использует утверждённый визуальный язык из мудборда для дизайн-системы