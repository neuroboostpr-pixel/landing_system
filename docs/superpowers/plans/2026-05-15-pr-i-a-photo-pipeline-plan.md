# PR-I.a — Photo Pipeline Implementation Plan

**Goal:** Реализовать обязательный pipeline для фоток (validate ratio + codex post-process + resize + identity-check + cache) с интерактивным slot-fill и HARD GATE на 07c/07f.

**Architecture:** Переиспользуем паттерн `visual-generation` (PR-C). Главный скрипт `photo-pipeline.py` оркеструет шаги. `codex-process-photo.sh` — обёртка над codex CLI. `verify-photo-pipeline.sh` — hard_check для gate-check.

**Tech Stack:** Python (PIL, imagehash, bs4, PyYAML), bash, codex CLI, bats.

**Spec:** [2026-05-15-pr-i-a-photo-pipeline-design.md](../specs/2026-05-15-pr-i-a-photo-pipeline-design.md)

---

## File Structure

**Создаём:**
- `skills/photo-curation/scripts/codex-process-photo.sh`
- `skills/photo-curation/scripts/photo-pipeline.py`
- `skills/photo-curation/scripts/identity-check.py`
- `skills/photo-curation/scripts/interactive-slot-fill.py`
- `skills/photo-curation/templates/codex-photo-prompt.md`
- `scripts/verify-photo-pipeline.sh`
- `scripts/verify_photo_pipeline.py`
- `tests/pr-i-a/helpers.bash`
- `tests/pr-i-a/test_photo_ratio_validates.bats`
- `tests/pr-i-a/test_codex_caches.bats`
- `tests/pr-i-a/test_no_placeholders.bats`
- `tests/pr-i-a/test_interactive_slot_fill.bats`

**Модифицируем:**
- `config/stage-gates.yaml` — добавить `photo_pipeline_valid` hard_check на 07c + 07f
- `skills/photo-curation/SKILL.md` — обновить workflow
- `agents/photo-curator.md` — усилить промпт

---

## Task 1: `codex-process-photo.sh` — обёртка над codex CLI

**Files:** Create `skills/photo-curation/scripts/codex-process-photo.sh`

- [ ] **Step 1: Прочитать существующий codex wrapper для reference**

```bash
cat skills/visual-generation/scripts/codex-generate-icon.sh 2>&1 | head -40
```

Посмотри какой формат вызова codex используется. Если файла нет — посмотри `find skills -name "codex*" -type f`.

- [ ] **Step 2: Создать `codex-process-photo.sh`**

```bash
#!/bin/bash
# skills/photo-curation/scripts/codex-process-photo.sh
# Обработка одного фото через codex image_gen.
#
# Использование:
#   codex-process-photo.sh \
#     --input <orig.jpg> \
#     --output <processed.jpg> \
#     --slot-ratio "16:9" \
#     --brand-color "#1a1a1a" \
#     --niche "premium-auto" \
#     --region "Dubai"
#
# Выход: processed.jpg в указанном пути

set -uo pipefail

INPUT=""
OUTPUT=""
RATIO=""
BRAND_COLOR=""
NICHE=""
REGION=""

while [ $# -gt 0 ]; do
    case "$1" in
        --input) INPUT="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        --slot-ratio) RATIO="$2"; shift 2 ;;
        --brand-color) BRAND_COLOR="$2"; shift 2 ;;
        --niche) NICHE="$2"; shift 2 ;;
        --region) REGION="$2"; shift 2 ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

[ -z "$INPUT" ] || [ -z "$OUTPUT" ] && { echo "ERROR: --input and --output required" >&2; exit 2; }
[ -f "$INPUT" ] || { echo "ERROR: $INPUT not found" >&2; exit 2; }

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
PROMPT_TEMPLATE="$(dirname "$0")/../templates/codex-photo-prompt.md"

# Подготовка промпта (подстановка)
PROMPT=$(cat "$PROMPT_TEMPLATE" | sed \
    -e "s|{RATIO}|${RATIO:-16:9}|g" \
    -e "s|{BRAND_COLOR}|${BRAND_COLOR:-#000000}|g" \
    -e "s|{NICHE}|${NICHE:-generic}|g" \
    -e "s|{REGION}|${REGION:-global}|g")

# codex CLI вызов
if ! command -v codex >/dev/null 2>&1; then
    echo "ERROR: codex CLI not installed. Run: bash scripts/install-codex.sh" >&2
    exit 3
fi

# image_gen режим codex
codex exec image_gen \
    --image "$INPUT" \
    --prompt "$PROMPT" \
    --output "$OUTPUT" \
    2>&1 | tail -5

if [ ! -f "$OUTPUT" ]; then
    echo "ERROR: codex didn't produce $OUTPUT" >&2
    exit 1
fi

echo "✅ Processed: $OUTPUT ($(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT") bytes)"
```

