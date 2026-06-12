---
slug: 07b-composed
type: stage
name: "07b — Composed HTML"
stage: "07b"
tags: [compose, html, design-tokens, premium, placeholder, wireframe]
inputs: [05-dizayn-sistema, 07-prototip, landing-wireframe]
outputs: [07b_COMPOSED/composed.html, 07b_COMPOSED/composed-mobile-preview.html, 07b_COMPOSED/composed-explained.md, 07b_COMPOSED/block-injection-log.md]
gates: [verify-composed-premium]
pre_reqs: [05-dizayn-sistema, 07-prototip, landing-wireframe]
related: [landing-compose, block-composer, landing-photos, landing-visuals, landing-build]
sources: ["template/07b_COMPOSED/README.md"]
updated: 2026-05-26
---

# 07b — Composed HTML

## Что делает

Этап собирает предфинальный цветной макет лендинга: берёт дизайн-токены из этапа 05, тексты и CTA из прототипа и wireframe, подставляет их в блоки через `block-composition`. Там, где будут реальные фото, иконки и инфографика, остаются явные слот-заглушки с описанием. Результат — `composed.html` — это практически финальный лендинг, которому не хватает только визуальных ассетов.

## Когда вызывается

Запускается командой `/landing-compose` (или через `landing-orchestrator`) после того, как пользователь утвердил дизайн-систему (этап 05) и выбрал варианты блоков в wireframe (07a). Без `selections.yaml` из wireframe и без готового прототипа этап не стартует.

## Вход → выход

**Вход:** утверждённая дизайн-система (`tokens.json`, CSS), результат wireframe (`selections.yaml`), тексты из `prototype.md` и `07-kontent`.

**Выход:** `composed.html` (desktop-макет с токенами и текстами), `composed-mobile-preview.html` (iframe iPhone/iPad), `composed-explained.md` (объяснение решений), `block-injection-log.md` (лог подстановок).

## Чем закрывается этап (gates)

- **verify-composed-premium** — скрипт `scripts/verify-composed-premium.sh` проверяет наличие всех 13 обязательных интерактивных фич (parallax, glassmorphism, slider, lightbox, count-up, reveal-on-scroll, gradient-text и др.) по чеклисту `docs/standards/premium-07b-checklist.md`. HARD GATE: exit code ≠ 0 блокирует переход к этапу 08.

## Failure modes

- Скрипт `verify-composed-premium.sh` возвращает ненулевой код — одна или несколько из 13 фич отсутствуют или реализованы формально; нужна доработка `composed.html`.
- `selections.yaml` из wireframe не найден или не положен в `07a_WIREFRAME/` — compose не может определить выбранные варианты блоков.
- Дизайн-токены не импортированы: `tokens.json` отсутствует или CSS-переменные не применены — макет рендерится без брендинга.
- Слоты для фото/иконок не размечены явно — PR-B (photos) и PR-C (visuals) не смогут заменить заглушки автоматически.
- Мобильный preview (`composed-mobile-preview.html`) не создан — нет возможности визуально проверить адаптив до этапа 08.

## Related

- [[landing-compose]] — slash-команда, которая запускает этот этап
- [[block-composer]] — агент, собирающий блоки и инжектирующий токены
- [[landing-photos]] — PR-B: заменяет photo-слоты реальными изображениями
- [[landing-visuals]] — PR-C: заменяет icon/infographic-слоты сгенерированными ассетами
- [[landing-build]] — следующий этап после approve 07b