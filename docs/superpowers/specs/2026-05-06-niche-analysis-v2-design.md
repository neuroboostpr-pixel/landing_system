# Niche Analysis v2 — Positioning Modes & Market Profile

**Status:** Draft
**Date:** 2026-05-06
**Supersedes** (частично): [`2026-05-06-niche-analysis-design.md`](2026-05-06-niche-analysis-design.md), [`2026-05-06-visual-requirements-design.md`](2026-05-06-visual-requirements-design.md)
**Stage affected:** `01a_АНАЛИЗ_НИШИ`
**Implementing agent:** `niche-analyst` (расширяется)

---

## §1. Цель и проблема

### Проблема

Текущая v1 этапа `01a` пишет `positioning.md` в одном универсальном формате (core promise + 1–2 угла отстройки + tone of voice + чего избегать). На реальном пилоте `lixiang-dubai` обнаружились две системные проблемы:

**Проблема A — рациональная отстройка не работает в premium-нишах.** В `lixiang-dubai` агент выбрал угол «1421 km — three times the range of typical EV». Маркетолог отверг: для premium-автомобилей в ОАЭ покупатель выбирает не запас хода, а **статус и тактильное ощущение** (кожа, экраны, royal seating). Маркетинговая литература это подтверждает: «чем выше цена, тем эмоциональнее решение» (Nielsen, MBLM). Один универсальный формат `positioning.md` структурно не отличает эмоциональный режим от рационального.

**Проблема B — структура лендинга не зависит от типа бренда.** Глобальному бренду (Audi) не нужен блок «Brand story» — он узнаваемый. Региональному (lixiang) нужен короткий нарратив доверия. Локальному без бренда (бурение скважин) — обязательно «о компании», команда, кейсы. Сейчас все проекты получают один и тот же набор блоков от `wp-builder`.

**Проблема C — цена в позиционировании учитывается в абсолюте, а не относительно рынка.** AED 250k — это «дорого» в Воронеже и «средне-доступно» в Дубае. Игрушка за 1kk ₽ — это не «дорогая игрушка», а другая категория product (collector statement piece). Без рыночного контекста режим позиционирования выбирается неверно.

### Цель v2

Расширить этап `01a` так, чтобы агент:
1. Собирал **рыночный профиль** (6 параметров, включая accessibility tier на основе медианного дохода региона)
2. Классифицировал **режим позиционирования** (`rational` / `emotional_aspiration` / `trust_authority` / гибрид) по матрице параметров
3. Заполнял **один из трёх шаблонов** `positioning.md` соответствующего режима
4. Генерировал **карту структуры лендинга** (`landing-structure.md`), которая зависит от типа бренда + режима позиционирования
5. Все downstream-агенты (brand-architect, content-writer, wp-builder) уважали выбранную структуру и режим

### Принцип

Zero-touch остаётся: агент сам собирает рыночные данные, сам классифицирует режим, сам пишет артефакты. При неоднозначности — `[ДОПУЩЕНИЕ]` с пометкой confidence.

---

## §2. Что меняется в этапе 01a

### Артефакты этапа (после v2)

| # | Файл | Статус | Назначение |
|---|---|---|---|
| 1 | `niche-analysis.md` | существующий | Нарратив для человека (обновляется — добавляется секция о режиме и market-profile) |
| 2 | `competitors.yaml` | существующий | 15–25 конкурентов (без изменений) |
| 3 | **`market-profile.md`** | **новый** | 6 параметров рыночного профиля |
| 4 | `positioning.md` | **переписан** | StoryBrand-style по выбранному режиму (3 разные формы) |
| 5 | **`landing-structure.md`** | **новый** | Карта блоков лендинга |
| 6 | `visual-requirements.md` | существующий | Визуальные правила (учитывает выбранный режим — обновление) |

Всего **6 артефактов** вместо текущих 4.

### Алгоритм агента (12 шагов)

