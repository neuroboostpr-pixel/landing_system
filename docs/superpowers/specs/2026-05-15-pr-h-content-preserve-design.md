# PR-H — Content Preserve (текст прототипа неприкосновенен)

**Дата:** 2026-05-15
**Источник:** ПЛАН-ДОРАБОТОК.md пункт №2 («Текст прототипа нельзя менять»)
**Статус:** draft на ревью
**Связанный PR:** PR-G (Stage Lock) — фундамент hard_checks

---

## 1. Зачем (простым языком)

Клиент даёт прототип с конкретными заголовками, кнопками, текстами. Агент при компоновке `composed.html` иногда «улучшает» — переписывает заголовок, меняет CTA, переставляет блоки. **Это нельзя.** Текст клиента = финальный текст.

PR-H добавляет автоматическую проверку: при закрытии этапа 07c сравнивается `composed.html` с `prototype.yaml`. Любое несовпадение → HARD GATE, этап не закрывается.

---

## 2. Главные решения (из брейншторма)

| Решение | Значение |
|---|---|
| Источник правды | `<project>/07_ПРОТОТИП/prototype.yaml` (структурированный YAML) |
| Цель сравнения | `<project>/07b_COMPOSED/composed.html` (рендеренный HTML) |
| Метод | Substring match с whitespace-нормализацией |
| Case sensitivity | Case-sensitive — клиентский регистр сохраняется |
| Поведение при fail | HARD GATE — exit 1, gate-check блокирует 07c |
| Escape hatch | НЕТ на этом PR (YAGNI) — хочешь поменять текст, обнови prototype.yaml |

---

## 3. Что проверяем (4 категории)

### 3.1 Заголовки блоков
**Из:** `prototype.yaml: blocks[].title`
**Где ищем:** весь `<h1>`, `<h2>`, `<h3>` текст в composed.html

### 3.2 CTA-кнопки
**Из:** `prototype.yaml: blocks[].cta` (если есть)
**Где ищем:** `<button>`, `<a>` с классом `cta` или `lp-cta` или внутри `data-block="cta-*"` секций

### 3.3 Тексты блоков
**Из:** `prototype.yaml: blocks[].body`, `.items[].text`, `.description`, `.subtitle` и т.д. (рекурсивный обход всех строковых полей кроме `id`, `type`, `block_id`, `class`, `tag`)
**Где ищем:** весь видимый текст composed.html (после удаления тегов через BeautifulSoup)

### 3.4 Порядок блоков
**Из:** `prototype.yaml: blocks[]` — порядок индексов
**Где ищем:** `composed.html` — секции с `data-block="<id>"` должны идти в том же порядке

---

## 4. Скрипт `scripts/verify-content-preserved.sh`

### 4.1 Сигнатура

```bash
verify-content-preserved.sh <path-to-project>
```

**Exit codes:**
- `0` — все тексты прототипа найдены в composed.html, порядок блоков сохранён
- `1` — несовпадение (детали в stderr)
- `2` — файл не найден (prototype.yaml или composed.html)

**Использование:** вызывается из `gate-check.sh` как `hard_check` для этапа `07c_composed`.

### 4.2 Архитектура

Тонкий bash-враппер вокруг Python helper'а (где удобнее парсить YAML + HTML):

```bash
#!/bin/bash
# scripts/verify-content-preserved.sh
set -uo pipefail
PROJECT="${1:?ERROR: project path required}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$REPO_ROOT/scripts/verify_content_preserved.py" "$PROJECT"
```

Питон делает всю работу:

```python
# scripts/verify_content_preserved.py
import sys, re, yaml
from pathlib import Path
from bs4 import BeautifulSoup

def normalize(s: str) -> str:
    """Нормализует whitespace, сохраняет case."""
    return re.sub(r"\s+", " ", s).strip()

def extract_yaml_strings(node, skip_keys=("id", "type", "block_id", "class", "tag")) -> list[str]:
    """Рекурсивно собирает все строковые значения из YAML, исключая служебные ключи."""
    if isinstance(node, str):
        s = node.strip()
        return [s] if len(s) > 1 else []
    if isinstance(node, list):
        return [s for item in node for s in extract_yaml_strings(item, skip_keys)]
    if isinstance(node, dict):
        result = []
        for k, v in node.items():
            if k in skip_keys:
                continue
            result.extend(extract_yaml_strings(v, skip_keys))
        return result
    return []

def main(project_dir: Path) -> int:
    proto = project_dir / "07_ПРОТОТИП" / "prototype.yaml"
    composed = project_dir / "07b_COMPOSED" / "composed.html"
    if not proto.exists() or not composed.exists():
        print(f"ERROR: prototype.yaml или composed.html не найдены", file=sys.stderr)
        return 2

    proto_data = yaml.safe_load(proto.read_text(encoding="utf-8"))
    html = composed.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    html_text = normalize(soup.get_text(separator=" "))

    # 1. Substring match для всех текстовых полей
    missing = []
    for s in extract_yaml_strings(proto_data.get("blocks", [])):
        norm = normalize(s)
        if norm and norm not in html_text:
            # Допускаем что в шаблоне prototype есть плейсхолдеры (___) — пропускаем
            if "____" in norm or norm.startswith("TBD"):
                continue
            missing.append(norm[:80])

    # 2. Порядок блоков
    block_ids_proto = [b.get("id") for b in proto_data.get("blocks", []) if b.get("id")]
    block_ids_html = [el.get("data-block") for el in soup.find_all(attrs={"data-block": True})]
    order_ok = True
    if block_ids_proto and block_ids_html:
        # Извлечь только те block_id из html которые есть в proto (по факту они и должны быть)
        seen = [b for b in block_ids_html if b in block_ids_proto]
        if seen != block_ids_proto[: len(seen)]:
            order_ok = False

    fail = bool(missing) or not order_ok
    if fail:
        if missing:
            print(f"❌ В composed.html не найдено {len(missing)} строк из prototype.yaml:", file=sys.stderr)
            for m in missing[:10]:
                print(f"   - «{m}»", file=sys.stderr)
            if len(missing) > 10:
                print(f"   ... ещё {len(missing) - 10}", file=sys.stderr)
        if not order_ok:
            print(f"❌ Порядок блоков в composed.html отличается от prototype.yaml", file=sys.stderr)
            print(f"   Прототип: {block_ids_proto}", file=sys.stderr)
            print(f"   HTML:     {[b for b in block_ids_html if b in block_ids_proto]}", file=sys.stderr)
        return 1

    print(f"✅ Контент прототипа сохранён ({len(extract_yaml_strings(proto_data.get('blocks', [])))} строк проверено)")
    return 0

if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
```

---

## 5. Интеграция в `stage-gates.yaml`

В существующую секцию `"07c_composed"` добавляется новый `hard_check`:

```yaml
"07c_composed":
  name: "Composed"
  lock: hard
  require_approved: ["05_design", "07a_prototype", "07b_wireframe"]
  hard_checks:
    # ... существующие ...
    - id: content_preserved
      type: script
      script: "scripts/verify-content-preserved.sh"
      args: ["{project}"]
      required: true
      fix_hint: "Текст прототипа изменён в composed.html. Откати правки или обнови prototype.yaml если клиент дал новый текст."
```

Аналогично — `"07f_composed_final"` (после фото и иконок composed.html перерендеривается, проверка должна оставаться).

---

## 6. Усиление промпта `block-composer`

В `agents/block-composer.md` добавляется секция:

```markdown
## СТРОГО: контент прототипа неприкосновенен

Текст из `<project>/07_ПРОТОТИП/prototype.yaml` — финальный.

**Правила:**
- Заголовки блоков (`title`) — переноси ДОСЛОВНО, не «улучшай».
- CTA-тексты (`cta`) — ДОСЛОВНО.
- Абзацы и пункты (`body`, `items`) — ДОСЛОВНО.
- Порядок блоков — точно как в `blocks[]` массиве.

**Если хочешь что-то изменить:**
- НЕ делай этого молча.
- Спроси пользователя явно: «Я предлагаю переписать заголовок hero с
  '[X]' на '[Y]' потому что [причина]. Разрешаешь?»
- Только после «да» — меняй сначала в `prototype.yaml`, потом в HTML.

**HARD GATE 07c:** `scripts/verify-content-preserved.sh` запустится при
закрытии этапа. Если найдёт расхождение — этап не закроется.
```

---

## 7. Тесты (4 bats)

### 7.1 `test_content_preserved_pass.bats`
- Setup: fake-проект с prototype.yaml (2 блока) и composed.html где все строки совпадают
- Action: `verify-content-preserved.sh <project>`
- Expected: exit 0, `✅ Контент прототипа сохранён`

### 7.2 `test_content_preserved_fail_title.bats`
- Setup: prototype.yaml содержит `title: "Original"`, composed.html содержит `<h1>Changed</h1>`
- Action: `verify-content-preserved.sh <project>`
- Expected: exit 1, stderr содержит «Original» в списке missing

### 7.3 `test_content_preserved_fail_cta.bats`
- Setup: prototype.yaml `cta: "Запросить тест-драйв"`, composed.html `<button>Request test drive</button>`
- Action: verify
- Expected: exit 1, stderr содержит «Запросить тест-драйв»

### 7.4 `test_content_preserved_fail_order.bats`
- Setup: prototype.yaml `blocks: [hero, features, cta]`, composed.html секции в порядке `[hero, cta, features]`
- Action: verify
- Expected: exit 1, stderr содержит «Порядок блоков»

---

## 8. Объём

| Задача | Время | SDK |
|---|---|---|
| `verify-content-preserved.sh` (bash wrapper) | 10 мин | 0 |
| `verify_content_preserved.py` (главная логика) | 30 мин | 0 |
| Дополнить `stage-gates.yaml` (07c + 07f) | 10 мин | 0 |
| Усилить `agents/block-composer.md` | 10 мин | 0 |
| 4 bats-теста с фикстурами | 40 мин | 0 |
| Smoke на dubai-avto-liza | 15 мин | 0 |

**Итого:** 7 задач, ~2 часа, **0 SDK calls**.

---

## 9. Открытые вопросы (для финального ревью)

1. **Минимальная длина проверяемой строки** — сейчас в коде `len(s) > 1`. Для очень коротких ("OK", "Да") false positives. Может стоит `> 3`?
2. **Плейсхолдеры (`____`)** — сейчас пропускаются. Достаточно ли этого паттерна или клиент может использовать другие маркеры?
3. **TBD-строки** — `s.startswith("TBD")` пропускается. Норм?

Эти 3 нюанса можно поправить итеративно после первого прогона на реальном проекте.

---

## 10. Что меняется для пользователя

**До PR-H:**
- Агент мог переписать `"Запросить тест-драйв"` на `"Получить предложение"` молча
- При финальной проверке косяк не виден

**После PR-H:**
- Любое отклонение от prototype.yaml ловится автоматически
- `gate-check.sh --stage 07c_composed --project <project>` падает с понятным списком расхождений
- Агент **обязан** спросить разрешение если хочет изменить текст
- Закрыть 07c невозможно пока текст не совпадает

---

## 11. Связь с другими PR

- **PR-F** (вики) — фундамент, агент знает текущий этап
- **PR-G** (Stage Lock) — фундамент hard_checks, PR-H добавляет новый hard_check
- **Premium-07b** (существующий) — параллельный hard_check на CSS-фичи, не конфликтует
- Будущее: PR-I (если понадобится) — `--allow-rewrite` флаг для редких случаев правки клиентского текста. Сейчас YAGNI.
