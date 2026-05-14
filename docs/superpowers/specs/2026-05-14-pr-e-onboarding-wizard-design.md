# PR-E — Onboarding Wizard (Materials Walkthrough)

**Date:** 2026-05-14
**Status:** draft
**Scope:** Interactive `/landing-start` wizard. Объясняет систему новому маркетологу за 2 минуты, создаёт папку проекта, проводит step-by-step по 4 типам материалов с проверкой наличия. Финиширует запуском `/landing-go`.

---

## Problem

Сейчас `/landing-new <slug>`:
- Просто создаёт пустую папку из template (18 пустых директорий)
- Не объясняет что такое landing-system
- Не говорит маркетологу куда что класть
- Папки template не содержат READMEs (кроме 07c_PHOTOS/ и 07d_VISUALS/)
- **Нет папки для логотипов клиента** (04_БРЕНД/ пустая)

Маркетолог открывает 18 папок и не понимает что с этим делать. Текущий PR-D `/landing-go` тоже ничего не подсказывает — он начинает с 07a_prototype, предполагая что прототип уже на месте.

## Goals

1. Команда `/landing-start` — главная точка входа для маркетолога.
2. **3-абзацный онбординг** в начале — что такое landing-system, что произойдёт, сколько раз спросят.
3. **Создание проекта с явным анонсом** — «создаю папку здесь, держи путь».
4. **Step-by-step walkthrough** по 4 типам материалов:
   - Шаг 1: Прототип (обязательно) → `07_ПРОТОТИП/source/`
   - Шаг 2: Фото клиента (рекомендую) → `07c_PHOTOS/inbox/`
   - Шаг 3: Логотип клиента (рекомендую) → `04_БРЕНД/logos/`
   - Шаг 4: Референсы дизайна (опционально) → `03_РЕФЕРЕНСЫ/`
5. **Проверка наличия материалов** на каждом шаге через `wizard-check-materials.py`.
6. **READMEs во всех 18 папках template** — чтобы маркетолог открыв любую папку видел подсказку.
7. **Новая папка `04_БРЕНД/logos/`** в template.
8. После wizard → подсказка `/landing-go`.

## Non-goals

- ❌ Веб-форма wizard (отдельный PR-G позже)
- ❌ Auto-extract brand colors из логотипа (опц. в PR-F)
- ❌ Авто-скачивание референсов с URL (это уже умеет references-curator на этапе 03)
- ❌ Замена `/landing-new` — он остаётся для advanced users
- ❌ Дублирование `landing-onboarding` skill — wizard вызывает её для проверки зависимостей системы

## Decisions log

| # | Решение | Источник |
|---|---|---|
| D1 | `/landing-start` = **главная** точка входа. `/landing-new` помечен как advanced. | "удобно, находит сразу папочки" |
| D2 | Wizard состоит из 4 шагов по материалам (prototype / photos / logos / references). Не больше — не перегружаем. | "рассказывает и кладёт по папкам" |
| D3 | На каждом шаге wizard ждёт «готово» или «пропустить» (для опциональных). | Step-by-step UX |
| D4 | Verification через `scripts/wizard-check-materials.py` — проверяет наличие файлов по шаблону. | Trust-but-verify |
| D5 | Шаг 1 (прототип) hard-required. Без него wizard exit 1. | Pipeline requirement |
| D6 | Шаги 2-4 — optional, можно «пропустить». Без них pipeline продолжает работать (AI fallback). | Backward compat с PR-B/C/D |
| D7 | Каждая папка template получает русский README. Формат как `07c_PHOTOS/README.md` из PR-B. | "удобно находит" |
| D8 | Новая папка `template/04_БРЕНД/logos/` с README. Туда кладутся `logo.svg/png`, `logo-dark.svg`, `favicon.png`. | Logos требуются клиенту |
| D9 | Wizard в конце предлагает запустить `/landing-go`. Не запускает сам — даёт пользователю передохнуть. | UX — не overwhelm |
| D10 | Onboarding текст 3 коротких абзаца — без воды. | "немного действий, без усложнений" |

---

## Architecture

### Поток `/landing-start`

```
Step 0: Pre-flight checks (codex installed via install-codex.sh)
   │
   ▼
Step 1: Welcome + 3-paragraph onboarding text
   │
   ▼
Step 2: Ask for project slug (kebab-case)
   │
   ▼
Step 3: Create folder ~/Lendings/<slug>/ from template
   │  (uses existing landing-project-init skill under the hood)
   │
   ▼
Step 4: Material walkthrough (4 steps)
   ├─ Step 4.1: Prototype — REQUIRED
   ├─ Step 4.2: Photos — recommended
   ├─ Step 4.3: Logos — recommended
   └─ Step 4.4: References — optional
   │
   ▼
Step 5: Summary + suggest /landing-go
```

