---
slug: paralaximus-codex
type: skill
name: "Параллакс-герой Paralaximus Codex"
stage: "07d"
tags: [parallax, hero, codex, image-gen, visual, css, js, chroma-key]
triggers: [landing-visuals, wow-hero-request]
inputs: [04_БРЕНД/brand-kit.md, 05_ДИЗАЙН/tokens.json]
outputs: [assets/background.png, assets/far.png, assets/near.png, assets/subject.png, assets/css/parallax.css, assets/js/parallax.js]
gates: []
pre_reqs: [brand-kit-build, design-system-generator]
related: [icon-generator, infographic-builder, visual-curator, scene-director, block-composer]
sources: ["skills/paralaximus-codex/SKILL.md"]
updated: 2026-05-26
confidence: {stage: low, triggers: low}
---

# Параллакс-герой Paralaximus Codex

## Что делает

Генерирует эффектный hero-блок с многослойным параллаксом из одного 2K-атласа. Через Codex CLI рисует единое изображение 2048×1152, где четыре квадранта — фон, дальний план, ближний план и главный объект. Затем нарезает атлас на четыре PNG, снимает chroma-key фон с трёх слоёв через `remove_chroma_key.py` (из системного навыка `imagegen`), после чего подключает готовые CSS+JS-файлы параллакса: слои двигаются по скроллу и мыши с разными скоростями, создавая иллюзию глубины.

## Когда вызывается

Запускается вручную, когда проект запрашивает «вау-эффект» для hero-блока: продукт, персонаж или метафора с ощущением пространства. Не используется, если клиент потребовал «только типографика, без иллюстраций», или если тема визуала ещё не определена.

## Вход → выход

**Вход:** папка проекта с `brand-kit.md` и `tokens.json`; готовый промпт-шаблон из `templates/atlas-prompt.md` с заполненными плейсхолдерами (визуальный стиль, свет, расположение subject, цвет chroma-key, объекты дальнего и ближнего плана).

**Выход:** четыре PNG-слоя в `assets/` (один opaque + три RGBA без фона), `parallax.css`, `parallax.js` и `hero.html` как markup-референс. Для WordPress `hero.html` переписывается в `template-parts/block-hero.php` с энqueue в `functions.php`.

## Failure modes

- **Silent fail Codex:** генерация прошла, но stdout пуст — картинка обычно есть в `~/.codex/generated_images/`; скрипт копирует её сам.
- **Зелёный fringe на краях:** освещение дало rim glow вокруг subject — повторить шаг 6 с флагом `--edge-contract 1`.
- **Неправильные квадранты:** промпт не зафиксировал «Each quadrant occupies exactly one quarter of the 2048×1152 atlas» — атлас рисуется общей сценой.
- **Foreground закрывает лицо subject:** промпт не ограничил foreground нижней рамкой («lower 20–35 % only»).
- **`remove_chroma_key.py` не найден:** системный навык `imagegen` не установлен — восстановить `${CODEX_HOME}/skills/.system/imagegen/`.

## Related

- [[icon-generator]] — аналогичный visual-этап, генерирует SVG-иконки; часто идёт параллельно
- [[infographic-builder]] — генерирует инфографику; тот же stage 07d
- [[visual-curator]] — курирует итоговые ассеты перед сборкой
- [[scene-director]] — определяет визуальную концепцию и стиль сцены до генерации атласа
- [[block-composer]] — встраивает готовый hero-блок в `composed.html` на этапе 07b