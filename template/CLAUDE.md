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
