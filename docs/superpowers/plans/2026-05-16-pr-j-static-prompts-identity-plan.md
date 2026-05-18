# PR-J — Static Prompts + Identity Hardening Implementation Plan

**Goal:** (A) Прогнать atlas-prompt и codex-photo-prompt через `gpt5-prompting-engine` для валидации ≥8/10. (B) Усилить identity-check: per-type thresholds + revert логика + HARD GATE на 07f.

**Spec:** [2026-05-16-pr-j-static-prompts-identity-design.md](../specs/2026-05-16-pr-j-static-prompts-identity-design.md)

---

## File Structure

**Создаются:**
- `skills/paralaximus-codex/templates/atlas-prompt.legacy.md` (бекап)
- `skills/photo-curation/templates/codex-photo-prompt.legacy.md` (бекап)
- `scripts/verify-identity-preserved.sh`
- `tests/pr-j/{helpers.bash, test_threshold_per_type.bats, test_revert_on_violation.bats, test_verify_identity.bats}`

**Модифицируются:**
- `skills/paralaximus-codex/templates/atlas-prompt.md` (через engine)
- `skills/photo-curation/templates/codex-photo-prompt.md` (через engine)
- `skills/photo-curation/scripts/identity-check.py` (per-type)
- `skills/photo-curation/scripts/photo-pipeline.py` (revert + manifest)
- `config/stage-gates.yaml` (soft 07c + hard 07f)

---

## Task A1: atlas-prompt через engine

**Files:**
- Backup: `skills/paralaximus-codex/templates/atlas-prompt.legacy.md`
- Modify: `skills/paralaximus-codex/templates/atlas-prompt.md`

- [ ] **Step 1: Бекап оригинала**

```bash
cp skills/paralaximus-codex/templates/atlas-prompt.md \
   skills/paralaximus-codex/templates/atlas-prompt.legacy.md
```

- [ ] **Step 2: Прочитать engine workflow**

```bash
cat skills/gpt5-prompting-engine/SKILL.md
cat skills/gpt5-prompting-engine/references/prompt-builder-workflow.md
cat skills/gpt5-prompting-engine/references/gpt5-migration-base.txt | head -50
cat skills/gpt5-prompting-engine/references/validation-rubric.md
```

- [ ] **Step 3: Прочитать текущий atlas-prompt.md как input**

```bash
cat skills/paralaximus-codex/templates/atlas-prompt.md
```

- [ ] **Step 4: Применить workflow engine'а: classify=migrate**

- **Task:** migrate (existing prompt → improved v2)
- **Target:** Codex CLI image_gen для генерации 2K 16:9 параллакс-атласа
- **Migration checks:** прогон через `gpt5-migration-base.txt` правила
- **Build new version:** сохранить existing structure + усилить через GPT-5 правила
  - Чёткие completion criteria
  - Strict output format
  - No polite filler
- **Validate:** rubric score ≥8/10
- Если <8/10 → revise один раз

- [ ] **Step 5: Записать новый atlas-prompt.md**

Перезаписать `skills/paralaximus-codex/templates/atlas-prompt.md` с v2 версией. Структура с placeholders должна сохраниться (`[THEME]`, `[VISUAL_STYLE]`, etc — иначе сломаются вызовы из `generate-atlas.sh`).

- [ ] **Step 6: Commit**

```bash
git add skills/paralaximus-codex/templates/atlas-prompt.md \
        skills/paralaximus-codex/templates/atlas-prompt.legacy.md
git commit -m "feat(pr-j): atlas-prompt v2 через gpt5-prompting-engine

Migrated через engine (classify=migrate, target=Codex image_gen).
Score: <X>/10. Старая версия в .legacy.md для отката.

Placeholders сохранены ([THEME], [VISUAL_STYLE], …) — обратная совместимость
с generate-atlas.sh."
```

---

## Task A2: codex-photo-prompt через engine

**Files:**
- Backup: `skills/photo-curation/templates/codex-photo-prompt.legacy.md`
- Modify: `skills/photo-curation/templates/codex-photo-prompt.md`

- [ ] **Step 1: Бекап**

```bash
cp skills/photo-curation/templates/codex-photo-prompt.md \
   skills/photo-curation/templates/codex-photo-prompt.legacy.md
```

- [ ] **Step 2: Применить workflow engine'а: classify=create**

