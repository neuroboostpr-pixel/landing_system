# Visual Requirements Artifact — Design Spec

**Status:** Draft
**Date:** 2026-05-06
**Builds on:** [`2026-05-06-niche-analysis-design.md`](2026-05-06-niche-analysis-design.md)
**Stage affected:** `01a_АНАЛИЗ_НИШИ` (новый артефакт), читатели — этапы 02, 03, 08

---

## 1. Цель и проблема

### Проблема

В пилотном прогоне на `lixiang-dubai` обнаружился системный провал: на проде вышел premium-автомобильный лендинг со стоковой ночной дорогой Дубая в Hero. Маркетолог квалифицировал результат как «дешманский». Технически ошибки не было — `client-assets-collector` собрал что было у клиента, `wp-builder` подставил Pexels-stock как fallback, `gate-check` не имел оснований что-либо запретить.

Корневая причина: **визуальные требования никак не зафиксированы**. Никто из агентов не знает «премиум-автодилеры в Hero показывают машину студийно, а не stock-cityscape», и не имеет места это записать. `niche-analysis.md` фиксирует позиционирование (что говорим), но не фиксирует визуальный язык (что показываем).

### Цель

Добавить в этап `01a_АНАЛИЗ_НИШИ` новый артефакт `visual-requirements.md`, который:
- Определяет визуальный язык лендинга (Hero focal point, фотостиль, product treatment, фон, red flags) на основе типа ниши и конкурентного анализа
- Является контрактом для downstream-агентов: `client-assets-collector` (брифинг клиенту по фото), `moodboard-composer` (поиск референсов), `references-curator` (отбраковка), `wp-builder` (sanity-check ассетов)
- Использует data-driven подход (справочник по категориям + derive из competitors.yaml), а не «угадывание»

### Принцип

`niche-analyst` пишет artifact автоматически в zero-touch режиме (как и остальные artifacts этапа 01a). При нехватке данных — `[ДОПУЩЕНИЕ]` и пониженный confidence. Категория ниши классифицируется на основе встроенного справочника; если не подходит — default-шаблон + пометка.

---

## 2. Артефакт `visual-requirements.md`

Markdown, на русском (как и остальные artifacts этапа), 250–400 слов, читается за 2 минуты.

### Структура

```markdown
# Визуальные требования: <Название клиента/проекта>

> Тип ниши: <category-key из niche-visual-rules.yaml>
> Тип бренда: 1 | 2 | 3
> Дата: YYYY-MM-DD
> Источник: 00_БРИФ/brief.md, 01_КОНТЕКСТ/context.md, 01a_АНАЛИЗ_НИШИ/competitors.yaml

## 1. Hero focal point
**Что в центре первого экрана:** product | environment | person | abstract
**Композиция:** <правило процентов кадра, фон, что не показывать>

## 2. Photography style
studio | lifestyle | documentary | journalistic
**Почему:** <обоснование на основе типа ниши и анализа конкурентов>

## 3. People in frame
yes | no | optional
**Если yes — кто и зачем:** <…>

## 4. Product treatment в каталоге/услугах
studio | context | detail | hybrid
**Описание:** <как показываются модели/услуги в блоке «Каталог» или эквиваленте>

## 5. Background palette
**Допустимые фоны:** studio neutral | dark premium | warm interior | outdoor | abstract (нужное)
**Запрещённые:** 3–5 явных запретов

## 6. Red flags для этой ниши
- ❌ <запрет 1> — <почему: ссылка на конкурента или категорийное правило>
- ❌ <запрет 2>
- ❌ <запрет 3>
- ✅ <предпочтение 1>
- ✅ <предпочтение 2>
- ✅ <предпочтение 3>

## 7. Источники правил
- Справочник: `config/niche-visual-rules.yaml` → category `<key>`
- Derive из `competitors.yaml`: <какие конкуренты повлияли и как>
- [ДОПУЩЕНИЕ] (если есть): <…>
```

### Пример (lixiang-dubai)

