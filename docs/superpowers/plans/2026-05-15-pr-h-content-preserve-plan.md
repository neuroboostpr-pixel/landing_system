# PR-H — Content Preserve Implementation Plan

**Goal:** Скрипт verify-content-preserved блокирует закрытие 07c если текст composed.html разошёлся с prototype.yaml.

**Architecture:** bash wrapper → python helper (yaml + bs4). HARD GATE через stage-gates.yaml.

**Tech Stack:** bash, python3 + PyYAML + beautifulsoup4 (уже установлены), bats.

**Spec:** [2026-05-15-pr-h-content-preserve-design.md](../specs/2026-05-15-pr-h-content-preserve-design.md)

---

## File Structure

**Создаём:**
- `scripts/verify-content-preserved.sh` — bash wrapper
- `scripts/verify_content_preserved.py` — главная логика
- `tests/pr-h/test_pass.bats`
- `tests/pr-h/test_fail_title.bats`
- `tests/pr-h/test_fail_cta.bats`
- `tests/pr-h/test_fail_order.bats`
- `tests/pr-h/helpers.bash`

**Модифицируем:**
- `config/stage-gates.yaml` — добавить `content_preserved` hard_check в 07c (+ 07f)
- `agents/block-composer.md` — раздел «контент прототипа неприкосновенен»

---

## Task 1: verify_content_preserved.py (главная логика)

**Files:**
- Create: `scripts/verify-content-preserved.sh`
- Create: `scripts/verify_content_preserved.py`

- [ ] **Step 1: Создать bash wrapper `scripts/verify-content-preserved.sh`**

```bash
#!/bin/bash
# scripts/verify-content-preserved.sh — wrapper for verify_content_preserved.py
set -uo pipefail
PROJECT="${1:?ERROR: project path required}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$REPO_ROOT/scripts/verify_content_preserved.py" "$PROJECT"
```

`chmod +x scripts/verify-content-preserved.sh`

- [ ] **Step 2: Создать `scripts/verify_content_preserved.py`**

```python
#!/usr/bin/env python3
"""Проверяет что текст из prototype.yaml присутствует в composed.html.

Exit codes:
  0 — все строки прототипа найдены, порядок блоков сохранён
  1 — есть расхождения (детали в stderr)
  2 — файл prototype.yaml или composed.html не найден
"""
import re
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup


SKIP_KEYS = {"id", "type", "block_id", "class", "tag", "data-block"}
MIN_LEN = 3  # минимальная длина строки чтобы проверять (короткие — false positives)
PLACEHOLDER_MARKERS = ("____", "___", "TBD", "tbd")


def normalize(s: str) -> str:
    """Нормализует whitespace, сохраняет регистр."""
    return re.sub(r"\s+", " ", s).strip()


def is_placeholder(s: str) -> bool:
    return any(m in s for m in PLACEHOLDER_MARKERS)


def extract_yaml_strings(node) -> list[str]:
    """Рекурсивно собирает все строковые значения, кроме служебных."""
    if isinstance(node, str):
        s = node.strip()
        if len(s) >= MIN_LEN and not is_placeholder(s):
            return [s]
        return []
    if isinstance(node, list):
        out = []
        for item in node:
            out.extend(extract_yaml_strings(item))
        return out
    if isinstance(node, dict):
        out = []
        for k, v in node.items():
            if k in SKIP_KEYS:
                continue
            out.extend(extract_yaml_strings(v))
        return out
    return []


def main(project_dir: Path) -> int:
    proto_path = project_dir / "07_ПРОТОТИП" / "prototype.yaml"
    composed_path = project_dir / "07b_COMPOSED" / "composed.html"

    if not proto_path.exists():
        print(f"ERROR: {proto_path} не найден", file=sys.stderr)
        return 2
    if not composed_path.exists():
        print(f"ERROR: {composed_path} не найден", file=sys.stderr)
        return 2

    proto_data = yaml.safe_load(proto_path.read_text(encoding="utf-8")) or {}
    html_raw = composed_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_raw, "html.parser")
    html_text = normalize(soup.get_text(separator=" "))

    # 1. Substring match для всех значимых строк
    blocks = proto_data.get("blocks", [])
    all_strings = extract_yaml_strings(blocks)
    missing = []
    for s in all_strings:
        norm = normalize(s)
        if norm and norm not in html_text:
            missing.append(norm[:100])

    # 2. Порядок блоков по data-block="<id>"
    proto_ids = [b.get("id") for b in blocks if isinstance(b, dict) and b.get("id")]
    html_ids_all = [el.get("data-block") for el in soup.find_all(attrs={"data-block": True})]
    html_ids = [b for b in html_ids_all if b in proto_ids]
    order_ok = True
    if proto_ids and html_ids:
        expected_order = [b for b in proto_ids if b in html_ids]
        if html_ids[: len(expected_order)] != expected_order:
            order_ok = False

    fail = bool(missing) or not order_ok

    if fail:
        if missing:
            print(
                f"❌ В composed.html не найдено {len(missing)} строк из prototype.yaml:",
                file=sys.stderr,
            )
            for m in missing[:10]:
                print(f"   - «{m}»", file=sys.stderr)
            if len(missing) > 10:
                print(f"   ... ещё {len(missing) - 10}", file=sys.stderr)
        if not order_ok:
            print("❌ Порядок блоков в composed.html отличается от prototype.yaml", file=sys.stderr)
            print(f"   Прототип: {proto_ids}", file=sys.stderr)
            print(f"   HTML:     {html_ids}", file=sys.stderr)
        return 1

    print(f"✅ Контент прототипа сохранён ({len(all_strings)} строк проверено)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: verify_content_preserved.py <project-dir>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
```