### Компоненты PR-E

| # | Файл | Действие | Ответственность |
|---|---|---|---|
| 1 | `commands/landing-start.md` | NEW | Slash command, frontmatter + dispatches to wizard agent |
| 2 | `agents/landing-onboarding-wizard.md` | NEW | Agent — ведёт диалог, печатает шаги, читает «готово/пропустить», валидирует |
| 3 | `scripts/wizard-check-materials.py` | NEW | Проверяет наличие материалов в папке по шаблону (extension + min count). Возвращает summary JSON |
| 4 | `template/04_БРЕНД/logos/` + README | NEW | Новая папка для логотипов |
| 5 | `template/04_БРЕНД/README.md` | NEW | Объясняет что 04_БРЕНД делает (brand-kit + logos) |
| 6 | `template/00_БРИФ/README.md` | NEW | «автогенерируется из прототипа, не заполняй руками» |
| 7 | `template/01_КОНТЕКСТ/README.md` | NEW | «автогенерируется» |
| 8 | `template/01a_АНАЛИЗ_НИШИ/README.md` | NEW | «генерится niche-analyst или derive-landing-structure» |
| 9 | `template/02_МАТЕРИАЛЫ_КЛИЕНТА/README.md` | NEW | «эта папка legacy — фото клади в 07c_PHOTOS/inbox/» |
| 10 | `template/03_РЕФЕРЕНСЫ/README.md` | NEW | Формат index.yaml + куда класть screenshots/ |
| 11 | `template/05_ДИЗАЙН-СИСТЕМА/README.md` | NEW | «генерится design-system-generator» |
| 12 | `template/06_СТЕК/README.md` | NEW | «генерится stack-planner» |
| 13 | `template/07_КОНТЕНТ/README.md` | NEW | «генерится content-writer из prototype.yaml» |
| 14 | `template/07_ПРОТОТИП/README.md` + `source/README.md` + `source/.gitkeep` | NEW | Главная папка для прототипа, куда класть PDF/MD |
| 15 | `template/07a_WIREFRAME/README.md` | NEW | «генерится /landing-wireframe» |
| 16 | `template/07b_COMPOSED/README.md` | NEW | «генерится /landing-compose» |
| 17 | `template/08_КОД/README.md` | NEW | «генерится wp-builder» |
| 18 | `template/09_ДЕПЛОЙ/README.md` | NEW | «генерится wp-deployer» |
| 19 | `template/10_QA/README.md` | NEW | «генерится qa-auditor» |
| 20 | `template/11_АНАЛИТИКА/README.md` | NEW | «генерится analytics-engineer» |
| 21 | `template/12_SEO/README.md` | NEW | «генерится seo-optimizer» |
| 22 | `tests/phase-pre/` | NEW | Тесты на wizard, materials check, READMEs presence |

**Итого ~10 задач (READMEs пакетно в одну задачу).** Реалистично за сегодня.

### Wizard agent flow (упрощённо)

```
agent landing-onboarding-wizard:
  1. Print welcome text (3 paragraphs)
  2. Ask for slug, validate (kebab-case)
  3. Call landing-project-init skill → создаёт ~/Lendings/<slug>/
  4. Print location: «создал ~/Lendings/<slug>/. Сейчас покажу что куда класть»
  5. Loop через 4 материальных шагов:
     для каждого:
       a. Print step header (ШАГ N ИЗ 4 — <name>)
       b. Print folder path
       c. Print what goes there (с примером)
       d. Wait for «готово» / «пропустить»
       e. If «готово»: run wizard-check-materials.py
          - if PASS: print check summary, next step
          - if FAIL: print what missing, repeat e
       f. If «пропустить»: mark optional, next step (only allowed for steps 2-4)
  6. Print final summary (4 материала: prototype ✅, photos ✅, logos ✅, references ⊘)
  7. Print: «Готов запустить /landing-go? (или подожди)»
```

### wizard-check-materials.py spec

```bash
python3 scripts/wizard-check-materials.py --project <dir> --step <name>
```

`<name>` ∈ `prototype | photos | logos | references`

Output (JSON to stdout):
```json
{
  "step": "prototype",
  "status": "pass" | "fail" | "warn",
  "found": ["prototype.pdf (1.2 MB)"],
  "missing": [],
  "summary": "Найден prototype.pdf"
}
```

