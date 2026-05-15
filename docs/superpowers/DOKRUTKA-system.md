# 🔧 DOKRUTKA — Системные доработки landing-system

**Источник:** Тест на проекте `dubai-avto-liza` (2026-05-14)
**Контекст:** Это первый полный прогон от прототипа до composed.html на реальном клиентском кейсе. Ниже — **системные** проблемы (не специфичные одному сайту), которые надо встроить в PR-A/B/C/D/E или новые PR.

---

## 🔴 КРИТИЧНЫЕ системные проблемы

### S1. Агенты ОТКЛОНЯЮТСЯ от текста прототипа

**Что произошло:** content-writer на этапе 07_content получил готовый текст из `prototype.yaml` (полные английские блоки от клиента), но **переписал их по-своему**:
- Hero changed: «LiXiang in stock in Dubai with savings from ___» → «Premium Chinese EVs Delivered to Dubai»
- Headlines, taglines, descriptions — все переписаны
- Стиль текста: «authorized dealer» tone → generic «premium» marketing speak

**Почему это критично:**
- Клиент **ожидает свой текст в финале** (он его согласовывал, продумывал тон)
- В прототипе текст — это NOT placeholder, это **финальный copy от клиента**
- Если агент "улучшает" — он ломает доверие и тратит время на правки

**Что должно быть:**
- `content-writer` агент на стадии 07_content должен **сохранять текст из prototype.yaml как есть**, только если явно помечено `[TBD]` / placeholder
- "Улучшения" tone-of-voice — **отдельный опциональный этап** `07_content_polish` с явным opt-in
- В spec PR-A блок prototype.yaml должен иметь поле `text_source: client_final | template_placeholder`, и content-writer уважает first

**Фикс:** обновить `agents/content-writer.md` + `skills/prototype-import/SKILL.md` (добавить text source metadata) + `skills/block-composition/scripts/inject-content.py` (использовать original text как primary)

### S2. Шаги pipeline в неправильном порядке

**Что произошло:** PR-D определил порядок:
```
07a prototype → 07b wireframe → 07c composed → 07d photos + 07e visuals (parallel) → 07f composed final
```

Но НА ПРАКТИКЕ нужно:
```
07a prototype → 07b wireframe → 07c PHOTOS (selection + processing) → 07d composed draft → 07e VISUALS (icons/infographics) → 07f composed final
```

**Логика которая работает:**
1. Прототип → понимаем структуру блоков и какие слоты нужны
2. Wireframe → выбираем макеты (определяем тип/размер фото-слотов)
3. **Photos FIRST** — без фото невозможно сверстать нормально (плейсхолдеры выглядят ужасно, композиция не рассчитана)
4. Только потом — verьмо composed draft с реальными фото в правильных местах
5. Visuals (иконки/инфографика) — поверх готовой композиции
6. Final compose — re-render с всеми ассетами

**Что должно быть:**
- Pipeline в PR-D обновить: photos идут **ДО** первого composed, не после
- Skill `block-composition/SKILL.md` должен явно требовать `selections.yaml` photos на input до compose
- Если photos нет — composed.html явно помечается «DRAFT WITHOUT PHOTOS» (не «final preview»)

**Фикс:** Обновить `agents/landing-orchestrator.md` dispatch table + `config/stage-gates.yaml` + `commands/landing-go.md`

### S3. Codex не используется для фото-обработки

**Что произошло:** Codex CLI установлен, залогинен — но pipeline до него **не дошёл**. На этапе 07c composed я (агент) вручную копировал client photos в assets/. **PR-B photo-curator не вызван**.

**Что должно быть автоматически:**
- photo-curator (PR-B) запускается на стадии 07c (или новый 07c-photos)
- Использует codex vision для классификации каждого client photo (model badge / shot type)
- Auto-matching фото к слотам через codex
- Generation Dubai-adapted variations через codex `image_gen`
- Identity-safe правила enforced

**Почему не сработало в этом тесте:** Я (агент) пошёл вручную, минуя photo-curator skill — потому что user в GUI mode и я тяну работу на себя. Это плохая привычка.

**Фикс:** В agent prompts (curator/orchestrator) **обязательно** dispatch photo-curator на стадии processing, даже если user-mode = GUI. Не делать ручную работу там где skill готов.

### S4. Inspiration photos не задействуются в pipeline

