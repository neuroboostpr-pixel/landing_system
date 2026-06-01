# Content Extraction from Prototype — Specification

**Дата:** 2026-06-01  
**Статус:** 🔴 CRITICAL (блокирует neurokreator)  
**Автор:** Claude Code  
**Версия:** 1.0  

---

## Проблема

Этап **07_content** (agent content-writer) заполняет `07_КОНТЕНТ/content.md` **шаблонными текстами** вместо того, чтобы извлечь **реальные тексты** из исходного прототипа клиента.

### Влияние

1. **Wireframe показывает неправильный контент** — маркетолог выбирает макет на основе Lorem Ipsum
2. **Compose stage получает неправильные тексты** — вся последующая цепочка (07c, 07d-07e, 07f) работает с шаблоном
3. **QA не может валидировать контент** — нет способа проверить совпадение prototype → content → wireframe → composed
4. **Клиент видит не свой контент на лендинге** — deploy заполняет WordPress неправильными данными

### Корневая причина

Agent `content-writer` на этапе 07_content:
- **Не читает** `07_ПРОТОТИП/prototype.yaml` или `prototype.md`
- **Не парсит** исходный прототип из `07_ПРОТОТИП/source/prototype.{docx,pdf,md}`
- **Генерирует generic template** вместо extraction

---

## Решение

### Архитектура

```
07_ПРОТОТИП/source/prototype.docx (клиент загружает)
    ↓
prototype-importer (stage 07a)
    ↓ outputs:
    07_ПРОТОТИП/prototype.yaml (структура секций)
    07_ПРОТОТИП/prototype.md (human-readable)
    ↓
content-writer (stage 07, НОВЫЙ FLOW)
    ↓ должен читать:
    07_ПРОТОТИП/prototype.yaml
    07_ПРОТОТИП/prototype.md
    ↓ extraction:
    Заголовки (h1, h2, h3)
    Описания (body text)
    Названия блоков / курсов
    CTA тексты на кнопках
    ↓ outputs:
    07_КОНТЕНТ/content.md (РЕАЛЬНЫЕ тексты!)
    07_КОНТЕНТ/extraction-log.md (лог что извлекли)
    ↓
wireframe-selector (stage 07b)
    ↓ uses:
    07_КОНТЕНТ/content.md (теперь правильный)
    ↓
wireframe.html (показывает РЕАЛЬНЫЙ контент)
```

### Алгоритм extraction

#### 1. Parse prototype.yaml

Читает структуру из `07_ПРОТОТИП/prototype.yaml`:

```yaml
sections:
  - id: "header"
    name: "Навигация и Header"
    blocks:
      - type: "logo"
        label: "Логотип + текст"
      - type: "menu"
        label: "Горизонтальное меню"
        items: ["Home", "About", "Service", "Contact"]
      - type: "button"
        label: "CTA кнопка"
        text: "Get Started"  # ← EXTRACT
        
  - id: "hero"
    name: "Hero Section"
    blocks:
      - type: "heading"
        text: "The Skills You Need"  # ← EXTRACT
        
  - id: "courses"
    blocks:
      - type: "course_card"
        title: "Foundation Of (ux) Design Basics To Advance"  # ← EXTRACT
        price: "$135.00"  # ← EXTRACT
```

**Алгоритм:**
1. Открыть `07_ПРОТОТИП/prototype.yaml`
2. Для каждого блока с `type: "heading"`, `type: "button"`, `type: "paragraph"`, `type: "course_card"` и т.д.
3. Если блок имеет поле `text`, `title`, `label` → **EXTRACT** в соответствующий раздел content.md
4. Если нет текста в YAML → прочитать из `07_ПРОТОТИП/prototype.md` (markdown fallback)

#### 2. Structure content.md by sections

Выход `07_КОНТЕНТ/content.md` должен быть структурирован **по секциям прототипа**, а не generic template:

```markdown
# Текстовый контент — НейроКреатор

## 1. Header & Navigation

### Логотип
НейроКреатор

### Меню
- Home → /
- About → /#about
- Service → /#services
- Contact → /#contact

### CTA Кнопка
- Text: "Get Started"
- Action: Scroll to registration

---

## 2. Hero Section

### Заголовок (h1)
"The Skills You Need, The Success You Deserve"

### Описание
"Join thousands of professionals mastering new skills..."

### Кнопки
1. Learn More (primary orange)
2. Sign Up for Free (secondary outline)

---

## 3. Features

### Карточка 1: 60+ Online Courses
"Access our extensive library..."

### Карточка 2: Lifetime Access
"Learn at your own pace..."

### Карточка 3: Expert Mentors
"Learn directly from industry professionals..."

---

## 4. Courses Grid

### Заголовок
"Popular Courses"

### Курс 1
- Title: "Foundation of UX Design: Basics to Advanced"
- Level: "Beginner"
- Students: "1,250 enrolled"
- Rating: "★ 4.8 (324 reviews)"
- Price: "$135.00"

### Курс 2
...

---

## 5. Registration Form

### Заголовок (левая)
"Register Your Account"

### Поля
1. Full Name * (placeholder: "John Doe")
2. Email * (placeholder: "you@example.com")
...

### Справа (CTA text)
"GET FREE ACCESS TO 5,000+ ONLINE COURSES"
"No credit card required..."

---

## 6. Footer

### Колонка 1: Company
...
```

#### 3. Validation

