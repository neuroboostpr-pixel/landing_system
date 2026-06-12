---
name: paralaximus-codex
description: Generate a layered parallax hero block by producing one 2K 16:9 atlas via codex exec (built-in image_gen / gpt-image-2), slicing into 4 layers (background/far/near/subject), removing chroma-key backgrounds with the imagegen helper, and wiring up scroll+mouse parallax CSS+JS. Use when a project asks for a "wow hero" with depth.
---

# paralaximus-codex

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill paralaximus-codex --stage 07b
```

Производство параллакс-героя: одна 2K-картинка → 4 слоя → CSS+JS параллакс с распадом по скроллу и движению мыши. Под капотом — Codex CLI built-in `image_gen` + локальный `remove_chroma_key.py` из системного навыка `imagegen`.

## Когда использовать

- Hero-блок просит «вау-эффект», глубину, ощущение пространства.
- Тема визуала ясна (продукт, персонаж, объект). Если темы нет — сначала уточнить.
- В клиентских требованиях нет запрета на иллюстрацию hero (если клиент явно сказал «type-only, без картинки» — не использовать).

## Концепция

`gpt-image-2` не поддерживает native transparency. Поэтому атлас рисуется так:
- **TL (background)** — opaque сцена.
- **TR / BL / BR (far / near / subject)** — на perfectly flat solid `#00ff00` (или `#ff00ff` если subject зелёный) — chroma-key, который снимется локально.

```
┌─────────────────┬─────────────────┐
│ TL: BACKGROUND  │ TR: FAR         │
│ (opaque scene)  │ (chroma-key)    │
├─────────────────┼─────────────────┤
│ BL: NEAR        │ BR: SUBJECT     │
│ (chroma-key)    │ (chroma-key)    │
└─────────────────┴─────────────────┘
```

После генерации — нарезка `prepare-layers.py` → снятие фона `remove-bg.sh` (вызывает локальный `remove_chroma_key.py` из imagegen) → 4 PNG: 1 opaque (background) + 3 RGBA (far / near / subject).

## Зависимости

- `codex` CLI v0.125+ (логин: `codex login`)
- Системный Codex skill `imagegen` (содержит `remove_chroma_key.py`)
- Python 3.10+ с `Pillow`
- bash (Git Bash на Windows подходит)

Проверка `imagegen`:
```bash
ls "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/remove_chroma_key.py"
```

## Workflow (8 шагов)

### 1. Уточнить тему и subject

Конкретный продукт / персонаж / метафора. Без этого скил не запускать.

### 2. Composition contract

Прежде чем сочинять промпт, ответить:
- **Visual style:** Studio Photography / Cinematic Matte Painting / 3D Render / Editorial.
- **Lighting:** Soft studio / Cinematic rim / Golden hour / Moody neon.
- **Где стоит/сидит subject:** земля, стол, подиум, кресло — обязательно.
- **Что в foreground (BL):** обрамляет низ/бока. **Не главный объект.** Не закрывает лицо/торс.
- **Цветокор:** под бренд-кит проекта.
- **Что в far (TR):** 4–7 средне-крупных объектов с чёткими краями.
- **Chroma key:** `#00ff00` по умолчанию. `#ff00ff` если subject содержит зелёный (растения, зелёная одежда).

### 3. Собрать prompt

Использовать шаблон из `templates/atlas-prompt.md`. Подставить плейсхолдеры. В шаблоне уже учтены:
- размер `2048x1152` (2K, 16:9)
- chroma-key инструкции для TR/BL/BR
- запреты на тени/градиенты/чужие цвета на квадрантах с chroma
- subject ≈ две трети высоты квадранта

### 4. Запустить генерацию

```bash
bash skills/paralaximus-codex/scripts/generate-atlas.sh \
    /path/to/project \
    --prompt "$(cat /tmp/prompt.txt)"
```

или передать файл с промптом первым аргументом.

Под капотом:
- `codex exec --skip-git-repo-check "<prompt>"` рендерит атлас в `~/.codex/generated_images/<новый-uuid>/ig_*.png`
- Codex попытается скопировать в проект и **получит отказ от своей же sandbox-политики** — это нормально, не ошибка.
- Скрипт сам копирует свежий PNG в `<project>/assets/atlas.png`.

Если выход Codex'а пуст (silent fail) — проверь `ls -t ~/.codex/generated_images/ | head`. Картинка обычно появляется даже когда stdout молчит.

### 5. Нарезать на слои

```bash
python skills/paralaximus-codex/scripts/prepare-layers.py /path/to/project
```

Создаст:
- `<project>/assets/background.png` — opaque (top-left квадрант)
- `<project>/assets/far.png` — chroma-key, 1024×576 (top-right)
- `<project>/assets/near.png` — chroma-key (bottom-left)
- `<project>/assets/subject.png` — chroma-key (bottom-right)
- `<project>/assets/layers-report.json` — отчёт по альфе

