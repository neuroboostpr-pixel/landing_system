# Project Lending — CLAUDE Instructions

Это папка одного **проекта-лендинга**, созданная из template мастер-системой landing-system.

## Контекст

Ты находишься в проекте, который должен пройти **13 этапов workflow**:

| # | Папка | Этап |
|---|---|---|
| 00 | `00_БРИФ/` | Бриф проекта (ниша, KPI, ЦА) |
| 01 | `01_КОНТЕКСТ/` | Снепшот данных о нише, ЦА, конкурентах |
| 01a | `01a_АНАЛИЗ_НИШИ/` | Анализ ниши, типа бренда, конкурентов |
| 02 | `02_МАТЕРИАЛЫ_КЛИЕНТА/` | Фото, видео, отзывы клиента |
| 03 | `03_РЕФЕРЕНСЫ/` | Визуальные референсы + мудборд |
| 04 | `04_БРЕНД/` | Бренд-кит с трассировкой источников |
| 05 | `05_ДИЗАЙН-СИСТЕМА/` | DESIGN.md (единый источник истины токенов) |
| 06 | `06_СТЕК/` | Плагины, библиотеки, иконки, шрифты |
| 07 | `07_КОНТЕНТ/` | Финальные тексты под блоки лендинга |
| 08 | `08_КОД/` | WP-тема, Gutenberg-блоки, ACF |
| 09 | `09_ДЕПЛОЙ/` | Конфиг, скрипт, лог деплоев на Бегет |
| 10 | `10_QA/` | Чек-листы, скриншоты, отчёты |
| 11 | `11_АНАЛИТИКА/` | Я.Метрика, цели, события, UTM |
| 12 | `12_SEO/` | Ключи, мета, Schema.org, sitemap |

> Канонический порядок этапов (включая подэтапы 03b/07a/07c–07f/08b) —
> `landing-system/config/stages.yaml` (single source of truth).

## Главный агент

`landing-orchestrator` ведёт через все 13 этапов. На каждом этапе:
1. Дёргает специализированных агентов (см. master-system `agents/`)
2. Генерирует визуальный артефакт (`.html` preview в соответствующей папке)
3. **HARD GATE**: ждёт явного утверждения от пользователя перед переходом на следующий этап

## Правила

1. **Никогда не пропускай HARD GATE.** Не идём на этап N+1 без утверждения этапа N.
2. **Все артефакты идут в свою номерную папку.** Никаких файлов в корне проекта (кроме CLAUDE.md, README.md, .env, deploy.sh).
3. **TDD при разработке кода темы:** тесты (PHPUnit/Pest) идут в `08_КОД/wp-theme/tests/`.
4. **Один проект = один WordPress = один поддомен.** Изоляция строгая.
5. **Я.Директ-копии** делаются через мастер-команду `/landing-clone`, не вручную.
6. **Premium 07b — обязательный стандарт.** Каждый `composed.html` должен соответствовать `landing-system/docs/standards/premium-07b-checklist.md`. HARD GATE 07b не закрывается без exit 0 от `verify-composed-premium.sh`.

## Premium 07b — стандарт качества composed.html

Этот пункт критичен — без него лендинги получаются «средние», а не уровня эталона.

**Эталон-референс:** `~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html`
(1757 строк, ~130 KB, реальные фото).

**Стандарт (обязательно к прочтению перед сборкой):**
`landing-system/docs/standards/premium-07b-checklist.md`

**Обязательный минимум (verify v2):** токены в `:root`, `clamp()`, движение,
hover, `prefers-reduced-motion`, OG/favicon/theme-color/шрифты, БЕЗ эмодзи в заголовках.

**Интерактивные фичи (рекомендации — под потребность места, см. design-elements-rules.md):**

1. CSS-переменные `:root` (никакого хардкода цветов)
2. `clamp()` для крупной типографики
3. Glassmorphism sticky nav (`backdrop-filter: blur`)
4. Parallax hero-фон
5. `IntersectionObserver` для fade-in и count-up
6. Класс `.reveal` + delay-каскад
7. Gradient text на ключевых словах
8. Hover lift на карточках
9. Per-product vanilla-JS слайдер
10. Lightbox с keyboard navigation (ESC/←/→)
11. Count-up анимация для статистики
12. Smooth scroll с offset под fixed nav
13. Pulse-dot на live-бейджах

**Перед HARD GATE 07b прогнать:**
```bash
bash "$LANDING_SYSTEM_ROOT/scripts/verify-composed-premium.sh" \
     "$PWD/07b_COMPOSED/composed.html"
```

Если exit ≠ 0 — доработать и прогнать снова. Не сообщать пользователю об
успехе, пока verify не вернёт 0.

**Анти-паттерны (запрещено):**
- ❌ Эмодзи как «иконки» в production-блоках
- ❌ Хардкод цветов в коде блоков (только `var(--...)`)
- ❌ `font-size: 48px` без `clamp()`
- ❌ Слайдер «4 картинки в ряд» вместо настоящего слайдера
- ❌ `<a target="_blank">` вместо lightbox
- ❌ jQuery/Swiper/AOS — только vanilla
- ❌ Скрывать блоки на mobile через `display: none` — стекируй

## Полезные команды

**Доступно сейчас (Phase 1):**
- `/landing-status` — на каком ты этапе

**Будут доступны (Phase 2+, после реализации):**
- `/landing-references` — перезапустить этап 03
- `/landing-deploy` — задеплоить на Бегет
- `/landing-rollback v1.0` — откат к версии
- `/landing-clone` — А/Б-копия лендинга (Phase 5)

## Источник правды

Все системные правила и архитектура: см. spec-документ в master-system (`landing-system/docs/superpowers/specs/`).

## Reserved body classes (lp-preview-panel)

These class prefixes are reserved by the `lp-preview-panel` plugin:

- `body.theme-<id>` — palette axis. CSS tokens live under each block.
- `body.hero--<id>` — hero variant axis. Theme controls visibility per block.

Do NOT add or remove these classes from theme code. The plugin's JS owns them.
For hero variants, keep both DOM subtrees rendered and toggle visibility via
`body.hero--<id>` selectors in CSS. Non-active hero assets must use
`loading="lazy"`.