```markdown
# Визуальные требования: LiXiang Dubai

> Тип ниши: premium_automotive
> Тип бренда: 2 (региональный)
> Дата: 2026-05-06

## 1. Hero focal point
**Что в центре:** product
**Композиция:** Машина занимает 50–70% кадра, фон — нейтральный
(studio neutral или тёмный premium-фон). Никаких городских пейзажей,
никаких highway-shots, никаких off-road сцен.

## 2. Photography style
studio
**Почему:** В категории premium-electric-SUV в ОАЭ Mercedes EQS, BMW iX,
Tesla Model X — все используют студийные shots или близко к ним. Stock
cityscape backgrounds — сигнал cheap dealer, противоречит позиционированию.

## 3. People in frame
optional
**Если yes:** только family-сцены в интерьере, не водительские sport-shots.

## 4. Product treatment в каталоге
studio
**Описание:** Каждая модель — на нейтральном или тёмном premium-фоне,
3/4-ракурс или прямой профиль. Без landscape под колёсами.

## 5. Background palette
**Допустимые:** studio neutral, dark premium, warm interior
**Запрещённые:**
- Stock cityscape (looks cheap)
- Highway driving shots (generic, дилерские шаблоны)
- Off-road dramatic landscapes (Range Rover territory)
- Sport-lifestyle (Tesla/Zeekr territory)

## 6. Red flags для этой ниши
- ❌ Pexels-stock cityscape в Hero — главная ловушка для китайских EV-дилеров,
  моментально снижает воспринимаемый ценник
- ❌ Cool minimalism с холодным освещением — поляна BMW iX
- ❌ Stark monochrome / tech-flexing UI — поляна Tesla
- ❌ Off-road landscapes — поляна Range Rover
- ✅ Studio shots на нейтральном или тёмном фоне
- ✅ Detail shots premium-материалов (Nappa, OLED, ambient lighting)
- ✅ Family-interior moments (royal seating, panoramic roof)

## 7. Источники правил
- Справочник: `config/niche-visual-rules.yaml` → `premium_automotive`
- Derive из competitors.yaml: visual_notes BMW iX (холодный минимализм →
  избегать), Tesla Model X (stark monochrome → избегать), Range Rover
  (dramatic landscapes → избегать), Hongqi (dark + gold lux — есть риск
  сходства, отстраиваемся через family-warmth).
```

---

## 3. Справочник `config/niche-visual-rules.yaml`

### Расположение и формат

Файл живёт в `config/niche-visual-rules.yaml`. Читается агентом `niche-analyst` и любыми downstream-инструментами (валидаторами, редакторами артефакта).

### Стартовый набор категорий (MVP)

4 категории + `default`:

```yaml
schema_version: 1

categories:
  premium_automotive:
    description: "Премиум-автодилеры (EV, гибриды, luxury ICE)"
    examples: ["BMW dealer", "Mercedes dealer", "Lixiang Dubai", "Tesla showroom"]
    hero_focal: product
    hero_composition: "Машина 50–70% кадра, фон — нейтральный или тёмный premium. Без городских пейзажей и driving shots."
    photography: studio
    people: optional
    people_note: "Если есть — family-интерьерные сцены, не sport-водительские"
    product_treatment: studio
    background_allowed:
      - studio_neutral
      - dark_premium
      - warm_interior
    universal_red_flags:
      - "Stock cityscape backgrounds (cheap dealer signal)"
      - "Highway driving shots (generic dealership template)"
      - "Off-road dramatic landscapes (Range Rover territory)"
      - "Sport-lifestyle shots (Tesla/Zeekr territory unless brand is sport-positioned)"
    universal_preferences:
      - "Studio shots с нейтральным или тёмным premium-фоном"
      - "Interior detail shots premium-материалов"
      - "Family moments внутри салона (если family-positioned brand)"

  local_services:
    description: "Локальные услуги: ремонт, бурение, монтаж, мастера"
    examples: ["бурение скважин", "ремонт квартир", "натяжные потолки", "клининг"]
    hero_focal: person_or_process
    hero_composition: "Реальный человек делает работу или готовый результат. Не stock-актёры."
    photography: documentary
    people: yes
    people_note: "Реальная команда клиента, а не stock smiling actors"
    product_treatment: context
    background_allowed:
      - real_workplace
      - finished_result
      - geo_local
    universal_red_flags:
      - "Stock smiling actors в касках (low trust signal)"
      - "Generic abstract icons в Hero вместо реальных людей/процесса"
      - "Tools/equipment вне контекста использования"
      - "Photoshop-составные коллажи"
    universal_preferences:
      - "Real team photos с лицами"
      - "Before/after или process shots"
      - "Geo-cues локального рынка (виды конкретного города/района)"

  professional_services:
    description: "Профессиональные услуги: медицина, право, консалтинг, образование"
    examples: ["частная стоматология", "адвокатский кабинет", "психолог", "репетитор-онлайн"]
    hero_focal: person_or_environment
    hero_composition: "Портрет эксперта или среда профессии. Trust signal на первом месте."
    photography: lifestyle_or_studio
    people: yes
    people_note: "Реальный эксперт/команда, не stock business meeting"
    product_treatment: hybrid
    background_allowed:
      - real_office
      - real_clinic
      - portrait_studio
      - documentary_moment
    universal_red_flags:
      - "Stock 'business meeting' photos"
      - "Generic handshakes"
      - "Suit-and-tie cliche shots"
      - "Stock medical actors (особенно для клиник)"
    universal_preferences:
      - "Real expert portraits с подписями (имя, регалии)"
      - "Environment, signaling competence (реальная клиника, реальный кабинет)"
      - "Documentary moments из работы"

  b2c_consumer:
    description: "B2C-товары: e-commerce, FMCG, товары через лендинги"
    examples: ["косметика DTC", "одежда", "электроника", "БАДы"]
    hero_focal: product_or_usage
    hero_composition: "Продукт в использовании или hero shot. Lifestyle-контекст допускается."
    photography: lifestyle_or_studio
    people: optional
    people_note: "Если есть — diverse, authentic, не stock-модели"
    product_treatment: context_or_studio
    background_allowed:
      - studio_neutral
      - lifestyle_context
      - in_use
    universal_red_flags:
      - "Pure abstract gradients без продукта"
      - "Mock UI с fake данными (для физических товаров)"
      - "Чрезмерно ретушированные модели"
    universal_preferences:
      - "Продукт в реальном использовании"
      - "Diverse, authentic модели если люди в кадре"
      - "Размер/масштаб продукта понятен"

  default:
    description: "Шаблон по умолчанию когда категория не определена"
    hero_focal: product_or_person
    hero_composition: "Понятный focal point. Без stock-подделок."
    photography: documentary_or_studio
    people: optional
    product_treatment: hybrid
    background_allowed:
      - studio_neutral
      - relevant_context
    universal_red_flags:
      - "Stock photos без relevance к нише"
      - "Generic abstract gradients вместо контента"
      - "Mismatch между обещанием и визуалом"
    universal_preferences:
      - "Authentic content над stock"
      - "Focal point должен быть понятен за 1 секунду"
```

### Расширение справочника

Когда появляется проект, не подходящий ни под одну категорию:
1. Агент использует `default` + пометка `[ДОПУЩЕНИЕ] категория не в справочнике`
2. После approval лендинга разработчик системы добавляет новую категорию в `niche-visual-rules.yaml` с примерами и правилами
3. Категории в backlog: `medical_clinic`, `restaurant`, `real_estate`, `b2b_saas`, `beauty_salon`, `fitness`, `education_courses`

Не добавляем эти категории сейчас (YAGNI — реальных проектов в этих нишах ещё не было).

---

## 4. Алгоритм агента (расширение `niche-analyst`)

В существующий алгоритм `niche-analyst` (см. [niche-analysis-design.md §4.2](2026-05-06-niche-analysis-design.md)) добавляется **шаг 9** перед записью артефактов:

### Шаг 9: Визуальные требования

```
9.1. Классификация категории:
     - На основе бренда/продукта/категории из брифа сопоставить с
       categories[].examples в config/niche-visual-rules.yaml
     - Если совпадение явное (Lixiang Dubai → premium_automotive) → берём
       category_key
     - Если неоднозначное (например, элитный дантист — это
       professional_services или premium consumer?) — выбираем по тому,
       что доминирует в брифе/contexte
     - Если нет совпадения — category_key = default,
       пометка "[ДОПУЩЕНИЕ] категория не в справочнике"

9.2. Базовые правила:
     - Скопировать из categories[category_key]: hero_focal,
       hero_composition, photography, people, product_treatment,
       background_allowed, universal_red_flags, universal_preferences

9.3. Derive из конкурентов:
     - Прочитать competitors.yaml, поле visual_notes каждой записи
     - Для записей role=direct и role=local_competitor найти
       повторяющиеся визуальные коды (≥2 конкурента упоминают похожее)
       → добавить в red_flags как "занятая поляна <имя_кода>: <конкуренты>"
     - Найти gaps (визуальный язык, который никто не использует, но
       уместен по типу ниши) → добавить в preferences как
       "доступный gap: <описание>"
     - Для role=manufacturer и role=local_dealer (особенно если у
       клиента global brand) — отметить визуальные коды как
       "наследовать" в preferences

9.4. Запись в visual-requirements.md:
     - Заполнить разделы 1–6 по схеме
     - Section 7 заполнить со ссылками на справочник и конкретные
       записи competitors.yaml
     - Если есть [ДОПУЩЕНИЕ] — выписать в Section 7 явно

9.5. Sanity-check:
     - В Section 6 должно быть минимум 3 ❌ и 3 ✅
     - Каждый ❌ должен иметь обоснование (категорийное или конкурент)
     - Если меньше — агент дополняет из справочника
```

