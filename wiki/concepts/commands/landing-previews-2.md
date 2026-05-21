---
type: command
name: landing-previews
sources: ["commands/landing-previews 2.md"]
updated: 2026-05-19
triggers:
  - "покажи превью лендинга на разных устройствах"
  - "сгенерируй desktop и mobile preview"
  - "хочу проверить как выглядит на телефоне"
  - "открой превью composed.html"
stage: "07b"
uses:
  - "block-composer"
  - "landing-compose"
tags: ["preview", "responsive", "composed", "desktop", "mobile"]
---

# /landing-previews — Превью лендинга на разных устройствах

## Что делает

Генерирует три HTML-файла-обёртки над готовым `composed.html`, чтобы визуально проверить, как лендинг выглядит на desktop, мобильном и планшете — прямо в браузере, без деплоя.

## Когда вызывать / в каком этапе

Вызывается вручную после завершения этапа **07b (Compose)**, то есть когда `07b_COMPOSED/composed.html` уже собран. Обычно запускается сразу после `/landing-compose`, чтобы маркетолог мог визуально оценить макет перед переходом к этапам фото (07c) и визуала (07d).

```
/landing-previews <project>
```

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — финальный составной HTML лендинга (обязателен).

**Выход** (три файла в той же папке):
- `composed-desktop-preview.html` — обёртка с viewport 1280×800.
- `composed-mobile-preview.html` — обёртка с viewport 375×812.
- `composed-previews-index.html` — единый файл с переключателем между всеми устройствами (mobile / tablet / desktop / wide).

Файлы открываются локально в браузере — ничего не деплоится.

## Связанные концепты

- [[block-composer]] — агент, который собирает `composed.html` на этапе 07b; его результат является входом для этой команды.
- [[landing-compose]] — команда, запускающая block-composer; `/landing-previews` логично идёт сразу после неё.
- [[07b-composed]] — этап pipeline, к которому относится эта команда.

## Источник

- `commands/landing-previews 2.md`