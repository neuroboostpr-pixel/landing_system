---
slug: style-decomposition
type: skill
name: "Декомпозиция стиля (Style Decomposition)"
stage: "04"
tags: [brand, palette, fonts, icons, extraction, design-tokens]
triggers: [landing-brand]
inputs: [03_РЕФЕРЕНСЫ/, 04_БРЕНД/logos/]
outputs: [04_БРЕНД/extracted/palette.yaml, 04_БРЕНД/extracted/fonts.yaml, 04_БРЕНД/extracted/icons.yaml, 04_БРЕНД/extracted/grid.md, 04_БРЕНД/extracted/motion.md]
gates: []
pre_reqs: [references-curator]
related: [style-extractor, brand-architect, brand-kit-build, design-tokens-generation, design-system-generator, moodboard-composer]
sources: ["skills/style-decomposition/SKILL.md"]
updated: 2026-05-26
confidence: {triggers: low, gates: low}
---

# Декомпозиция стиля (Style Decomposition)

## Что делает

Скилл извлекает визуальный DNA проекта из референсных материалов: доминирующую цветовую палитру из изображений (через colorthief + Pillow), шрифты со страниц конкурентов через DOM-инспекцию (Playwright), подходящие иконки из библиотеки Iconify. Дополнительно скачивает рекомендованные шрифты в формате WOFF2 для офлайн-использования. Все результаты укладываются в 5 структурированных файлов в папку `04_БРЕНД/extracted/`, которые затем использует `brand-architect` для сборки brand-kit.

## Когда вызывается

Вызывается агентом `style-extractor` в рамках этапа 04 (бренд) — после того как папка `03_РЕФЕРЕНСЫ/` укомплектована ссылками или изображениями, и до начала генерации design-system. Точкой входа служит `scripts/orchestrate.py`, который последовательно запускает все четыре специализированных скрипта.

## Вход → выход

**Вход:** референсные изображения и/или URL из папки `03_РЕФЕРЕНСЫ/`, логотип клиента из `04_БРЕНД/logos/` (опционально).

**Выход:** пять файлов в `04_БРЕНД/extracted/`:
- `palette.yaml` — hex-коды доминирующих цветов с семантическими ролями
- `fonts.yaml` — идентифицированные гарнитуры с источником (Google Fonts / локальный WOFF2)
- `icons.yaml` — рекомендованные иконки из Iconify с матчингом по семантике
- `grid.md` — наблюдения по сетке и отступам
- `motion.md` — наблюдения по анимациям и переходам

## Failure modes

- **Playwright не поднялся** — DOM-инспекция шрифтов падает, если Chromium не установлен или URL закрыт за авторизацией; `fonts.yaml` выйдет пустым.
- **colorthief даёт нерелевантную палитру** — при слишком мелких или белофоновых изображениях доминирующие цвета вырождаются в белый/серый; требуется ручная правка.
- **Iconify не находит совпадений** — при узкоотраслевой семантике `icons.yaml` получает низкий confidence-score; нужен ручной подбор через `icon-generator`.
- **WOFF2-загрузка заблокирована** — Google Fonts CDN может быть недоступен в сети; скрипт пишет fallback-ссылку вместо файла.
- **Оркестратор прерван на полпути** — при частичном прогоне `orchestrate.py` могут существовать файлы от предыдущего запуска; повторный запуск перезаписывает их, что ожидаемо.

## Related

- [[style-extractor]] — агент-владелец, вызывает этот скилл
- [[references-curator]] — формирует входные референсы для скилла
- [[brand-architect]] — потребляет выходные файлы для сборки brand-kit
- [[brand-kit-build]] — следующий этап, использует extracted/
- [[design-tokens-generation]] — преобразует palette.yaml и fonts.yaml в CSS-переменные
- [[moodboard-composer]] — параллельный скилл этапа 04, работает с теми же референсами