### Tools

`niche-analyst` уже использует Read, Write, WebSearch, Firecrawl. Дополнительно — нужно читать `config/niche-visual-rules.yaml`. Это всё ещё Read, новых tool-разрешений не нужно.

---

## 5. Контракты с downstream-агентами

### `client-assets-collector` (этап 02)

**Что читает:** `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — Sections 1, 2, 3, 4, 6.

**Зачем:** при сборе материалов клиента агент не запрашивает «дайте фото моделей» абстрактно, а запрашивает конкретно: «нам нужны студийные фото машин на нейтральном фоне, family-интерьерные сцены приветствуются; не нужны driving-shots и cityscape-фоны».

**Изменение в `agents/client-assets-collector.md`:** добавить секцию «Inputs from earlier stages» со ссылкой на `visual-requirements.md` и инструкцией использовать его при формировании запроса клиенту.

### `moodboard-composer` (этап 03)

**Что читает:** Sections 1, 2, 3, 5, 6.

**Зачем:** определяет визуальный язык референсов. Если Section 6 говорит «Stock cityscape — red flag», агент не сохраняет такие референсы.

**Изменение в `agents/moodboard-composer.md`:** дополнить существующую «Inputs from earlier stages» секцию (уже добавили в Task 9 предыдущего плана) ссылкой на visual-requirements.md.

### `references-curator` (этап 03)

**Что читает:** Section 6 (Red flags).

**Зачем:** при оценке предложенного референса (от пользователя или от moodboard-composer) сравнивает с red flags. Если референс попадает в запрет — отвергает со ссылкой на конкретный пункт visual-requirements.

**Изменение:** в `agents/references-curator.md` дополнить контракт.

### `wp-builder` (этап 08)

**Что читает:** Sections 1, 4, 5.

**Зачем:** sanity-check ассетов перед сборкой темы:
- Если Section 1 говорит `hero_focal: product`, а в `02_МАТЕРИАЛЫ_КЛИЕНТА/` единственный hero-кандидат имеет имя файла `cityscape-bg.jpg` или метаданные `landscape` — warning в build log
- Fallback-картинки в коде темы (если кто-то добавляет в `block-hero.php` дефолтное изображение) — должны соответствовать требованиям; запрещено фоллбекать на Pexels stock без проверки
- Code review во время сборки: grep по теме на признаки запрещённых паттернов из Section 5

**Изменение:** в `agents/wp-builder.md` добавить раздел «Visual sanity-checks» с алгоритмом.

### `gate-check` для этапа 01a

Добавить hard_check на наличие `visual-requirements.md` в `config/stage-gates.yaml`:

```yaml
"01a_niche_analysis":
  hard_checks:
    - id: visual_requirements_md
      type: file_exists
      path: "{project}/01a_АНАЛИЗ_НИШИ/visual-requirements.md"
      required: true
      fix_hint: "niche-analyst agent creates this"