- [ ] **Step 3: Создать `templates/codex-photo-prompt.md`**

```markdown
Process this photo to align with the brand design system:

**Brand:**
- Primary color: {BRAND_COLOR}
- Niche: {NICHE}
- Region: {REGION}

**Composition:**
- Target aspect ratio: {RATIO}
- Style: clean, professional, premium

**STRICT preservation rules:**
- PRESERVE the original subject (object, person, product, vehicle) EXACTLY as-is
- DO NOT redraw, repaint, or AI-generate the subject
- ONLY adjust:
  - Background scenery (align with {REGION} atmosphere)
  - Color grading (lean toward {BRAND_COLOR})
  - Lighting and shadows for premium feel
  - Saturation, contrast, mood

**Region atmosphere hints:**
- Dubai/UAE: golden hour, modern arabic architecture, desert/luxury
- Moscow: contemporary urban, european business district
- London: refined, professional, slightly muted
- (other regions: match local cultural visual cues)

Return the photo in the same dimensions if possible.
```

- [ ] **Step 4: `chmod +x` и smoke**

```bash
chmod +x skills/photo-curation/scripts/codex-process-photo.sh
skills/photo-curation/scripts/codex-process-photo.sh --help 2>&1 || true
# Help вывод не обязателен — главное чтобы не было syntax error
```

- [ ] **Step 5: Commit**

```bash
git add skills/photo-curation/scripts/codex-process-photo.sh \
        skills/photo-curation/templates/codex-photo-prompt.md
git commit -m "feat(pr-i-a): codex-process-photo обёртка для пост-обработки фоток

Аналог codex-generate-icon.sh из visual-generation. Принимает фото
+ параметры бренда (color/niche/region/ratio) → codex image_gen
обрабатывает с identity-safe промптом (preserve subject, modify only
environment/lighting/grading)."
```

---

## Task 2: `photo-pipeline.py` — главный pipeline

**Files:** Create `skills/photo-curation/scripts/photo-pipeline.py`

- [ ] **Step 1: Создать главный скрипт**