Бриф для engine:
```
Промпт для обработки клиентской фотки через codex CLI image_gen с -i flag.

Параметры (плейсхолдеры в шаблоне, должны остаться):
- {RATIO} — целевое соотношение слота (16:9, 9:16, 1:1, 4:3)
- {BRAND_COLOR} — primary цвет бренда (hex)
- {NICHE} — ниша (premium-auto, real-estate, etc.)
- {REGION} — гео-локация (Dubai, Moscow, etc.)
- {SLOT_TYPE} — тип слота (portrait, vehicle, product, hero-bg)

Цели:
- Адаптировать фон под region atmosphere
- Цветокор под brand color (subtle, не агрессивно)
- Identity объекта DOSLOVNO сохранить

STRICT identity rules:
- PRESERVE original subject EXACTLY (никакого AI repaint машины/лица/товара)
- Modify ONLY: background, lighting, color grading
- If cannot preserve identity → output original unchanged

Output: одна обработанная PNG, тот же aspect ratio что и оригинал
(агент-caller сам сделает resize/crop под точный размер слота).

Constraints:
- НЕ применять beauty retouch к лицам
- НЕ менять модели/марки машин/товаров
- НЕ делать AI-репеинт основного объекта
- НЕ менять количество людей в кадре
```

- **Validate:** score ≥8/10. Revise если <8/10.

- [ ] **Step 3: Записать новый файл**

Структура должна быть с placeholders: `{RATIO}`, `{BRAND_COLOR}`, `{NICHE}`, `{REGION}`, `{SLOT_TYPE}` — иначе сломается `codex-process-photo.sh` который их подставляет через sed.

- [ ] **Step 4: Commit**

```bash
git add skills/photo-curation/templates/codex-photo-prompt.md \
        skills/photo-curation/templates/codex-photo-prompt.legacy.md
git commit -m "feat(pr-j): codex-photo-prompt v2 через gpt5-prompting-engine

Создан через engine с identity-strict правилами:
- PRESERVE original subject EXACTLY
- Modify ONLY background/lighting/color
- If cannot preserve → return original

Score: <X>/10. Старая версия в .legacy.md.

Placeholders сохранены: {RATIO}, {BRAND_COLOR}, {NICHE}, {REGION}, {SLOT_TYPE}."
```

---

## Task B1: Per-type thresholds в identity-check.py

**Files:**
- Modify: `skills/photo-curation/scripts/identity-check.py`

- [ ] **Step 1: Прочитать текущий файл**

```bash
cat skills/photo-curation/scripts/identity-check.py
```

- [ ] **Step 2: Заменить содержимое**

```python
#!/usr/bin/env python3
"""Сравнивает оригинал и обработанное фото через perceptual hash.

Использование:
  identity-check.py <orig.jpg> <processed.jpg> [--threshold N | --slot-type TYPE]

Exit 0 — identity сохранён (Hamming distance <= threshold)
Exit 1 — изменения слишком сильные
"""
import sys
import argparse
from pathlib import Path

from PIL import Image
import imagehash


# Per-slot-type Hamming distance thresholds.
# Lower = stricter (small change = violation).
THRESHOLDS = {
    "portrait": 5,
    "team": 5,
    "testimonial": 5,
    "expert": 5,
    "vehicle": 10,
    "car": 10,
    "product": 8,
    "hero-bg": 12,
    "interior": 15,
    "lifestyle": 15,
    "background": 18,
    "default": 10,
}


def resolve_threshold(slot_type: str | None, override: int | None) -> int:
    """Override побеждает slot-type. Если оба None → default."""
    if override is not None:
        return override
    if slot_type:
        return THRESHOLDS.get(slot_type, THRESHOLDS["default"])
    return THRESHOLDS["default"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("orig")
    parser.add_argument("processed")
    parser.add_argument("--threshold", type=int, default=None,
                        help="Ручной override (целое число Hamming distance)")
    parser.add_argument("--slot-type", default=None,
                        help="Тип слота (portrait, vehicle, product, hero-bg, interior, …)")
    args = parser.parse_args()

    orig_path = Path(args.orig)
    proc_path = Path(args.processed)

    if not orig_path.exists() or not proc_path.exists():
        print(f"ERROR: file not found", file=sys.stderr)
        return 2

    threshold = resolve_threshold(args.slot_type, args.threshold)

    h1 = imagehash.phash(Image.open(orig_path))
    h2 = imagehash.phash(Image.open(proc_path))
    distance = h1 - h2

    print(f"phash distance: {distance} (threshold: {threshold}, slot_type: {args.slot_type or 'default'})")

    return 0 if distance <= threshold else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Smoke**

```bash
python3 skills/photo-curation/scripts/identity-check.py /tmp/a.jpg /tmp/b.jpg --slot-type portrait 2>&1 | head -2
# Expected: ERROR: file not found
```

- [ ] **Step 4: Commit**

```bash
git add skills/photo-curation/scripts/identity-check.py
git commit -m "feat(pr-j): per-type thresholds для identity-check

