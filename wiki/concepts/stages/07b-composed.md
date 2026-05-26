---
type: stage
name: stage-07b-composed
sources: ["template/07b_COMPOSED/README.md"]
updated: 2026-05-26
triggers: []
stage: "07b"
uses: ["premium-07b-checklist", "landing-compose", "stage-07a-wireframe", "landing-photos", "landing-visuals", "verify-composed-premium"]
tags: ["compose", "html", "design-tokens", "placeholders", "premium"]
---

# 07b Composed — Цветной макет с дизайн-системой и текстами

## Что делает
Собирает итоговый HTML-макет лендинга, в котором дизайн-система (цвета, шрифты, токены) наложена поверх структуры прототипа, а реальные тексты и CTA подставлены из прототипа. Там, где ещё нет финальных фото, иконок или инфографики, стоят явные placeholders с описанием слота.

## Когда вызывать / в каком этапе
Этап 07b запускается командой [[landing-compose]] после того, как пройден и утверждён этап 07a (интерактивный wireframe с выбором вариантов блоков). Пользователь должен явно подтвердить выбор вариантов в `07a_WIREFRAME/selections.yaml`, только тогда оркестратор переходит к 07b.

## Что на вход / на выход

**Вход:**
- `07a_WIREFRAME/selections.yaml` — выбор вариантов блоков из wireframe
- Дизайн-токены из этапа 05 (`tokens.json`)
- Тексты и CTA из `prototype.md` (этап 07a)

**Выход:**
- `composed.html` — основная desktop-сборка
- `composed-mobile-preview.html` — iframe-превью для iPhone и iPad
- `composed-explained.md` — описание принятых решений на русском языке
- `block-injection-log.md` — лог подстановок по блокам

## Требования к качеству (HARD GATE)

`composed.html` обязан пройти проверку скриптом:

```bash
bash "$LANDING_SYSTEM_ROOT/scripts/verify-composed-premium.sh" \
     "$PWD/07b_COMPOSED/composed.html"
```

Стандарт описан в `docs/standards/premium-07b-checklist.md` — 13 разделов и 13 обязательных интерактивных фич: parallax, glassmorphism, slider, lightbox, count-up, reveal-on-scroll, gradient text и другие. Пока `verify-composed-premium.sh` возвращает ненулевой exit code — этап не закрыт.

Эталон для сравнения: `~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html` (1757 строк, ~130 KB, все 13 premium-фич, реальные фото).

## Место в пайплайне

Этап 07b — предфинальный визуальный артефакт. После него подключаются:
- [[stage-07c-photos]] (PR-B) — заменяет photo-placeholders реальными фото клиента
- [[stage-07d-visuals]] (PR-C) — заменяет icon/infographic-placeholders AI-генерацией

## Связанные концепты
- [[landing-compose]] — команда, генерирующая composed.html
- [[premium-07b-checklist]] — стандарт качества с 13 обязательными фичами
- [[verify-composed-premium]] — скрипт проверки перед закрытием HARD GATE
- [[stage-07a-wireframe]] — предыдущий этап, поставляет selections.yaml
- [[landing-photos]] — PR-B, следующий этап: финальные фото
- [[landing-visuals]] — PR-C, следующий этап: иконки и инфографика

## Источник
- `template/07b_COMPOSED/README.md`