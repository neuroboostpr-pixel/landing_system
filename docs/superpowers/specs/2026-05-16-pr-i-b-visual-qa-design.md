# PR-I.b — Visual QA (Playwright + codex vision + auto-fix)

**Дата:** 2026-05-16
**Источник:** ПЛАН-ДОРАБОТОК.md пункт №3 (часть Б)
**Статус:** draft на ревью
**Связанные PR:** PR-I.a (Photo Pipeline) + gpt5-prompting-engine (только что установлен)

---

## 1. Зачем

После того как `composed.html` собран и фото обработаны (PR-I.a) — финальная **визуальная** проверка нужна потому что:
- DOM проверки не ловят «фото обрезано так что машина без капота»
- Stage-gates не видят что текст вылез за блок
- placeholder может пройти все checks но визуально не вписаться

Решение из видео-метода: агент сам открывает страницу в Playwright, делает скриншоты, **анализирует их через codex CLI с `-i screenshot.png`** (вижн-режим), получает структурированный список проблем, пробует auto-fix.

---

## 2. Главные решения (из брейншторма)

| Решение | Значение |
|---|---|
| Анализ скриншота | `codex exec -i screenshot.png` (тот же CLI что уже работает для генерации) |
| Где живёт скилл | `skills/visual-qa/` (отдельный, переиспользуется для 07c/07f/08/09) |
| Промпт для codex | Сгенерирован через `gpt5-prompting-engine` (Task 0) — валидированный |
| Auto-fix scope | CSS-tweak, photo crop/resize, photo re-process через codex |
| Запрещено auto-fix | Менять текст (блокирует PR-H verify), менять структуру блоков |
| Итерации | Максимум 3 (потом ручной отчёт) |
| HARD GATE | Опционально через `--strict`; по умолчанию warning |

---

## 3. Архитектура

```
skills/visual-qa/
├── SKILL.md                              описание навыка
├── scripts/
│   ├── take-screenshots.py               Playwright → desktop_*.png + mobile_*.png
│   ├── codex-review-screenshot.sh        wrapper над codex exec -i
│   ├── visual-qa-loop.py                 главный цикл (3 итерации)
│   └── apply-fix.py                      применить fix_hint в HTML/CSS
└── templates/
    └── review-prompt.md                  ГЕНЕРИРУЕТСЯ через gpt5-prompting-engine
                                           на Task 0 (не пишется руками)
```

### Pipeline

```
visual-qa-loop.py:
  iteration = 0
  while iteration < 3:
    1. take-screenshots.py <composed.html>
       → 10_QA/screenshots/iter-N/desktop.png
       → 10_QA/screenshots/iter-N/mobile.png
    2. codex-review-screenshot.sh <desktop.png> → desktop-review.json
       codex-review-screenshot.sh <mobile.png>  → mobile-review.json
    3. Парсим JSON → список issues с severity/type/selector/fix_hint
    4. Если нет critical issues → break (успех)
    5. Для каждой critical: apply-fix.py <issue>
    6. iteration++
  → 10_QA/visual-qa-report.md (итоговый отчёт)
  → 10_QA/screenshots/final/ (финальные скриншоты)
```

---

## 4. Промпт для codex (review-prompt.md)

**НЕ пишется руками.** Task 0 PR-I.b:
- Вызвать `gpt5-prompting-engine`
- Бриф: "напиши промпт для codex CLI (vision mode) который анализирует скриншот лендинга и возвращает JSON со списком visual issues"
- Engine выдаст: финальный промпт + validation score
- Если score ≥8/10 → используем как `templates/review-prompt.md`
- Если <8/10 → одна итерация revise

Ожидаемая структура output JSON от codex (примерно — точный формат engine спроектирует):

```json
{
  "issues": [
    {
      "severity": "critical | warning | info",
      "type": "photo_cropped | text_overflow | image_failed | empty_block | low_contrast | layout_broken",
      "description": "...",
      "selector": "section[data-block='hero-1'] img",
      "fix_hint": "..."
    }
  ],
  "summary": "N critical, M warning"
}
```

---

## 5. Auto-fix scope

`apply-fix.py` умеет применять следующие типы fix_hint'ов:

| Type | Действие |
|---|---|
| `css_tweak` | Добавить инлайн style в указанный selector (например `object-position: center 20%`) |
| `photo_recrop` | Пересоздать processed/<slot>.jpg с новым crop center (через photo-pipeline.py) |
| `photo_reprocess` | Перегенерировать через codex с уточнённым промптом |
| `text_*` | **ОТКАЗ** — text fixes блокированы (PR-H content-preserve) |
| `block_*` | **ОТКАЗ** — структурные изменения только вручную |

Если fix_hint не из разрешённого списка → попадает в warning отчёта (а не auto-fix).

