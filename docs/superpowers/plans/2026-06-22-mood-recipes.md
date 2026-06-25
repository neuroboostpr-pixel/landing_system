# Mood Recipes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Доказать переносимость «вайба» мода через `recipes.yaml` — агент рисует блоки по рецепту + прототипу, сохраняя слот-контракт 08, тест на fresh-green.

**Architecture:** `recipes.yaml` — 4-й файл мода с приёмами декора (не текст, не слоты). Читает агент при compose, не код. Тест: зелёный recipes + тексты prototype-01 → 3 блока в характере реф 29.

**Tech Stack:** YAML (recipes), HTML/CSS (composed, slot-contract), bash (проверки).

**Спек:** `docs/superpowers/specs/2026-06-22-mood-recipes-design.md`

---

## Task 1: recipes.yaml для fresh-green (приёмы, снятые глазами с реф 29)

**Files:**
- Create: `~/Lendings/Тест/05_ДИЗАЙН-СИСТЕМА/moods/fresh-green/recipes.yaml`
  (фактический путь: `d:/AI_TEAMS/Lendings/Тест/05_ДИЗАЙН-СИСТЕМА/moods/fresh-green/recipes.yaml`)

- [ ] **Step 1: Прочитать токены fresh-green** чтобы рецепт ссылался на существующие переменные

Run: `cat "d:/AI_TEAMS/Lendings/Тест/05_ДИЗАЙН-СИСТЕМА/moods/fresh-green/palette.css"`
Expected: видим имена `--lp-accent`, pink-CTA, золотой и т.д. Если pink/золото отсутствуют как токены — рецепт фиксирует hex из реф 29 (`#E0379A` pink, зелёный, золотой) и помечает «добавить в palette».

- [ ] **Step 2: Написать recipes.yaml** — приёмы из спека §«Тест», в терминах lp-классов + токенов:
  - `block_divider`: волнистый SVG-переход (clip-path / svg wave), не прямая линия
  - `cta`: pink-кнопка `#E0379A`, скруглённая, не зелёная
  - `headline_anchor`: 2-е слово italic + зелёный/золотой
  - `accent_zone`: сочно-зелёная заливка, обёрнута волнами сверху+снизу
  - `mask`: круглый аватар в зелёном кольце
  - `void_decor`: колоски/листья/конфетти по углам, золотой вторичный акцент
  - `list_marker`: (нейтральный для зелёного — точка/галка зелёная)

  Каждый приём = блок: `intent`, `lp_class`, `css_hint`, `tokens`, `when_to_use`.
  Шапка файла: «Снято ГЛАЗАМИ с ___References/29/ (01,02,04.jpg). Читает АГЕНТ при 07c, НЕ код. Слоты/структуру даёт прототип.»

- [ ] **Step 3: Проверить YAML валиден**

Run: `python3 -c "import yaml,sys; yaml.safe_load(open(r'd:/AI_TEAMS/Lendings/Тест/05_ДИЗАЙН-СИСТЕМА/moods/fresh-green/recipes.yaml',encoding='utf-8')); print('YAML OK')"`
Expected: `YAML OK`

- [ ] **Step 4: Commit**

```bash
cd "d:/AI_TEAMS/Lendings/Тест" && git add "05_ДИЗАЙН-СИСТЕМА/moods/fresh-green/recipes.yaml" 2>/dev/null || echo "Тест не git-repo — пропустить коммит, файл создан"
```
(Примечание: проект `Тест` может быть вне git — тогда коммит пропускаем, файл остаётся на диске.)

---

## Task 2: Агент рисует 3 блока ТОЛЬКО по recipes (тест воспроизводимости)

**Files:**
- Create: `d:/AI_TEAMS/Lendings/Тест/07b_COMPOSED/composed-test-greenrecipes.html`

**Критично:** при рисовании НЕ открывать реф 29 заново. Источник вида = `recipes.yaml` (Task 1). Источник текста = `prototype-01.yaml`. Это и есть тест: если recipes полон — вайб воспроизведётся без картинки.