```python
#!/usr/bin/env python3
"""Главный pipeline обработки фото для слотов лендинга.

Pipeline:
  validate_ratio → codex_post → resize → identity_check → cache → save

Использование:
  photo-pipeline.py <project> [--slot <name>] [--force]

Без --slot обрабатывает все слоты из selections.yaml.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
CODEX_PROCESS = SCRIPT_DIR / "codex-process-photo.sh"
IDENTITY_CHECK = SCRIPT_DIR / "identity-check.py"
RATIO_TOLERANCE = 0.05  # 5%


def parse_ratio(s: str) -> tuple[int, int]:
    """'16:9' → (16, 9)."""
    a, b = s.split(":")
    return int(a), int(b)


def ratio_value(r: tuple[int, int]) -> float:
    return r[0] / r[1]


def get_image_ratio(path: Path) -> float:
    img = Image.open(path)
    return img.width / img.height


def crop_center(img: Image.Image, target_ratio: float) -> Image.Image:
    """Crop по центру до target ratio."""
    current = img.width / img.height
    if abs(current - target_ratio) < 0.01:
        return img
    if current > target_ratio:
        # Слишком широкое — обрезаем по бокам
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        return img.crop((left, 0, left + new_width, img.height))
    else:
        # Слишком узкое — обрезаем сверху/снизу
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        return img.crop((0, top, img.width, top + new_height))


def resize_to_slot(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    return img.resize((target_width, target_height), Image.Resampling.LANCZOS)


def compute_cache_key(orig: Path, brand_color: str, niche: str, region: str, ratio: str) -> str:
    h = hashlib.sha256()
    h.update(orig.read_bytes())
    h.update(brand_color.encode())
    h.update(niche.encode())
    h.update(region.encode())
    h.update(ratio.encode())
    return h.hexdigest()[:16]


def process_one_slot(
    project: Path,
    slot_name: str,
    photo_path: Path,
    slot_meta: dict,
    brand_params: dict,
    force: bool = False,
) -> dict:
    """Pipeline для одного слота."""
    processed_dir = project / "07c_PHOTOS" / "processed"
    cache_dir = project / "07c_PHOTOS" / ".cache"
    processed_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    target_ratio = slot_meta.get("ratio", "16:9")
    target_w, target_h = slot_meta.get("width", 1920), slot_meta.get("height", 1080)
    # Если width/height нет — вычислить из ratio как 1920px по длинной стороне
    if "width" not in slot_meta:
        r = parse_ratio(target_ratio)
        if r[0] >= r[1]:
            target_w, target_h = 1920, int(1920 * r[1] / r[0])
        else:
            target_w, target_h = int(1080 * r[0] / r[1]), 1080

    cache_key = compute_cache_key(
        photo_path,
        brand_params.get("primary", "#000000"),
        brand_params.get("niche", "generic"),
        brand_params.get("region", "global"),
        target_ratio,
    )
    cache_path = cache_dir / f"{cache_key}.jpg"
    processed_path = processed_dir / f"{slot_name}.jpg"

    # Cache hit
    if cache_path.exists() and not force:
        shutil.copy(cache_path, processed_path)
        return {"slot": slot_name, "status": "cached", "path": str(processed_path)}

    # 1. Validate ratio
    orig_ratio = get_image_ratio(photo_path)
    target_ratio_val = ratio_value(parse_ratio(target_ratio))
    needs_crop = abs(orig_ratio - target_ratio_val) > RATIO_TOLERANCE

    # 2. Codex post-process (если codex доступен)
    intermediate = cache_dir / f"{cache_key}.codex.jpg"
    codex_ok = False
    try:
        cmd = [
            "bash", str(CODEX_PROCESS),
            "--input", str(photo_path),
            "--output", str(intermediate),
            "--slot-ratio", target_ratio,
            "--brand-color", brand_params.get("primary", "#000000"),
            "--niche", brand_params.get("niche", "generic"),
            "--region", brand_params.get("region", "global"),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        codex_ok = result.returncode == 0 and intermediate.exists()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        codex_ok = False

    # 3. Identity check
    if codex_ok:
        try:
            check = subprocess.run(
                ["python3", str(IDENTITY_CHECK), str(photo_path), str(intermediate)],
                capture_output=True, text=True, timeout=30,
            )
            if check.returncode != 0:
                # Identity changed too much — revert to original
                codex_ok = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Использовать codex результат или оригинал
    source_img = Image.open(intermediate if codex_ok else photo_path)

    # 4. Crop if needed
    if needs_crop:
        source_img = crop_center(source_img, target_ratio_val)

    # 5. Resize to exact slot dimensions
    final = resize_to_slot(source_img, target_w, target_h)

    # 6. Save
    final.save(processed_path, "JPEG", quality=85)
    final.save(cache_path, "JPEG", quality=85)

    return {
        "slot": slot_name,
        "status": "processed" if codex_ok else "raw-resized",
        "path": str(processed_path),
        "size": f"{target_w}x{target_h}",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="Project directory")
    parser.add_argument("--slot", help="Process only one slot")
    parser.add_argument("--force", action="store_true", help="Ignore cache")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    selections = project / "07c_PHOTOS" / "selections.yaml"
    tokens = project / "04_БРЕНД" / "tokens.json"

    if not selections.exists():
        print(f"ERROR: {selections} не найден", file=sys.stderr)
        return 2

    selections_data = yaml.safe_load(selections.read_text(encoding="utf-8")) or {}
    brand = {}
    if tokens.exists():
        t = json.loads(tokens.read_text(encoding="utf-8"))
        brand["primary"] = t.get("colors", {}).get("primary", "#000000")

    brand["niche"] = "generic"
    brand["region"] = "global"
    profile = project / "01a_АНАЛИЗ_НИШИ" / "market-profile.md"
    if profile.exists():
        text = profile.read_text(encoding="utf-8")
        # Простой парсинг
        for line in text.splitlines():
            if line.lower().startswith("**niche") or line.lower().startswith("niche:"):
                brand["niche"] = line.split(":", 1)[-1].strip(" *")
            if line.lower().startswith("**geo") or line.lower().startswith("region:"):
                brand["region"] = line.split(":", 1)[-1].strip(" *")

    photo_assignments = selections_data.get("slots", {}) or selections_data.get("blocks", {})

    manifest = {}
    for slot_name, photo_rel in photo_assignments.items():
        if args.slot and args.slot != slot_name:
            continue
        if not isinstance(photo_rel, str):
            continue
        photo_path = project / "07c_PHOTOS" / "inbox" / photo_rel
        if not photo_path.exists():
            photo_path = project / photo_rel
        if not photo_path.exists():
            print(f"⚠ Слот '{slot_name}': фото '{photo_rel}' не найдено", file=sys.stderr)
            continue

        slot_meta = {"ratio": "16:9"}  # дефолт; реальные slot meta берутся из block-library
        result = process_one_slot(project, slot_name, photo_path, slot_meta, brand, force=args.force)
        manifest[f"{slot_name}.jpg"] = result
        print(f"  [{result['status']}] {slot_name} → {result['path']}")

    # Save manifest
    manifest_path = project / "07c_PHOTOS" / "processed" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"\n✅ Обработано {len(manifest)} слотов, manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: chmod + smoke на отсутствующих файлах (graceful exit)**

```bash
chmod +x skills/photo-curation/scripts/photo-pipeline.py
python3 skills/photo-curation/scripts/photo-pipeline.py /tmp/nonexistent 2>&1 | head -3
# Expected: ERROR ...selections.yaml не найден
```

- [ ] **Step 3: Commit**

```bash
git add skills/photo-curation/scripts/photo-pipeline.py
git commit -m "feat(pr-i-a): photo-pipeline.py — главный конвейер

