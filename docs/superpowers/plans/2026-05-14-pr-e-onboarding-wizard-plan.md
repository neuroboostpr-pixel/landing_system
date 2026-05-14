# PR-E Onboarding Wizard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Build interactive `/landing-start` wizard that explains the system, creates project folder, walks user through 4 material steps (prototype/photos/logos/references) with verification.

**Architecture:** New `commands/landing-start.md` slash command → dispatches `landing-onboarding-wizard` agent → uses existing `landing-project-init` skill for folder creation → uses new `wizard-check-materials.py` for per-step verification → ends by suggesting `/landing-go`. Template gets READMEs in all 18 folders + new `04_БРЕНД/logos/`.

**Tech Stack:** Python 3.10+ (Pillow, PyYAML), bash + bats, pytest. No new external deps.

**Spec:** [`docs/superpowers/specs/2026-05-14-pr-e-onboarding-wizard-design.md`](../specs/2026-05-14-pr-e-onboarding-wizard-design.md)

---

## Task dependency graph

```
[Task 1: wizard-check-materials.py] ─┐
[Task 2: Template READMEs + logos/]  ─┤
                                       │
                                       ▼
                              [Task 3: wizard agent doc]
                                       │
                                       ▼
                              [Task 4: /landing-start command]
                                       │
                                       ▼
                              [Task 5: migration script for old projects]
                                       │
                                       ▼
                              [Task 6: CLAUDE.md + final review]
```

**6 tasks total.** Tasks 1 + 2 parallelizable.

---

## Task 1: `wizard-check-materials.py` — verify materials per step

**Files:**
- Create: `scripts/wizard-check-materials.py`
- Create: `tests/phase-pre/__init__.py` (empty)
- Create: `tests/phase-pre/conftest.py`
- Create: `tests/phase-pre/test-wizard-check-materials.py`

- [ ] **Step 1: Create test scaffold**

`tests/phase-pre/__init__.py`: empty.

`tests/phase-pre/conftest.py`:
```python
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
```

- [ ] **Step 2: Write failing tests**

`tests/phase-pre/test-wizard-check-materials.py`:
```python
"""Tests for wizard-check-materials.py."""
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "wizard-check-materials.py"


def _run(project, step):
    r = subprocess.run(
        ["python3", str(SCRIPT), "--project", str(project), "--step", step],
        capture_output=True, text=True,
    )
    return r.returncode, r.stdout, r.stderr


def _mkproject(tmp_path):
    p = tmp_path / "proj"
    for sub in ("07_ПРОТОТИП/source", "07c_PHOTOS/inbox/_свалка",
                "07c_PHOTOS/inbox/портреты_и_команда",
                "04_БРЕНД/logos", "03_РЕФЕРЕНСЫ"):
        (p / sub).mkdir(parents=True, exist_ok=True)
    return p


def test_prototype_pass_when_pdf_present(tmp_path):
    proj = _mkproject(tmp_path)
    (proj / "07_ПРОТОТИП/source/prototype.pdf").write_bytes(b"%PDF-1.4\n" + b"\x00" * 500)
    rc, out, _ = _run(proj, "prototype")
    assert rc == 0
    data = json.loads(out)
    assert data["status"] == "pass"
    assert any("prototype.pdf" in f for f in data["found"])


def test_prototype_fail_when_missing(tmp_path):
    proj = _mkproject(tmp_path)
    rc, out, _ = _run(proj, "prototype")
    data = json.loads(out)
    assert data["status"] == "fail"
    # rc non-zero for fail
    assert rc != 0


def test_prototype_accepts_md(tmp_path):
    proj = _mkproject(tmp_path)
    (proj / "07_ПРОТОТИП/source/prototype.md").write_text("# Prototype")
    rc, out, _ = _run(proj, "prototype")
    data = json.loads(out)
    assert data["status"] == "pass"


def test_photos_pass_with_jpgs(tmp_path):
    proj = _mkproject(tmp_path)
    (proj / "07c_PHOTOS/inbox/_свалка/a.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 500)
    (proj / "07c_PHOTOS/inbox/портреты_и_команда/b.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 500)
    rc, out, _ = _run(proj, "photos")
    data = json.loads(out)
    assert data["status"] == "pass"
    assert "2" in data["summary"] or "photos" in data["summary"].lower()


def test_photos_warn_when_empty(tmp_path):
    proj = _mkproject(tmp_path)
    rc, out, _ = _run(proj, "photos")
    data = json.loads(out)
    assert data["status"] == "warn"


def test_logos_pass_with_png(tmp_path):
    proj = _mkproject(tmp_path)
    (proj / "04_БРЕНД/logos/logo.png").write_bytes(b"\x89PNG\r\n" + b"\x00" * 300)
    rc, out, _ = _run(proj, "logos")
    data = json.loads(out)
    assert data["status"] == "pass"


def test_logos_warn_when_empty(tmp_path):
    proj = _mkproject(tmp_path)
    rc, out, _ = _run(proj, "logos")
    data = json.loads(out)
    assert data["status"] == "warn"


def test_references_pass_with_yaml_urls(tmp_path):
    proj = _mkproject(tmp_path)
    (proj / "03_РЕФЕРЕНСЫ/index.yaml").write_text(
        "references:\n  - {url: https://example.com, status: candidate}\n"
    )
    rc, out, _ = _run(proj, "references")
    data = json.loads(out)
    assert data["status"] == "pass"


def test_references_warn_when_empty(tmp_path):
    proj = _mkproject(tmp_path)
    rc, out, _ = _run(proj, "references")
    data = json.loads(out)
    assert data["status"] == "warn"


def test_invalid_step_fails(tmp_path):
    proj = _mkproject(tmp_path)
    rc, out, err = _run(proj, "nonexistent")
    assert rc != 0
```

