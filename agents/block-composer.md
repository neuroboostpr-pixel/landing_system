---
name: block-composer
description: Use during stage 07b (Block Compose) to render composed.html — final pre-build assembly with design-tokens injected and prototype texts substituted. Visual content (photos/icons/infographics) remain as labeled placeholders (filled by PR-B/PR-C).
---

# block-composer

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 07c_composed`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `07c_composed` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 07c_composed --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-07c_composed-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-07c_composed.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 07c_composed`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

## СТРОГО: контент прототипа неприкосновенен (PR-H)

Текст из `<project>/07_ПРОТОТИП/prototype.yaml` — **финальный**.

**Правила:**
- Заголовки блоков (`title`) — переноси ДОСЛОВНО, не «улучшай».
- CTA-тексты (`cta`) — ДОСЛОВНО.
- Абзацы и пункты (`body`, `items`) — ДОСЛОВНО.
- Порядок блоков — точно как в `blocks[]` массиве.

**Если хочешь что-то изменить:**
- НЕ делай этого молча.
- Спроси пользователя явно: «Я предлагаю переписать заголовок hero
  с '[X]' на '[Y]' потому что [причина]. Разрешаешь?»
- После «да» — обнови сначала `prototype.yaml`, потом HTML.

**HARD GATE 07c:** `scripts/verify-content-preserved.sh` запустится
при закрытии 07c. Если найдёт расхождение — этап не закроется.
Подробнее: `docs/superpowers/specs/2026-05-15-pr-h-content-preserve-design.md`.

## Mission

Сборка `<project>/07b_COMPOSED/composed.html` + `composed-mobile.html` из утверждённых `selections.yaml`, `prototype.yaml` и `tokens.json`. На выходе — цветной макет с реальными текстами/CTA и visible placeholders для фото/иконок/инфографики.

## Inputs

- `<project>/07_ПРОТОТИП/prototype.yaml`
- `<project>/07a_WIREFRAME/selections.yaml`
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json`
- `block-library/` (общая)
- **`docs/standards/premium-07b-checklist.md`** — обязательный стандарт качества (см. ниже)

## PREMIUM QUALITY BAR (обязательный стандарт)

Каждый `composed.html` ДОЛЖЕН соответствовать
`landing-system/docs/standards/premium-07b-checklist.md`.

Это не «рекомендация» — это **definition of done** для этапа 07b.

Стандарт требует 13 обязательных премиум-фич:

1. CSS-переменные в `:root` (все цвета/тени/шрифты — токены, не хардкод)
2. `clamp()` для всей крупной типографики
3. Glassmorphism sticky nav (`backdrop-filter: blur(20px) saturate(180%)`)
4. Parallax hero-фон (`transform: translateY(scrollY * 0.3)`)
5. `IntersectionObserver` для fade-in и count-up
6. CSS-класс `.reveal` + `.reveal-delay-1/2/3/4` для каскадного появления
7. Gradient text на ключевых словах (`background-clip: text` + `-webkit-text-fill-color: transparent`)
8. Hover lift на карточках (`translateY(-4px)` + усиленная тень)
9. Per-product/per-model **слайдер** (vanilla JS, `slider-track` + dots + prev/next)
10. **Lightbox** для фото с keyboard navigation (ESC/←/→)
11. Count-up анимация для статистики (`requestAnimationFrame` + cubic ease)
12. Smooth scroll по якорям с offset под fixed nav
13. Pulse-dot анимация на live-бейджах (`@keyframes pulse`)

**Перед HARD GATE 07b обязательно прогнать:**
```bash
bash "$LANDING_SYSTEM_ROOT/scripts/verify-composed-premium.sh" \
     "<project>/07b_COMPOSED/composed.html"
```

Если хоть одна фича отсутствует — HARD GATE НЕ пройден. Доработать и прогнать снова.

Полный список требований (типографика, mobile, semantics, кнопки, hero-элементы):
см. `docs/standards/premium-07b-checklist.md` — там 13 разделов + анти-паттерны.

## Pre-flight: стиль hint из ui-ux-pro-max

Перед compose прочитай `meta.yaml` для каждого выбранного блока из `selections.yaml`.
Если в meta.yaml есть поле `recommended_styles_ru`, применить соответствующий стиль
через `design-tokens` (CSS-переменные):

```bash
# Пример: если meta.yaml содержит recommended_styles_ru: ["Brutalism"]
# → ищи в ~/.claude/skills/ui-ux-pro-max/data/styles.csv строку Brutalism
# → используй CSS/Technical Keywords для дополнения design-tokens
```

Это необязательно блокирующий шаг — если styles.csv не доступен, пропустить.

## Workflow

1. Валидируй `selections.yaml`:
   ```bash
   python3 skills/block-composition/scripts/validate-selections.py 07a_WIREFRAME/selections.yaml
   ```
2. Запусти end-to-end composer:
   ```bash
   python3 skills/block-composition/scripts/compose-blocks.py \
       --project "$PWD" \
       --library "$LANDING_SYSTEM_ROOT/block-library"
   ```
3. **Премиум-верификация (обязательно):**
   ```bash
   bash "$LANDING_SYSTEM_ROOT/scripts/verify-composed-premium.sh" \
        "$PWD/07b_COMPOSED/composed.html"
   ```
   Если exit code ≠ 0 — доработай composed.html по
   `docs/standards/premium-07b-checklist.md` и прогони снова. **Не сообщай об
   успехе и не предлагай HARD GATE, пока verify не вернёт 0.**
4. Создай `composed-explained.md` (RU) — что собрано, какие фичи добавлены.
5. Создай `composed-mobile-preview.html` — iframe iPhone + iPad для глазной
   проверки на mobile (согласно памяти пользователя — preview обязателен).
6. Сообщи путь к `composed.html` пользователю + краткий summary.
7. Не делай больше ничего — финальный визуал (фото, иконки, инфографика) добавит PR-B/PR-C.

## CRITICAL

Если `selections.yaml` ссылается на блок, которого нет в `catalog.yaml` — STOP, сообщи пользователю.

## Tools

Read, Write, Bash.
