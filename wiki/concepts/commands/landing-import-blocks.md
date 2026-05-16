---
type: command
name: landing-import-blocks
sources: ["commands/landing-import-blocks.md"]
updated: 2026-05-16
triggers:
  - "хочу добавить блок из другого сайта"
  - "импортировать блоки в библиотеку"
  - "забрать паттерн с сайта"
  - "расширить block-library"
stage: ""
uses:
  - block-library-management
  - visual-generation
tags: ["block-library", "codex", "import", "vision"]
---

# /landing-import-blocks — Импорт блоков из URL в библиотеку

## Что делает
Анализирует любой сайт или PDF через AI-зрение, вычленяет структурные паттерны блоков и добавляет универсальные HTML+CSS шаблоны в `block-library/`. Чужой контент (фото, тексты, логотипы) не копируется — только структура и стиль.

## Когда вызывать / в каком этапе
Команда не привязана к конкретному этапу pipeline. Вызывать когда:
- Нашёл крутой сайт с интересным структурным паттерном и хочешь забрать его в библиотеку.
- Нужно расширить `block-library/` новыми типами блоков перед началом проекта.
- Есть PDF с референсным дизайном, из которого хочется извлечь блоки.

```
/landing-import-blocks <url> [niche]
/landing-import-blocks https://example.com premium-auto
/landing-import-blocks https://example.com/portfolio.pdf
```

## Что на вход / на выход

**Вход:**
- URL сайта или PDF-файла (обязательно)
- Необязательный параметр `niche` (например: `premium-auto`) — влияет на тегирование блоков

**Выход:**
- Папки `block-library/<type>/<unique-id>/` с файлами:
  - `index.html` — универсальный шаблон блока с `{{slot:*}}` placeholders
  - `styles.css` — стили на CSS-переменных системы
  - `meta.yaml` — тип, настроение, layout, ниши
  - `reference.png` — скриншот-референс оригинала
- Обновлённый `block-library/catalog.yaml`

**Под капотом:**
- Playwright делает full-page скриншот desktop+mobile (или pdftoppm конвертит PDF)
- Codex vision анализирует скриншот → JSON со списком блоков
- Codex text-mode генерирует HTML+CSS в стиле системы
- Рабочая папка `.import-blocks-work/<sha>/` (в .gitignore)
- Промпты из `scripts/import-blocks/templates/`

**Стоимость:** ~$0.20–0.40 codex API на один URL.

## Связанные концепты
- [[block-library-management]] — управление каталогом блоков, куда сохраняются импортированные блоки
- [[visual-generation]] — смежный процесс AI-генерации визуала через codex
- [[ux-composer]] — использует `block-library/` при построении wireframe

## Источник
- `commands/landing-import-blocks.md`