- [ ] **Step 1: Перечитать только recipes + prototype-01** (не реф)

Run: `cat "d:/AI_TEAMS/Lendings/Тест/05_ДИЗАЙН-СИСТЕМА/moods/fresh-green/recipes.yaml"`
(тексты prototype-01 уже в контексте сессии)

- [ ] **Step 2: Нарисовать HTML** — 3 блока (hero + stats + problem→solution):
  - `data-mood="fresh-green"`, импорт токенов fresh-green (palette/typography)
  - применить КАЖДЫЙ приём recipes: волны-разделители, pink-CTA, italic-якорь, зелёная акцент-зона с волнами, маски, золотой декор
  - тексты дословно из prototype-01 (eyebrow, H1, 4 фишки, 4 цифры, 5 болей, 5 выгод, обе CTA)
  - **слот-контракт:** редактируемый текст через `{{slot:name}}`; каждый блок = `<section class="lp-...">`; предсказуемые lp-классы; фрагменты (не вложенные документы внутри секций)

- [ ] **Step 3: Проверить, что файл открывается и не пустой**

Run: `wc -l "d:/AI_TEAMS/Lendings/Тест/07b_COMPOSED/composed-test-greenrecipes.html"`
Expected: > 150 строк

---

## Task 3: Проверка слот-контракта 08 (Lazy Blocks не сломается)

**Files:** (только чтение `composed-test-greenrecipes.html`)

- [ ] **Step 1: Проверить наличие слотов и lp-классов**

Run:
```bash
cd "d:/AI_TEAMS/Lendings/Тест/07b_COMPOSED" && \
echo "slots:" && grep -o '{{slot:[a-z0-9-]*}}' composed-test-greenrecipes.html | wc -l && \
echo "lp-sections:" && grep -o '<section class="lp-[a-z-]*"' composed-test-greenrecipes.html | wc -l && \
echo "nested docs (должно быть 0):" && grep -c '<!DOCTYPE\|<html\|<body' composed-test-greenrecipes.html
```
Expected: slots > 10, lp-sections = 3, nested docs (внутри секций) = 0 кроме корневого документа-обёртки теста

- [ ] **Step 2: Проверить, что зашитого осмысленного текста вне слотов нет** (выборочно — H1/CTA)

Run: `grep -n 'Наведите\|Получить свой план\|Вы узнаете' composed-test-greenrecipes.html`
Expected: текст найден ВНУТРИ `{{slot:...}}`-обёрток или помечен как slot. Если зашит напрямую — пометить как недочёт (для теста подхода допустимо, но зафиксировать).

---

## Task 4: Визуальная проверка пользователем (критерий успеха)

- [ ] **Step 1: Показать пользователю файл и критерий**

Открыть `composed-test-greenrecipes.html` в браузере. Вопрос пользователю:
«Узнаётся ли вайб реф 29 — волны-разделители, pink-CTA, italic-акцент, круглые маски, зелёные зоны? Это нарисовано ТОЛЬКО по recipes, без просмотра картинки во время рисования.»

- [ ] **Step 2: Зафиксировать вывод**
  - ✅ узнаётся → подход работает → следующий шаг: зашить правило в `block-composer.md` + `landing-compose.md` (вне scope этого плана — отдельная задача).
  - ❌ не узнаётся / чего-то нет → recipes неполон → вернуться к Task 1, дописать недостающий приём.

---

## Self-Review notes

- **Spec coverage:** recipes-структура (Task 1), агент-читатель (Task 2), слот-контракт 08 (Task 3), тест-критерий fresh-green (Task 4) — все разделы спека покрыты. Починка build_composed.py и перенос на др. моды — явно out of scope в спеке, задач нет (корректно).
- **Placeholders:** нет TODO/TBD; приёмы recipes перечислены поimenно.
- **Consistency:** пути к fresh-green одинаковы во всех тасках; имя выходного файла `composed-test-greenrecipes.html` едино.