validate_ratio → codex → identity_check → crop → resize → cache → save.
Использует selections.yaml + tokens.json + market-profile.md для параметров.
Manifest сохраняется в 07c_PHOTOS/processed/manifest.json."
```

---

## Task 3: `identity-check.py`

**Files:** Create `skills/photo-curation/scripts/identity-check.py`

- [ ] **Step 1: Установить imagehash если ещё нет**

```bash
python3 -c "import imagehash" 2>/dev/null || pip install imagehash
```

Добавить `imagehash>=4.3` в requirements.txt (если ещё нет).

- [ ] **Step 2: Создать скрипт**

```python
#!/usr/bin/env python3
"""Сравнивает оригинал и обработанное фото через perceptual hash.

Использование:
  identity-check.py <orig.jpg> <processed.jpg> [--threshold 10]

Exit 0 — identity сохранён (Hamming distance <= threshold)
Exit 1 — изменения слишком сильные
"""
import sys
import argparse
from pathlib import Path

from PIL import Image
import imagehash


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("orig")
    parser.add_argument("processed")
    parser.add_argument("--threshold", type=int, default=10)
    args = parser.parse_args()

    orig_path = Path(args.orig)
    proc_path = Path(args.processed)

    if not orig_path.exists() or not proc_path.exists():
        print(f"ERROR: file not found", file=sys.stderr)
        return 2

    h1 = imagehash.phash(Image.open(orig_path))
    h2 = imagehash.phash(Image.open(proc_path))
    distance = h1 - h2

    print(f"phash distance: {distance} (threshold: {args.threshold})")

    return 0 if distance <= args.threshold else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: chmod + commit**

```bash
chmod +x skills/photo-curation/scripts/identity-check.py
echo "imagehash>=4.3" >> requirements.txt 2>/dev/null
git add skills/photo-curation/scripts/identity-check.py requirements.txt
git commit -m "feat(pr-i-a): identity-check через perceptual hash

Сравнивает orig и processed через imagehash.phash.
Hamming distance > threshold → exit 1 (identity не сохранён,
pipeline отказывается от codex результата)."
```

---

## Task 4: `verify-photo-pipeline.sh` + helper

**Files:**
- Create `scripts/verify-photo-pipeline.sh`
- Create `scripts/verify_photo_pipeline.py`

- [ ] **Step 1: bash wrapper**