Validation rules per step:
- **prototype**: must have `07_ПРОТОТИП/source/prototype.*` (pdf, md, html). FAIL if missing.
- **photos**: count files in `07c_PHOTOS/inbox/**/*.{jpg,jpeg,png,heic}`. WARN if 0, PASS if >= 1.
- **logos**: must have `04_БРЕНД/logos/logo.{svg,png,jpg}` или любой логотип. WARN if 0, PASS if >= 1.
- **references**: check `03_РЕФЕРЕНСЫ/index.yaml` exists и не пустой, или `screenshots/` непустой. WARN if 0, PASS if any.

### Welcome onboarding text (3 paragraphs)

```
👋 Добро пожаловать в landing-system!

Я помогу собрать лендинг от готового прототипа до live сайта на Бегете.
Вся обработка фото, генерация иконок, сборка WordPress-темы и деплой —
автоматически. Тебя я спрошу 5-7 раз за весь процесс: подтверди дизайн,
расставь фотки по слотам, дай Бегет credentials.

Сейчас попрошу тебя:
1. Назвать имя проекта
2. Положить prototype.pdf в нужную папку (обязательно)
3. Положить фото клиента, логотип, референсы (рекомендую)

Готов? Назови короткое имя проекта (например, `stroyka-pro` или `lp-marafon`):
```

### Per-folder README pattern

Каждый template README следует одной структуре:

```markdown
# <Имя папки>

## Что здесь будет

(1-2 строки что в папке появится / что нужно положить)

## Кто это создаёт

(Авто-генерация / Маркетолог руками / Wizard кладёт)

## Когда

(На каком этапе pipeline эта папка заполняется)
```

Пример для `template/04_БРЕНД/logos/README.md`:
```markdown
# 04_БРЕНД/logos/

## Что сюда класть

Логотип клиента:
- `logo.svg` или `logo.png` — основной логотип
- `logo-dark.svg` — версия для светлого фона (опц.)
- `favicon.png` — иконка вкладки 32×32 (опц.)

## Кто кладёт

Маркетолог через /landing-start wizard.

## Если логотипа нет

brand-architect сгенерит текстовый логотип на этапе 04_brand.
```

---

## Step-by-step UX (полный пример)

```
$ /landing-start

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👋 Добро пожаловать в landing-system!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Я помогу собрать лендинг от готового прототипа до live сайта на Бегете.
Вся обработка фото, генерация иконок, сборка WordPress-темы и деплой —
автоматически. Тебя я спрошу 5-7 раз за весь процесс.

Сейчас попрошу тебя:
1. Назвать имя проекта
2. Положить prototype.pdf (обязательно)
3. Положить фото, логотип, референсы (рекомендую)

Назови короткое имя проекта (kebab-case):
> stroyka-pro

📁 Создаю папку: ~/Lendings/stroyka-pro/
   ↓ Копирую template (18 папок с подсказками)
✅ Готово. Открой Finder и убедись что папка появилась.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ШАГ 1 ИЗ 4 — Прототип (ОБЯЗАТЕЛЬНО)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 ~/Lendings/stroyka-pro/07_ПРОТОТИП/source/

Положи туда:
  • prototype.pdf — экспорт из Figma/Tilda/etc
  • Или prototype.md — текстовое описание блоков

Открой папку (Finder → cmd+click), скопируй файл, напиши "готово".

> готово

🔍 Проверяю... ✅ Найден prototype.pdf (1.2 MB)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ШАГ 2 ИЗ 4 — Фото клиента (рекомендую)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 ~/Lendings/stroyka-pro/07c_PHOTOS/inbox/

Внутри 7 подпапок с подсказками — открой и посмотри.
Кратко куда что класть:
  • _свалка/ — если не знаешь, кидай сюда (AI разберётся)
  • портреты_и_команда/ — фото людей
  • процесс_работы/ — мастер за работой
  • объекты_и_продукты/ — готовые работы
  • интерьер_экстерьер/ — офис, цех
  • до_после/ — пары «было → стало»
  • документы_сертификаты/ — дипломы

Если у тебя нет фоток — напиши "пропустить" (я сгенерю через AI).

> готово

🔍 Проверяю... ✅ Найдено 47 фоток
   (5 портретов, 12 процесс, 30 в _свалке)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ШАГ 3 ИЗ 4 — Логотип клиента (рекомендую)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 ~/Lendings/stroyka-pro/04_БРЕНД/logos/

Положи туда:
  • logo.svg или logo.png — основной логотип
  • logo-dark.svg — версия для светлого фона (опц.)
  • favicon.png — иконка вкладки 32×32 (опц.)

Если логотипа нет — напиши "пропустить" (brand-architect сгенерит текстовый).

> готово

🔍 Проверяю... ✅ Найден logo.png (45 KB)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ШАГ 4 ИЗ 4 — Референсы дизайна (опционально)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 ~/Lendings/stroyka-pro/03_РЕФЕРЕНСЫ/

Если у тебя есть лендинги-образцы которые нравятся:
  • Положи URL в index.yaml (формат внутри README)
  • Или скриншоты в screenshots/

Если нет — references-curator подберёт сам по нише.

> пропустить

⊘ Пропускаем — подберу автоматически на этапе 03.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ИТОГ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Прототип: prototype.pdf
✅ Фото: 47 шт
✅ Логотип: logo.png
⊘ Референсы: будут подобраны автоматически

Проект готов к сборке. Запускай:
  /landing-go

Или сделай паузу — оркестратор продолжит с того же места.
```