- [ ] **Step 3: Smoke на минимальной фикстуре**

```bash
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/07_ПРОТОТИП" "$TMPDIR/07b_COMPOSED"
cat > "$TMPDIR/07_ПРОТОТИП/prototype.yaml" <<'EOF'
blocks:
  - id: hero-1
    type: hero
    title: "Hello World"
    cta: "Press me"
EOF
cat > "$TMPDIR/07b_COMPOSED/composed.html" <<'EOF'
<!DOCTYPE html>
<html><body>
<section data-block="hero-1"><h1>Hello World</h1><button>Press me</button></section>
</body></html>
EOF
bash scripts/verify-content-preserved.sh "$TMPDIR"
echo "exit=$?"
```
Expected: `✅ Контент прототипа сохранён...`, exit 0.

Тест на fail:
```bash
sed -i.bak 's/Hello World/Goodbye/' "$TMPDIR/07b_COMPOSED/composed.html"
bash scripts/verify-content-preserved.sh "$TMPDIR"
echo "exit=$?"
```
Expected: `❌ ... не найдено ... «Hello World»`, exit 1.

- [ ] **Step 4: Commit**

```bash
git add scripts/verify-content-preserved.sh scripts/verify_content_preserved.py
git commit -m "feat(pr-h): verify-content-preserved — сравнение prototype.yaml ↔ composed.html

Substring match + проверка порядка блоков. Без SDK.
Exit 1 при любом расхождении. Используется как hard_check для 07c."
```

---

## Task 2: stage-gates.yaml integration

**Files:**
- Modify: `config/stage-gates.yaml`

- [ ] **Step 1: Найти секцию `"07c_composed"` в `config/stage-gates.yaml`**

```bash
grep -n '"07c_composed"' config/stage-gates.yaml
```

- [ ] **Step 2: Добавить новый hard_check в массив `hard_checks` для 07c_composed**

В секции `"07c_composed"`, внутри `hard_checks:` ДОПИСАТЬ (в конец списка) новый чек. Найти где заканчивается последний элемент `hard_checks` и **перед** `soft_checks:` или следующей секцией добавить:

```yaml
      - id: content_preserved
        type: script
        script: "scripts/verify-content-preserved.sh"
        args: ["{project}"]
        required: true
        fix_hint: "Текст прототипа изменён в composed.html. Откати правки или обнови prototype.yaml если клиент дал новый текст."
```

То же самое для `"07f_composed_final"` если такая секция существует (она тоже должна сохранять текст после фото-перерендера).