```
1. Парсинг входов (как сейчас)
2. Язык и регион поиска (как сейчас)
3. Классификация типа бренда: 1/2/3 (как сейчас)
4. (новый) Рыночный профиль → market-profile.md
5. Сбор конкурентов (как сейчас, с учётом profile для подбора алтернатив для luxury_status)
6. Скрейп конкурентов (как сейчас)
7. (новый) Классификация режима позиционирования (по матрице из §4)
8. (изменён) Позиционирование по шаблону выбранного режима → positioning.md
9. (новый) Карта структуры лендинга → landing-structure.md
10. Визуальные требования (с учётом режима) → visual-requirements.md
11. Самопроверка через 5 валидаторов
12. Hand-off в landing-orchestrator
```

---

## §3. Артефакт `market-profile.md` (новый)

### Назначение

Машиночитаемое описание рынка: цена в относительной системе координат, цикл принятия решения, единица решения, регуляция, эмоциональная нагрузка, культурный контекст. Используется для:
- Выбора режима позиционирования (§4)
- Адаптации структуры лендинга (§7)
- Уточнения визуальных требований (§8 модификация)

### Структура

Markdown с явными типизированными полями. Формат:

```markdown
# Рыночный профиль: <Название>

> Дата: YYYY-MM-DD
> Регион: <страна/город>

## 1. Accessibility tier
**Tier:** utility_essential | mass_consumer | mid_premium | premium | luxury_status | ultra_luxury

**Обоснование:**
- Цена клиента/категории: <X> в <локальной валюте>
- Медианный доход региона: <Y> / месяц (источник: <URL>)
- Соотношение: <X / Y> месячных доходов
- Сравнение с медианной ценой в категории: <Z×>

**Что это значит для позиционирования:** <1–2 предложения о том, как tier влияет на режим>

## 2. Consideration cycle
**Тип:** impulse | short | medium | long | very_long

**Обоснование:** Категория и средний цикл выбора (от первого касания до покупки).

**Что это значит:** <hook стратегия — мгновенный emotional vs deep narrative>

## 3. Decision unit
**Тип:** individual | family | corporate

**Обоснование:** Кто принимает решение (один человек, семья с consensus, B2B-stakeholders).

**Что это значит:** <как адаптировать tone и блоки лендинга>

## 4. Regulated category
**Регулируется:** yes | no

**Если yes — какие требования:** <лицензии, сертификаты, обязательные disclosure>

**Что это значит:** <насколько обязательны trust-сигналы>

## 5. Emotional load
**Уровень:** low | medium | high

**Обоснование:** Насколько эмоционально нагружена покупка (свадьба/медицина/благотворительность = high; продукты/бытовая химия = low).

**Что это значит:** <на каком уровне StoryBrand-проблемы говорить — external/internal/philosophical>

## 6. Cultural context
**Регион:** <страна/город>
**Ключевые культурные особенности рынка:**
- <статус-код этого рынка: открытый/скромный/демонстративный>
- <отношение к иностранным брендам>
- <релевантные локальные привычки потребления>

**Что это значит:** <как культура корректирует тон и визуал>

## 7. Сводная рекомендация режима
На основе параметров 1–6 — предварительная рекомендация режима позиционирования:
**Predicted mode:** rational | emotional_aspiration | trust_authority | hybrid:<X>+<Y>

(Окончательный выбор фиксируется в `positioning.md` после анализа конкурентов.)

## 8. Источники и допущения
- WebSearch queries использованные для accessibility_tier: <list>
- Регион + медианный доход источник: <URL>
- [ДОПУЩЕНИЕ] (если есть): <…>
```

### Алгоритм заполнения параметра 1 (accessibility tier) — самый сложный

