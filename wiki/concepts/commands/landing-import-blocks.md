---
type: command
name: landing-import-blocks
sources: ["commands/landing-import-blocks.md"]
updated: 2026-05-25
triggers:
  - "хочу импортировать блоки с сайта"
  - "забрать структуру с URL в библиотеку"
  - "добавить новые блоки из существующего сайта"
  - "расширить block-library новыми паттернами"
stage: ""
uses:
  - block-library
  - landing-wireframe
tags:
  - block-library
  - import
  - codex
  - vision
---

# /landing-import-blocks — Импорт блоков с URL в библиотеку

## Что делает

Берёт ссылку на сайт или PDF, анализирует структуру страницы через codex vision и добавляет универсальные HTML+CSS шаблоны блоков в `block-library/`. Чужой контент (фото, тексты, логотипы) не копируется — только структурные паттерны оформления.

## Когда вызывать

Используй, когда нашёл интересный сайт с крутой версталкой и хочешь забрать структурный паттерн в свою библиотеку блоков. Также подходит для планомерного расширения `block-library/` перед этапами wireframe и compose.

Примеры команды:
```
/landing-import-blocks https://example.com premium-auto
/landing-import-blocks https://example.com/portfolio.pdf
```

## Что на вход / на выход

**Вход:**
- URL сайта или PDF
- опциональная ниша (например, `premium-auto`, `medclinic`)

**Выход:**
- Новые блоки в `block-library/<type>/<unique-id>/` — каждый блок содержит `index.html`, `styles.css`, `meta.yaml`, `reference.png`
- Обновлённый `block-library/catalog.yaml`

## Как работает внутри

1. Скачивает страницу через Playwright (HTML) или curl (PDF → PNG через pdftoppm/pdfimages)
2. Делает full-page скриншот desktop + mobile
3. Codex CLI vision анализирует скриншот → JSON с описанием блоков (type, style_mood, layout, niches)
4. Codex (text-mode) генерирует **универсальный** HTML+CSS в стиле системы: CSS vars, `{{slot:*}}` placeholders вместо чужого контента
5. Сохраняет результаты, обновляет каталог

Рабочая папка `.import-blocks-work/<sha>/` — в `.gitignore`.  
Стоимость: **~$0.20–0.40** на один URL (1 vision-вызов + N text-generation вызовов).

## Связанные концепты

- [[block-library]] — целевое хранилище, куда добавляются импортированные блоки
- [[landing-wireframe]] — использует block-library при выборе вариантов блоков на этапе 07a

## Источник

- `commands/landing-import-blocks.md`