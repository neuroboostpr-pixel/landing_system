---
type: skill
name: paralaximus-codex
sources: ["skills/paralaximus-codex/SKILL.md"]
updated: 2026-05-15
triggers:
  - "сделай wow-эффект на герое"
  - "параллакс hero-блок с глубиной"
  - "анимированный герой с несколькими слоями"
  - "эффект параллакса при скролле"
stage: "07b"
uses:
  - block-composition
  - visual-generation
  - landing-content
tags:
  - parallax
  - hero
  - codex
  - image-generation
  - visual
---

# paralaximus-codex — параллакс-герой с 4 слоями

## Что делает

Создаёт hero-блок с эффектом глубины: одна 2K-картинка нарезается на 4 слоя (фон, дальний план, ближний план, главный объект), фоны снимаются через chroma-key, и всё оборачивается CSS+JS-движком — слои плавно расходятся при скролле и движении мыши.

## Когда вызывать / в каком этапе

Используется на этапе **07b (compose)** или позже, когда нужен «вау»-герой с ощущением пространства. Активировать только если:
- визуальная тема и главный объект ясны (продукт, персонаж, объект);
- клиент не запрещал иллюстрацию в hero (не «type-only»).

Если тема не определена — сначала уточнить у пользователя.

## Что на вход / на выход

**Вход:**
- путь к проекту (`/path/to/project`)
- описание визуальной темы: стиль, освещение, главный объект, цветокор под бренд-кит
- chroma-key цвет (`#00ff00` по умолчанию; `#ff00ff` если subject содержит зелёный)

**Выход:**
- `assets/atlas.png` — оригинальный 2K атлас (2048×1152, 4 квадранта)
- `assets/background.png` — opaque фон (верхний левый квадрант)
- `assets/far.png`, `near.png`, `subject.png` — RGBA-слои с прозрачным фоном
- `assets/layers-report.json` — отчёт по альфе
- `assets/css/parallax.css`, `assets/js/parallax.js` — CSS+JS движок
- `boilerplate/hero.html` — markup-референс (для WP переписывается в `block-hero.php`)

**Рабочий пайплайн (8 шагов):**
1. Уточнить тему и subject
2. Зафиксировать composition contract (стиль/свет/позиция/foreground/far/chroma-key)
3. Собрать промпт через шаблон `templates/atlas-prompt.md`
4. Запустить `generate-atlas.sh` → атлас появляется в `~/.codex/generated_images/` и копируется в проект
5. Нарезать `prepare-layers.py`
6. Снять chroma-key `remove-bg.sh` (внутри — `remove_chroma_key.py` из системного скилла `imagegen`)
7. Подключить boilerplate CSS/JS
8. Проверить локально: скролл, мышь, чистые края, subject не закрыт foreground

**Жёсткие ограничения:**
- Один запрос к `image_gen` (атлас), никогда не 4 отдельных
- Background removal только через `remove_chroma_key.py` из `imagegen`
- Foreground — рамка/обрамление, не главный объект

## Связанные концепты

- [[block-composition]] — скил compose (07b), в котором hero-блок встраивается в composed.html
- [[visual-generation]] — параллельный скил для иконок и инфографики (07d)
- [[landing-content]] — этап текстового наполнения, после которого верстается hero

## Источник

- `skills/paralaximus-codex/SKILL.md`