```
4a.1 Найти медианный месячный доход региона:
     - WebSearch: "median household income <region> <year>"
     - WebSearch: "average salary <region>" (fallback если медианы нет)
     - Если оба не дают результата — взять «GDP per capita / 12» как грубую оценку
     - Записать значение + URL источника в market-profile.md

4a.2 Найти медианную цену в категории:
     - Из competitors.yaml — взять поле price_range всех direct/local_competitor
     - Если у клиента есть цена в брифе — использовать её. Если нет —
       взять медиану конкурентов как proxy для цены клиента.
     - Если категория не имеет регулярной цены (услуги-под-проект) —
       зафиксировать [ДОПУЩЕНИЕ] и взять «средний чек проекта» из брифа

4a.3 Сопоставить:
     ratio = client_price / median_monthly_income

     Шкала tier:
       utility_essential: ratio < 0.05  (до 5% месячного дохода)
       mass_consumer:     0.05 ≤ ratio < 0.30
       mid_premium:       0.30 ≤ ratio < 2.0   (до 2 зарплат)
       premium:           2.0 ≤ ratio < 12     (2–12 зарплат)
       luxury_status:     12 ≤ ratio < 60      (1–5 годовых доходов)
       ultra_luxury:      ratio ≥ 60           (>5 годовых, доступ <1%)

4a.4 Sanity-check:
     - Если категория сама по себе luxury (Hermès, Bentley, ультра-яхты) —
       но ratio выходит низким (например потому что регион супер-богатый
       и медианный доход высокий) — переопределить через категорийный признак
       («это luxury категория глобально → tier=luxury_status»)
     - Если ratio даёт luxury_status, но категория явно массовая —
       пометить [ДОПУЩЕНИЕ] и понизить confidence
```

### Шкала accessibility_tier — что значит для режима

| tier | Доминирующий режим | Почему |
|---|---|---|
| `utility_essential` | `rational` | Покупка по необходимости, выбор по цене |
| `mass_consumer` | `rational` или `trust_authority` | Цена/качество vs «можно ли довериться» |
| `mid_premium` | `trust_authority` или `rational` | Стрейч-покупка, нужно обосновать |
| `premium` | `emotional_aspiration` | Статус и эмоция начинают доминировать |
| `luxury_status` | **только `emotional_aspiration`** | Рацио уже не работает |
| `ultra_luxury` | **только `emotional_aspiration`** | Statement piece, не функция |

### Валидатор `validate-market-profile.py`

- Все 8 секций присутствуют (regex per section header)
- accessibility_tier — один из 6 разрешённых значений
- consideration_cycle — один из 5
- decision_unit — один из 3
- regulated — yes/no
- emotional_load — low/medium/high
- Section 7 содержит явный `Predicted mode:` с одним из 4 значений

---

## §4. Классификация режима позиционирования (шаг 7 алгоритма)

### Три режима

**`rational`** — продажа через функциональный benefit.
- Job statement → Desired outcomes → Metrics → Functional benefit ladder
- Подходит для: B2B-SaaS, утилитарные услуги, дешёвые товары, тех-инструменты
- Tone: factual, specific, ROI-driven
- Пример: «Бурим скважины глубиной до 80 м, гарантия точки бурения»

**`emotional_aspiration`** — продажа через статус/эмоцию/принадлежность.
- StoryBrand 7-part: Character / Problem (3 уровня) / Guide / Plan / CTA / Success / Failure
- Подходит для: premium consumer, luxury, lifestyle, fashion, premium авто
- Tone: aspirational, sensory, identity-led
- Пример: «Кожа Nappa и тишина бизнес-класса. Твой путь — твой стандарт.»

**`trust_authority`** — продажа через доверие и снятие риска.
- Authority signals → Social proof tiers → Process transparency → Risk reversal
- Подходит для: медицина, право, финансы, премиум-услуги, локальные мастера
- Tone: confident, transparent, evidence-based
- Пример: «15 лет частной практики, 2400 успешных операций, лицензия №…»

### Гибрид

Когда одного режима недостаточно. Записывается как `hybrid:<primary>+<secondary>`. Примеры:
- Премиум-клиника: `hybrid:trust_authority+emotional_aspiration` (доверие первично, эмоция вторична)
- Премиум-DTC косметика: `hybrid:emotional_aspiration+rational` (эмоция первична, ингредиенты как поддержка)
- Дорогой курс/образование: `hybrid:trust_authority+rational` (авторитет автора + ROI)

В шаблоне `positioning.md` выбирается **primary** режим, **secondary** добавляется как поддерживающие блоки.

### Матрица выбора (упрощённая)

