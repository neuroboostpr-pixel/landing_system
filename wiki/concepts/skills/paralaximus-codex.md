---
slug: paralaximus-codex
type: skill
name: "Параллакс-герой через Codex (Paralaximus)"
stage: "07b"
tags: [parallax, hero, codex, image-gen, visual, css-animation]
triggers: [landing-compose, landing-visuals]
inputs: [07b-composed, 05-dizayn-sistema]
outputs: [07b-composed]
gates: []
pre_reqs: [05-dizayn-sistema, 07b-composed]
related: [landing-compose, landing-visuals, visual-generation, block-composer, visual-curator]
sources: ["skills/paralaximus-codex/SKILL.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Параллакс-герой через Codex (Paralaximus)

## Что делает

Превращает одну сгенерированную Codex'ом 2K-картинку (атлас 2048×1152) в четырёхслойный параллакс-блок. Атлас делится на четыре квадранта: фон (opaque), дальний план, передний план и главный объект (subject). Три нижних квадранта рисуются на chroma-key фоне (`#00ff00` или `#ff00ff`) — локальный скрипт `remove_chroma_key.py` снимает фон и делает их RGBA-прозрачными. Итог: четыре PNG-слоя, которые двигаются с разной скоростью при скролле и движении мыши через готовый `parallax.css` + `parallax.js`. CSS-переменные подхватываются из токенов проекта автоматически.

## Когда вызывается

Вручную — когда hero-блок проекта требует «вау-эффекта» с ощущением глубины и пространства. Условие: визуальная тема ясна (продукт, персонаж, объект), клиент не запрещал иллюстрацию hero, этап 05 (design-system) и `composed.html` (07b) уже готовы.

## Вход → выход

**Вход:** путь к папке проекта, утверждённые токены из этапа 05, `composed.html` из 07b, описание visual-темы и subject (продукт / персонаж / метафора).

**Выход:** четыре PNG-слоя (`background.png`, `far.png`, `near.png`, `subject.png`) в `<project>/assets/`, `parallax.css`, `parallax.js`, `hero.html` (markup-референс для WordPress-темы), `layers-report.json`.

## Failure modes

- **Silent fail Codex** — генерация завершилась без сообщений; картинка обычно есть в `~/.codex/generated_images/`, скрипт копирует её сам после выхода.
- **Зелёный fringe на краях** — lighting дал rim-glow на chroma-key; повторить шаг 6 с флагом `--edge-contract 1`.
- **Subject слишком мелкий** — промпт не зафиксировал «two-thirds of quadrant height»; перегенерировать с явным указанием размера.
- **Foreground закрывает лицо/торс** — промпт не ограничил near нижними 20–35%; исправить composition contract и перегенерировать.
- **`remove_chroma_key.py` не найден** — imagegen-навык Codex не установлен; восстановить `${CODEX_HOME}/skills/.system/imagegen/`.

## Related

- [[07b-composed]] — целевой артефакт, в который встраивается героблок
- [[landing-compose]] — этап, на котором вызывается скил
- [[landing-visuals]] — параллельный визуал-пайплайн иконок и инфографики
- [[visual-generation]] — общий концепт AI-генерации визуала в системе
- [[block-composer]] — агент, который собирает composed.html и может инициировать вызов