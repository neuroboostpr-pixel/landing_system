---
type: command
name: landing-previews
sources: ["commands/landing-previews.md"]
updated: 2026-05-16
triggers: ["посмотреть превью лендинга", "проверить вёрстку на мобильном", "как выглядит на телефоне", "responsive-просмотр", "открыть превью composed"]
stage: "07b"
uses: ["block-composer", "block-composition"]
tags: ["preview", "responsive", "composed", "07b"]
---

# landing-previews — Просмотр лендинга на разных устройствах

## Что делает
Генерирует три HTML-файла-обёртки, чтобы можно было открыть `composed.html` в браузере и сразу увидеть, как лендинг выглядит на мобильном, планшете, десктопе и широком экране — без деплоя и настройки окружения.

## Когда вызывать / в каком этапе
Вызывается вручную после завершения этапа **07b (Compose)**, когда `07b_COMPOSED/composed.html` уже готов. Обычно запускается сразу после `/landing-compose`, чтобы визуально проверить результат перед переходом к этапу 08 (код).

```
/landing-previews <project>
```

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — итоговый скомпонованный лендинг (результат этапа 07b)

**Выход:**
- `composed-desktop-preview.html` — обёртка шириной 1280×800 (десктоп)
- `composed-mobile-preview.html` — обёртка шириной 375×812 (iPhone-размер)
- `composed-previews-index.html` — единый индекс с переключателем между всеми устройствами (mobile / tablet / desktop / wide)

Все три файла кладутся рядом с `composed.html` в папку `07b_COMPOSED/`. Достаточно открыть `composed-previews-index.html` в браузере — переключатель устройств встроен прямо в страницу.

## Связанные концепты
- [[block-composer]] — агент, который генерирует `composed.html` на этапе 07b; его результат — входной файл для этой команды
- [[block-composition]] — скилл, описывающий правила сборки composed.html с токенами и текстами
- [[landing-compose]] — команда, которую нужно запустить перед `/landing-previews`

## Источник
- `commands/landing-previews.md`