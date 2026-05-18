---
description: Импорт блоков с любого URL (сайт или PDF) в block-library через codex CLI vision.
---

# /landing-import-blocks

Берёт URL, делает скриншот, анализирует структуру через codex, генерирует универсальные HTML+CSS шаблоны блоков и добавляет в `block-library/`.

## Использование

```
/landing-import-blocks <url> [niche]
/landing-import-blocks https://example.com premium-auto
/landing-import-blocks https://example.com/portfolio.pdf
```

## Что делает

1. Скачивает страницу (HTML через playwright или PDF через curl).
2. Делает full-page скриншот desktop+mobile (или конвертит PDF в PNG через pdftoppm / pdfimages).
3. Codex CLI vision анализирует скриншот → JSON со списком блоков (type, style_mood, layout, niches).
4. Для каждого блока codex (text-mode) генерирует **универсальный** HTML+CSS — наш стиль, наши CSS vars, `{{slot:*}}` placeholders вместо чужого контента. Чужие фото/тексты/логотипы не копируются.
5. Сохраняет в `block-library/<type>/<unique-id>/{index.html, styles.css, meta.yaml, reference.png}`.
6. Обновляет `block-library/catalog.yaml`.

## Под капотом

- Pipeline: `scripts/import-blocks/import-from-url.sh <url> [niche]`
- Промпты: `scripts/import-blocks/templates/structure-analysis-prompt.md` и `block-generation-prompt.md` (оба прошли gpt5-prompting-engine, score 10/10).
- Рабочая папка `.import-blocks-work/<sha>/` (в .gitignore).

## Цена

~$0.20–0.40 codex на URL (1 vision-call + N text-generation calls по блокам).

## Когда использовать

- Расширение `block-library/` новыми паттернами оформления.
- Нашёл крутой сайт → хочешь забрать структурный паттерн в свою библиотеку (без копирования контента).
