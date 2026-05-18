# 07b Composed

Цветной макет с наложенной дизайн-системой и реальными текстами/CTA из прототипа.
Места для финального визуального контента (фото/иконки/инфографика) показаны
как явные placeholders с описаниями слотов.

## Артефакты

- `composed.html` — desktop сборка
- `composed-mobile-preview.html` — iframe iPhone + iPad для глазной проверки
- `composed-explained.md` — что собрано и почему (на русском)
- `block-injection-log.md` — лог что куда подставлено

## Premium quality bar — НЕ ПРОПУСКАТЬ

Каждый `composed.html` ДОЛЖЕН соответствовать стандарту:

📋 **`landing-system/docs/standards/premium-07b-checklist.md`**

В нём 13 разделов и 13 обязательных интерактивных фич (parallax, glassmorphism,
slider, lightbox, count-up, reveal-on-scroll, gradient text и т.д.) +
анти-паттерны, которые делать НЕЛЬЗЯ.

**Перед HARD GATE 07b обязательно прогнать:**

```bash
bash "$LANDING_SYSTEM_ROOT/scripts/verify-composed-premium.sh" \
     "$PWD/07b_COMPOSED/composed.html"
```

Если exit code ≠ 0 — HARD GATE НЕ пройден. Доработать composed.html и прогнать
снова.

## Эталон-референс

`~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html` —
1757 строк, ~130 KB, все 13 premium-фич, реальные фото. Когда сомневаешься,
«достаточно ли премиум» — открой эталон и сравни.

Этот артефакт — пред-финальный. Финальный визуал добавит PR-B (Photo Pipeline)
и PR-C (Icon/Infographic generators).
