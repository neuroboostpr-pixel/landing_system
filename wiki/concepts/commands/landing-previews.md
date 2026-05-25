---
type: command
name: landing-previews
sources: ["commands/landing-previews.md"]
updated: 2026-05-25
triggers:
  - "сгенерировать превью лендинга"
  - "посмотреть как выглядит на мобильном"
  - "desktop и mobile preview"
  - "открыть composed в разных устройствах"
stage: "07b"
uses:
  - landing-compose
tags:
  - preview
  - responsive
  - composed
---

# Landing Previews — генерация HTML-превью для разных устройств

## Что делает

Создаёт три HTML-файла-обёртки вокруг готового `composed.html`, позволяя увидеть, как лендинг выглядит на разных устройствах — без деплоя, прямо в браузере.

## Когда вызывать / в каком этапе

Вызывать после завершения этапа **07b (compose)** — когда `composed.html` уже собран командой `/landing-compose`. Используется для визуальной проверки перед утверждением макета и переходом к этапам сборки (08) и деплоя (09).

Вызов вручную:

```
/landing-previews <project>
```

## Что на вход / на выход

**Вход:**
- Готовый `07b_COMPOSED/composed.html` в папке проекта.
- Слаг проекта как аргумент команды.

**Выход — три файла в `07b_COMPOSED/`:**
| Файл | Размер viewport |
|---|---|
| `composed-desktop-preview.html` | 1280×800 |
| `composed-mobile-preview.html` | 375×812 |
| `composed-previews-index.html` | переключатель всех устройств |

Открой `composed-previews-index.html` в браузере — там можно переключаться между mobile, tablet, desktop и wide-режимами.

## Связанные концепты

- [[landing-compose]] — создаёт `composed.html`, который является входом для этой команды
- [[landing-wireframe]] — предшествующий этап выбора вариантов блоков

## Источник

- `commands/landing-previews.md`