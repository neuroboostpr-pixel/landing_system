---
type: stage
name: stage-07b-composed
sources: ["template/07b_COMPOSED/README.md"]
updated: 2026-05-25
triggers: []
stage: "07b"
uses: ["landing-compose", "premium-07b-checklist", "landing-wireframe", "landing-photos", "landing-visuals", "landing-orchestrator"]
tags: ["composed", "html", "design-system", "prototype", "placeholder", "premium"]
---

# Этап 07b — Composed HTML

## Что делает

Собирает итоговый цветной макет лендинга: накладывает дизайн-систему на структуру прототипа, подставляет реальные тексты и CTA, оставляет явные placeholders для фото, иконок и инфографики, которые появятся позже.

## Когда вызывать / в каком этапе

Запускается командой `/landing-compose` после того, как утверждены:
- этап 07a (wireframe с выбором вариантов блоков),
- этап 05 (design-system с токенами).

Является пред-финальным этапом визуала. После него идут PR-B (фото, 07c) и PR-C (иконки/инфографика, 07d), которые заменяют placeholders на реальные ассеты.

## Что на вход / на выход

**Вход:**
- `07a_WIREFRAME/selections.yaml` — выбранные варианты блоков
- `tokens.json` — дизайн-токены из design-system
- `prototype.md` / `prototype.yaml` — тексты и CTA из прототипа

**Выход:**
- `composed.html` — desktop-сборка с токенами и текстами
- `composed-mobile-preview.html` — iframe-превью под iPhone/iPad
- `composed-explained.md` — описание решений на русском
- `block-injection-log.md` — лог подстановок по блокам

## Hard Gate — обязательно

Этап не считается закрытым, пока не пройдена проверка:

```bash
bash "$LANDING_SYSTEM_ROOT/scripts/verify-composed-premium.sh" \
     "$PWD/07b_COMPOSED/composed.html"
```

`composed.html` обязан соответствовать **13 premium-фичам** из `docs/standards/premium-07b-checklist.md`: parallax, glassmorphism, slider, lightbox, count-up, reveal-on-scroll, gradient text и другие. Если `exit code ≠ 0` — доработать и прогнать снова.

**Эталон-референс:** `~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html` — 1757 строк, ~130 KB, все 13 фич, реальные фото. При сомнениях «достаточно ли премиум» — сравнить с эталоном.

## Связанные концепты

- [[landing-compose]] — slash-команда, запускающая сборку composed.html
- [[landing-wireframe]] — предыдущий этап (07a), поставляет selections.yaml
- [[premium-07b-checklist]] — стандарт качества с 13 обязательными фичами и анти-паттернами
- [[landing-photos]] — следующий этап (07c), заменяет photo-placeholders на реальные фото
- [[landing-visuals]] — следующий этап (07d), заменяет icon/infographic-placeholders
- [[landing-orchestrator]] — управляет последовательностью этапов и hard gate

## Источник

- `template/07b_COMPOSED/README.md`