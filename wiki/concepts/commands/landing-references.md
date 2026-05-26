---
slug: landing-references
type: command
name: "Сбор визуальных референсов"
stage: "03"
tags: [references, moodboard, visual, stage-03, curation]
triggers: [landing-references]
inputs: [03_РЕФЕРЕНСЫ/, landing.project]
outputs: [03_РЕФЕРЕНСЫ/index.yaml, 03_РЕФЕРЕНСЫ/moodboard.html]
gates: [stage-03-approved]
pre_reqs: [landing-onboarding, system-setup]
related: [references-curator, moodboard-composer, landing-brand, landing-moodboard, references-collection, moodboard-creation]
sources: ["commands/landing-references.md"]
updated: 2026-05-26
---

# /landing-references — Сбор визуальных референсов

## Что делает

Команда запускает пайплайн сбора и отбора визуальных референсов для лендинга на этапе 03. Агент `references-curator` собирает ссылки и файлы, тегирует их и сохраняет в реестр `index.yaml` со статусами `candidate`, `approved` или `rejected`. После того как пользователь одобряет нужные референсы, агент `moodboard-composer` рендерит интерактивный HTML-мудборд для финального визуального подтверждения. Без явного approve мудборда переход на этап 04 (бренд-кит) заблокирован.

## Когда вызывается

Вызывается вручную командой `/landing-references` из папки проекта после успешного завершения этапа 01. Предварительно проверяется onboarding-флаг (`setup_complete`) и gate-check этапа 03 — если предыдущие этапы не пройдены, команда останавливается с пояснением.

## Вход → выход

**Вход:** папка проекта с заполненными материалами после этапа 01; URLs или файлы референсов, которые предоставляет пользователь в ходе диалога с агентом.

**Выход:** `03_РЕФЕРЕНСЫ/index.yaml` — реестр референсов с тегами и статусами; `03_РЕФЕРЕНСЫ/moodboard.html` — визуальный мудборд для просмотра и одобрения.

## Чем закрывается этап (gates)

- `stage-03-approved` — пользователь явно одобряет `moodboard.html` перед переходом к этапу 04; gate фиксируется скриптом `gate-check.sh --approve`.

## Failure modes

- Onboarding не пройден — команда останавливается, требует `/landing-onboarding`.
- Gate предыдущего этапа не пройден — команда сообщает какой этап пропущен и прекращает работу.
- Пользователь не предоставил референсы — `index.yaml` остаётся пустым или заполнен только candidates без approved.
- `moodboard-composer` не смог отрендерить `moodboard.html` из-за недоступных URL-ссылок (битые ссылки или нет сети).
- Пользователь пропустил явное одобрение — HARD GATE блокирует запуск этапа 04 до подтверждения.

## Related

- [[references-curator]] — агент, который непосредственно собирает и тегирует референсы
- [[moodboard-composer]] — агент-рендерер итогового мудборда в HTML
- [[references-collection]] — концепт-процесс сбора референсов
- [[moodboard-creation]] — концепт-процесс создания мудборда
- [[landing-brand]] — следующий этап (04): бренд-кит, открывается после approve этапа 03
- [[landing-moodboard]] — родственная команда для работы с мудбордом