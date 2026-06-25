---
slug: block-composer
type: agent
name: "Block Composer — сборщик composed.html"
stage: "07b"
tags: [compose, html, design-tokens, prototype, premium, collage]
triggers: [landing-compose]
inputs:
  - 07_ПРОТОТИП/prototype-*.yaml
  - 05_ДИЗАЙН-СИСТЕМА/moods/{mood}/objects.yaml
  - 05_ДИЗАЙН-СИСТЕМА/moods/{mood}/palette.css
  - 05_ДИЗАЙН-СИСТЕМА/moods/{mood}/metrics.css
  - 05_ДИЗАЙН-СИСТЕМА/moods/{mood}/typography.css
  - 05_ДИЗАЙН-СИСТЕМА/moods/{mood}/motion.css
  - 07b_COMPOSED/build-spec.md
outputs:
  - 07b_COMPOSED/composed.html
  - 07b_COMPOSED/composed-mobile-preview.html
  - 07b_COMPOSED/structure-check.md
  - 07b_COMPOSED/composed-explained.md
  - 07b_COMPOSED/collage-plan.md
pre_reqs: [07-prototip, 05-dizayn-sistema, 06-stek, 07-kontent]
related:
  - landing-compose
  - stage-execution-protocol
  - premium-07b-checklist
  - design-system-generator
  - prototype-importer
  - 07b-composed
  - 07c-photos
  - 07d-visuals
  - landing-go
sources: ["agents/block-composer.md"]
updated: 2026-06-22
confidence: {triggers: low}
---

# Block Composer — сборщик composed.html

## Что делает

Агент рисует финальный HTML-макет лендинга (`07b_COMPOSED/composed.html`) в reference-driven режиме — без подбора готовых блоков из библиотеки. Берёт структуру и тексты из активного прототипа (`prototype-*.yaml`, `active: true`) дословно и 1:1, а вид (цвета, шрифты, кегли, эффекты) — из дизайн-системы проекта, собранной из референса клиента. Визуальные заглушки для фото, иконок и инфографики остаются: их заполнят PR-B (`/landing-photos`) и PR-C (`/landing-visuals`). По завершении запускает премиум-верификацию и не закрывает этап, пока `verify-composed-premium.sh` не вернёт exit 0.

## Когда вызывается

Вызывается командой `/landing-compose` (скилл `landing-compose`) после того, как этапы 05 (дизайн-система), 06 (стек), 07a (прототип разобран) и 07 (контент) закрыты и одобрены пользователем. Harness-хук `enforce_stage_gate.py` физически блокирует запись в файлы этапа, если предшественники не закрыты.

## Вход → выход

**Вход:** активный `prototype-*.yaml` (флаг `active: true`), `build-spec.md` (ТЗ — маппинг контента на роли ДС), `objects.yaml` / `palette.css` / `metrics.css` / `typography.css` / `motion.css` из папки нужного муда дизайн-системы.

**Выход:** `composed.html` (цветной макет с реальными текстами и видимыми плейсхолдерами), `composed-mobile-preview.html` (iframe iPhone+iPad), `structure-check.md` (поблочная сверка, должна заканчиваться `STRUCTURE_MATCH: PASS`), `collage-plan.md` (анализ блоков по глубине коллажа), `composed-explained.md` (краткое описание на русском), опционально `.stage-decisions/07b_composed.md` (самостоятельные решения агента).

## Failure modes

- **Нет активного прототипа** — файл не найден или `active: true` не выставлен; агент не может определить структуру и останавливается.
- **Галлюцинация структуры** — агент добавил блок или элемент, которого нет в прототипе; гейт `structure_check_md` падает (`STRUCTURE_MATCH: FAIL`).
- **Хардкод цветов / размеров** — прямые hex-значения или числа вне `var()` нарушают гейт `tokens_only_colors`; `verify_tokens.py` вернёт ошибки.
- **Отсутствие премиум-фич** — одна или несколько из 13 обязательных фич пропущены; `verify-composed-premium.sh` возвращает exit != 0, этап не закрывается.
- **Изменённый или выдуманный текст** — любое «улучшение» заголовка или добавление нового смысла без явного разрешения пользователя нарушает гейты `content_preserved` и `no_invented_text`.
- **Предшественник не закрыт** — попытка записать файл при незакрытом этапе 05/06/07 блокируется harness-хуком со сообщением «Stage gate enforcement».

## Related

- [[landing-compose]] — скилл-точка входа, вызывает этого агента
- [[stage-execution-protocol]] — обязательный протокол pre-flight перед любым Write/Edit
- [[premium-07b-checklist]] — definition of done: 13 премиум-фич, без которых этап не закрыть
- [[design-system-generator]] — создаёт дизайн-систему (05), которую читает агент
- [[prototype-importer]] — разбирает прототип (07a), из которого берётся структура
- [[07b-composed]] — этап pipeline, который закрывает этот агент
- [[07c-photos]] — следующий этап: подставляет реальные фото в плейсхолдеры
- [[07d-visuals]] — следующий этап: подставляет иконки и инфографику
- [[landing-go]] — оркестратор, диспатчит агента в нужный момент конвейера