```
Параметры:                                    Доминирующий режим:
─────────────────────────────────────────────────────────────────
accessibility_tier=utility_essential       → rational
accessibility_tier=mass_consumer           → rational | trust_authority
                                             (regulated=yes → trust)
accessibility_tier=mid_premium             → trust_authority | rational
                                             (high emotional_load → +emotional)
accessibility_tier=premium                 → emotional_aspiration
                                             (regulated=yes → +trust)
accessibility_tier=luxury_status           → emotional_aspiration
accessibility_tier=ultra_luxury            → emotional_aspiration

regulated=yes                              → +trust_authority в hybrid
emotional_load=high                        → +emotional_aspiration в hybrid
decision_unit=corporate                    → +rational в hybrid
consideration_cycle=impulse                → +emotional (быстрый hook)
consideration_cycle=very_long              → +trust (deep proof)

brand_type=1 (глобальный)                  → меньше brand story, режим
                                             решается по tier категории
brand_type=3 (локальный)                   → +trust_authority almost always
```

### Override-индикаторы из брифа

Слова в брифе/контексте, которые усиливают режим:
- → `rational`: «экономия», «гарантия», «дешевле», «KPI», «срок», «ROI», «эффективность»
- → `emotional_aspiration`: «премиум», «эксклюзив», «статус», «династия», «безупречный», «culture»
- → `trust_authority`: «сертификат», «опыт», «отзывы», «лицензия», «врач», «лет на рынке», «клиники Москвы»

Если индикаторы конфликтуют с матрицей — фиксируется `[ДОПУЩЕНИЕ]`, выбирается доминирующий маркер с пометкой confidence.

### Оверрайд от пользователя

Если пользователь/маркетолог в брифе явно говорит «давим на статус и кожу» — это перевешивает любую матрицу. Фиксируется в market-profile.md → секция «Override от клиента».

---

## §5. Шаблоны `positioning.md` — три формы

### 5.1 Шаблон `rational`

```markdown
# Позиционирование: <Название>

**Mode:** rational

## Job statement
Когда <ситуация>, я хочу <функциональная задача>, чтобы <измеримый результат>.

Пример (бурение скважин):
«Когда мне нужна вода на участке, я хочу заказать бурение, чтобы получить
гарантированный объём воды с понятными сроками и ценой.»

## Desired outcomes (3–5)
- <измеримый результат 1>
- <измеримый результат 2>
- ...

## Metrics that matter
| Метрика | Наш показатель | Бенчмарк ниши |
|---|---|---|
| <…> | <…> | <…> |

## Functional benefit ladder
1. **Feature:** <конкретная характеристика>
   **Benefit:** <что это даёт клиенту>
   **Outcome:** <измеримый результат для клиента>
2. ...

## Чего избегать
- Эмоциональные обещания без подтверждения
- Аспирационные claim'ы (для rational это разрушает доверие)
```

### 5.2 Шаблон `emotional_aspiration` (StoryBrand 7-part)

```markdown
# Позиционирование: <Название>

**Mode:** emotional_aspiration

## 1. Character (Hero — клиент)
Кто покупатель не как сегмент, а как живой человек:
- Кто он/она
- Как себя видит
- Чего хочет от жизни (не от продукта)

## 2. Problem (3 уровня)
**External (внешняя проблема):** <что физически нужно решить>
**Internal (внутренняя):** <что чувствует, какие frustrations>
**Philosophical (философская):** <почему это несправедливо/не должно быть так>

Пример (lixiang Dubai):
- External: нужен большой семейный SUV в Дубае
- Internal: устал от компромиссов «или статус или семья»
- Philosophical: семья заслуживает лучшего, а технология должна служить ей,
  не наоборот

## 3. Guide (мы, бренд)
Не «мы герои», а «мы тот, кто знает дорогу». Эмпатия + авторитет:
- Empathy statement: «Мы понимаем, что…»
- Authority statement: «Поэтому мы…»

## 4. Plan
3 простых шага клиента:
1. <шаг 1>
2. <шаг 2>
3. <шаг 3>

## 5. Call to Action
- Direct CTA: <главное действие>
- Transitional CTA: <мягкая альтернатива для тех, кто не готов>

## 6. Success vision
Каким станет клиент после покупки. Один абзац яркого описания.

## 7. Failure vision (что потеряет, не купив)
Один абзац — что он упустит. Без давления, через картину.

## Tone of voice
- 3–5 атрибутов

## Чего избегать
- Сухой functional copy в Hero
- Сравнения с конкурентами по цифрам
- Прямые superlatives без emotional attachment
```

### 5.3 Шаблон `trust_authority`