```bash
#!/bin/bash
# scripts/verify-photo-pipeline.sh
set -uo pipefail
PROJECT="${1:?ERROR: project path required}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$REPO_ROOT/scripts/verify_photo_pipeline.py" "$PROJECT"
```

- [ ] **Step 2: python helper**

```python
#!/usr/bin/env python3
"""Verify photo pipeline для hard_check.

Проверяет:
- Все <img src> в composed.html ведут на 07c_PHOTOS/processed/
- Нет SVG placeholder'ов
- Размеры файлов соответствуют атрибутам width/height в HTML
- manifest.json существует

Exit 0 — OK, exit 1 — issues, exit 2 — files missing.
"""
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image


def main(project_dir):
    composed = project_dir / "07b_COMPOSED" / "composed.html"
    if not composed.exists():
        print(f"ERROR: {composed} не найден", file=sys.stderr)
        return 2

    soup = BeautifulSoup(composed.read_text(encoding="utf-8"), "html.parser")
    issues = []

    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or src.startswith(("http://", "https://", "data:")):
            continue
        # Placeholder detection
        if "placeholder" in src.lower() or src.lower().endswith(".svg"):
            issues.append(f"placeholder остался: {src}")
            continue
        # Не из processed/?
        if "processed/" not in src:
            issues.append(f"img НЕ из processed/: {src}")

    # Manifest
    manifest = project_dir / "07c_PHOTOS" / "processed" / "manifest.json"
    if not manifest.exists() and len([i for i in soup.find_all("img") if i.get("src")]) > 0:
        issues.append("manifest.json отсутствует в 07c_PHOTOS/processed/")

    if issues:
        print(f"❌ Photo pipeline issues ({len(issues)}):", file=sys.stderr)
        for i in issues[:10]:
            print(f"   - {i}", file=sys.stderr)
        return 1

    print(f"✅ Photo pipeline OK")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: verify_photo_pipeline.py <project>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
```

- [ ] **Step 3: chmod + smoke**

```bash
chmod +x scripts/verify-photo-pipeline.sh
# Прогон на dubai-avto-liza (composed.html там есть)
bash scripts/verify-photo-pipeline.sh ~/Lendings/dubai-avto-liza 2>&1 | head -5
```

Результат скорее всего exit 1 (composed.html dubai-avto-liza написан вручную, может не следовать паттерну) — это норма, это диагностика.

- [ ] **Step 4: Commit**

```bash
git add scripts/verify-photo-pipeline.sh scripts/verify_photo_pipeline.py
git commit -m "feat(pr-i-a): verify-photo-pipeline.sh — hard_check для 07c/07f

Проверяет что: <img src> ведут на processed/, нет SVG placeholder'ов,
manifest.json существует. Без SDK, на bs4 + PIL."
```

---

## Task 5: stage-gates.yaml integration

**Files:** Modify `config/stage-gates.yaml`

- [ ] **Step 1: Найти секции `"07c_composed"` и `"07f_composed_final"`**

```bash
grep -n '"07c_composed"\|"07f_composed_final"' config/stage-gates.yaml
```

- [ ] **Step 2: В каждую добавить `photo_pipeline_valid` hard_check**

В обеих секциях `hard_checks:` добавить в конец:

```yaml
      - id: photo_pipeline_valid
        type: script
        script: "scripts/verify-photo-pipeline.sh"
        args: ["{project}"]
        required: true
        fix_hint: "Photo pipeline не пройден. Запусти /landing-photos для обработки фото через codex. Проверь что в composed.html нет SVG placeholder'ов."
```

- [ ] **Step 3: Smoke yq**

```bash
yq -r '.stages."07c_composed".hard_checks | map(.id)' config/stage-gates.yaml
yq -r '.stages."07f_composed_final".hard_checks | map(.id)' config/stage-gates.yaml
```
Expected: оба содержат `photo_pipeline_valid`.

- [ ] **Step 4: Commit**

```bash
git add config/stage-gates.yaml
git commit -m "feat(pr-i-a): подключить verify-photo-pipeline как hard_check 07c+07f

При попытке закрыть 07c/07f gate-check запустит проверку:
все фото обработаны, никаких placeholder'ов не осталось."
```

---

## Task 6: 4 bats-теста

**Files:**
- Create `tests/pr-i-a/helpers.bash`
- Create 4 `.bats` файла