- [ ] **Step 3: Run — fails**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
python3 -m pytest tests/phase-pre/test-wizard-check-materials.py -v 2>&1 | head -20
```

- [ ] **Step 4: Implement wizard-check-materials.py**

`scripts/wizard-check-materials.py`:
```python
#!/usr/bin/env python3
"""Verify materials in a project folder per wizard step.

Output: JSON to stdout with {step, status, found, missing, summary}.
Exit code: 0 if pass or warn, 1 if fail.

Steps:
- prototype: REQUIRED. 07_ПРОТОТИП/source/prototype.{pdf,md,html}
- photos: optional. Count files in 07c_PHOTOS/inbox/**/*.{jpg,jpeg,png,heic}
- logos: optional. 04_БРЕНД/logos/logo.* or any image in logos/
- references: optional. 03_РЕФЕРЕНСЫ/index.yaml non-empty OR screenshots/ non-empty
"""
import argparse
import json
import sys
from pathlib import Path


PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}
LOGO_EXTS = {".svg", ".png", ".jpg", ".jpeg", ".webp"}
PROTOTYPE_EXTS = {".pdf", ".md", ".html", ".htm"}


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def check_prototype(project: Path) -> dict:
    src = project / "07_ПРОТОТИП" / "source"
    found: list[str] = []
    if src.exists():
        for p in src.iterdir():
            if p.is_file() and p.suffix.lower() in PROTOTYPE_EXTS and p.name.lower().startswith("prototype"):
                found.append(f"{p.name} ({_human_size(p.stat().st_size)})")
    if not found:
        return {
            "step": "prototype",
            "status": "fail",
            "found": [],
            "missing": ["prototype.pdf or prototype.md in 07_ПРОТОТИП/source/"],
            "summary": "Прототип не найден. Положи prototype.pdf или prototype.md в 07_ПРОТОТИП/source/",
        }
    return {
        "step": "prototype",
        "status": "pass",
        "found": found,
        "missing": [],
        "summary": f"Найдено: {', '.join(found)}",
    }


def check_photos(project: Path) -> dict:
    inbox = project / "07c_PHOTOS" / "inbox"
    photos: list[Path] = []
    if inbox.exists():
        for f in inbox.rglob("*"):
            if f.is_file() and f.suffix.lower() in PHOTO_EXTS:
                photos.append(f)
    if not photos:
        return {
            "step": "photos",
            "status": "warn",
            "found": [],
            "missing": ["any image in 07c_PHOTOS/inbox/"],
            "summary": "Фото клиента не найдены. На отсутствующие слоты сгенерится AI fallback.",
        }
    # Group by subfolder for summary
    by_folder: dict[str, int] = {}
    for p in photos:
        rel = p.relative_to(inbox)
        folder = rel.parts[0] if len(rel.parts) > 1 else "inbox"
        by_folder[folder] = by_folder.get(folder, 0) + 1
    breakdown = ", ".join(f"{n} в {fld}" for fld, n in by_folder.items())
    return {
        "step": "photos",
        "status": "pass",
        "found": [f"{len(photos)} photos"],
        "missing": [],
        "summary": f"Найдено {len(photos)} фото ({breakdown})",
    }


def check_logos(project: Path) -> dict:
    logos_dir = project / "04_БРЕНД" / "logos"
    logos: list[Path] = []
    if logos_dir.exists():
        for f in logos_dir.iterdir():
            if f.is_file() and f.suffix.lower() in LOGO_EXTS:
                logos.append(f)
    if not logos:
        return {
            "step": "logos",
            "status": "warn",
            "found": [],
            "missing": ["logo.svg or logo.png in 04_БРЕНД/logos/"],
            "summary": "Логотип не найден. brand-architect сгенерит текстовый логотип на этапе 04.",
        }
    return {
        "step": "logos",
        "status": "pass",
        "found": [f"{p.name} ({_human_size(p.stat().st_size)})" for p in logos],
        "missing": [],
        "summary": f"Найдено: {', '.join(p.name for p in logos)}",
    }


def check_references(project: Path) -> dict:
    refs_dir = project / "03_РЕФЕРЕНСЫ"
    index_yaml = refs_dir / "index.yaml"
    screenshots_dir = refs_dir / "screenshots"

    has_yaml = False
    if index_yaml.exists():
        text = index_yaml.read_text(encoding="utf-8")
        # Crude check: any non-comment line with content
        for line in text.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                has_yaml = True
                break

    has_screenshots = False
    if screenshots_dir.exists() and any(screenshots_dir.iterdir()):
        has_screenshots = True

    if has_yaml or has_screenshots:
        parts = []
        if has_yaml:
            parts.append("index.yaml заполнен")
        if has_screenshots:
            parts.append("есть скриншоты")
        return {
            "step": "references",
            "status": "pass",
            "found": parts,
            "missing": [],
            "summary": ", ".join(parts),
        }

    return {
        "step": "references",
        "status": "warn",
        "found": [],
        "missing": ["URLs in 03_РЕФЕРЕНСЫ/index.yaml or screenshots/"],
        "summary": "Референсы не заданы. references-curator подберёт автоматически.",
    }