```markdown
# Позиционирование: <Название>

**Mode:** trust_authority

## Authority signals
**Кто мы и почему нам можно доверять:**
- Опыт: <X лет, Y проектов/пациентов/кейсов>
- Регалии: <лицензии, сертификаты, образование, награды>
- Affiliation: <профессиональные сообщества, где состоим>

## Process transparency
Как мы работаем — открыто, по шагам:
1. <шаг 1 с деталью, что клиент получит>
2. <шаг 2>
3. ...

## Social proof tiers
**Tier 1 — Authority figures:** отзывы экспертов индустрии (если есть)
**Tier 2 — Quantified results:** «<X> успешных кейсов», «<Y> лет средняя
длительность отношений с клиентами»
**Tier 3 — Peer reviews:** отзывы клиентов с именами/фото

## Risk reversal
Что снимает страх покупки:
- Гарантия: <…>
- Возврат/refund: <…>
- Бесплатная консультация: <…>

## Чего избегать
- Аспирационные claim'ы без подтверждения (особенно в medical/legal)
- Stock «business meeting» photos
- Generic «happy customers» без конкретных имён
- Цена без объяснения (для trust mode цена раскрывается с context'ом)
```

### Валидатор `validate-positioning.py` (расширяется)

Текущий validator не проверяет режим. Новая версия:
1. Читает `Mode: <режим>` из заголовка positioning.md
2. По режиму выбирает соответствующий чеклист обязательных секций
3. Проверяет наличие всех секций для выбранного шаблона
4. Если режим = `hybrid:X+Y`, проверяет primary шаблон, плюс наличие явного блока «Secondary mode signals»

---

## §6. Артефакт `landing-structure.md` (новый)

### Назначение

Карта блоков лендинга в зависимости от типа бренда + режима позиционирования. Читается `wp-builder` (этап 08) для генерации структуры темы и `content-writer` (этап 07) для распределения контента по блокам.

### Структура

```markdown
# Структура лендинга: <Название>

> Тип бренда: 1 | 2 | 3
> Режим: <mode>
> Дата: YYYY-MM-DD

## Блоки лендинга (в порядке отображения)

| # | Блок | Обязательный? | Цель | Содержание (откуда) |
|---|---|---|---|---|
| 1 | Hero | yes | <главная задача блока> | <что сюда: positioning §3, market-profile cultural> |
| 2 | <…> | yes/optional | <…> | <…> |
| ... | ... | ... | ... | ... |

## Обоснование выбора структуры
<2–4 абзаца: почему именно такие блоки в таком порядке для этого типа бренда + режима>

## Что НЕ включаем (и почему)
- <блок 1>: <почему пропускаем>
- ...

## Контракт с wp-builder
Список template-parts, которые должны быть сгенерированы:
- block-hero.php (всегда)
- <блок>.php
- ...
```

### Шаблонные карты для 9 комбинаций (3 типа бренда × 3 режима)

Не все комбинации одинаково осмысленны, поэтому даются **рекомендуемые карты** для типичных случаев. Агент адаптирует под конкретный проект:

#### Тип 1 (глобальный) + emotional_aspiration
```
Hero (имя бренда + продукт + статус-кадр)
→ Featured Models (без brand story — бренд знают)
→ Lifestyle/Experience block
→ Trust signals (гарантия, сервис)
→ Test Drive / CTA
→ FAQ
→ Footer
```

#### Тип 1 (глобальный) + rational
```
Hero (продукт + ключевая характеристика)
→ Spec table / comparison
→ Use cases
→ CTA
→ Footer
```

#### Тип 2 (региональный) + emotional_aspiration
```
Hero (продукт + emotional hook)
→ Brand short story (1 экран — кто мы и почему мы здесь)
→ Featured Models / Catalog
→ Experience/Lifestyle
→ Trust (warranty, service centre, GCC certified)
→ Test Drive / CTA
→ FAQ
→ Footer
```

#### Тип 2 (региональный) + trust_authority
```
Hero (продукт + ключевой trust-signal)
→ Brand credentials (years, certifications, affiliations)
→ Process transparency
→ Catalog/Models
→ Social proof (отзывы с именами)
→ Risk reversal
→ CTA
→ FAQ
→ Footer
```