- [ ] **Step 3: Проверить yaml валиден**

```bash
yq -r '.stages."07c_composed".hard_checks | map(.id)' config/stage-gates.yaml
```
Expected: список с `content_preserved` в конце.

- [ ] **Step 4: Commit**

```bash
git add config/stage-gates.yaml
git commit -m "feat(pr-h): подключить verify-content-preserved как hard_check 07c

При попытке закрыть 07c — gate-check.sh запустит verify.
Exit 1 → этап не закрывается."
```

---

## Task 3: Усилить промпт block-composer

**Files:**
- Modify: `agents/block-composer.md`

- [ ] **Step 1: Прочитать промпт**

```bash
head -40 agents/block-composer.md
```

- [ ] **Step 2: Добавить новый раздел в начало промпта (после frontmatter и первого заголовка)**

Использовать Edit чтобы вставить перед `## Mission` или эквивалентным первым разделом:

```markdown

## СТРОГО: контент прототипа неприкосновенен (PR-H)

Текст из `<project>/07_ПРОТОТИП/prototype.yaml` — **финальный**.

**Правила:**
- Заголовки блоков (`title`) — переноси ДОСЛОВНО, не «улучшай».
- CTA-тексты (`cta`) — ДОСЛОВНО.
- Абзацы и пункты (`body`, `items`) — ДОСЛОВНО.
- Порядок блоков — точно как в `blocks[]` массиве.

**Если хочешь что-то изменить:**
- НЕ делай этого молча.
- Спроси пользователя явно: «Я предлагаю переписать заголовок hero
  с '[X]' на '[Y]' потому что [причина]. Разрешаешь?»
- После «да» — обнови сначала `prototype.yaml`, потом HTML.

**HARD GATE 07c:** `scripts/verify-content-preserved.sh` запустится
при закрытии 07c. Если найдёт расхождение — этап не закроется.
Подробнее: `docs/superpowers/specs/2026-05-15-pr-h-content-preserve-design.md`.

```

- [ ] **Step 3: Commit**

```bash
git add agents/block-composer.md
git commit -m "feat(pr-h): block-composer — правило о неприкосновенности текста

Текст из prototype.yaml должен переноситься в composed.html дословно.
Изменения только с явного разрешения пользователя."
```

---

## Task 4: bats-тесты

**Files:**
- Create: `tests/pr-h/helpers.bash`
- Create: `tests/pr-h/test_pass.bats`
- Create: `tests/pr-h/test_fail_title.bats`
- Create: `tests/pr-h/test_fail_cta.bats`
- Create: `tests/pr-h/test_fail_order.bats`

- [ ] **Step 1: Создать helpers**

```bash
mkdir -p tests/pr-h
cat > tests/pr-h/helpers.bash <<'HELPER'
#!/usr/bin/env bash
PR_H_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

make_fake_project() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07_ПРОТОТИП" "$tmpdir/07b_COMPOSED"
    cat > "$tmpdir/07_ПРОТОТИП/prototype.yaml" <<'YAML'
blocks:
  - id: hero-1
    type: hero
    title: "Welcome to LiXiang"
    cta: "Request a test drive"
  - id: features-1
    type: features
    title: "World of comfort"
    items:
      - text: "Safety first"
      - text: "Quiet ride"
YAML
    cat > "$tmpdir/07b_COMPOSED/composed.html" <<'HTML'
<!DOCTYPE html>
<html><body>
<section data-block="hero-1">
  <h1>Welcome to LiXiang</h1>
  <button>Request a test drive</button>
</section>
<section data-block="features-1">
  <h2>World of comfort</h2>
  <ul><li>Safety first</li><li>Quiet ride</li></ul>
</section>
</body></html>
HTML
    echo "$tmpdir"
}
HELPER
```

- [ ] **Step 2: test_pass.bats**

```bash
cat > tests/pr-h/test_pass.bats <<'BATS'
#!/usr/bin/env bats
load 'helpers.bash'

@test "pass: все строки прототипа есть в composed.html, порядок верный" {
    project="$(make_fake_project)"
    run bash "$PR_H_REPO_ROOT/scripts/verify-content-preserved.sh" "$project"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Контент прототипа сохранён"* ]]
}
BATS
```