```

(Существующие 4 hard_checks остаются.)

---

## 6. Backward compatibility

Существующие проекты:

- `lixiang-dubai`: этап `01a` имеет статус `skipped` (после миграции). Hard-checks для skipped не запускаются. Если пользователь захочет добавить `visual-requirements.md` в существующий lixiang-dubai — это делается вручную или через перевод 01a в `in_progress`. Не блокирует существующий деплой.
- Любые другие legacy-проекты: миграция через `migrate-state-add-01a.sh` (уже существует) — статус `skipped`, hard-checks не валидируют.

Новые проекты после реализации этого спека: `visual-requirements.md` обязателен, `niche-analyst` создаёт его автоматически в шаге 9.

---

## 7. Файлы (что создаётся/меняется)

### Новые
- `config/niche-visual-rules.yaml` — справочник
- `tests/phase-niche/test-visual-rules.bats` — тесты на справочник (yaml валидный, обязательные поля присутствуют, у каждой категории есть `universal_red_flags` минимум 3 элементов и `universal_preferences` минимум 3 элементов)
- `tests/phase-niche/fixtures/visual-requirements-valid.md` — пример для тестов
- `skills/niche-analysis/scripts/validate-visual-requirements.py` — валидатор формата визуальных требований (опционально для MVP, может остаться на следующую итерацию)

### Модифицируемые
- `agents/niche-analyst.md` — добавить шаг 9 в алгоритм, обновить раздел Outputs
- `agents/client-assets-collector.md` — Inputs from earlier stages с ссылкой на visual-requirements
- `agents/moodboard-composer.md` — дополнить существующий Inputs-блок
- `agents/references-curator.md` — дополнить
- `agents/wp-builder.md` — добавить раздел Visual sanity-checks
- `config/stage-gates.yaml` — добавить hard_check для visual-requirements.md
- `template/01a_АНАЛИЗ_НИШИ/README.md` — упомянуть 4-й артефакт
- `tests/phase-niche/test-niche-stage.bats` — расширить (новые тесты на наличие visual-requirements.md в ожидаемых артефактах)

---

## 8. Acceptance criteria

- ✅ В новом проекте после `/landing-niche` в папке `01a_АНАЛИЗ_НИШИ/` появляется 4 файла, включая `visual-requirements.md` на русском
- ✅ `visual-requirements.md` имеет 7 разделов в правильной структуре
- ✅ Section 6 содержит минимум 3 ❌ и 3 ✅, каждый с обоснованием
- ✅ Если категория из бритого классифицируется в одну из 4 готовых (`premium_automotive`, `local_services`, `professional_services`, `b2c_consumer`) — universal_red_flags и universal_preferences берутся из справочника
- ✅ Если категория не классифицируется — используется `default` + явная пометка `[ДОПУЩЕНИЕ]`
- ✅ Минимум 1 red flag в Section 6 явно ссылается на конкретного конкурента из `competitors.yaml` («поляна BMW iX», «поляна Range Rover» и т.п.)
- ✅ `gate-check.sh --stage 01a_niche_analysis` проходит ТОЛЬКО если все 5 hard_checks (включая visual_requirements_md) green
- ✅ Existing проекты (lixiang-dubai) не падают из-за нового hard_check (через `skipped` статус)
- ✅ Bats-тесты проверяют yaml валидность и схему справочника

---

## 9. Out of scope

- ML/CV-классификация изображений (определять «cityscape vs studio» по содержимому файла) — слишком дорого для MVP
- UI для маркетолога/клиента для редактирования visual-requirements — артефакт остаётся markdown
- Автоматическая миграция lixiang-dubai с генерацией visual-requirements.md — делается вручную, если потребуется
- Категории справочника `medical_clinic`, `b2b_saas`, `restaurant`, `real_estate`, `beauty`, `fitness`, `education` — добавляются по мере появления реальных проектов
- Версионирование справочника `niche-visual-rules.yaml` (мигрировать старые `visual-requirements.md` при изменении категории) — пока schema_version: 1, миграции не требуется
- Автогенерация HTML-preview для visual-requirements.md (как у brand-kit.html) — markdown достаточно для MVP

---

## 10. Открытые вопросы (закрыты решениями inline)

1. **Один артефакт или yaml + md?** — md, потому что он для людей и для агентов одновременно. yaml-структуру можно вытащить позже, если понадобится программный доступ к полям.
2. **Кто пишет — niche-analyst или новый агент?** — `niche-analyst`, шаг 9. Не множим агентов ради одного артефакта.
3. **Где справочник — в репо системы или в плагине?** — в репо системы (`config/niche-visual-rules.yaml`). Команда расширяет его коллективно.
4. **Что с lixiang-dubai визуалом?** — это отдельная фиксация (заменить hero-bg на studio-shot машины), не входит в этот спек. Этот спек — про систему, не про ремонт конкретного проекта.