#### Тип 3 (локальный) + trust_authority (самый частый case)
```
Hero (фото команды или результата работы + trust hook)
→ About (короткая история компании, лица команды)
→ Process transparency (как мы работаем)
→ Cases / Portfolio
→ Reviews (с фото, именами, датами)
→ Pricing (прозрачное)
→ CTA
→ FAQ
→ Footer
```

#### Тип 3 (локальный) + emotional_aspiration
Редкий случай (например, premium-стилист, авторская кондитерская). Карта:
```
Hero (mood-кадр)
→ About founder (личность, философия)
→ Signature works/services
→ Lifestyle/Experience
→ Trust (авторитет автора)
→ CTA (часто личная — «связаться напрямую»)
→ FAQ
→ Footer
```

#### Тип 3 (локальный) + rational
```
Hero (продукт/услуга + цифра)
→ Что входит (transparent scope)
→ Pricing
→ Process (быстро)
→ FAQ
→ CTA
→ Footer
```

### Адаптация под cultural_context

`landing-structure.md` имеет дополнительную секцию «Cultural adjustments»:
- Например, для арабских/мусульманских рынков → отдельный блок про халяль/семейные ценности
- Для скандинавских → блок про устойчивость
- Для рынков с low trust в новых брендах (Россия, Индия) → усиление trust-блоков

### Валидатор `validate-landing-structure.py`

- Проверяет наличие обязательных секций
- Проверяет, что Mode совпадает с positioning.md
- Проверяет, что в карте блоков обязательно есть Hero, CTA, Footer
- Проверяет, что для Тип 3 + trust_authority обязательно есть About и Reviews

---

## §7. Обновление `visual-requirements.md`

В существующий артефакт добавляется новая секция `## 8. Adaptation per positioning mode`:

```markdown
## 8. Adaptation per positioning mode

**Active mode:** <mode из positioning.md>

**Visual implications:**
- Hero focal point теперь определяется и режимом, не только категорией:
  - rational: продукт + ключевой spec/число
  - emotional_aspiration: lifestyle moment + продукт в контексте, либо
    студийный shot с premium-обработкой
  - trust_authority: лицо человека (founder/expert) или результат работы

- Photography style overrides:
  - emotional_aspiration: lifestyle/editorial допускается, не только studio
  - trust_authority: documentary обязательно, studio только для product
  - rational: studio или product-in-use

- People in frame:
  - emotional_aspiration: yes (target persona в желаемой ситуации)
  - trust_authority: yes (реальные эксперты/команда)
  - rational: optional
```

---

## §8. Контракты с downstream-агентами

### `brand-architect` (этап 04)

Дополнительно к существующему чтению `positioning.md` теперь читает:
- `market-profile.md` — для понимания cultural context, accessibility tier
- `landing-structure.md` — чтобы brand-kit покрывал все необходимые блоки

### `content-writer` (этап 07)

Дополнительно читает:
- `landing-structure.md` — пишет копирайт **по структуре**, не угадывает блоки
- `positioning.md` — теперь в одном из 3 шаблонов, content-writer должен распознать режим и адаптировать тон

### `wp-builder` (этап 08)

Дополнительно читает:
- `landing-structure.md` — генерирует **только те template-parts**, которые есть в карте
- `market-profile.md` — для адаптации поведения (например, accessibility_tier=luxury_status → не показывать price prominently в Hero)

### `seo-optimizer` (этап 12)

Без изменений — читает только `competitors.yaml`.

---

## §9. Изменения в `gate-check.sh` / `stage-gates.yaml`

В блок `01a_niche_analysis` добавляется 4 новых hard_check:

```yaml
      - id: market_profile_md
        type: file_exists
        path: "{project}/01a_АНАЛИЗ_НИШИ/market-profile.md"
        required: true
      - id: market_profile_schema
        type: script
        script: "skills/niche-analysis/scripts/validate-market-profile.py"
        args: ["{project}/01a_АНАЛИЗ_НИШИ/market-profile.md"]
        required: true
      - id: landing_structure_md
        type: file_exists
        path: "{project}/01a_АНАЛИЗ_НИШИ/landing-structure.md"
        required: true
      - id: landing_structure_schema
        type: script
        script: "skills/niche-analysis/scripts/validate-landing-structure.py"
        args: ["{project}/01a_АНАЛИЗ_НИШИ/landing-structure.md"]
        required: true
```