Скрипт пометит `far/near/subject` как «без альфы — нужна chroma-key removal». Это ожидаемо.

### 6. Снять chroma-key

```bash
bash skills/paralaximus-codex/scripts/remove-bg.sh /path/to/project
```

Если chroma-key не `#00ff00`:
```bash
bash skills/paralaximus-codex/scripts/remove-bg.sh /path/to/project --key '#ff00ff'
```

После запуска `far.png / near.png / subject.png` — RGBA с прозрачным фоном. `background.png` остаётся opaque.

Помощник внутри: `${CODEX_HOME}/skills/.system/imagegen/scripts/remove_chroma_key.py` с soft-matte, despill, auto-key border.

### 7. Подключить boilerplate

Скопировать в проект:
- `boilerplate/parallax.css` → `<project>/assets/css/parallax.css`
- `boilerplate/parallax.js`  → `<project>/assets/js/parallax.js`
- `boilerplate/hero.html` — markup-референс. Для WordPress переписать в `template-parts/block-hero.php`, добавить enqueue в `functions.php`.

Атрибут `[data-parallax-hero]` на корневом элементе включает движок. CSS-переменные (`--font-display`, `--font-body`, `--text-primary`) подхватятся из существующих токенов проекта.

### 8. Проверить локально

- Открыть страницу в браузере.
- Скролл + движение мыши: четыре слоя двигаются с разной скоростью и направлением.
- Subject и near не двигаются одинаково.
- Foreground (`near`) не закрывает лицо/торс subject больше чем на 10–25 %.
- Subject крупный — около двух третей высоты. Если нет — перегенерировать.
- Edges на subject/far/near чистые, без зелёного fringe. Если есть — повторить шаг 6 с `--edge-contract 1`.
- На `prefers-reduced-motion: reduce` параллакс выключен.

## Жёсткие правила

- ❌ **Никогда** не делать 4 отдельных запроса к `image_gen`. Только один атлас.
- ❌ **Никогда** не использовать DIY background removal (`rembg` и т.п.). Только `remove_chroma_key.py` из imagegen.
- ❌ **Никогда** не делать foreground главным объектом. Это рамка, не звезда.
- ❌ **Никогда** не публиковать на прод, если пользователь просил локальный прототип.
- ✅ Всегда сохранять оригинал Codex'а в `~/.codex/generated_images/`. Только копировать в проект.
- ✅ Subject должен иметь точку контакта со средой.
- ✅ Большой текст-заголовок (`.lp-hero__title`) встаёт между background и subject — даёт 3D-эффект.
- ✅ Цвет chroma-key — `#00ff00` по умолчанию; `#ff00ff` для зелёных subjects; `#0000ff` НЕ использовать.

## Грабли

| Симптом | Причина | Решение |
|---|---|---|
| Файл не появился в проекте после `generate-atlas.sh` | Sandbox Codex'а блокирует копию | Скрипт копирует сам после выхода Codex. Если копии нет — посмотри `~/.codex/generated_images/` напрямую |
| `silent fail` — Codex закрылся без сообщения | Sandbox блокирует write — Codex не успел сообщить | Картинка обычно создана. `ls -t ~/.codex/generated_images/` |
| Зелёный fringe на edges после chroma-key | Lighting в изображении дал rim glow | Повторить с `--edge-contract 1` (отредактировать `remove-bg.sh` или `remove_chroma_key.py`-аргументы) |
| Subject слишком мелкий | Промпт не зафиксировал размер | Добавить «approximately two-thirds of quadrant height» |
| Foreground закрывает лицо | Промпт не зафиксировал «lower 20-35% only» | Промпт должен явно требовать нижней рамки |
| Codex генерирует общий фон вместо 4 квадрантов | Композиционный контракт пропущен | В промпте обязательно: «Each quadrant occupies exactly one quarter of the 2048x1152 atlas» |
| `remove_chroma_key.py` not found | imagegen-навык не установлен | Скачать/восстановить `${CODEX_HOME}/skills/.system/imagegen/` |

## Структура скила

```
skills/paralaximus-codex/
├── SKILL.md                       # ← вы здесь
├── scripts/
│   ├── generate-atlas.sh          # codex exec wrapper + копирование из ~/.codex/generated_images
│   ├── prepare-layers.py          # резка 2K атласа на 4 квадранта
│   └── remove-bg.sh               # batch chroma-key removal (вызывает remove_chroma_key.py)
├── boilerplate/
│   ├── parallax.css               # стили слоёв и параллакса
│   ├── parallax.js                # scroll/mouse engine
│   └── hero.html                  # markup-референс
└── templates/
    └── atlas-prompt.md            # промпт-шаблон с placeholders + filled example
```

## Лицензия

Базируется на PARALAXIMUS by Horosheff (MIT, https://github.com/Horosheff/paralaximus-agent), переписан под Claude Code + Codex CLI built-in `image_gen` workflow.