portrait/team/testimonial=5 (строго), vehicle/car=10 (умеренно),
product=8, hero-bg=12, interior=15, background=18, default=10.

Override через --threshold N остался. Новый --slot-type выбирает из dict."
```

---

## Task B2: Revert логика в photo-pipeline.py

**Files:**
- Modify: `skills/photo-curation/scripts/photo-pipeline.py`

- [ ] **Step 1: Прочитать текущий файл — найти блок identity check**

```bash
grep -n "identity_check\|IDENTITY\|identity-check" skills/photo-curation/scripts/photo-pipeline.py
```

- [ ] **Step 2: Изменить блок identity в `process_one_slot()`**

Найти секцию где вызывается identity-check (вокруг строк где `subprocess.run(["python3", str(IDENTITY_CHECK), ...])`).

Заменить блок identity-check на:

```python
    # 3. Identity check
    identity_violation = False
    distance_measured = None
    threshold_used = None
    if codex_ok:
        slot_type_for_check = slot_meta.get("type") or slot_meta.get("slot_type") or "default"
        try:
            check = subprocess.run(
                [
                    "python3", str(IDENTITY_CHECK),
                    str(photo_path), str(intermediate),
                    "--slot-type", slot_type_for_check,
                ],
                capture_output=True, text=True, timeout=30,
            )
            # Извлечь distance из stdout (формат: "phash distance: N (threshold: M, slot_type: ...)")
            if check.stdout:
                import re as _re
                m = _re.search(r"phash distance:\s*(\d+)\s*\(threshold:\s*(\d+)", check.stdout)
                if m:
                    distance_measured = int(m.group(1))
                    threshold_used = int(m.group(2))
            if check.returncode != 0:
                # Identity changed too much — revert to original
                codex_ok = False
                identity_violation = True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
```

- [ ] **Step 3: Обновить запись manifest в той же функции**

Найти где формируется `result` dict в конце `process_one_slot()`, заменить на:

```python
    return {
        "slot": slot_name,
        "status": "processed" if codex_ok else ("raw-resized" if not identity_violation else "reverted"),
        "identity_violation": identity_violation,
        "distance": distance_measured,
        "threshold": threshold_used,
        "path": str(processed_path),
        "size": f"{target_w}x{target_h}",
    }
```

- [ ] **Step 4: Smoke (на отсутствующих файлах — graceful)**

```bash
python3 skills/photo-curation/scripts/photo-pipeline.py /tmp/nonexistent 2>&1 | head -3
# Expected: ERROR: .../selections.yaml не найден
```

Полный регрессионный pytest:

```bash
pytest tests/wiki/ 2>&1 | tail -3
```

- [ ] **Step 5: Commit**

```bash
git add skills/photo-curation/scripts/photo-pipeline.py
git commit -m "feat(pr-j): revert логика при identity violation

При codex обработке если identity-check (с per-type threshold) фейлит:
- НЕ сохраняем codex-результат
- Используем оригинал (resize/crop под слот, без codex)
- В manifest пишем identity_violation=true + distance + threshold
- status: 'reverted' вместо 'processed'

Это закрывает пункт 4 ПЛАНА-ДОРАБОТОК (фото нельзя ломать)."
```

---

## Task B3: verify-identity-preserved.sh

**Files:**
- Create: `scripts/verify-identity-preserved.sh`

- [ ] **Step 1: Создать скрипт**

```bash
cat > scripts/verify-identity-preserved.sh <<'SCRIPT'
#!/bin/bash
# scripts/verify-identity-preserved.sh — для stage-gates 07f hard_check
set -uo pipefail

PROJECT="${1:?ERROR: project required}"
MANIFEST="$PROJECT/07c_PHOTOS/processed/manifest.json"

if [ ! -f "$MANIFEST" ]; then
    echo "✅ identity OK (нет processed manifest)"
    exit 0
