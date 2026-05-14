# 📸 Photo Selection Guide

**Цель:** Формальное руководство для photo-matcher (PR-B) и любого агента/человека который кладёт фото в слоты лендинга. Это **source of truth** — без него получается рандом.

---

## Принципы

1. **Сначала тип съёмки → потом место**. Не "куда влезет это фото", а "какой тип фото нужен на этом слоте".
2. **Hero / first impression = чистый exterior**. Не interior, не top-down, не detail. Только полная машина в продающем ракурсе.
3. **Slider order**: от общего к частному. Сначала exterior, потом hero context (окружение), потом interior tech, потом lifestyle.
4. **Top-down фотографии — это lifestyle**. НЕ main photo модели. Они показывают «что влезает», «как разместить семью», «cargo capacity» — это вторичные слайды или отдельный showcase-блок.
5. **Identity-safe лица**: реальные фото клиентов / команды — только с разрешением. Inspiration с лицами — НЕ использовать в близком плане, только blur/crop или замена через AI.

---

## Классификация типов фото (для photo-matcher / классификатора)

| Тип | Описание | Куда подходит |
|---|---|---|
| **exterior_studio** | Полная машина в студии (¾ или side profile), neutral bg | Hero (если premium), model card main slot, comparison gallery |
| **exterior_lifestyle** | Машина в реальном окружении (улица, природа, landmark) | Hero (если aspirational), gallery slide 2 (context), CTA backgrounds |
| **exterior_front** | Фронтальный кадр (часто dark, c badge модели) | Model card main (если хорошее качество), tech section |
| **exterior_rear** | Кадр сзади (taillights, trunk closed) | Slider slide 3-4, не main |
| **interior_dashboard** | Передняя панель, экран, руль | Tech section, features-block (если о технологиях), slider slide 3-4 |
| **interior_rear** | Задний салон, entertainment screen, второй ряд | Features-block "comfort", slider slide 4 |
| **interior_detail** | Close-up (door, mirror, badge, control) | Trust section, features small slots, NO main |
| **top_down_lifestyle** | Вид сверху с салоном видимым (ski, beach, family, cargo) | **Отдельный showcase-блок "Lifestyle scenarios"**, slider slide 5 (last) |
| **top_down_tech** | Top-down с overlay (audio waves, sensors, airbags) | Tech/safety section, infographic-style block |
| **lifestyle_people** | Люди вокруг или в машине (живые сцены) | Trust/testimonials section (только client-owned!) |
| **detail_tech** | Камера, mirror display, charging port | Features specific tech sections |
| **sleep_mode** | Кровать-режим, beds inside | Niche feature highlight (отдельная карточка), не main |
| **safety_demo** | Airbags, crash demonstration | Trust/safety section |
| **stock_brand** | Видны brand bagdes (L6/L7/L8/L9/Mega badge) | **Только в соответствующий model slot** |
| **dashboard_apps** | UI cars OS (apps, music, navigation) | Tech features section |

---

## Правила matching по типу блока

### Hero block (любой `category: hero`)

**Required:** `exterior_studio` OR `exterior_lifestyle`. Полная машина, не обрезанная.
**Forbidden:** top-down, close-up, interior. Эти кадры НЕ передают что продукт = автомобиль.
**Fallback if нет:** AI-generate `exterior_lifestyle` под Dubai backdrop.
**object-fit:** `cover` с `object-position: center` — НЕ обрезать машину.

### Model card в gallery (per-model)

**Slot main:** `exterior_studio` модели с этим badge. Если нет — `exterior_studio` с похожим body (помечается `needs_replacement`).
**Slot context (slide 2):** `exterior_lifestyle` модели.
**Slot tech (slide 3):** `interior_dashboard` или `interior_detail`.
**Slot comfort (slide 4):** `interior_rear` (для multi-row моделей).
**Slot lifestyle (slide 5):** `top_down_lifestyle` ОДИН.

### Features block (преимущества)

**Если про tech:** `dashboard_apps` / `interior_dashboard` / `detail_tech` / `top_down_tech`.
**Если про comfort:** `interior_rear` / `sleep_mode`.
**Если про safety:** `safety_demo` / `top_down_tech` overlay (sensors).
**Если про range/efficiency:** `exterior_lifestyle` long road / charging port.
**Если про design:** `exterior_studio` close-up exterior.

### Trust / social-proof block

**Если testimonials:** `lifestyle_people` (client-owned) или AI portraits (с approval).
**Если KPI/числа:** не нужны фото (только цифры в большом размере).
**Если awards/certifications:** scans/icons, не фото.

### Lifestyle scenarios block (если есть)

**Все слоты:** `top_down_lifestyle` различных сценариев — ski, beach, camping, family, cargo. 4-5 шт горизонтальным slider.