И обновление существующего `validate-positioning.py` (новый — текущей версии нет):

```yaml
      - id: positioning_schema
        type: script
        script: "skills/niche-analysis/scripts/validate-positioning.py"
        args: ["{project}/01a_АНАЛИЗ_НИШИ/positioning.md"]
        required: true
```

Итого: **9 hard_checks** для этапа 01a (вместо текущих 6).

---

## §10. Справочник `config/positioning-modes.yaml` (новый)

Не путать с существующим `niche-visual-rules.yaml`. Этот — про шаблоны позиционирования и матрицу выбора режима.

```yaml
schema_version: 1

modes:
  rational:
    description: "Продажа через функциональный benefit, метрики, ROI"
    template_sections:
      - "Job statement"
      - "Desired outcomes"
      - "Metrics that matter"
      - "Functional benefit ladder"
      - "Чего избегать"
    typical_categories: ["b2b_saas", "utility_services", "tools", "commodity"]

  emotional_aspiration:
    description: "Продажа через статус, эмоцию, identity"
    template_sections:
      - "Character"
      - "Problem (external/internal/philosophical)"
      - "Guide"
      - "Plan"
      - "Call to Action"
      - "Success vision"
      - "Failure vision"
      - "Tone of voice"
      - "Чего избегать"
    typical_categories: ["luxury", "premium_consumer", "lifestyle", "fashion", "premium_automotive"]

  trust_authority:
    description: "Продажа через доверие и снятие риска"
    template_sections:
      - "Authority signals"
      - "Process transparency"
      - "Social proof tiers"
      - "Risk reversal"
      - "Чего избегать"
    typical_categories: ["medical", "legal", "financial", "premium_services", "local_services_high_trust"]

# Матрица предсказания режима по market-profile параметрам
mode_prediction_matrix:
  - if:
      accessibility_tier: ["utility_essential", "mass_consumer"]
      regulated: false
    predict: "rational"

  - if:
      accessibility_tier: ["mass_consumer", "mid_premium"]
      regulated: true
    predict: "trust_authority"

  - if:
      accessibility_tier: ["mid_premium"]
      emotional_load: "high"
    predict: "hybrid:emotional_aspiration+trust_authority"

  - if:
      accessibility_tier: ["premium", "luxury_status", "ultra_luxury"]
      regulated: false
    predict: "emotional_aspiration"

  - if:
      accessibility_tier: ["premium"]
      regulated: true
    predict: "hybrid:trust_authority+emotional_aspiration"

# Override индикаторы из брифа
brief_indicators:
  rational: ["экономия", "гарантия", "дешевле", "KPI", "срок", "ROI", "эффективность", "fixed price", "transparent"]
  emotional_aspiration: ["премиум", "эксклюзив", "статус", "династия", "безупречный", "culture", "lifestyle", "luxury"]
  trust_authority: ["сертификат", "опыт", "отзывы", "лицензия", "врач", "лет на рынке", "клиника", "credentials"]
```

---

## §11. Файлы (что создаётся / меняется)

### Новые
- `config/positioning-modes.yaml` — справочник режимов и матрица
- `skills/niche-analysis/scripts/validate-market-profile.py`
- `skills/niche-analysis/scripts/validate-positioning.py` (новый — раньше positioning не валидировался)
- `skills/niche-analysis/scripts/validate-landing-structure.py`
- `tests/phase-niche/test-positioning-modes.bats`
- `tests/phase-niche/test-validate-market-profile.py`
- `tests/phase-niche/test-validate-positioning.py`
- `tests/phase-niche/test-validate-landing-structure.py`
- `tests/phase-niche/fixtures/market-profile-valid.md`
- `tests/phase-niche/fixtures/positioning-rational-valid.md`
- `tests/phase-niche/fixtures/positioning-emotional-valid.md`
- `tests/phase-niche/fixtures/positioning-trust-valid.md`
- `tests/phase-niche/fixtures/landing-structure-valid.md`
- (и invalid фикстуры для каждого валидатора)