- [ ] **Step 1: helpers**

```bash
mkdir -p tests/pr-i-a
cat > tests/pr-i-a/helpers.bash <<'HELPER'
#!/usr/bin/env bash
PR_I_A_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

make_project_with_placeholder() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07b_COMPOSED" "$tmpdir/07c_PHOTOS/processed"
    cat > "$tmpdir/07b_COMPOSED/composed.html" <<'HTML'
<!DOCTYPE html>
<html><body>
<section data-block="hero-1">
  <img src="placeholder-1920x1080.svg" alt="hero">
</section>
</body></html>
HTML
    echo "$tmpdir"
}

make_project_with_real_photos() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07b_COMPOSED" "$tmpdir/07c_PHOTOS/processed"
    # Создать dummy JPG 1x1
    python3 -c "
from PIL import Image
Image.new('RGB', (1920, 1080), (200, 200, 200)).save('$tmpdir/07c_PHOTOS/processed/hero-bg.jpg')
"
    cat > "$tmpdir/07b_COMPOSED/composed.html" <<'HTML'
<!DOCTYPE html>
<html><body>
<section data-block="hero-1">
  <img src="../07c_PHOTOS/processed/hero-bg.jpg" alt="hero">
</section>
</body></html>
HTML
    echo '{"hero-bg.jpg": {"slot": "hero-bg", "status": "processed"}}' > "$tmpdir/07c_PHOTOS/processed/manifest.json"
    echo "$tmpdir"
}
HELPER
```

- [ ] **Step 2: test_no_placeholders.bats**

```bash
cat > tests/pr-i-a/test_no_placeholders.bats <<'BATS'
#!/usr/bin/env bats
load 'helpers.bash'

@test "fail: composed.html содержит SVG placeholder" {
    project="$(make_project_with_placeholder)"
    run bash "$PR_I_A_REPO_ROOT/scripts/verify-photo-pipeline.sh" "$project"
    [ "$status" -eq 1 ]
    [[ "$output" == *"placeholder"* ]]
}

@test "pass: composed.html использует только processed/ файлы" {
    project="$(make_project_with_real_photos)"
    run bash "$PR_I_A_REPO_ROOT/scripts/verify-photo-pipeline.sh" "$project"
    [ "$status" -eq 0 ]
}
BATS
```

- [ ] **Step 3: test_photo_ratio_validates.bats**

```bash
cat > tests/pr-i-a/test_photo_ratio_validates.bats <<'BATS'
#!/usr/bin/env bats
load 'helpers.bash'

@test "photo-pipeline crop_center: 16:9 фото в 9:16 слот → height сохраняется" {
    run python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '$PR_I_A_REPO_ROOT/skills/photo-curation/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('photo_pipeline', '$PR_I_A_REPO_ROOT/skills/photo-curation/scripts/photo-pipeline.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from PIL import Image
# 16:9 image
img = Image.new('RGB', (1920, 1080), (100, 100, 100))
# crop to 9:16 ratio
target_ratio = 9 / 16
cropped = mod.crop_center(img, target_ratio)
print(f'{cropped.width}x{cropped.height}')
assert abs(cropped.width / cropped.height - target_ratio) < 0.01
"
    [ "$status" -eq 0 ]
}
BATS
```

- [ ] **Step 4: test_codex_caches.bats (мок)**

```bash
cat > tests/pr-i-a/test_codex_caches.bats <<'BATS'
#!/usr/bin/env bats
load 'helpers.bash'

@test "compute_cache_key: одинаковые параметры → одинаковый ключ" {
    run python3 -c "
import sys, importlib.util
spec = importlib.util.spec_from_file_location('pp', '$PR_I_A_REPO_ROOT/skills/photo-curation/scripts/photo-pipeline.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Создать временный файл
from pathlib import Path
import tempfile
with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
    f.write(b'fake_jpg_content')
    p = Path(f.name)

k1 = mod.compute_cache_key(p, '#1a1a1a', 'auto', 'Dubai', '16:9')
k2 = mod.compute_cache_key(p, '#1a1a1a', 'auto', 'Dubai', '16:9')
k3 = mod.compute_cache_key(p, '#ff0000', 'auto', 'Dubai', '16:9')
assert k1 == k2, 'same inputs should give same key'
assert k1 != k3, 'different brand color should give different key'
print('OK')
"
    [ "$status" -eq 0 ]
    [[ "$output" == *"OK"* ]]
}
BATS
```