---

## 6. Файлы

**Создаются:**
- `skills/visual-qa/SKILL.md`
- `skills/visual-qa/scripts/take-screenshots.py`
- `skills/visual-qa/scripts/codex-review-screenshot.sh`
- `skills/visual-qa/scripts/visual-qa-loop.py`
- `skills/visual-qa/scripts/apply-fix.py`
- `skills/visual-qa/templates/review-prompt.md` (генерируется в Task 0)
- `commands/landing-qa.md` (слеш-команда)
- `scripts/verify-visual-qa.sh` (для hard_check)
- `scripts/verify_visual_qa.py` (helper)
- `tests/pr-i-b/test_screenshots.bats`
- `tests/pr-i-b/test_review_parse.bats`
- `tests/pr-i-b/test_apply_fix.bats`
- `tests/pr-i-b/helpers.bash`

**Модифицируются:**
- `config/stage-gates.yaml` — опциональный soft_check `visual_qa_passed` для 07c/07f (default warning, не блокирует)

---

## 7. Интеграция в pipeline

### Slash-команда `/landing-qa`

```bash
/landing-qa <project>            # запустить visual QA на текущей composed
/landing-qa <project> --strict   # ошибка если найдены critical issues
/landing-qa <project> --iterate  # auto-fix цикл до 3 итераций
```

### stage-gates.yaml

```yaml
"07c_composed":
  soft_checks:
    - id: visual_qa_passed
      prompt: "Запустить /landing-qa и посмотреть скриншоты? Опционально, не блокирует."
```

(soft_check — пользователь может скипнуть; **strict mode** включается флагом)

### Orchestrator

`landing-orchestrator` после успешного 07c будет **рекомендовать** `/landing-qa` (но не обязывать) — это в промпте.

---

## 8. Тесты

### Test 1: `test_screenshots.bats`
- Setup: статичный HTML с одним блоком
- Action: `take-screenshots.py <html> --out tmp/`
- Expected: `tmp/desktop.png` и `tmp/mobile.png` существуют, размер >5KB

### Test 2: `test_review_parse.bats`
- Setup: mock JSON-output от codex (через `MOCK_CODEX=1` env)
- Action: `visual-qa-loop.py --dry-run` парсит mock-output
- Expected: правильно идентифицирует critical/warning/info

### Test 3: `test_apply_fix.bats`
- Setup: HTML с переполняющимся `<h1>`, fix_hint=`css_tweak: overflow: hidden`
- Action: `apply-fix.py <html> --hint='css_tweak: ...'`
- Expected: HTML обновлён, inline-style добавлен

---

## 9. Объём и стоимость

| Задача | Время | Codex calls |
|---|---|---|
| Task 0: review-prompt через engine | 30 мин | 0 (engine локально) |
| `take-screenshots.py` | 30 мин | 0 |
| `codex-review-screenshot.sh` | 20 мин | 0 |
| `visual-qa-loop.py` | 1 ч | 0 |
| `apply-fix.py` | 40 мин | 0 |
| `SKILL.md` + слеш-команда | 20 мин | 0 |
| `verify-visual-qa.sh` + stage-gates | 20 мин | 0 |
| 3 bats теста | 40 мин | 0 |
| Smoke на dubai-avto-liza | 30 мин | ~$0.20-0.40 (2-4 codex review calls) |

**Итого ~4-5 часов, ~$0.30 на smoke. Моки бесплатно.**

---

## 10. Открытые вопросы (на ревью)

1. **Soft vs hard check** на 07c — сейчас soft (рекомендация). Если хочешь строгий — переключим в hard_check.
2. **Mobile breakpoint** — сейчас 375×812 (iPhone 14). Достаточно или нужно 320/360 ещё?
3. **3 итерации auto-fix** — норма? Или 1-2 чтобы не транжирить codex?

Эти 3 можно подкрутить после smoke.

---

## 11. Что меняется для пользователя

**До PR-I.b:**
- Фото может быть кривовато обрезано — никто не заметит
- Текст наезжает на картинку на mobile — никто не заметит
- Финальный лендинг идёт в деплой с visible косяками

**После PR-I.b:**
- `/landing-qa` даёт **финальный визуальный отчёт** перед деплоем
- Критичные проблемы (обрезанная машина, вылазящий текст) — автомат пробует пофиксить
- Скриншоты desktop+mobile сохраняются в `10_QA/` — пользователь может посмотреть глазами
- В strict-режиме (опционально) — этап 07c не закроется пока critical не решены

---

## 12. Что НЕ в PR-I.b

- Auto-fix для текста — блокирован PR-H verify (по правилу неприкосновенности)
- A/B testing разных вариантов
- Live-preview UI (только файлы)
- Cross-browser testing (только chromium через Playwright)
