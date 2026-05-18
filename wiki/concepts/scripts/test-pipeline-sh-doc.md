---
type: command
name: test-pipeline
sources: ["scripts/test-pipeline.sh"]
updated: 2026-05-18
triggers:
  - "протестировать полный pipeline PR-A"
  - "проверить что prototype → wireframe → composed работает"
  - "запустить e2e тест нового проекта"
stage: ""
uses:
  - prototype-importer
  - ux-composer
  - block-composer
  - landing-prototype
  - landing-wireframe
  - landing-compose
tags: ["testing", "pr-a", "automation", "bash"]
---

# test-pipeline.sh — E2E-тест полного цикла PR-A

## Что делает

Запускает полный конвейер PR-A в одну команду: создаёт новый проект, подкладывает прототип и прогоняет всю цепочку — от исходного файла до готового `composed.html`. Используется для проверки работоспособности системы после изменений или при отладке нового проекта.

## Когда вызывать / в каком этапе

Запускается вручную из терминала разработчика или в CI. Не является slash-командой системы. Полезен когда нужно:
- убедиться что весь pipeline PR-A не сломан после правок
- быстро проверить новый прототип без ручного прохождения этапов 07→07b
- воспроизвести баг в конвейере на изолированном проекте

```bash
bash scripts/test-pipeline.sh <slug> <path-to-prototype>
```

**Примеры:**
```bash
bash scripts/test-pipeline.sh coffee-shop ~/Downloads/my-prototype.pdf
bash scripts/test-pipeline.sh saas-product ./samples/example-prototype.md
```

## Что на вход / на выход

**Вход:**
- `<slug>` — имя нового тестового проекта (kebab-case)
- `<path-to-prototype>` — путь к `.pdf` или `.md` файлу прототипа
- `TOKENS_FILE` *(env, опционально)* — путь к существующему `tokens.json`; по умолчанию встроенный заглушка
- `NICHE` *(env, опционально)* — `services|b2c|local`; по умолчанию выводится из прототипа или запрашивается
- `SKIP_OPEN=1` *(env, опционально)* — не открывать файлы по завершению

**Выход (артефакты в папке проекта):**
- `07_ПРОТОТИП/prototype.md` и `prototype.yaml` — нормализованный прототип
- `07a_WIREFRAME/wireframe.html` — интерактивный вайрфрейм
- `07b_COMPOSED/composed.html` — скомпонованная страница с токенами и текстами

## Связанные концепты

- [[prototype-importer]] — агент импорта прототипа (этап 07)
- [[ux-composer]] — агент рендеринга wireframe (этап 07a)
- [[block-composer]] — агент компоновки composed.html (этап 07b)
- [[landing-prototype]] — slash-команда запуска импорта
- [[landing-wireframe]] — slash-команда генерации вайрфрейма
- [[landing-compose]] — slash-команда финальной компоновки

## Источник

- `scripts/test-pipeline.sh`