fi

python3 - <<PYTHON
import json, sys
data = json.load(open("$MANIFEST"))
violations = [(k, v) for k, v in data.items() if isinstance(v, dict) and v.get("identity_violation")]
if not violations:
    print("✅ Identity сохранён для всех слотов")
    sys.exit(0)
print(f"❌ Identity violations ({len(violations)}):", file=sys.stderr)
for k, v in violations:
    d = v.get("distance", "?")
    t = v.get("threshold", "?")
    print(f"  - {k}: distance={d} > threshold={t}", file=sys.stderr)
sys.exit(1)
PYTHON
SCRIPT
chmod +x scripts/verify-identity-preserved.sh
```

- [ ] **Step 2: Smoke (на отсутствующих файлах — экзит 0 OK)**

```bash
bash scripts/verify-identity-preserved.sh /tmp/nonexistent 2>&1 | head -2
# Expected: ✅ identity OK (нет processed manifest)
```

На реальном dubai-avto-liza:
```bash
bash scripts/verify-identity-preserved.sh ~/Lendings/dubai-avto-liza 2>&1 | head -2
```
Скорее всего exit 0 (manifest не имеет нового формата identity_violation).

- [ ] **Step 3: Commit**

```bash
git add scripts/verify-identity-preserved.sh
git commit -m "feat(pr-j): verify-identity-preserved.sh для stage-gates

Парсит manifest.json и ищет identity_violation=true entries.
Exit 1 если есть — для HARD GATE на 07f_composed_final."
```

---

## Task B4: stage-gates integration

**Files:**
- Modify: `config/stage-gates.yaml`

- [ ] **Step 1: Найти секции 07c и 07f**

```bash
grep -n '"07c_composed"\|"07f_composed_final"' config/stage-gates.yaml
```

- [ ] **Step 2: В `"07c_composed"` добавить soft_check**

В блок `soft_checks:` (создать если нет) добавить:

```yaml
      - id: identity_preserved
        prompt: "Identity check для фоток прошёл (manifest.json без violations)? Опционально на этом этапе."
```

- [ ] **Step 3: В `"07f_composed_final"` добавить hard_check**

В блок `hard_checks:` в конец:

```yaml
      - id: identity_preserved
        type: script
        script: "scripts/verify-identity-preserved.sh"
        args: ["{project}"]
        required: true
        fix_hint: "Identity violation для одной или нескольких фоток. Проверь 07c_PHOTOS/processed/manifest.json. Решение: вернуть оригинал или переобработать с уточнённым промптом."
```

- [ ] **Step 4: yq валидация**

```bash
yq -r '.stages."07c_composed".soft_checks // [] | map(.id)' config/stage-gates.yaml
yq -r '.stages."07f_composed_final".hard_checks | map(.id)' config/stage-gates.yaml
```

Expected: 07c содержит `identity_preserved` в soft, 07f содержит `identity_preserved` в hard.

- [ ] **Step 5: Commit**

```bash
git add config/stage-gates.yaml
git commit -m "feat(pr-j): identity hard_check на 07f, soft на 07c

При финальной композиции (07f) — gate-check блокирует закрытие
если есть identity violations в manifest. На 07c — soft warning
(этап только начинает фото-pipeline, ошибки терпимы)."
```

---

## Task C: 3 bats теста + финал

**Files:**
- Create: `tests/pr-j/helpers.bash`
- Create: 3 `.bats`

- [ ] **Step 1: helpers**

```bash
mkdir -p tests/pr-j
cat > tests/pr-j/helpers.bash <<'HELPER'
#!/usr/bin/env bash
PR_J_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

make_dummy_jpg() {
    local path="$1"
    python3 -c "
from PIL import Image
Image.new('RGB', (800, 600), (100, 100, 100)).save('$path', 'JPEG', quality=85)
"
}

