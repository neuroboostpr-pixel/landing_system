---
type: command
name: landing-previews
sources: ["commands/landing-previews.md"]
updated: 2026-05-26
triggers:
  - "покажи превью лендинга"
  - "сгенерируй предпросмотр для разных устройств"
  - "хочу посмотреть как выглядит на мобильном"
  - "открой превью composed.html"
stage: "07b"
uses:
  - landing-compose
tags:
  - preview
  - responsive
  - composed
---

# Landing Previews — предпросмотр лендинга на разных устройствах

## Что делает

Генерирует три HTML-файла-обёртки вокруг `composed.html`, чтобы маркетолог мог увидеть лендинг сразу на desktop, планшете и мобильном — без реального браузерного инструмента разработчика.

## Когда вызывать / в каком этапе

Вызывается вручную после того, как этап **07b (Compose)** завершён и `composed.html` уже готов. Используй команду, когда нужно визуально проверить адаптивность вёрстки перед переходом к этапу 08 (Build).

```
/landing-previews <project>
```

Где `<project>` — slug папки проекта внутри `~/Lendings/`.

## Что на вход / на выход

**Вход:**
- Готовый `07b_COMPOSED/composed.html` в папке проекта.

**Выход** (три файла в `07b_COMPOSED/`):
- `composed-desktop-preview.html` — обёртка с шириной 1280×800 (desktop).
- `composed-mobile-preview.html` — обёртка с шириной 375×812 (iPhone-формат).
- `composed-previews-index.html` — единый файл с переключателем между всеми устройствами (mobile / tablet / desktop / wide).

Открой `composed-previews-index.html` в браузере — переключатель позволит быстро проверить все форм-факторы.

## Связанные концепты

- [[landing-compose]] — создаёт `composed.html`, который является обязательным входом для этой команды
- [[landing-wireframe]] — предшествующий этап 07a, после которого запускается compose

## Источник

- `commands/landing-previews.md`