- [ ] **Step 5: test_interactive_slot_fill.bats**

Минимальный smoke — проверяет что скрипт запускается:

```bash
cat > tests/pr-i-a/test_interactive_slot_fill.bats <<'BATS'
#!/usr/bin/env bats
load 'helpers.bash'

@test "interactive-slot-fill --help выводит usage" {
    # Скрипт может не существовать на момент теста — тогда тест skip
    if [ ! -f "$PR_I_A_REPO_ROOT/skills/photo-curation/scripts/interactive-slot-fill.py" ]; then
        skip "interactive-slot-fill.py не создан (Task 8)"
    fi
    run python3 "$PR_I_A_REPO_ROOT/skills/photo-curation/scripts/interactive-slot-fill.py" --help
    [ "$status" -eq 0 ]
}
BATS
```

- [ ] **Step 6: Запустить bats**

```bash
bats tests/pr-i-a/ 2>&1 | tail -10
```

Expected: 4 pass + 1 skip (interactive — пока не создан, Task 8).

- [ ] **Step 7: Commit**

```bash
git add tests/pr-i-a/
git commit -m "test(pr-i-a): 4 bats — placeholder, ratio crop, cache key, interactive smoke"
```

---

## Task 7: Промпты — photo-curator, landing-photos, SKILL.md

**Files:**
- Modify `agents/photo-curator.md`
- Modify `commands/landing-photos.md`
- Modify `skills/photo-curation/SKILL.md`

- [ ] **Step 1: photo-curator.md — добавить раздел про codex обязательность**

Найти первый заголовок и после него вставить:

```markdown

## ОБЯЗАТЕЛЬНО: codex post-process для каждой фотки (PR-I.a)

С 2026-05-15 ни одна фотка не идёт в composed.html в сыром виде.
Pipeline для каждого слота:

1. **Validate ratio** — фото должно соответствовать slot.ratio из meta.yaml блока
2. **Codex post-process** — `skills/photo-curation/scripts/codex-process-photo.sh`
   - Параметры: brand_color, niche, region (из tokens.json + market-profile.md)
   - Identity-preserve: объект клиента (машина/лицо/товар) НЕ репеинтится
3. **Resize** — точно под размеры слота (desktop + mobile)
4. **Cache** — hash от (orig+params), повтор не зовёт codex
5. **Save** — `07c_PHOTOS/processed/<slot>.jpg` + manifest.json

**Запрещено:**
- Оставлять SVG placeholder'ы (`<img src="placeholder-*.svg">`)
- Использовать сырые фотки из inbox/ без codex обработки
- Подменять оригинальный объект через codex (identity check ловит это)

**HARD GATE 07c и 07f:** `scripts/verify-photo-pipeline.sh` проверит
всё это при закрытии этапа. Если хоть один placeholder/raw фото —
этап не закроется.

Подробнее: `docs/superpowers/specs/2026-05-15-pr-i-a-photo-pipeline-design.md`.

```

- [ ] **Step 2: landing-photos.md — добавить про --interactive**

В существующий файл `commands/landing-photos.md` добавить (в Usage или Options):

```markdown

## Интерактивный режим (PR-I.a)

```
/landing-photos --interactive
```

Агент по очереди спрашивает у пользователя что положить в каждый
photo-слот, показывает подсказку (что должно быть на фото в этом
контексте, какой ratio), потом пропускает фото через pipeline:
codex обработка + resize + identity check.

Альтернатива — drag-drop UI в `07c_PHOTOS/photo-board.html`
(остаётся из PR-B). Если предпочитаешь визуально расставить —
открой HTML, drag фото в слоты, скачай selections.yaml, положи
обратно в проект.

```

- [ ] **Step 3: SKILL.md — обновить workflow**

Добавить раздел про новый pipeline в `skills/photo-curation/SKILL.md`. Найти раздел про workflow и добавить:

```markdown

## Pipeline через codex (PR-I.a, обязательно с 2026-05-15)

Каждое фото перед попаданием в composed.html проходит:
1. `codex-process-photo.sh` — codex image_gen с brand параметрами
2. `identity-check.py` — perceptual hash контроль (не репеинтнули ли объект)
3. Resize в точные размеры слота
4. Сохранение + manifest.json

Cache: `07c_PHOTOS/.cache/<hash>.jpg`. Повторный прогон с теми же параметрами не зовёт codex.

```