После extraction:
- ✅ Проверить что **каждая секция** в content.md имеет хотя бы один реальный текст (не "Lorem ipsum")
- ✅ Проверить что **нет generic шаблонных фраз** ("learn more", "description goes here", и т.д.)
- ✅ Сравнить **кол-во секций** в prototype.yaml == кол-во секций в content.md
- ❌ FAIL если content.md содержит шаблонные тексты → требует manual review

#### 4. Logging

Создать `07_КОНТЕНТ/extraction-log.md`:

```markdown
# Content Extraction Log

**Source:** 07_ПРОТОТИП/prototype.yaml + prototype.md  
**Generated:** 2026-06-01 14:30:00Z  
**Status:** ✅ SUCCESS  

## Extraction Summary

| Section | Blocks Extracted | Sample Text |
|---------|-----------------|-------------|
| Header | 3/3 | "Get Started" |
| Hero | 3/3 | "The Skills You Need..." |
| Features | 3/3 | "60+ Online Courses" |
| Courses | 4/4 | "Foundation of UX Design..." |
| Form | 5/5 | "Register Your Account" |
| Footer | 4/4 | "Company" |

**Total:** 22 blocks extracted  
**Generic templates detected:** 0  
**Validation:** ✅ PASSED  

## What Was Extracted

### Header
- Logo: НейроКреатор
- Menu items: Home, About, Service, Contact
- CTA Button: "Get Started"

### Hero
- Headline: "The Skills You Need, The Success You Deserve"
- Description: "Join thousands of professionals..."
- Buttons: Learn More, Sign Up for Free

... (full list)

## Issues Found

None ✅

---

## Next Steps

1. Review content.md for accuracy
2. Use content.md in wireframe-selector (stage 07b)
3. Proceed to 07c_COMPOSED
```

---

## Implementation Requirements

### Agent: content-writer

**입력:**
- `07_ПРОТОТИП/prototype.yaml` (структура)
- `07_ПРОТОТИП/prototype.md` (fallback текст)
- `07_ПРОТОТИП/source/prototype.{docx,pdf,md}` (исходный файл, для parse fallback)

**Алгоритм:**
1. Прочитать `prototype.yaml`
2. Для каждого блока с текстовым контентом → extract в content.md
3. Если текст не найден в YAML → fallback на `prototype.md`
4. Если всё ещё не найден → WARN в логе

**Выход:**
- `07_КОНТЕНТ/content.md` (структурирован по секциям, все текст из прототипа)
- `07_КОНТЕНТ/extraction-log.md` (лог с summary)
- `.landing-state.yaml` → `07_content: approved` (только если validation passed)

**Gate-check (soft):**
```bash
# Убедиться что content.md не содержит generic шаблон
grep -i "lorem\|description goes here\|add your text" 07_КОНТЕНТ/content.md && exit 1
# Убедиться что кол-во секций совпадает
YAML_SECTIONS=$(grep "^  - id:" 07_ПРОТОТИП/prototype.yaml | wc -l)
MD_SECTIONS=$(grep "^##" 07_КОНТЕНТ/content.md | wc -l)
[ "$YAML_SECTIONS" -eq "$MD_SECTIONS" ] || exit 1
exit 0
```

---

## Testing

### Unit tests

```bash
# test_extraction.bats

@test "content.md is generated from prototype.yaml" {
  [ -f 07_КОНТЕНТ/content.md ]
}

@test "content.md has all sections from prototype.yaml" {
  SECTIONS=$(grep "^  - id:" 07_ПРОТОТИП/prototype.yaml | cut -d'"' -f2)
  while read section; do
    grep -q "## $section" 07_КОНТЕНТ/content.md
  done <<< "$SECTIONS"
}

@test "content.md does NOT contain generic templates" {
  ! grep -i "lorem\|description goes here\|your text" 07_КОНТЕНТ/content.md
}

@test "extraction-log.md is created and valid" {
  [ -f 07_КОНТЕНТ/extraction-log.md ]
  grep -q "✅ SUCCESS\|✅ PASSED" 07_КОНТЕНТ/extraction-log.md
}

@test "stage gate passes when content is real" {
  bash scripts/gate-check.sh --stage 07_content && true
}
```

### Integration test

1. Upload prototype.docx с реальными текстами
2. Run `/landing-prototype` → генерирует prototype.yaml
3. Run `/landing-content` (07_content agent)
4. **Verify:** content.md содержит реальные тексты из prototype.yaml, **не generic template**
5. Run `/landing-wireframe` → wireframe.html показывает РЕАЛЬНЫЙ контент
6. **Success:** маркетолог видит свой контент, а не Lorem Ipsum

---

## Acceptance Criteria

- [ ] content-writer agent читает prototype.yaml
- [ ] content.md заполняется РЕАЛЬНЫМИ текстами из прототипа
- [ ] extraction-log.md создаётся и валидирует что тексты реальные
- [ ] stage gate 07_content проверяет что content.md не содержит template
- [ ] wireframe.html автоматически использует content.md (если правильный)
- [ ] neurokreator проект: wireframe.html показывает реальный контент, не "Lorem ipsum"

---

## Rollout Plan

1. **Phase 1:** Написать spec (THIS FILE) ✅
2. **Phase 2:** Обновить agent `content-writer` (skills/landing-system/agents/content-writer.md)
3. **Phase 3:** Добавить unit + integration тесты
4. **Phase 4:** Проверить на neurokreator проекте
5. **Phase 5:** Update CLAUDE.md с правильным flow

**ETA:** 2–3 часа разработки + 1 час тестирования