- [ ] **Step 3: test_fail_title.bats**

```bash
cat > tests/pr-h/test_fail_title.bats <<'BATS'
#!/usr/bin/env bats
load 'helpers.bash'

@test "fail: заголовок hero изменён в composed.html" {
    project="$(make_fake_project)"
    sed -i.bak 's/Welcome to LiXiang/Welcome to BMW/' "$project/07b_COMPOSED/composed.html"
    run bash "$PR_H_REPO_ROOT/scripts/verify-content-preserved.sh" "$project"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Welcome to LiXiang"* ]] || [[ "$output" == *"не найдено"* ]]
}
BATS
```

- [ ] **Step 4: test_fail_cta.bats**

```bash
cat > tests/pr-h/test_fail_cta.bats <<'BATS'
#!/usr/bin/env bats
load 'helpers.bash'

@test "fail: CTA-текст изменён в composed.html" {
    project="$(make_fake_project)"
    sed -i.bak 's/Request a test drive/Get a quote/' "$project/07b_COMPOSED/composed.html"
    run bash "$PR_H_REPO_ROOT/scripts/verify-content-preserved.sh" "$project"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Request a test drive"* ]] || [[ "$output" == *"не найдено"* ]]
}
BATS
```

- [ ] **Step 5: test_fail_order.bats**

```bash
cat > tests/pr-h/test_fail_order.bats <<'BATS'
#!/usr/bin/env bats
load 'helpers.bash'

@test "fail: порядок блоков отличается от prototype.yaml" {
    project="$(make_fake_project)"
    # Поменяем секции местами в composed.html
    python3 -c "
from pathlib import Path
p = Path('$project/07b_COMPOSED/composed.html')
text = p.read_text()
# swap: features section appears BEFORE hero section
hero = text.split('<section data-block=\"hero-1\">')[1].split('</section>')[0]
features = text.split('<section data-block=\"features-1\">')[1].split('</section>')[0]
new = text.replace(
    f'<section data-block=\"hero-1\">{hero}</section>',
    'HERO_PLACEHOLDER'
).replace(
    f'<section data-block=\"features-1\">{features}</section>',
    f'<section data-block=\"features-1\">{features}</section><section data-block=\"hero-1\">{hero}</section>'
).replace('HERO_PLACEHOLDER', '')
p.write_text(new)
"
    run bash "$PR_H_REPO_ROOT/scripts/verify-content-preserved.sh" "$project"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Порядок блоков"* ]] || [[ "$output" == *"order"* ]]
}
BATS
```

- [ ] **Step 6: Запустить все**

```bash
bats tests/pr-h/
```
Expected: 4/4 pass.

- [ ] **Step 7: Commit**

```bash
git add tests/pr-h/
git commit -m "test(pr-h): 4 bats — pass + fail на title/cta/order

Тесты доказывают что verify ловит изменения заголовков, CTA
и переставленные блоки."
```

---

## Task 5: Smoke на реальном dubai-avto-liza

- [ ] **Step 1: Запустить verify на реальном проекте**

```bash
bash scripts/verify-content-preserved.sh ~/Lendings/dubai-avto-liza
```

Возможные исходы:
- **Exit 0** — контент сохранён, всё ОК
- **Exit 1 с короткими missing** — нормально для существующего проекта где могут быть placeholder'ы или агент уже что-то менял; задокументировать как known issue
- **Exit 2** — prototype.yaml или composed.html отсутствуют, тоже норма для не доделанного проекта

- [ ] **Step 2: Если exit 1 — глянуть глазами что не нашлось**

