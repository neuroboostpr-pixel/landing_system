---
type: stage
name: 07a-wireframe
sources: ["template/07a_WIREFRAME/README.md"]
updated: 2026-05-26
triggers: []
stage: "07a"
uses: ["landing-wireframe", "ux-composer", "landing-compose"]
tags: ["wireframe", "preview", "ux", "prototype"]
---

# 07a Wireframe — интерактивный выбор композиций блоков

## Что делает
Показывает маркетологу интерактивный HTML-превью лендинга, где для каждого блока предложены 2–3 варианта компоновки. Пользователь выбирает лучший вариант и сохраняет итоговый выбор.

## Когда вызывать / в каком этапе
Этап 07a запускается командой `/landing-wireframe` после того, как прототип обработан (`/landing-prototype`). В автоматическом workflow — оркестратор вызывает этот этап после parse прототипа (07a prototype parse). Вручную: когда нужно утвердить визуальную структуру страницы перед сборкой `composed.html`.

## Что на вход / на выход

**Вход:**
- `prototype.md` / `prototype.yaml` — распаршенный прототип из папки `07_ПРОТОТИП/`
- Блок-библиотека с кандидатами вариантов (генерирует `ux-composer`)

**Выход:**
- `wireframe.html` — интерактивный превью с radio-кнопками (desktop + mobile), работает на `file://`
- `candidates.yaml` — 2–3 кандидата на каждый блок страницы
- `selections.yaml` — финальный выбор пользователя (скачивается после нажатия «Confirm selections»)

**Дальнейшее использование:** `selections.yaml` кладётся в папку `07a_WIREFRAME/` и передаётся на вход `/landing-compose` (этап 07b).

## Как пользоваться превью
1. Открыть `wireframe.html` двойным кликом — radio-кнопки работают без сервера.
2. Если iframe-превью не рендерится, запустить хелпер:
   ```bash
   bash skills/wireframe-rendering/scripts/serve-preview.sh 07a_WIREFRAME/
   ```
3. Выбрать вариант для каждого блока.
4. Нажать «Confirm selections» внизу страницы — скачается `selections.yaml`.
5. Положить файл в `07a_WIREFRAME/` и запустить `/landing-compose`.

## Связанные концепты
- [[landing-wireframe]] — slash-команда, запускающая генерацию wireframe.html
- [[ux-composer]] — агент, создающий `candidates.yaml` с вариантами блоков
- [[landing-compose]] — следующий этап (07b), потребляет `selections.yaml`
- [[landing-prototype]] — предшествующий этап, готовит prototype.md как входные данные

## Источник
- `template/07a_WIREFRAME/README.md`