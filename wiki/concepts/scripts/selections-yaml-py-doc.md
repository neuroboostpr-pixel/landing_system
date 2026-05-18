---
type: rule
name: selections-yaml-parser
sources: ["scripts/wiki/parsers/selections_yaml.py"]
updated: 2026-05-18
triggers: []
stage: "07a, 07c"
uses: ["ux-composer", "photo-curator", "block-composer", "photo-preview-board"]
tags: ["parser", "yaml", "wireframe", "photos", "selections"]
---

# selections_yaml — Парсер файлов выбора (wireframe + фото)

## Что делает

Читает и разбирает файл `selections.yaml`, который пользователь скачивает после подтверждения выбора блоков в wireframe или расстановки фотографий на photo-board. Превращает сырой YAML в структурированный объект, понятный другим агентам системы.

## Когда вызывать / в каком этапе

Используется на двух этапах:

- **07a (Wireframe)** — после того как пользователь открыл `wireframe.html`, выбрал варианты блоков и нажал «Confirm». Скачанный `selections.yaml` кладётся в `07a_WIREFRAME/` — парсер валидирует его перед запуском [[block-composer]].
- **07c (Photos)** — после того как пользователь расставил фотографии в `photo-board.html` и подтвердил выбор. Скачанный `selections.yaml` кладётся в `07c_PHOTOS/` — парсер передаёт данные в [[photo-preview-board]].

Вызывается автоматически внутри pipeline, не требует ручного запуска.

## Что на вход / на выход

**Вход:**
- `selections.yaml` — YAML-файл с выборами пользователя (вариант блока или фото для каждого слота)

**Выход:**
- Структурированный Python-объект / словарь с разобранными слотами и их значениями
- Валидационные ошибки, если файл некорректен (отсутствует обязательное поле, неверный формат)

## Связанные концепты

- [[ux-composer]] — генерирует `wireframe.html`, из которого пользователь скачивает `selections.yaml`
- [[block-composer]] — получает разобранные данные из wireframe-selections, чтобы собрать `composed.html`
- [[photo-curator]] — orchestrator этапа 07c, вызывает парсер после того как пользователь сдал photo selections
- [[photo-preview-board]] — использует разобранные photo-selections для генерации `photo-preview.html`
- [[prototype-import]] — смежный парсер этапа 07, разбирает `prototype.yaml`

## Источник

- `scripts/wiki/parsers/selections_yaml.py`