---

## Error handling

| Сценарий | Поведение |
|---|---|
| Slug не kebab-case (содержит пробелы/CAPS) | Просит ввести заново с примером правильного |
| Папка `~/Lendings/<slug>/` уже существует | Спрашивает: «Использовать существующую?» или «Назови другое имя» |
| `codex` не установлен | Запускает `scripts/install-codex.sh`, потом продолжает |
| Шаг 1 (прототип) — пользователь пишет «пропустить» | Refuse: «Прототип обязательный. Положи файл или прерви wizard через Ctrl+C» |
| `wizard-check-materials.py` падает (Permission denied на папке) | Сообщение об ошибке + инструкция (например chmod) |
| После шага 4 пользователь не хочет /landing-go | Печатает «Когда будешь готов — запусти /landing-go вручную» и завершает |

---

## Testing

| Что | Чем | Сценарий |
|---|---|---|
| `wizard-check-materials.py` prototype | pytest | папка с prototype.pdf → PASS, пустая → FAIL |
| `wizard-check-materials.py` photos | pytest | inbox с 3 jpg → PASS, пустой → WARN |
| `wizard-check-materials.py` logos | pytest | logos/logo.png → PASS, пустой → WARN |
| `wizard-check-materials.py` references | pytest | index.yaml с URL → PASS, пустой → WARN |
| Template READMEs presence | bats | каждая папка template/* имеет README.md |
| `04_БРЕНД/logos/` exists in template | bats | dir present |
| `/landing-start` command file shape | bats | frontmatter + references wizard agent |
| Wizard agent doc shape | bats | frontmatter + 4 step description + step 1 hard-required mention |

**Объём:** ~15 тестов.

---

## Acceptance criteria

- [ ] `/landing-start` запускается и показывает welcome text (3 параграфа)
- [ ] Wizard создаёт `~/Lendings/<slug>/` через landing-project-init
- [ ] Wizard ведёт через 4 шага материалов с верификацией
- [ ] Step 1 (prototype) hard-required
- [ ] Steps 2-4 поддерживают «пропустить»
- [ ] `wizard-check-materials.py` корректно проверяет каждый тип материала
- [ ] Каждая из 18 папок template имеет README.md
- [ ] Новая папка `template/04_БРЕНД/logos/` существует с README
- [ ] После wizard — подсказка `/landing-go`
- [ ] PR-A + PR-B + PR-C + PR-D регрессионные тесты не падают
- [ ] 15+ новых тестов проходят

---

## Dependencies

- Existing `landing-project-init` skill (для создания папки) — не модифицируется
- Existing `install-codex.sh` (PR-D) — вызывается из pre-flight
- Python 3.10+ + PyYAML + Pillow (для image header checks)
- bats для shell тестов

---

## Migration

- Существующие проекты не затрагиваются — PR-E добавляет новую команду + новые READMEs в template
- Существующая команда `/landing-new` остаётся as-is (для advanced users)
- Старые проекты могут запустить `bash scripts/migrate-template-readmes.sh <project>` чтобы получить новые READMEs в свои папки (опционально, не обязательно)

---

## Open questions / future PRs

- **PR-G** — Веб-интерфейс поверх wizard
- **PR-E.1** — Auto-extract brand colors из логотипа (после parsing logo.svg/png)
- **Interactive folder open** — wizard сам открывает Finder/Explorer на нужной папке (для macOS: `open ~/Lendings/<slug>/07_ПРОТОТИП/source/`)
- **Drag-and-drop через terminal** — некоторые терминалы (iTerm2) поддерживают drag-drop файлов как text input