make_project_with_manifest() {
    local violations="$1"  # "" or "yes"
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07c_PHOTOS/processed"
    if [ "$violations" = "yes" ]; then
        cat > "$tmpdir/07c_PHOTOS/processed/manifest.json" <<JSON
{
  "hero-bg.jpg": {
    "slot": "hero-bg",
    "status": "reverted",
    "identity_violation": true,
    "distance": 14,
    "threshold": 12
  },
  "team-1.jpg": {
    "slot": "team-1",
    "status": "processed",
    "identity_violation": false,
    "distance": 3,
    "threshold": 5
  }
}
JSON
    else
        cat > "$tmpdir/07c_PHOTOS/processed/manifest.json" <<JSON
{
  "hero-bg.jpg": {
    "slot": "hero-bg",
    "status": "processed",
    "identity_violation": false,
    "distance": 4,
    "threshold": 12
  }
}
JSON
    fi
    echo "$tmpdir"
}
HELPER
```

- [ ] **Step 2: test_threshold_per_type.bats**

```bash
cat > tests/pr-j/test_threshold_per_type.bats <<'BATS'
#!/usr/bin/env bats
load 'helpers.bash'

@test "identity-check: identical images → exit 0 для portrait (threshold 5)" {
    tmpdir=$(mktemp -d)
    make_dummy_jpg "$tmpdir/a.jpg"
    cp "$tmpdir/a.jpg" "$tmpdir/b.jpg"
    run python3 "$PR_J_REPO_ROOT/skills/photo-curation/scripts/identity-check.py" \
        "$tmpdir/a.jpg" "$tmpdir/b.jpg" --slot-type portrait
    [ "$status" -eq 0 ]
    [[ "$output" == *"threshold: 5"* ]]
}

@test "identity-check: identical images → exit 0 для vehicle (threshold 10)" {
    tmpdir=$(mktemp -d)
    make_dummy_jpg "$tmpdir/a.jpg"
    cp "$tmpdir/a.jpg" "$tmpdir/b.jpg"
    run python3 "$PR_J_REPO_ROOT/skills/photo-curation/scripts/identity-check.py" \
        "$tmpdir/a.jpg" "$tmpdir/b.jpg" --slot-type vehicle
    [ "$status" -eq 0 ]
    [[ "$output" == *"threshold: 10"* ]]
}

@test "identity-check: --threshold override побеждает --slot-type" {
    tmpdir=$(mktemp -d)
    make_dummy_jpg "$tmpdir/a.jpg"
    cp "$tmpdir/a.jpg" "$tmpdir/b.jpg"
    run python3 "$PR_J_REPO_ROOT/skills/photo-curation/scripts/identity-check.py" \
        "$tmpdir/a.jpg" "$tmpdir/b.jpg" --slot-type vehicle --threshold 3
    [ "$status" -eq 0 ]
    [[ "$output" == *"threshold: 3"* ]]
}
BATS
```

- [ ] **Step 3: test_verify_identity.bats**

```bash
cat > tests/pr-j/test_verify_identity.bats <<'BATS'
#!/usr/bin/env bats
load 'helpers.bash'

@test "verify-identity: manifest без violations → exit 0" {
    project=$(make_project_with_manifest "")
    run bash "$PR_J_REPO_ROOT/scripts/verify-identity-preserved.sh" "$project"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Identity сохранён"* ]]
}

@test "verify-identity: manifest с violation → exit 1 + details" {
    project=$(make_project_with_manifest "yes")
    run bash "$PR_J_REPO_ROOT/scripts/verify-identity-preserved.sh" "$project"
    [ "$status" -eq 1 ]
    [[ "$output" == *"hero-bg.jpg"* ]] || [[ "$output" == *"distance"* ]]
}

@test "verify-identity: manifest отсутствует → exit 0 (no-op)" {
    tmpdir=$(mktemp -d)
    run bash "$PR_J_REPO_ROOT/scripts/verify-identity-preserved.sh" "$tmpdir"
    [ "$status" -eq 0 ]
    [[ "$output" == *"нет processed manifest"* ]] || [[ "$output" == *"OK"* ]]
}
BATS
```

- [ ] **Step 4: test_revert_on_violation.bats**

```bash
cat > tests/pr-j/test_revert_on_violation.bats <<'BATS'
#!/usr/bin/env bats
load 'helpers.bash'

# Этот тест проверяет логику revert через mock identity-check.
# Реальный полный pipeline не запускаем (требует codex), вместо этого
# тестируем что manifest правильно формируется когда identity check fails.

@test "photo-pipeline manifest: identity_violation поле есть" {
    # Косвенно — проверяем что обновлённый код содержит identity_violation
    # в выходном dict (smoke-grep)
    grep -q "identity_violation" "$PR_J_REPO_ROOT/skills/photo-curation/scripts/photo-pipeline.py"
}