### Модифицируемые
- `agents/niche-analyst.md` — алгоритм 12 шагов вместо 9, новые шаги 4, 7, 9
- `agents/brand-architect.md` — читает `market-profile.md`, `landing-structure.md`
- `agents/content-writer.md` — читает `landing-structure.md`, распознаёт режим
- `agents/wp-builder.md` — генерирует темы по `landing-structure.md`, не догадывается
- `config/stage-gates.yaml` — 4 новых hard_check
- `config/niche-visual-rules.yaml` — добавляются маркеры режимов в категории
- `template/01a_АНАЛИЗ_НИШИ/README.md` — упоминание 6 артефактов
- `tests/phase-niche/test-niche-stage.bats` — новые проверки

---

## §12. Backward compatibility

### Существующие проекты
- `lixiang-dubai` имеет `01a` со статусом `in_progress` (после миграции). 4 артефакта v1 уже есть. Новые 2 артефакта (`market-profile.md`, `landing-structure.md`) — отсутствуют. После реализации v2 — gate-check этапа 01a начнёт фейлить, потому что добавлены 4 новых hard_check.

### Стратегия
**Опция A:** Перевести `lixiang-dubai` в `skipped` для 01a. Плохо — теряем работу, проделанную по визуальным требованиям.

**Опция B (рекомендуется):** Создать миграционный скрипт `scripts/migrate-niche-to-v2.sh`, который:
- Проверяет, есть ли в проекте 4 v1-артефакта
- Если есть — генерирует stub `market-profile.md` и `landing-structure.md` с пометкой `[ДОПУЩЕНИЕ] миграция от v1, требуется ручное заполнение`
- Не блокирует gate-check (stub-артефакты проходят валидаторы по структуре, но содержат предупреждения)
- В positioning.md — добавляет фронтмадду `Mode: legacy_v1` (легитимный режим только для миграции, не для новых проектов)

**Опция C:** На уровне `gate-check.sh` — игнорировать v2-checks для проектов с `state.schema_version: 1`.

Я выберу **B** — миграция через stub. Это и не теряет работу, и не вводит ветвление логики в gate-check.

---

## §13. Acceptance criteria

- ✅ В новом проекте после `/landing-niche` в папке `01a_АНАЛИЗ_НИШИ/` появляется 6 файлов
- ✅ `market-profile.md` содержит 8 секций, accessibility_tier — один из 6 разрешённых значений
- ✅ accessibility_tier рассчитан с явной ссылкой на медианный доход региона (URL источника)
- ✅ `positioning.md` использует один из 3 шаблонов в зависимости от Mode header'а
- ✅ Validator `validate-positioning.py` распознаёт Mode и проверяет шаблон-специфичные секции
- ✅ `landing-structure.md` содержит таблицу блоков с обязательными Hero, CTA, Footer
- ✅ Для Тип 3 + trust_authority в landing-structure.md обязательно есть блоки About и Reviews
- ✅ Все 4 новых hard_check в gate-check.sh проходят
- ✅ Existing проект lixiang-dubai мигрирован через stub без break-checks
- ✅ Bats и pytest зелёные, минимум +12 новых тестов
- ✅ На lixiang-dubai после миграции в v2 (manual smoke) — режим определяется как `emotional_aspiration` (не `rational` как сейчас)

---

## §14. Out of scope

- Автоматическое A/B-тестирование разных режимов на одном проекте (это lifecycle-keeper, не niche-analyst)
- ML-классификация режима (использует только rule-based матрицу + индикаторы)
- Автоматический подбор фотографов/студий для emotional_aspiration shoots
- Полная переработка downstream-агентов под динамическую структуру (контракты обновляются, но wp-builder продолжает использовать существующую систему template-parts; динамическая генерация структуры — отдельный спек)
- Многоязычные шаблоны positioning.md (mode templates пока только русский, английский — backlog)

---

## §15. Размер реализации

Это V2 этапа 01a — большой апгрейд. Реалистично:
- ~18–22 task'a (vs 14 в v1)
- ~6–10 часов inline execution или 1.5–2× через subagent-driven
- 5 новых валидаторов (Python)
- 3 новых markdown-шаблона
- 1 новый yaml-справочник
- Миграция существующих проектов

Рекомендация: реализовывать через subagent-driven для надёжности (большой scope + критическая методика, цена ошибки высокая).