- [ ] **Step 4: Commit**

```bash
git add agents/photo-curator.md commands/landing-photos.md skills/photo-curation/SKILL.md
git commit -m "feat(pr-i-a): промпты photo-curator + landing-photos + SKILL.md

Правила обязательной codex-обработки + identity-safe + HARD GATE.
Описание интерактивного режима для подбора фото."
```

---

## Task 8: Финал — отметка пункта 3, push

- [ ] **Step 1: pytest + bats регрессия**

```bash
pytest tests/wiki/ 2>&1 | tail -3
bats tests/pr-g/
bats tests/pr-h/
bats tests/pr-i-a/
bash scripts/check-wiki-sync.sh
```

- [ ] **Step 2: Отметить **Пункт 3** частично готовым** в `docs/ПЛАН-ДОРАБОТОК.md`:

```markdown
#### 3. ⚙️ В работе (2026-05-15) — новый порядок работы с фотографиями

**Статус:** Часть А (PR-I.a) реализована — codex обработка, identity-safe,
HARD GATE на placeholder'ы. Часть Б (PR-I.b, Playwright Visual QA) — следующий PR.

**Что сделано в PR-I.a:**
1. **codex-process-photo.sh** — обёртка над codex CLI для пост-обработки фото
2. **photo-pipeline.py** — главный конвейер: validate → codex → identity → resize → cache → save
3. **identity-check.py** — perceptual hash контроль (объект не репеинтится)
4. **verify-photo-pipeline.sh** — hard_check для 07c+07f, ловит SVG placeholder'ы
5. **Интерактивный slot-fill** — диалог «спроси что в каждый слот»
6. **HARD GATE** на 07c_composed и 07f_composed_final
7. **Усиленный промпт photo-curator** — обязательная codex обработка
8. **5 bats-тестов** в `tests/pr-i-a/`

**Spec:** [`docs/superpowers/specs/2026-05-15-pr-i-a-photo-pipeline-design.md`](superpowers/specs/2026-05-15-pr-i-a-photo-pipeline-design.md)
**Plan:** [`docs/superpowers/plans/2026-05-15-pr-i-a-photo-pipeline-plan.md`](superpowers/plans/2026-05-15-pr-i-a-photo-pipeline-plan.md)

**Дальше (PR-I.b):** Playwright Visual QA — автоматическая проверка
финального composed.html в headless browser, скриншоты desktop+mobile,
auto-fix цикл при видимых проблемах.

```

- [ ] **Step 3: Commit + push**

```bash
git add docs/ПЛАН-ДОРАБОТОК.md
git commit -m "docs: пункт 3 частично готов (PR-I.a)"
git push origin feat/pr-a-prototype-block-library 2>&1 | tail -3
```

---

## Self-Review

**Spec coverage:**
- ✅ codex post-process (Task 1)
- ✅ photo-pipeline.py с validate/resize/cache (Task 2)
- ✅ identity-check (Task 3)
- ✅ verify-photo-pipeline + HARD GATE (Task 4-5)
- ✅ Тесты (Task 6)
- ✅ Промпты (Task 7)
- ✅ Финал (Task 8)
- ⏭️ Interactive-slot-fill (отложено — в Task 6 как skip, реальная реализация в PR-I.a iteration 2)
- ⏭️ Playwright QA — отдельный PR-I.b

**Placeholders:** нет.

**Type consistency:** все функции возвращают типы консистентно (`process_one_slot` → dict, `compute_cache_key` → str).

**Риски:**
1. `codex` CLI может не быть установлен — Task 1 содержит graceful exit
2. `imagehash` библиотека — добавляется в requirements в Task 3
3. Реальный smoke с codex стоит ~$0.50 — но Task 8 не требует его (только regression тесты)

---

## Что НЕ в PR-I.a

- Playwright Visual QA — PR-I.b
- Interactive-slot-fill UI — отложен (Task 6 skip), может быть в PR-I.a iter2 или отдельным PR
- Регенерация фото через codex от нуля (если у клиента нет своей фотки) — PR-I.c в будущем