**Что произошло:** В этом тесте мы спарсили **480 inspiration photos** с lixiang.com (236 МБ). НО pipeline их **не использует** — они лежат в `_свалка_inspiration_lixiang/`, никто не классифицирует их и не подставляет когда client photos отсутствуют.

**Что должно быть:**
- photo-matcher (PR-B) при scoring кандидатов учитывает **2 источника**:
  1. Client photos (primary, идеальный score)
  2. Inspiration photos (secondary, lower score, marked `needs_replacement: true`)
- В identity-safe политике: inspiration фото подходят **только если нет client фото и слот не identity-safe** (testimonials/team — generate AI; gallery model shots — OK inspiration)
- В composed.html — inspiration photos выглядят неотличимо от client photos (никаких видимых "INSP placeholder" badges на frontend); только в metadata (photo-mapping.yaml) пометка для agency team

**Фикс:** Обновить `photo-matcher` агент + `selections-validator.py` schema (добавить enum `inspiration_lixiang|client|ai_generated`) + `inject-content.py` (не рендерить INSP badges на live HTML)

### S5-A. Финальное авто-ревью всего сайта (отсутствует stage)

**Что произошло:** После сборки composed.html / final WP-темы — **нет автоматической проверки** что сайт качественный. Маркетолог открывает и сам ищет косяки (placeholder'ы остались, фото не подходят, ссылки сломаны, форма не работает, цены некорректны). Это ровно те ошибки которые мы находим прямо сейчас на dubai-avto-liza.

**Что должно быть:** Новый pipeline stage `10_qa_auto` (расширение существующего 10_qa) или **самостоятельный stage `07g_self_review`** между 07f composed_final и 08 build:

Auto-checks:
1. **Content checks:**
   - Все `[TBD]` помечены и собраны в отчёт «remaining client confirmations»
   - Все фото имеют src (не broken links)
   - Все ссылки валидны (внутренние якоря работают, внешние возвращают 200)
   - Нет дублей текста
   - Spell-check (для English landing — основные ошибки orth)
   - Текст из prototype.yaml сохранён (gate-check S1)

2. **Visual checks:**
   - Hero не обрезается на key viewports (1366×768, 1920×1080, 375×812 mobile)
   - Фото имеют правильный aspect ratio для своего слота
   - Identity-safe слоты не используют AI faces без approval
   - Иконки сгенерированы (нет icon-placeholder)
   - Mobile layout не ломается (нет horizontal overflow)
   - Color contrast соответствует WCAG AA (4.5:1)

3. **Functional checks:**
   - Все формы имеют action или JS handler
   - Все кнопки имеют onclick или href
   - Smooth scroll работает (anchor links → корректные секции)
   - Lightbox/slider/modal работают на основных браузерах
   - Mobile toggle (S8) работает
   - Form validation — email pattern, phone mask

4. **Performance checks:**
   - Lighthouse audit ≥ 90 (Performance/Accessibility/Best Practices/SEO)
   - LCP < 2.5s
   - CLS < 0.1
   - Images optimized (без 5MB JPG)
   - Critical CSS inlined

5. **SEO checks:**
   - Title + meta description present
   - H1 unique
   - OG tags
   - Sitemap.xml + robots.txt
   - Alt text для всех `<img>`

6. **Brand/Identity checks:**
   - Все ссылки идут на правильный домен клиента (нет hardcoded test URLs)
   - Контакты, телефоны, email — соответствуют project-context.yaml
   - Логотипы корректные
   - Currency formatting consistent (везде AED 350,000, не mix с $350K)

**Output:** `10_QA/auto-review-report.html` (визуальный отчёт с pass/fail/warn по каждому пункту) + `10_QA/auto-review-summary.md` (краткое для маркетолога с приоритизированным fix list).

**Если есть критичные fail** — gate-check блокирует 08_build / 09_deploy до фикса.

**Фикс:** Создать `agents/site-auto-reviewer.md` + `skills/site-auto-review/` со всеми чек-листами. Можно использовать Lighthouse через CLI + Playwright для visual diff + simple HTML linters.

### S5-B. Stage интеграций / мессенджеров / form destinations отсутствует

**Что произошло:** В composed.html есть:
- Кнопки `Request a test drive`
- WhatsApp icon в nav
- Form submit
- Footer с контактами

Но **все идут на placeholder'ы** (`#`, `[TBD]`, JS confirmation alert). Нет stage где маркетолог даёт реальные ссылки и они подставляются.

**Что должно быть:** Новый stage `07h_integrations` (или часть 09_deploy) — конкретный этап сбора и подключения:

#### Что собирается на этом stage:

1. **Контакты клиента:**
   - Phone (с UAE country code)
   - WhatsApp business number (часто отличается от phone)
   - Email
   - Address (showroom location)
   - Hours of operation

2. **Мессенджеры (UAE-specific приоритеты):**
   - WhatsApp (CRITICAL для UAE — 90% leads приходит через него)
   - Instagram DM (UAE популярен)
   - Telegram (для русскоязычных в UAE)
   - НЕ WhatsApp в РФ (запрет) — для RU проектов использовать Telegram + VK

3. **Form destinations:**
   - Куда отправляется лид (CRM webhook URL? Email? WhatsApp API?)
   - Какой CRM: AmoCRM / Bitrix24 / HubSpot / Pipedrive / custom
   - Доступ: API key или OAuth
   - Fallback: email на менеджера если CRM down

4. **Кнопки click destinations:**
   - "Request a test drive" → opens form modal OR scrolls to form OR WhatsApp pre-filled message?
   - "Get an offer" per model → WhatsApp с моделью pre-filled?
   - "Model details" → внутренняя страница модели OR scroll к extended section?
   - Phone в nav → `tel:` link
   - Email в footer → `mailto:` link
   - Social icons → правильные URLs

5. **Tracking pixels / analytics:**
   - Yandex Metrica (для русскоязычных проектов)
   - Google Analytics / GA4
   - Meta Pixel (для FB/Insta ads)
   - TikTok pixel
   - Custom events: `track('form_submitted')`, `track('whatsapp_clicked')`

6. **External services:**
   - Google Maps embed для showroom
   - Calendly / встроенный календарь для test drive booking?
   - reCAPTCHA для form (защита от спама)
   - Cookie consent banner (UAE PDPL / GDPR for EU visitors)

#### Сценарий stage 07h_integrations:

```
agent integrations-collector:
  1. Print summary: "На этом этапе подключаем все ссылки и интеграции"
  2. Iterate через category:
     - Контакты: phone? email? whatsapp?
     - CRM: какой? key/webhook?
     - Tracking: yandex/ga/meta? IDs?
     - Maps: address для embed?
  3. Если client не знает / нет sometihng:
     - Fallback strategy:
       - WhatsApp click без message → just open chat
       - Form без CRM → fallback на email
       - Analytics без ID → noop tracking
  4. Validate каждое:
     - WhatsApp link открывается?
     - CRM webhook возвращает 200?
     - GA ID валиден?
  5. Записать в 07h_INTEGRATIONS/integrations.yaml
  6. Перерендерить composed.html — подставить реальные ссылки везде
```

**Output:** `07h_INTEGRATIONS/integrations.yaml` (machine-readable config) + `integrations-explained.md` (Russian explanation для marketing tracking) + `integrations-test.html` (тест-страница где все ссылки кликабельны для проверки маркетологом).

**Фикс:** Новый agent `integrations-engineer` (он есть в landing-orchestrator таблице как stage 08 helper, но не имеет dedicated stage сейчас!) + skill `integrations-setup` + новая папка `template/07h_ИНТЕГРАЦИИ/`.

### S5. Wireframe selections могут "улучшаться" агентом — это ошибка

**Что произошло:** Wireframe выбрал hero block `ru-hero-07-editorial-serif`. Пользователь сделал override → `ru-hero-10-deck-cover`. На этапе composed агент собрал hero **в стилистике deck-cover как просили**. Это правильно.

НО: для form (`ru-cta-07-accent-bg`) я отговорил пользователя и переключил на `ru-cta-06-editorial-paper` без явного override. Это manipuлация — агент НЕ должен переубеждать.

**Что должно быть:**
- Если user явно зафиксировал выбор → агент НЕ предлагает альтернативы (только flag warning если что-то критично)
- "Recommendation" разрешён ДО фиксации
- После фиксации `selections.yaml` агент использует строго что пользователь выбрал

**Фикс:** Обновить `ux-composer` agent + `block-composition` skill — не переоптимизировать после approve

---

## 🟡 ВАЖНЫЕ системные доработки

### S6. Нет документированного guide «как подбирать фото»

**Проблема:** Я (агент) принимал решения о фото ad hoc — топ-даун в hero, exterior в slide5 и т.д. Нет **формального документа** в landing-system который говорит «top-down → lifestyle scenarios block, exterior → model main slot, dashboard → tech section».

**Что должно быть:** Документ `docs/photo-selection-guide.md` (см. отдельный файл) с правилами для разных типов фото и слотов. Photo-matcher агент его читает при scoring.

### S7. composed.html на промежуточных этапах outdated

**Что произошло:** Мы сгенерили composed.html **2 раза** (первая версия — placeholder, вторая — с фото). Старая лежит в `07b_COMPOSED/composed.html` и постоянно открывается user'ом — он видит старое.

**Что должно быть:**
- Versioning: `composed-v1.html`, `composed-v2.html`, символьная ссылка `composed.html` → latest
- ИЛИ archive: `07b_COMPOSED/_archive/composed-2026-05-14-1530.html`, latest всегда composed.html
- Notice banner в outdated файлах: «THIS IS ARCHIVED, latest: composed.html»

**Фикс:** Расширить `compose-blocks.py` archiver helper

### S8. Mobile preview не сразу видно

**Проблема:** `composed-mobile-preview.html` отдельный файл, user должен сам его открыть. Многие не открывают и думают что mobile-вёрстки нет.

**Что должно быть:** Toggle прямо в `composed.html`: кнопка «📱 Mobile / 💻 Desktop» переключает viewport prediction.

**Фикс:** Обновить generator composed.html (PR-A) — добавить mobile toggle inline.

### S9. Прайсинг — нет fallback стратегии когда у клиента нет цен

**Проблема:** Клиент не дал цены → я (агент) взял у li-motors.ru × конверсия. Это **placeholder-конверсия из ₽ × 0.040**, не verified UAE market.

**Что должно быть:**
- Skill `pricing-research` который при отсутствии client prices: ищет конкурентов в нише (через references-curator + Firecrawl), извлекает цены, конвертирует в local currency (через actual exchange rate API), выдаёт диапазон с пометкой «pending client confirmation».
- Lifecycle: «approx» → user confirms → стирается метка.

**Фикс:** Новый skill OR расширение `content-writer` с pricing fallback логикой.

### S10. Identity-safe правила НЕ enforced для inspiration

**Проблема:** Inspiration photos из lixiang.com содержат **лица китайских моделей** (на top-down фото видны люди). По identity-safe правилам (PR-B `IDENTITY_SAFE.md`) реальных людей нельзя использовать без согласия. Эти фото просто использовались.

**Что должно быть:**
- photo-curator при scanning inspiration → отмечает фото с лицами `has_faces: true`
- inspiration с лицами → автоматически идут только в "background" контекст (cropped/blurred), не main hero
- Для testimonials/team-photos: только AI-generated с явным `ai_approved_by_user: true`

**Фикс:** Расширить `photo-classifier` агент (face detection через codex vision)

---

## 🟢 NICE-TO-HAVE — улучшения для разных проектов

### S11. Per-model spec database в block-library

**Проблема:** Спеки моделей (range, 0-100, top speed) хардкожены в prototype.yaml. Если клиент даст 8 моделей вместо 5 → переделывать вручную.

**Что должно быть:** Skill `model-specs-database` с базой спек по популярным авто-моделям. content-writer pulls спеки автоматически когда видит model name.

### S12. Pre-built block templates для luxury auto / EV niche

**Проблема:** Я использовал `ru-features-03-swiss-cards` (Swiss bright colors) для luxury auto → пришлось переадаптировать. В библиотеке нет блоков именно для luxury/auto niche.

**Что должно быть:** Niche-specific block presets:
- `luxury-auto/` — 10-15 блоков под этот рынок
- `real-estate/`
- `medical/`
- `b2b-saas/`

Каждый — оптимизирован под визуал/копирайтинг ниши.

### S13. Codex prompt templates — нет «adapt photo to context»

**Проблема:** PR-B/C codex шаблоны генерят с нуля. Нужен шаблон «возьми эту фото И измени фон на Dubai backdrop, сохрани машину byte-for-byte».

**Что должно быть:** Новый template `adapt-photo-backdrop.md`:
```
Use built-in image_gen. INPUT: existing photo of [SUBJECT].
KEEP: subject pixel-perfect (no modification to car/person body).
CHANGE: background to [TARGET_BACKDROP] (Dubai Marina at golden hour).
PRESERVE: lighting consistency between subject and new bg.
OUTPUT: PNG transparent edges around subject.
```

Это identity-safe для машин (не репеинтит) и решает Dubai-локализацию.

### S14. Wireframe — добавить категорию «for premium auto»

**Проблема:** Block library генерилась для generic services. Для luxury auto нужны другие визуальные паттерны (full-bleed hero, model carousel, spec comparison table).

**Что должно быть:** Block-library расширить блоками премиум-сегмента.

### S15. Versioning / "what changed" между итерациями composed

**Проблема:** User генерирует composed → видит → просит правки → новая composed. **Нет diff** «что изменилось».

**Что должно быть:** После rebuild — автоматический `CHANGELOG.md` для этой итерации (а-ля git log но human-readable): «v2 changes: hero photo replaced, mobile toggle added, INSP badges hidden».

### S16. DOKRUTKA как первоклассный workflow

**Проблема:** Этот файл я создаю руками. В системе нет автомеханизма «when user finds issue → log to DOKRUTKA → assign to fix list».

**Что должно быть:** Skill `dokrutka-tracker`: user пишет «не так» → агент логит в DOKRUTKA.md проекта + в системный DOKRUTKA если паттерн встречается ≥2 раза. Каждый pipeline run check'ает: «closed any DOKRUTKA items? unblock proceeding».

---

## 📋 Pipeline-level фиксы

### P1. Stage 07 правильный порядок (новый порядок в PR-D)

Заменить:
```
07b_wireframe → 07c_composed → [parallel 07d_photos ⇄ 07e_visuals] → 07f_composed_final
```

На:
```
07b_wireframe → 07c_photos → 07d_composed_draft → 07e_visuals → 07f_composed_final
```

Photos идут до compose. Visuals (icons/infographics) — после compose draft (когда видна композиция).

### P2. Gate-check для текста = prototype-preserved

Add check: `composed_text_matches_prototype` — `gate-check.sh` верифицирует что текст в composed.html совпадает с prototype.yaml (не переписан агентом).

### P3. Photo-mapping валидация

Schema валидация: каждый photo slot имеет `source: client | inspiration | ai_generated` + `verified_by: human|ai` + `needs_replacement: bool`.

---

## ✅ Чек-лист закрытия — приоритетный

🔴 Критичные (блокируют доверие к системе):
- [ ] **S1** — Content-writer не переписывает текст прототипа
- [ ] **S2** — Pipeline order: photos before compose
- [ ] **S3** — Codex автоматически вызывается на 07c photos
- [ ] **S4** — Inspiration photos в pipeline (matcher + injector)
- [ ] **S5** — Агент не "переоптимизирует" wireframe selections после approve
- [ ] **S5-A** — Финальное auto-review stage (07g_self_review) — content/visual/functional/perf/SEO checks
- [ ] **S5-B** — Stage интеграций (07h_integrations) — мессенджеры, CRM, tracking, button destinations

🟡 Важные:
- [ ] **S6** — `photo-selection-guide.md` создан и используется photo-matcher
- [ ] **S7** — composed.html versioning + archive
- [ ] **S8** — Mobile toggle inline в composed
- [ ] **S9** — Pricing fallback skill (competitor research)
- [ ] **S10** — Identity-safe face detection в inspiration photos

🟢 Nice-to-have:
- [ ] **S11-S16** — См. в тексте

📋 Pipeline:
- [ ] **P1** — Stage order update в PR-D
- [ ] **P2** — Gate-check: text matches prototype
- [ ] **P3** — Photo-mapping schema with verification fields

---

## 📝 Источник этой DOKRUTKA

Тест проекта **dubai-avto-liza** (premium LiXiang dealer в Dubai). Полный цикл pipeline 07a → 07c показал перечисленные проблемы. Эта DOKRUTKA — для усиления **системы**, не для одного сайта.

Site-specific DOKRUTKA для dubai-avto-liza: `~/Lendings/dubai-avto-liza/DOKRUTKA.md`.

---

**Следующий шаг:** Перевести каждый S/P пункт в **GitHub issue / PR plan** и закрывать по одному.
