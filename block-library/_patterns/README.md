# Visual Patterns Library

Ванильные CSS/JS паттерны без зависимостей. Источник — OpenDesign (Apache-2.0).

## Что это

9 переиспользуемых паттернов которые подключаются в WP-темы автоматически
через `generate-theme.py` в зависимости от `animation_mode` в `tokens.json`.

## Структура каждого паттерна

```
<pattern-name>/
  snippet.css    — production-ready CSS с prefers-reduced-motion
  snippet.js     — vanilla JS (только если нужен)
  snippet.html   — минимальный пример применения (3-15 строк)
  SOURCE.md      — откуда взято, когда применять, как подключить
```

## Таблица паттернов

| Паттерн | Что даёт | animation_mode |
|---|---|---|
| `scroll-reveal` | Плавное появление блоков при скролле | smooth, cinematic, editorial |
| `paper-texture` | Бумажная текстура фона | cinematic, editorial |
| `ambient-mesh-bg` | Живой mesh-фон без JS/Three.js | cinematic |
| `marquee-fade` | Бегущая строка с fade-краями | smooth, cinematic, editorial |
| `floating-pill-nav` | Sticky pill-nav с backdrop-blur | smooth, cinematic, editorial |
| `headroom-nav` | Nav прячется при скролле вниз | smooth, cinematic, editorial |
| `dot-grid-bg` | Editorial dot-pattern фон | editorial |
| `conic-ring` | Прогресс-кольцо без canvas | smooth, cinematic, editorial |
| `bento-grid-hairline` | 6-col Notion-style grid | smooth, cinematic, editorial |

## Правила использования

- **Только vanilla** — никакого npm, React, Webpack
- **RU-язык** в текстовых placeholders
- **Только нативный CSS** — без Tailwind/Bootstrap
- **prefers-reduced-motion** обязателен везде где есть transition/animation
- **НЕТ WhatsApp/вотсап** кнопок в примерах

## Подключение в generate-theme.py

```python
from pathlib import Path

PATTERNS_DIR = Path(__file__).parents[4] / "block-library" / "_patterns"
PATTERNS_BY_MODE = {
    'none': [],
    'smooth': ['scroll-reveal', 'headroom-nav'],
    'cinematic': ['scroll-reveal', 'headroom-nav', 'ambient-mesh-bg', 'paper-texture'],
    'editorial': ['scroll-reveal', 'paper-texture', 'dot-grid-bg'],
}
```

## Лицензия

Паттерны основаны на OpenDesign (Apache-2.0, github.com/nexu-io/open-design).
При воспроизведении — attribution в HTML-комментарии достаточен.
