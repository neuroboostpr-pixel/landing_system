---
slug: landing-previews
type: command
name: "/landing-previews — Превью на устройствах"
stage: "07b"
tags: [preview, composed, responsive, ux]
triggers: ["/landing-previews"]
inputs: ["07b_COMPOSED/composed.html"]
outputs:
  - "07b_COMPOSED/composed-desktop-preview.html"
  - "07b_COMPOSED/composed-mobile-preview.html"
  - "07b_COMPOSED/composed-previews-index.html"
gates: []
pre_reqs: [block-composition]
related: [block-composer, ux-composer, wireframe-rendering]
sources: ["commands/landing-previews.md"]
updated: 2026-05-26
confidence: {stage: low, pre_reqs: low}
---

# /landing-previews — Превью на устройствах

## Что делает

После того как `composed.html` готов, команда генерирует три HTML-обёртки для просмотра лендинга в разных разрешениях: десктоп (1280×800), мобильный (375×812) и сводный индекс с переключателем между устройствами. Все три файла появляются в папке `07b_COMPOSED/` текущего проекта. Задача команды — визуальная проверка макета без деплоя, прямо из браузера.

## Когда вызывается

Вызывается вручную после завершения этапа 07b (Compose) — как только `composed.html` существует и одобрен. Запускается командой `/landing-previews <project>`, где `<project>` — slug проекта.

## Вход → выход

**Вход:** `07b_COMPOSED/composed.html` — скомпонованный HTML-макет лендинга с design-токенами и контентом.

**Выход:**
- `composed-desktop-preview.html` — обёртка с viewport 1280×800.
- `composed-mobile-preview.html` — обёртка с viewport 375×812.
- `composed-previews-index.html` — единая страница с переключателем устройств (mobile / tablet / desktop / wide).

## Failure modes

- `composed.html` ещё не сгенерирован или отсутствует в `07b_COMPOSED/` — команда не найдёт входной файл и завершится с ошибкой.
- Slug проекта указан неверно или не совпадает с директорией — файлы могут быть записаны не в ту папку или команда не найдёт проект.
- Превью открывается в браузере с file://-протоколом, и относительные пути к ассетам (fonts, images) не резолвятся — визуал может сломаться.
- Если `composed.html` обновился после генерации превью, обёртки устаревают — нужно перезапустить команду.

## Related

- [[block-composition]] — этап 07b, на выходе которого появляется `composed.html`, обязательный вход для этой команды
- [[block-composer]] — агент, создающий `composed.html`
- [[ux-composer]] — связан с визуальной проверкой и компоновкой блоков
- [[wireframe-rendering]] — предыдущий этап визуального pipeline (07a), после которого идёт compose → previews