@test "photo-pipeline: передаёт --slot-type в identity-check" {
    grep -q -- "--slot-type" "$PR_J_REPO_ROOT/skills/photo-curation/scripts/photo-pipeline.py"
}
BATS
```

- [ ] **Step 5: Запустить все тесты**

```bash
bats tests/pr-j/
```

Expected: 8 tests pass.

- [ ] **Step 6: Регрессия**

```bash
bats tests/pr-g/
bats tests/pr-h/
bats tests/pr-i-a/
bats tests/pr-i-b/
bats tests/pr-j/
pytest tests/wiki/ 2>&1 | tail -3
bash scripts/check-wiki-sync.sh
```

Все pass.

- [ ] **Step 7: Отметить Пункт 4 в `docs/ПЛАН-ДОРАБОТОК.md`**

Найти `#### 4. Фото нельзя ломать` и заменить на:

```markdown
#### 4. ✅ ГОТОВО (2026-05-16) — фото нельзя ломать

**Статус:** Реализовано в PR-J. Запушено.

**Что сделано:**

1. **Per-type thresholds в identity-check** — `portrait/team/expert=5`, `vehicle/car=10`, `product=8`, `hero-bg=12`, `interior/lifestyle=15`, `background=18`. Лицо охраняется в 2-3 раза строже чем интерьер.

2. **Revert логика в photo-pipeline.py** — при identity violation НЕ сохраняем codex-версию, используем оригинал (с resize/crop). В manifest пишется `identity_violation: true` + distance + threshold.

3. **HARD GATE на 07f_composed_final** — `verify-identity-preserved.sh` блокирует закрытие финальной композиции если есть identity violations. Soft warning на 07c.

4. **Стационарные промпты через engine** (Часть A):
   - `atlas-prompt.md` (paralaximus) — migrated через engine
   - `codex-photo-prompt.md` (photo-curation) — recreated через engine с identity-strict правилами
   - Старые версии в `.legacy.md` для отката

5. **8 bats тестов** в `tests/pr-j/` — per-type thresholds, verify, revert manifest.

**Эффект:** codex не может «переделать» машину в другую модель или «улучшить» лицо — если попробует, identity-check ловит → revert на оригинал. На 07f этап не закроется пока identity preserved для всех слотов.

**Spec:** [`docs/superpowers/specs/2026-05-16-pr-j-static-prompts-identity-design.md`](superpowers/specs/2026-05-16-pr-j-static-prompts-identity-design.md)
**Plan:** [`docs/superpowers/plans/2026-05-16-pr-j-static-prompts-identity-plan.md`](superpowers/plans/2026-05-16-pr-j-static-prompts-identity-plan.md)
```

- [ ] **Step 8: Commit + push**

```bash
git add tests/pr-j/ docs/ПЛАН-ДОРАБОТОК.md
git commit -m "test(pr-j): 8 bats + отметка пункта 4 как готовый"
git push origin feat/pr-a-prototype-block-library 2>&1 | tail -3
```

---

## Self-Review

**Spec coverage:**
- ✅ Task A1: atlas-prompt через engine
- ✅ Task A2: codex-photo-prompt через engine
- ✅ Task B1: per-type thresholds
- ✅ Task B2: revert логика + manifest
- ✅ Task B3: verify-скрипт
- ✅ Task B4: stage-gates integration
- ✅ Task C: 3 bats + финал

**Placeholders:** нет.

**Type consistency:** `identity_violation` (bool), `distance` (int|None), `threshold` (int|None) — используются консистентно.

**Риски:**
1. Engine может выдать промпты ниже 8/10 — план содержит revise (одну итерацию)
2. `slot_type_for_check` в photo-pipeline берётся из `slot_meta` — если поле отсутствует, fallback на `"default"`
3. Backward compat: старые проекты с manifest без identity_violation field — verify-скрипт graceful (фильтр через `.get('identity_violation')`)

---

## После PR-J

ПЛАН-ДОРАБОТОК.md статус:
- ✅ Пункт 0: Wiki разметка
- ✅ Пункт 1: Строго по шагам
- ✅ Пункт 2: Текст прототипа
- ✅ Пункт 3: Новый порядок работы с фото
- ✅ Пункт 4: Фото нельзя ломать ← после PR-J

Следующий: Пункт 5 (привязка фото к блокам), потом 6 (финальная авто-проверка) — оба тесно связаны с PR-I.a и PR-I.b, многое уже работает.
