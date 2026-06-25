---
slug: landing-clone
type: command
name: "Клонирование сегмента ЦА"
stage: "13"
tags: [multisite, clone, segment, a-b-test]
triggers: [landing-clone]
inputs: [13-segmenty-tsa]
outputs: [13-segmenty-tsa]
gates: []
pre_reqs: [wp-multisite, landing-segment]
related: [landing-segment, wp-multisite, landing-versioning-and-cloning, 13-segmenty-tsa]
sources: ["commands/landing-clone.md"]
updated: 2026-06-22
confidence: {stage: low}
---

# Клонирование сегмента ЦА

## Что делает

Команда копирует существующий сегмент целевой аудитории в новый сегмент внутри одной WordPress multisite-сети. Используется для создания точной копии поддомена — все страницы переносятся по одной через `wp post get` + `wp post create`, переносятся настройки главной страницы (`show_on_front`, `page_on_front`). Под капотом для создания destination-сегмента вызывается `/landing-segment`, после чего запускается скрипт `skills/wp-multisite/scripts/clone-subsite.sh`.

## Когда вызывается

Пользователь явно вводит `/landing-clone <source-slug> <dest-slug>`. Типичные сценарии: тестирование изменений на копии без риска для основного сегмента, создание варианта сегмента для A/B-сплита. Команда НЕ предназначена для создания нового сегмента с другим брифом и контентом — для этого есть `/landing-segment`.

## Вход → выход

**Вход:** существующий сегмент (`source-slug`) зарегистрирован в `.landing-state.yaml::audience_segments`; WordPress multisite-сеть уже развёрнута.

**Выход:** новый subsite (`dest-slug`) с полной копией страниц source-сегмента; запись о новом сегменте добавлена в `.landing-state.yaml`; настройки главной страницы перенесены.

## Failure modes

- **Source-сегмент не найден в `.landing-state.yaml`** — команда падает на первом шаге проверки, клонирование не запускается.
- **Dest-slug уже занят** — `/landing-segment` под капотом вернёт ошибку конфликта имён.
- **Multisite не инициализирован** — команда не применима к single-site проектам без миграции; нужно сначала выполнить миграцию через `landing-segment`.
- **Частичное клонирование страниц** — если `wp post get` или `wp post create` упали на конкретной странице, остальные могут скопироваться, оставив dest-сегмент неполным.
- **Legacy-вызов без флага** — старая сигнатура `/landing-clone <new-slug>` (filesystem-клон) deprecated; случайное использование создаст ненужный single-site клон вместо multisite-сегмента.

## Related

- [[landing-segment]] — создаёт пустой skeleton нового сегмента; используется внутри команды для инициализации dest
- [[wp-multisite]] — скилл, содержащий `clone-subsite.sh` и все multisite-хелперы
- [[landing-versioning-and-cloning]] — legacy-скилл для filesystem-клонирования single-site проектов (deprecated для multisite)
- [[13-segmenty-tsa]] — этап проекта, в рамках которого живут все сегменты ЦА