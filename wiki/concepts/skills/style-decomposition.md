---
type: skill
name: style-decomposition
sources: ["skills/style-decomposition/SKILL.md"]
updated: 2026-05-15
triggers: []
stage: "04"
uses: ["style-extractor", "brand-architect", "brand-kit-build"]
tags: ["palette", "fonts", "icons", "extraction", "stage-04"]
---

# Style Decomposition — Извлечение стиля из референсов

## Что делает
Автоматически извлекает цвета, шрифты и иконки из картинок и веб-ссылок референсов. На выходе — пять структурированных файлов, которые потом использует `brand-architect` для сборки бренд-кита.

## Когда вызывать / в каком этапе
Запускается на **этапе 04** (Бренд), после того как мудборд утверждён и референсы собраны. Вызывается агентом `style-extractor`. Вручную пользователь этот скилл не трогает — он часть внутреннего пайплайна.

## Что на вход / на выход

**Вход:**
- Изображения референсов (скриншоты, фото) из `03_РЕФЕРЕНСЫ/`
- URL-ссылки сайтов-референсов

**Выход** (папка `04_БРЕНД/extracted/`):
- `palette.yaml` — доминантные цвета (HEX + роли: primary, accent, neutral)
- `fonts.yaml` — найденные шрифты с вариантами начертания
- `icons.yaml` — подобранные иконки из Iconify по семантическим именам
- `grid.md` — сетка и отступы, выведенные из референсов
- `motion.md` — паттерны анимации и переходов

**Внутренние скрипты:**
| Скрипт | Задача |
|---|---|
| `extract-palette.py` | Colorthief + Pillow → цвета из изображений |
| `identify-fonts.py` | Playwright DOM → CSS-шрифты с URL |
| `match-icons.py` | Semantic names → Iconify matching |
| `download-fonts.py` | Скачать WOFF2-файлы для офлайн-использования |
| `orchestrate.py` | Точка входа: запускает все 4 скрипта по очереди |

## Связанные концепты
- [[style-extractor]] — агент-владелец этого скилла, вызывает `orchestrate.py`
- [[brand-architect]] — следующий шаг: берёт 5 extracted-файлов и синтезирует `brand-kit.md`
- [[brand-kit-build]] — скилл, которому принадлежит `brand-architect`
- [[moodboard-creation]] — предшествующий этап, после которого запускается style-decomposition
- [[references-collection]] — поставляет исходные URL и изображения на вход

## Источник
- `skills/style-decomposition/SKILL.md`