CHECKERS = {
    "prototype": check_prototype,
    "photos": check_photos,
    "logos": check_logos,
    "references": check_references,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--step", required=True, choices=list(CHECKERS.keys()))
    args = ap.parse_args()

    project = Path(args.project)
    checker = CHECKERS[args.step]
    result = checker(project)

    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result["status"] in ("pass", "warn") else 1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run — pass**

```bash
python3 -m pytest tests/phase-pre/test-wizard-check-materials.py -v
```

Expected: 10/10 PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/wizard-check-materials.py tests/phase-pre/
git commit -m "feat(pr-e): wizard-check-materials.py — verify per-step materials"
```

---

## Task 2: Template READMEs + new `04_БРЕНД/logos/` folder

**Files:**
- Create: `template/04_БРЕНД/logos/.gitkeep`
- Create: `template/04_БРЕНД/logos/README.md`
- Create: `template/04_БРЕНД/README.md`
- Create: `template/00_БРИФ/README.md`
- Create: `template/01_КОНТЕКСТ/README.md`
- Create: `template/01a_АНАЛИЗ_НИШИ/README.md`
- Create: `template/02_МАТЕРИАЛЫ_КЛИЕНТА/README.md`
- Create: `template/03_РЕФЕРЕНСЫ/README.md`
- Create: `template/05_ДИЗАЙН-СИСТЕМА/README.md`
- Create: `template/06_СТЕК/README.md`
- Create: `template/07_КОНТЕНТ/README.md`
- Create: `template/07_ПРОТОТИП/README.md`
- Create: `template/07_ПРОТОТИП/source/.gitkeep`
- Create: `template/07_ПРОТОТИП/source/README.md`
- Create: `template/07a_WIREFRAME/README.md`
- Create: `template/07b_COMPOSED/README.md`
- Create: `template/08_КОД/README.md`
- Create: `template/09_ДЕПЛОЙ/README.md`
- Create: `template/10_QA/README.md`
- Create: `template/11_АНАЛИТИКА/README.md`
- Create: `template/12_SEO/README.md`
- Create: `tests/phase-pre/test-template-readmes.bats`

- [ ] **Step 1: Write failing test**

`tests/phase-pre/test-template-readmes.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "every template folder has README.md" {
    for d in "$REPO/template/"*/; do
        # Skip if not a directory
        [ -d "$d" ] || continue
        # template/07c_PHOTOS and 07d_VISUALS already have READMEs from PR-B/C — covered too
        [ -f "$d/README.md" ] || {
            echo "Missing README: $d"; return 1
        }
    done
}

@test "04_БРЕНД has logos/ subfolder with README" {
    [ -d "$REPO/template/04_БРЕНД/logos" ]
    [ -f "$REPO/template/04_БРЕНД/logos/README.md" ]
}

@test "07_ПРОТОТИП has source/ subfolder with README" {
    [ -d "$REPO/template/07_ПРОТОТИП/source" ]
    [ -f "$REPO/template/07_ПРОТОТИП/source/README.md" ]
}

@test "logos README mentions logo.png and favicon" {
    grep -qE "logo\.(svg|png)" "$REPO/template/04_БРЕНД/logos/README.md"
    grep -qE "favicon" "$REPO/template/04_БРЕНД/logos/README.md"
}

@test "prototype source README mentions prototype.pdf" {
    grep -q "prototype.pdf" "$REPO/template/07_ПРОТОТИП/source/README.md"
}
```

- [ ] **Step 2: Run — fails**

```bash
bats tests/phase-pre/test-template-readmes.bats 2>&1 | head -10
```

- [ ] **Step 3: Create logos/ folder + README**

```bash
mkdir -p template/04_БРЕНД/logos
touch template/04_БРЕНД/logos/.gitkeep
```

`template/04_БРЕНД/logos/README.md`:
```markdown
# 04_БРЕНД/logos/

## Что сюда класть

Логотип клиента:
- `logo.svg` или `logo.png` — основной логотип (предпочтительно SVG для масштабируемости)
- `logo-dark.svg` или `logo-dark.png` — версия для светлого фона (опц.)
- `logo-mono.svg` — одноцветная версия для печати/факсимиле (опц.)
- `favicon.png` — иконка вкладки браузера, 32×32 или 64×64 (опц.)

## Кто кладёт

Маркетолог через `/landing-start` wizard, либо вручную перед запуском `/landing-go`.

## Если логотипа нет

brand-architect сгенерит текстовый логотип на этапе 04_brand на основе названия компании.
```

- [ ] **Step 4: Create per-folder READMEs**

`template/04_БРЕНД/README.md`:
```markdown
# 04_БРЕНД

## Что здесь будет

- `logos/` — логотипы клиента (положи руками)
- `brand-kit.md` — генерируется brand-architect на этапе 04_brand
- `brand-kit.html` — visual preview brand-kit

## Кто создаёт

- `logos/` — маркетолог через `/landing-start` wizard
- `brand-kit.md/html` — brand-architect автоматически

## Этап

04_brand pipeline stage.
```

`template/00_БРИФ/README.md`:
```markdown
# 00_БРИФ

## Что здесь будет

`brief.md` — короткое описание проекта (ниша, аудитория, KPI).

## Кто создаёт

В **prototype-first flow** (PR-D) этот этап помечен `n/a` — информация выводится из прототипа автоматически.

В классическом flow заполняется `landing-orchestrator` на этапе 00_brief.

## Этап

00_brief (skipped in prototype-first).
```

`template/01_КОНТЕКСТ/README.md`:
```markdown
# 01_КОНТЕКСТ

## Что здесь будет

`context.md` — контекст проекта (детали клиента, целевая аудитория, дополнительные требования).

## Кто создаёт

В prototype-first flow — `n/a` (из прототипа).
Иначе — landing-orchestrator на этапе 01_context.
```

`template/01a_АНАЛИЗ_НИШИ/README.md`:
```markdown
# 01a_АНАЛИЗ_НИШИ

## Что здесь будет

- `niche-analysis.md` — анализ ниши
- `competitors.yaml` — конкуренты
- `positioning.md` — позиционирование
- `landing-structure.md` — структура лендинга (контракт с wp-builder)
- `market-profile.md` — профиль рынка
- `visual-requirements.md` — визуальные требования

## Кто создаёт

В prototype-first flow — `derive-landing-structure.py` создаёт минимум: только `landing-structure.md`.

В классическом flow — `niche-analyst` агент.

## Этап

01a_niche_analysis (минимизировано в prototype-first).
```

`template/02_МАТЕРИАЛЫ_КЛИЕНТА/README.md`:
```markdown
# 02_МАТЕРИАЛЫ_КЛИЕНТА (legacy)

## Что здесь было

Старая папка для материалов клиента (фото, документы).

## Что использовать вместо

**Фото клиента → `07c_PHOTOS/inbox/`** (PR-B pipeline).
**Логотипы → `04_БРЕНД/logos/`** (PR-E wizard).

## Этап

Помечен `n/a` в prototype-first flow.

`photo-curator` (PR-B) сканирует ОБА пути — `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` и `07c_PHOTOS/inbox/` — для backward compat со старыми проектами.
```

`template/03_РЕФЕРЕНСЫ/README.md`:
```markdown
# 03_РЕФЕРЕНСЫ

## Что сюда класть

- `index.yaml` — список URL лендингов-образцов (формат см. ниже)
- `screenshots/` — скриншоты референсов (опц.)

## Формат index.yaml

```yaml
references:
  - url: https://example.com/landing-1
    note: "Похожая ниша, нравится hero"
    status: candidate    # candidate | approved | rejected
  - url: https://example.com/landing-2
    status: candidate
```

## Кто кладёт

Маркетолог через `/landing-start` wizard (опц.) или references-curator автоматически.

## Этап

03_references.
```

`template/05_ДИЗАЙН-СИСТЕМА/README.md`:
```markdown
# 05_ДИЗАЙН-СИСТЕМА

## Что здесь будет

- `DESIGN.md` — единый источник истины токенов (цвета, шрифты, отступы)
- `tokens.json` — машиночитаемые токены
- `design-preview.html` — visual preview

## Кто создаёт

`design-system-generator` агент на основе `04_БРЕНД/brand-kit.md`.

## Этап

05_design.
```

`template/06_СТЕК/README.md`:
```markdown
# 06_СТЕК

## Что здесь будет

- `design-stack.yaml` — выбранный стек технологий (WordPress + Gutenberg + ACF + и т.д.)
- `mode` — режим (standard / cinematic)

## Кто создаёт

`stack-planner` агент автоматически.

## Этап

06_stack (АВТО).
```

`template/07_КОНТЕНТ/README.md`:
```markdown
# 07_КОНТЕНТ

## Что здесь будет

`final-copy.md` — финальный текст лендинга по секциям (H2-секции = блоки).

## Кто создаёт

`content-writer` агент. Извлекает текст из `07_ПРОТОТИП/prototype.yaml`.

## Этап

07_content (АВТО).
```

`template/07_ПРОТОТИП/README.md`:
```markdown
# 07_ПРОТОТИП

## Что здесь будет

- `source/` — куда маркетолог кладёт исходный прототип (см. `source/README.md`)
- `prototype.yaml` — структурированный прототип (auto)
- `prototype.md` — человеко-читаемая версия (auto)

## Кто создаёт

- `source/` — маркетолог через `/landing-start` wizard
- `prototype.yaml/.md` — `prototype-importer` агент через `/landing-prototype`

## Этап

07a_prototype (вход prototype-first flow).
```

`template/07_ПРОТОТИП/source/README.md`:
```markdown
# 07_ПРОТОТИП/source/

## Что сюда класть

**Один файл** — исходный прототип лендинга:
- `prototype.pdf` — экспорт из Figma/Tilda/любого инструмента
- ИЛИ `prototype.md` — текстовое описание блоков
- ИЛИ `prototype.html` — экспорт HTML

## Пример prototype.md

```markdown
# Лендинг для услуги ремонта

## Hero
Главный заголовок, подзаголовок, кнопка "Рассчитать стоимость"

## Features
3 преимущества с иконками

## Testimonials
3 отзыва клиентов
```

## Кто кладёт

Маркетолог. Это **обязательный** материал — без него `/landing-go` не запустится.

## Что произойдёт

`prototype-importer` на этапе 07a_prototype:
1. Парсит файл
2. Создаёт `07_ПРОТОТИП/prototype.yaml` (машиночитаемая структура)
3. Создаёт `07_ПРОТОТИП/prototype.md` (нормализованная человеко-читаемая версия)
```

```bash
touch template/07_ПРОТОТИП/source/.gitkeep
```

`template/07a_WIREFRAME/README.md`:
```markdown
# 07a_WIREFRAME

## Что здесь будет

- `wireframe.html` — интерактивный wireframe с 2-3 вариантами на блок (auto)
- `selections.yaml` — твой выбор вариантов (положи после Confirm в браузере)

## Кто создаёт

- `wireframe.html` — `/landing-wireframe` команда (АВТО)
- `selections.yaml` — маркетолог: открыть wireframe.html в браузере, выбрать варианты, нажать Confirm, скачать selections.yaml, положить сюда

## Этап

07b_wireframe (PR-A flow).
```

`template/07b_COMPOSED/README.md`:
```markdown
# 07b_COMPOSED

## Что здесь будет

`composed.html` — финальная композиция блоков с реальными текстами, токенами, фото, иконками.

## Кто создаёт

`/landing-compose` команда:
1. Первый прогон — composed.html с placeholders для фото/иконок (этап 07c_composed)
2. После /landing-photos + /landing-visuals — re-render с реальными визуалами (этап 07f_composed_final)

## Этап

07c_composed (draft) + 07f_composed_final (re-render).
```

`template/08_КОД/README.md`:
```markdown
# 08_КОД

## Что здесь будет

- `wp-theme/` — WordPress тема (PHP темплейты + CSS + JS)
- `gutenberg-blocks/` — Gutenberg blocks (JSON конфиги)
- `acf-fields.json` — Advanced Custom Fields config

## Кто создаёт

`wp-builder` агент через `/landing-build`.

## Этап

08_build (АВТО).
```

`template/09_ДЕПЛОЙ/README.md`:
```markdown
# 09_ДЕПЛОЙ

## Что здесь будет

- `deploy-log.md` — лог последнего деплоя
- `beget-config.yaml` — credentials Бегет (НЕ коммитить в git, см. .gitignore)

## Кто создаёт

`wp-deployer` агент через `/landing-deploy`.

## Что от маркетолога

Один раз ввести Бегет credentials (hostname, SSH user, password или ключ).

## Этап

09_deploy.
```

`template/10_QA/README.md`:
```markdown
# 10_QA

## Что здесь будет

- `qa-report.md` — отчёт по проверкам (PageSpeed, accessibility, SEO)
- `lighthouse.json` — Lighthouse audit

## Кто создаёт

`qa-auditor` агент.

## Этап

10_qa (АВТО после деплоя).
```

`template/11_АНАЛИТИКА/README.md`:
```markdown
# 11_АНАЛИТИКА

## Что здесь будет

- `analytics-config.md` — настройки Яндекс.Метрики / GA
- `events.yaml` — список событий для отслеживания

## Кто создаёт

`analytics-engineer` агент.

## Этап

11_analytics (АВТО).
```

`template/12_SEO/README.md`:
```markdown
# 12_SEO

## Что здесь будет

- `seo-meta.md` — title, description, OG-теги
- `sitemap.xml` — карта сайта
- `robots.txt`

## Кто создаёт

`seo-optimizer` агент.

## Этап

12_seo (АВТО, финал pipeline).
```

- [ ] **Step 5: Run — pass**

```bash
bats tests/phase-pre/test-template-readmes.bats
```

Expected: 5/5 PASS.

- [ ] **Step 6: Commit**

```bash
git add template/ tests/phase-pre/test-template-readmes.bats
git commit -m "feat(pr-e): READMEs in all 18 template folders + new 04_БРЕНД/logos/"
```

---

## Task 3: `landing-onboarding-wizard` agent doc

**Files:**
- Create: `agents/landing-onboarding-wizard.md`
- Create: `tests/phase-pre/test-wizard-agent.bats`

- [ ] **Step 1: Write failing test**

`tests/phase-pre/test-wizard-agent.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
AGENT="$REPO/agents/landing-onboarding-wizard.md"

@test "wizard agent file exists with frontmatter" {
    [ -f "$AGENT" ]
    head -10 "$AGENT" | grep -q "^name: landing-onboarding-wizard$"
    head -10 "$AGENT" | grep -q "^description:"
}

@test "wizard explains 3-paragraph welcome" {
    grep -q "Добро пожаловать" "$AGENT"
}

@test "wizard documents all 4 material steps" {
    grep -q "ШАГ 1" "$AGENT"
    grep -q "ШАГ 2" "$AGENT"
    grep -q "ШАГ 3" "$AGENT"
    grep -q "ШАГ 4" "$AGENT"
}

@test "wizard mentions step 1 prototype is REQUIRED" {
    grep -qE "ОБЯЗАТЕЛЬНО|обязательн|required" "$AGENT"
}

@test "wizard references wizard-check-materials.py" {
    grep -q "wizard-check-materials" "$AGENT"
}

@test "wizard references landing-project-init skill" {
    grep -q "landing-project-init" "$AGENT"
}

@test "wizard ends by suggesting /landing-go" {
    grep -q "/landing-go" "$AGENT"
}
```

- [ ] **Step 2: Run — fails**

```bash
bats tests/phase-pre/test-wizard-agent.bats 2>&1 | head -10
```

- [ ] **Step 3: Create agents/landing-onboarding-wizard.md**

```markdown
---
name: landing-onboarding-wizard
description: Interactive wizard для новых проектов. Объясняет систему, создаёт папку, ведёт маркетолога через 4 шага материалов (prototype/photos/logos/references) с верификацией. Триггерится через /landing-start.
---

# landing-onboarding-wizard

Я главный гид для маркетолога в landing-system. Запускаюсь через `/landing-start` и веду от приветствия до готового проекта с разложенными материалами.

## Mission

1. Объяснить систему за 3 коротких параграфа (без воды).
2. Создать папку проекта через `landing-project-init` skill.
3. Провести маркетолога через 4 шага материалов:
   - **Шаг 1: Прототип** (обязательно) → `07_ПРОТОТИП/source/`
   - **Шаг 2: Фото клиента** (рекомендую) → `07c_PHOTOS/inbox/`
   - **Шаг 3: Логотип** (рекомендую) → `04_БРЕНД/logos/`
   - **Шаг 4: Референсы** (опционально) → `03_РЕФЕРЕНСЫ/`
4. Верифицировать каждый шаг через `scripts/wizard-check-materials.py`.
5. В финале — подсказать `/landing-go`.

## Process

### Phase 0: Pre-flight

1. Проверить что codex CLI установлен: `bash scripts/install-codex.sh --check`.
   - Если нет — запустить `bash scripts/install-codex.sh` (с pause на login).
2. Проверить что мы в landing-system repo (наличие `template/` директории).

### Phase 1: Welcome (3 paragraphs)

Печатаю **дословно** (без воды):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👋 Добро пожаловать в landing-system!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Я помогу собрать лендинг от готового прототипа до live сайта на Бегете.
Вся обработка фото, генерация иконок, сборка WordPress-темы и деплой —
автоматически. Тебя я спрошу 5-7 раз за весь процесс.

Сейчас попрошу тебя:
1. Назвать имя проекта
2. Положить prototype.pdf (обязательно)
3. Положить фото, логотип, референсы (рекомендую)

Назови короткое имя проекта (kebab-case, например stroyka-pro):
```

### Phase 2: Slug input

1. Жду ответ.
2. Валидирую kebab-case (regex: `^[a-z0-9][a-z0-9-]*$`). Если нет — прошу заново с примером.
3. Если папка `~/Lendings/<slug>/` уже существует — спрашиваю: «Использовать существующую (1) или назвать другую (2)?»

### Phase 3: Create project

Вызываю `landing-project-init` skill:
```bash
bash skills/landing-project-init/scripts/init.sh <slug>
```

После успеха:
```
📁 Создаю папку: ~/Lendings/<slug>/
   ↓ Копирую template (18 папок с подсказками)
✅ Готово. Открой Finder и убедись что папка появилась.
```

### Phase 4: Material walkthrough (4 steps)

Для каждого шага следую шаблону:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ШАГ <N> ИЗ 4 — <Имя> (<статус>)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 ~/Lendings/<slug>/<папка>

<подсказка что класть>

<пример или подсказки>

<если опционально>
Если у тебя нет — напиши "пропустить".
<иначе>
Это обязательный шаг.

Когда положишь — напиши "готово".
```

После «готово»:
```bash
python3 scripts/wizard-check-materials.py --project ~/Lendings/<slug> --step <step-name>
```

- `pass` → печатаю summary, перехожу к следующему шагу
- `warn` → информирую о warning, спрашиваю «продолжить?», на yes — следующий шаг
- `fail` → печатаю что не так, прошу повторить шаг

Если на step 1 (prototype) пользователь пишет «пропустить» — **отказ**: «Прототип обязательный. Положи файл или прерви wizard через Ctrl+C».

### Step 1: Prototype (REQUIRED)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ШАГ 1 ИЗ 4 — Прототип (ОБЯЗАТЕЛЬНО)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 ~/Lendings/<slug>/07_ПРОТОТИП/source/

Положи туда:
  • prototype.pdf — экспорт из Figma/Tilda/etc
  • Или prototype.md — текстовое описание блоков
  • Или prototype.html — экспорт HTML

Открой папку и скопируй файл. Когда готов — напиши "готово".
```

### Step 2: Photos (recommended)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ШАГ 2 ИЗ 4 — Фото клиента (рекомендую)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 ~/Lendings/<slug>/07c_PHOTOS/inbox/

Внутри 7 подпапок — открой и посмотри:
  • _свалка/ — кидай сюда если не знаешь
  • портреты_и_команда/ — фото людей
  • процесс_работы/ — мастер за работой
  • объекты_и_продукты/ — готовые работы
  • интерьер_экстерьер/ — офис, цех
  • до_после/ — пары «было → стало»
  • документы_сертификаты/ — дипломы

Если фоток нет — напиши "пропустить" (я сгенерю через AI).
```

### Step 3: Logos (recommended)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ШАГ 3 ИЗ 4 — Логотип клиента (рекомендую)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 ~/Lendings/<slug>/04_БРЕНД/logos/

Положи:
  • logo.svg или logo.png — основной логотип
  • logo-dark.svg — версия для светлого фона (опц.)
  • favicon.png — иконка вкладки 32×32 (опц.)

Если логотипа нет — напиши "пропустить".
```

### Step 4: References (optional)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ШАГ 4 ИЗ 4 — Референсы дизайна (опционально)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 ~/Lendings/<slug>/03_РЕФЕРЕНСЫ/

Если у тебя есть лендинги-образцы:
  • Положи URL в index.yaml (формат внутри README)
  • Или скриншоты в screenshots/

Если нет — references-curator подберёт сам по нише.
```

### Phase 5: Final summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ИТОГ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<✅ или ⊘ для каждого шага>

Проект готов к сборке. Запускай:
  /landing-go

Или сделай паузу — оркестратор продолжит с того же места.
```

## Tools

Bash, Read, Write, Edit, Task (для дispatching landing-project-init), Glob.

## Что НЕ делаю

- Не запускаю `/landing-go` сам — пользователь должен явно начать.
- Не модифицирую существующие проекты — wizard только для НОВЫХ.
- Не парсю прототип — это уже делает `prototype-importer` на этапе 07a.
```

- [ ] **Step 4: Run — pass + commit**

```bash
bats tests/phase-pre/test-wizard-agent.bats
git add agents/landing-onboarding-wizard.md tests/phase-pre/test-wizard-agent.bats
git commit -m "feat(pr-e): landing-onboarding-wizard agent — step-by-step materials walkthrough"
```

---

## Task 4: `/landing-start` slash command

**Files:**
- Create: `commands/landing-start.md`
- Create: `tests/phase-pre/test-landing-start.bats`

- [ ] **Step 1: Write failing test**

`tests/phase-pre/test-landing-start.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
CMD="$REPO/commands/landing-start.md"

@test "/landing-start command file exists with frontmatter" {
    [ -f "$CMD" ]
    head -10 "$CMD" | grep -q "^description:"
}

@test "/landing-start references landing-onboarding-wizard agent" {
    grep -q "landing-onboarding-wizard" "$CMD"
}

@test "/landing-start documents 4 steps" {
    grep -q "Прототип" "$CMD"
    grep -q "Фото" "$CMD"
    grep -q "Логотип\|логотип" "$CMD"
    grep -q "Референс\|референс" "$CMD"
}

@test "/landing-start mentions /landing-go as next step" {
    grep -q "/landing-go" "$CMD"
}

@test "/landing-start mentions it's the main entry point" {
    body=$(cat "$CMD")
    echo "$body" | grep -qE "главн|main|основн|first|первая"
}
```

- [ ] **Step 2: Run — fails**

```bash
bats tests/phase-pre/test-landing-start.bats 2>&1 | head -10
```

- [ ] **Step 3: Create commands/landing-start.md**

```markdown
---
description: Главная точка входа в landing-system. Interactive wizard — объясняет систему, создаёт папку проекта, проводит маркетолога через 4 шага материалов (прототип/фото/логотип/референсы) с верификацией. Финиширует подсказкой /landing-go.
---

# /landing-start

**Главная команда** для нового лендинга. Запусти один раз — wizard объяснит систему, создаст папку, разложит подсказки куда что класть, и проверит что ты всё положил правильно.

## Использование

```
/landing-start
```

Никаких аргументов — wizard сам спросит имя проекта.

## Что произойдёт

1. **Welcome** — 3 параграфа объяснения системы (что произойдёт, сколько раз спросят).
2. **Имя проекта** — wizard спрашивает kebab-case slug.
3. **Создание папки** — `~/Lendings/<slug>/` со всеми 18 подпапками и подсказками в README.
4. **Walkthrough по 4 материалам**:
   - 🔴 **Прототип (обязательно)** — `prototype.pdf` или `.md` в `07_ПРОТОТИП/source/`
   - 🟡 **Фото клиента (рекомендую)** — в `07c_PHOTOS/inbox/`
   - 🟡 **Логотип (рекомендую)** — в `04_БРЕНД/logos/`
   - ⚪ **Референсы (опционально)** — в `03_РЕФЕРЕНСЫ/`
5. **Проверка материалов** — `wizard-check-materials.py` для каждого шага.
6. **Финиш** — подсказка `/landing-go` для запуска pipeline.

## Шаги опциональны

- **Прототип** — обязательно. Без него wizard exit 1.
- **Фото / Логотип / Референсы** — можно «пропустить». AI сгенерирует/подберёт сам.

## После wizard

Wizard **НЕ запускает** `/landing-go` автоматически — он только подсказывает. Это даёт тебе паузу убедиться что всё на месте, потом запустить вручную.

## Когда использовать /landing-new вместо /landing-start

`/landing-new <slug>` — быстрый вариант без онбординга и без walkthrough материалов. Подходит если ты уже опытный пользователь системы и просто хочешь чистую папку проекта.

`/landing-start` — для первого знакомства с системой и для новых проектов где хочется не забыть ни один материал.

## Под капотом

Команда вызывает `landing-onboarding-wizard` агента. См. [`agents/landing-onboarding-wizard.md`](../agents/landing-onboarding-wizard.md) для детального flow.

См. [spec](../docs/superpowers/specs/2026-05-14-pr-e-onboarding-wizard-design.md), [plan](../docs/superpowers/plans/2026-05-14-pr-e-onboarding-wizard-plan.md).
```

- [ ] **Step 4: Run — pass + commit**

```bash
bats tests/phase-pre/test-landing-start.bats
git add commands/landing-start.md tests/phase-pre/test-landing-start.bats
git commit -m "feat(pr-e): /landing-start slash command — main entry point with wizard"
```

---

## Task 5: Migration script for existing projects (add new READMEs)

**Files:**
- Create: `scripts/migrate-template-readmes.sh`
- Create: `tests/phase-pre/test-migrate-readmes.bats`

- [ ] **Step 1: Write failing test**

`tests/phase-pre/test-migrate-readmes.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
SCRIPT="$REPO/scripts/migrate-template-readmes.sh"

setup() {
    TMP="$(mktemp -d)"
    # Simulate a legacy project: copy template but without READMEs
    cp -r "$REPO/template/." "$TMP/project/"
    # Remove some READMEs to simulate legacy state
    find "$TMP/project" -name "README.md" -delete 2>/dev/null || true
}
teardown() { rm -rf "$TMP"; }

@test "migrate adds README to project folder if missing" {
    run bash "$SCRIPT" "$TMP/project"
    [ "$status" -eq 0 ]
    [ -f "$TMP/project/00_БРИФ/README.md" ]
    [ -f "$TMP/project/04_БРЕНД/logos/README.md" ]
    [ -f "$TMP/project/07_ПРОТОТИП/source/README.md" ]
}

@test "migrate is idempotent" {
    bash "$SCRIPT" "$TMP/project"
    bash "$SCRIPT" "$TMP/project"
    # Should still have README, no errors
    [ -f "$TMP/project/00_БРИФ/README.md" ]
}

@test "migrate skips existing READMEs (no overwrite)" {
    mkdir -p "$TMP/project/00_БРИФ"
    echo "CUSTOM README" > "$TMP/project/00_БРИФ/README.md"
    bash "$SCRIPT" "$TMP/project"
    grep -q "CUSTOM README" "$TMP/project/00_БРИФ/README.md"
}

@test "migrate creates logos/ subfolder if missing" {
    rm -rf "$TMP/project/04_БРЕНД/logos"
    bash "$SCRIPT" "$TMP/project"
    [ -d "$TMP/project/04_БРЕНД/logos" ]
}
```

- [ ] **Step 2: Run — fails**

```bash
bats tests/phase-pre/test-migrate-readmes.bats 2>&1 | head -10
```

- [ ] **Step 3: Implement script**

`scripts/migrate-template-readmes.sh`:
```bash
#!/usr/bin/env bash
# migrate-template-readmes.sh — copy missing READMEs from template/ into an existing project.
#
# Idempotent: existing READMEs preserved (no overwrite). Creates missing subfolders
# (e.g. 04_БРЕНД/logos/) if absent.
#
# Usage: bash migrate-template-readmes.sh <project_dir>

set -euo pipefail

PROJECT="${1:?ERROR: project dir required}"
[ -d "$PROJECT" ] || { echo "ERROR: $PROJECT not found" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE="$LS_ROOT/template"

[ -d "$TEMPLATE" ] || { echo "ERROR: template/ not found at $TEMPLATE" >&2; exit 2; }

added=0
created_dirs=0

# Walk template recursively, copy missing READMEs and missing folders
while IFS= read -r -d '' template_file; do
    rel="${template_file#$TEMPLATE/}"
    target="$PROJECT/$rel"
    target_dir="$(dirname "$target")"

    # Ensure target dir exists (create if missing)
    if [ ! -d "$target_dir" ]; then
        mkdir -p "$target_dir"
        created_dirs=$((created_dirs + 1))
    fi

    # Skip if target file already exists (preserve user customizations)
    if [ -e "$target" ]; then
        continue
    fi

    cp "$template_file" "$target"
    added=$((added + 1))
done < <(find "$TEMPLATE" -type f -print0)

# Also copy .gitkeep files explicitly (find with -type f catches them)
echo "✅ Migration done."
echo "   Added files: $added"
echo "   Created dirs: $created_dirs"
```

```bash
chmod +x scripts/migrate-template-readmes.sh
```

- [ ] **Step 4: Run — pass**

```bash
bats tests/phase-pre/test-migrate-readmes.bats
```

Expected: 4/4 PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/migrate-template-readmes.sh tests/phase-pre/test-migrate-readmes.bats
git commit -m "feat(pr-e): migrate-template-readmes.sh — backport READMEs to legacy projects"
```

---

## Task 6: CLAUDE.md + final review

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Read existing CLAUDE.md**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
grep -n "PR-D\|landing-go\|Block Library\|Главные команды" CLAUDE.md | head -15
```

- [ ] **Step 2: Insert PR-E section in CLAUDE.md**

Find the "Главные команды" section near the top. Update to make `/landing-start` the FIRST command. Add new section after PR-D section before "Block Library" section:

In "Главные команды" section, change:
```
- `/landing-new <slug>` — создать новый проект-лендинг с нуля
```
to:
```
- `/landing-start` — **главная команда для новичков**. Interactive wizard: объясняет систему, создаёт папку, проводит через 4 шага материалов (PR-E)
- `/landing-new <slug>` — advanced: создать пустой проект без wizard (для опытных)
```

After PR-D section, insert:

```markdown
## Новая команда PR-E (Onboarding Wizard)

- `/landing-start` — **главная точка входа** для нового проекта. Interactive wizard.

**Что делает:**
1. Welcome (3 параграфа объяснения системы)
2. Спрашивает имя проекта (kebab-case)
3. Создаёт `~/Lendings/<slug>/` с 18 подпапками и READMEs внутри
4. Проводит через 4 шага материалов:
   - 🔴 **Прототип** (обязательно) → `07_ПРОТОТИП/source/`
   - 🟡 **Фото клиента** (рекомендую) → `07c_PHOTOS/inbox/`
   - 🟡 **Логотип** (рекомендую) → `04_БРЕНД/logos/`
   - ⚪ **Референсы** (опционально) → `03_РЕФЕРЕНСЫ/`
5. Проверяет наличие материалов после каждого шага
6. Финиш — подсказка `/landing-go`

**Migration для старых проектов:**
```bash
bash scripts/migrate-template-readmes.sh ~/Lendings/<existing-project>
```
Добавит недостающие READMEs во все 18 папок + создаст `04_БРЕНД/logos/` если её нет.

См. [spec](docs/superpowers/specs/2026-05-14-pr-e-onboarding-wizard-design.md), [plan](docs/superpowers/plans/2026-05-14-pr-e-onboarding-wizard-plan.md).
```

- [ ] **Step 3: Final test run + commit**

```bash
# Run all PR-E tests
python3 -m pytest tests/phase-pre/ -v
bats tests/phase-pre/

# Regression
bats tests/phase-pra/ tests/gate-check/ tests/phase-prb/ tests/phase-prc/ tests/phase-prd/ 2>&1 | tail -5
python3 -m pytest tests/phase-prb/ tests/phase-prc/ tests/phase-prd/ -v 2>&1 | tail -5

# E2E
SKIP_OPEN=1 USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh pre-final-smoke tests/phase-pra/fixtures/prototype-sample.md 2>&1 | tail -10

git add CLAUDE.md
git commit -m "docs(pr-e): CLAUDE.md — /landing-start as main entry point + migration hint"
```

- [ ] **Step 4: Final holistic review**

Dispatch a final reviewer subagent (in execution phase) to do the acceptance criteria sanity check.

---

## Acceptance checklist

- [ ] `/landing-start` запускается и показывает welcome text (Task 4)
- [ ] Wizard создаёт `~/Lendings/<slug>/` через landing-project-init (Task 3 agent doc)
- [ ] Wizard ведёт через 4 шага с верификацией (Task 3 agent doc)
- [ ] Step 1 (prototype) hard-required (Task 3 agent doc)
- [ ] Steps 2-4 поддерживают «пропустить» (Task 3 agent doc)
- [ ] `wizard-check-materials.py` корректно проверяет 4 типа (Task 1, 10 tests)
- [ ] Все 18 папок template имеют README.md (Task 2)
- [ ] Новая `template/04_БРЕНД/logos/` существует с README (Task 2)
- [ ] Migration script работает на старых проектах (Task 5)
- [ ] PR-A/B/C/D регрессионные тесты не падают (Task 6 final run)
- [ ] 15+ новых тестов проходят (sum of Tasks 1-5)
- [ ] CLAUDE.md обновлён с PR-E section (Task 6)
