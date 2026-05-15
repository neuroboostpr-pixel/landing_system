---
type: stage
name: 07a-wireframe
sources: ["template/07a_WIREFRAME/README.md"]
updated: 2026-05-15
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition", "landing-wireframe"]
tags: ["wireframe", "preview", "блоки", "кандидаты", "выбор-пользователя"]
---

# 07a Wireframe — Интерактивный выбор блоков

## Что делает
На этом этапе система показывает маркетологу интерактивный HTML-превью будущего лендинга: для каждого блока страницы предлагается 2–3 варианта компоновки, между которыми можно переключаться прямо в браузере. После выбора лучших вариантов пользователь фиксирует решение — и система идёт дальше.

## Когда вызывать / в каком этапе
Этап 07a запускается командой `/landing-wireframe` после того, как импортирован прототип (этап 07, артефакт `prototype.yaml`). Агент [[ux-composer]] генерирует `wireframe.html` и `candidates.yaml`. Без подтверждения `selections.yaml` переход к этапу 07b (Compose) невозможен.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/prototype.yaml` — машиночитаемая структура прототипа (выход этапа 07)
- Библиотека блоков `block-library/` — источник кандидатов

**Выход:**
- `07a_WIREFRAME/wireframe.html` — интерактивный превью (desktop + mobile, radio-кнопки на `file://`)
- `07a_WIREFRAME/candidates.yaml` — 2–3 варианта-кандидата на каждый блок
- `07a_WIREFRAME/selections.yaml` — финальный выбор пользователя (скачивается по кнопке «Confirm selections»)

**Как открыть превью:** двойной клик по `wireframe.html`. Если iframe не рендерится — запустить вспомогательный скрипт:
```
bash skills/wireframe-rendering/scripts/serve-preview.sh 07a_WIREFRAME/
```

## Связанные концепты
- [[ux-composer]] — агент, который генерирует `wireframe.html` и `candidates.yaml` из `prototype.yaml`
- [[wireframe-rendering]] — скилл, реализующий логику рендера интерактивного wireframe
- [[prototype-importer]] — предшествующий агент, формирующий `prototype.yaml` на вход
- [[block-composition]] — следующий этап (07b), использует `selections.yaml` для сборки `composed.html`
- [[landing-wireframe]] — slash-команда, запускающая этот этап
- [[block-library-management]] — управляет библиотекой блоков-кандидатов

## Источник
- `template/07a_WIREFRAME/README.md`