Если список missing короткий (1-3 строк) — норма (placeholder'ы цен и т.д.). Если длинный (10+) — значит composed.html сильно расходится с прототипом. Записать в чате.

- [ ] **Step 3: НЕ КОММИТИТЬ если есть проблемы** — диагностика только

---

## Task 6: Финал — отметка пункта 2 в плане + push

- [ ] **Step 1: pytest + bats регрессия**

```bash
pytest tests/wiki/ -v 2>&1 | tail -3
bats tests/pr-g/
bats tests/pr-h/
bash scripts/check-wiki-sync.sh
```

- [ ] **Step 2: Отметить Пункт 2 в `docs/ПЛАН-ДОРАБОТОК.md`**

Заменить `#### 2. Текст прототипа нельзя менять` на `#### 2. ✅ ГОТОВО (2026-05-15) — текст прототипа неприкосновенен`. Дописать в начало раздела блок «Что сделано в PR-H» аналогично пунктам 0 и 1:

```markdown

**Статус:** Реализовано в PR-H (6 задач TDD, 0 SDK calls). Запушено на GitHub.

**Что сделано:**

1. **`scripts/verify-content-preserved.sh`** + python helper — сравнивает все текстовые поля из `prototype.yaml` (titles, CTAs, body, items) с `composed.html` через substring match с whitespace-нормализацией. Дополнительно проверяет порядок блоков по `data-block` атрибутам.

2. **HARD GATE в `stage-gates.yaml`** — добавлен `content_preserved` hard_check для этапа `07c_composed` (и `07f_composed_final` если есть). `gate-check.sh` НЕ ЗАКРЫВАЕТ этап если verify exit != 0.

3. **Усиленный промпт `block-composer`** — добавлен раздел «контент прототипа неприкосновенен» с правилами и обязанностью спросить разрешение перед любым изменением текста.

4. **Тесты:** 4 bats в `tests/pr-h/`:
   - pass — все строки совпадают
   - fail_title — заголовок изменён
   - fail_cta — CTA-кнопка изменена
   - fail_order — блоки переставлены

**Поведение verify:**
- Case-sensitive (клиентский регистр сохраняется)
- Whitespace-tolerant (переносы строк нормализуются)
- Placeholder'ы `____` и `TBD` пропускаются
- Минимальная длина строки 3 символа (короткие — false positives)

**Эффект для пользователя:**
- Агент не может молча переписать заголовок/CTA — verify его поймает
- При попытке закрыть 07c с изменённым текстом — список расхождений в stderr
- Если клиент дал новый текст — нужно сначала обновить `prototype.yaml`, потом composed.html

**Spec:** [`docs/superpowers/specs/2026-05-15-pr-h-content-preserve-design.md`](superpowers/specs/2026-05-15-pr-h-content-preserve-design.md)
**Plan:** [`docs/superpowers/plans/2026-05-15-pr-h-content-preserve-plan.md`](superpowers/plans/2026-05-15-pr-h-content-preserve-plan.md)

```

- [ ] **Step 3: Commit плана**

```bash
git add docs/ПЛАН-ДОРАБОТОК.md
git commit -m "docs: пункт 2 (content preserve) отмечен как готовый"
```

- [ ] **Step 4: Push**

```bash
git push origin feat/pr-a-prototype-block-library 2>&1 | tail -5
```

---

## Self-Review

**Spec coverage:**
- ✅ verify-content-preserved.sh + python helper (Task 1)
- ✅ Substring match + порядок (Task 1)
- ✅ Plaholder skip (Task 1)
- ✅ HARD GATE через stage-gates.yaml (Task 2)
- ✅ block-composer promt (Task 3)
- ✅ 4 bats (Task 4)
- ✅ Smoke (Task 5)
- ✅ Marker пункта 2 + push (Task 6)

**Placeholders:** нет.

**Type consistency:** функции `extract_yaml_strings`, `normalize`, exit codes 0/1/2 — везде одинаково.

**Риски:**
1. Real dubai-avto-liza prototype может НЕ содержать `blocks: [...]` в ожидаемой структуре — verify вернёт 0 (нет строк = нет missing) или 2 (yaml missing). Обработано через `proto_data.get("blocks", [])`.
2. BeautifulSoup может пропустить текст в JS-strings — это норма, мы проверяем только видимый HTML-текст.
3. `data-block` атрибуты могут отсутствовать в composed.html — тогда order check не сработает, но pass останется по содержимому. Это допустимо.
