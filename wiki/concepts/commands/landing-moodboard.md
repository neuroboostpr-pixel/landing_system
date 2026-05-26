---
slug: landing-moodboard
type: command
name: "Команда /landing-moodboard"
stage: "03"
tags: [moodboard, references, visual, stage-03]
triggers: [landing-moodboard]
inputs: [03_РЕФЕРЕНСЫ/index.yaml]
outputs: [03_РЕФЕРЕНСЫ/moodboard.html]
gates: [user-approval-moodboard]
pre_reqs: [references-collection, landing-onboarding]
related: [moodboard-composer, moodboard-creation, references-curator, style-extractor, brand-architect]
sources: ["commands/landing-moodboard.md"]
updated: 2026-05-26
---

# /landing-moodboard

## Что делает

Команда генерирует (или перегенерирует) визуальный мудборд для текущего лендинг-проекта на этапе 03. Она вызывает агента `moodboard-composer`, который считывает одобренные референсы из `03_РЕФЕРЕНСЫ/index.yaml` и рендерит итоговый HTML-файл `moodboard.html`. После генерации предъявляет путь к превью и ждёт явного подтверждения пользователя — без апрува дальнейшая работа (style extraction → brand-kit) не начинается.

## Когда вызывается

Запускается вручную командой `/landing-moodboard` внутри папки проекта после того, как референсы утверждены через `/landing-references` (поле `status: approved` в `index.yaml`). Предусловия: пройден онбординг (`setup_complete`), и gate-check по этапу `03_references` возвращает exit 0.

## Вход → выход

**Вход:** файл `03_РЕФЕРЕНСЫ/index.yaml` с хотя бы одним референсом в статусе `approved`; корректная установка системы (флаг onboarding).

**Выход:** `03_РЕФЕРЕНСЫ/moodboard.html` — визуальный HTML-мудборд, собранный из одобренных референсов и готовый к просмотру в браузере.

## Чем закрывается этап (gates)

- user-approval-moodboard — пользователь явно подтверждает мудборд перед переходом к style extraction; без этого апрува команда не вызывает следующий этап.

## Failure modes

- Онбординг не пройден (`setup_complete` отсутствует) — команда останавливается с сообщением «Запусти /landing-onboarding».
- Gate-check этапа `03_references` падает — в `index.yaml` нет ни одного референса со статусом `approved`, либо предыдущий этап не завершён.
- `moodboard-composer` не может найти проектную папку — аргумент `<project>` не передан и `landing.project` не настроен.
- Файл `moodboard.html` не обновляется при повторном запуске — агент кэшировал старые данные; решение: обновить статусы в `index.yaml` и перезапустить.
- Пользователь не даёт approve — pipeline зависает; следующий этап (04 brand-kit) недоступен до явного подтверждения.

## Related

- [[moodboard-composer]] — агент, непосредственно рендерящий мудборд
- [[moodboard-creation]] — концепт процесса создания мудборда
- [[references-curator]] — управляет статусами референсов, от которых зависит вход
- [[style-extractor]] — следующий этап после апрува мудборда
- [[brand-architect]] — использует результат мудборда при формировании brand-kit