---
type: agent
name: moodboard-composer
sources: ["agents/moodboard-composer.md"]
updated: 2026-05-20
triggers: []
stage: "03"
uses: ["references-curator", "style-extractor", "niche-analyst", "landing-orchestrator"]
tags: ["moodboard", "visual-direction", "stage-03", "references"]
---

# moodboard-composer — Составитель мудборда

## Что делает

Берёт утверждённые визуальные референсы и превращает их в два артефакта: текстовое описание визуального направления (`moodboard.md`) и интерактивную HTML-доску с карточками (`moodboard.html`). Фактически «кристаллизует» разрозненные вдохновляющие ссылки в единую визуальную концепцию лендинга.

## Когда вызывать / в каком этапе

Активируется на **этапе 03** (`03_references`), строго после того, как [[references-curator]] завершил работу и хотя бы часть референсов получила статус `approved` в `index.yaml`. До этого агент не запускается — harness-хук физически заблокирует запись в файлы этапа.

Перед началом агент обязан:
1. Прочитать `.landing-state.yaml` и убедиться, что `current_stage == 03_references`.
2. Запустить `scripts/render-pipeline-map.sh` и показать Mermaid-карту.
3. Запустить `scripts/gate-check.sh --stage 03_references` и получить exit 0.

## Что на вход / на выход

**Вход:**
- `03_РЕФЕРЕНСЫ/index.yaml` — список референсов со статусами (`approved`, `candidate`, `rejected`)
- `01a_АНАЛИЗ_НИШИ/niche-analysis.md` — раздел 6 задаёт допустимый визуальный язык
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — разделы 1–3, 5, 6 определяют, какие элементы референсов допустимы; красные флаги из раздела 6 = исключить референс

**Выход:**
- `03_РЕФЕРЕНСЫ/moodboard.md` — текстовый нарратив: палитра, типографика, характер движения, что берём / что отвергаем
- `03_РЕФЕРЕНСЫ/moodboard.html` — визуальная HTML-доска (генерируется через `python3 skills/moodboard-creation/scripts/render.py`)

**HARD GATE:** этап закрывается только после того, как пользователь открыл `moodboard.html` и явно подтвердил направление. После подтверждения агент фиксирует `approved` через `scripts/gate-state.sh`.

## Связанные концепты

- [[references-curator]] — собирает и тегирует референсы до запуска мудборд-агента
- [[style-extractor]] — следующий этап: извлекает палитру, шрифты и иконки из утверждённого мудборда
- [[niche-analyst]] — поставляет `niche-analysis.md` и `visual-requirements.md`, которые определяют, что допустимо включать в мудборд
- [[landing-orchestrator]] — управляет переходом между этапами, enforces gate

## Источник

- `agents/moodboard-composer.md`