### CTA block

**Если accent-bg (full-bleed):** опц. фоновое `exterior_lifestyle` blurred + overlay.
**Если editorial-paper:** студийное фото детали (door open, key handover в Dubai showroom).

### Footer / Contact

Никаких главных фото. Может быть маленький фото офиса/шоурума.

---

## Slider order в model card (правильный)

```
Slot 1 (main, viewport-default):  exterior_studio  ← полная машина
Slot 2:                            exterior_lifestyle ← окружение (Dubai)
Slot 3:                            interior_dashboard ← tech
Slot 4:                            interior_rear OR detail_tech ← comfort/details
Slot 5:                            top_down_lifestyle ← bonus lifestyle scene
```

**Принцип:** «WOW машина → реальная жизнь → внутри → детали → что влезет».

Если slot 5 не имеет фото — не показывать пустой. Просто 4 слайда.

---

## Что делать когда photo нет

Приоритет fallback:

1. **Client photos** — primary, идеальный score
2. **Inspiration photos** (для безопасных слотов: model exterior, tech, lifestyle):
   - Use as-is если визуально подходит и нет распознаваемых брендов в кадре кроме той которая нужна
   - Marker: `source: inspiration_lixiang, needs_replacement: true` в photo-mapping.yaml
   - На лицевой стороне — НЕ показывать "INSP" badge, выглядит непрофессионально
3. **AI-generated через codex `image_gen`** — для:
   - Hero Dubai backdrop с машиной (codex variation client photo + backdrop change)
   - Lifestyle people если identity-safe approved
   - Missing model exteriors (с явным `ai_approved_by_user: true`)
4. **SVG placeholder** — последний resort, только для prototype/draft не для production

---

## Identity-safe правила (повторение PR-B)

- **Реальные клиенты/команда** — только client-owned + согласие
- **Inspiration с лицами** — НЕ использовать close-up. Только blur/crop фоновое
- **AI-generated лица для testimonials** — обязательное `ai_approved_by_user: true` per slot
- **Машины** — реальные модели OK (factual product), badges OK если client = authorized dealer

---

## Mobile vs Desktop фото

- **Desktop hero:** wide landscape (16:9 или 21:9), `object-position: center`
- **Mobile hero:** crop variant (4:5 или 9:16), фокус на машине (lower half)
- В CSS: `<picture>` element с media queries
- Если client photo одна — generate mobile crop через codex (или crop client side в browser)

---

## Этапы pipeline где это применяется

| Стадия | Кто использует guide |
|---|---|
| **07c_photos** (photo-curator) | Классификация client/inspiration photos по этим типам |
| **07c.matcher** | Scoring photo → slot по правилам выше |
| **07c.generator** | Codex `image_gen` промпты используют тип-target в подсказках |
| **07d/07e composed** | inject-content.py подставляет с учётом slot order |
| **08_build** (wp-builder) | mobile/desktop variants через `<picture>` |

---

## Чек-лист правильного выбора фото для слота

Прежде чем подставить photo X в slot Y:

- [ ] Тип фото X соответствует таблице выше для slot Y?
- [ ] Если main slot — это exterior полной машины (не top-down, не close-up)?
- [ ] Identity-safe соблюдён (нет лиц без разрешения)?
- [ ] Source отмечен в photo-mapping.yaml (client/inspiration/ai)?
- [ ] Если inspiration — `needs_replacement: true` помечен для agency follow-up?
- [ ] Mobile crop вариант существует / можно сгенерить?
- [ ] Hero не обрезается на 1366×768 viewport?

---

## Примеры из теста dubai-avto-liza

**Что было неправильно:**
- `l6-main.jpg` = top-down с велосипедом и людьми (тип: top_down_lifestyle) → НЕ должно быть main slot модели
- `l9-main.jpg` = dashboard close-up (interior_dashboard) → НЕ main slot
- `mega-main.jpg` = top-down 4-seat config → должно быть slide 5 not main
- `hero-bg.jpg` = side profile silver (exterior_studio) → ✅ правильный тип, но **обрезается** при отрисовке (object-position fix needed)

**Что должно было быть:**
- L6 main: photo `15-44-16` (front view "理想 L6") — exterior_front с badge
- L9 main: photo `15-44-13` (3 машины в каньоне, badge "Lixiang L9") — exterior_lifestyle
- L7/L8/Mega main: подобрать из inspiration с visible badges (или ai-generate)
- Top-down фото (ski/beach/camping) → отдельный **«Lifestyle scenarios» showcase** или slide 5 each model

---

**Этот guide — обязателен** для photo-matcher (PR-B) и любого agent / human делающего photo assignment. Без него — рандом.
