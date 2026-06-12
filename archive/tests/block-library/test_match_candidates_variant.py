"""B34 Фаза 5 — match-candidates: variant-aware, без отсечки score>0.

Правила:
- Категория без use_cases больше НЕ теряет всех кандидатов (баг «hero только 3»):
  возвращаются ВСЕ блоки данной category (до --top), отсортированные по score.
- Опц. `--variant` фильтрует `category==type AND variant==variant`.
- Квиз-блоки теперь category=forms, variant=quiz; quiz-role путь их находит.
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MATCHER = REPO_ROOT / "skills" / "wireframe-rendering" / "scripts" / "match-candidates.py"


def _make_lib(tmp_path, blocks):
    lib = tmp_path / "lib"
    lib.mkdir(parents=True, exist_ok=True)
    (lib / "catalog.yaml").write_text(
        yaml.dump({"version": 3, "blocks": blocks}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return lib


def _run(lib, *extra):
    r = subprocess.run(
        [sys.executable, str(MATCHER), "--library", str(lib), *extra],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_hero_without_usecases_returns_all(tmp_path):
    # 5 hero-блоков без use_cases/style_mood → score 10 каждому, раньше score>0
    # их бы оставило, но без category-bonus (старый btype mismatch) выпадали.
    blocks = [
        {"id": f"hero-{i}", "path": f"hero/hero-{i}/", "category": "hero", "variant": None}
        for i in range(5)
    ]
    blocks.append({"id": "feat-1", "path": "features/feat-1/", "category": "features", "variant": None})
    lib = _make_lib(tmp_path, blocks)
    ids = _run(lib, "--type", "hero", "--niche", "generic")
    assert len(ids) == 5, f"ожидалось 5 hero, получено {len(ids)}: {ids}"
    assert all(i.startswith("hero-") for i in ids)


def test_variant_filter(tmp_path):
    blocks = [
        {"id": "quiz-1", "path": "quiz/quiz-1/", "category": "forms", "variant": "quiz"},
        {"id": "email-1", "path": "forms/email-1/", "category": "forms", "variant": "email"},
        {"id": "quiz-2", "path": "quiz/quiz-2/", "category": "forms", "variant": "quiz"},
    ]
    lib = _make_lib(tmp_path, blocks)
    ids = _run(lib, "--type", "forms", "--niche", "generic", "--variant", "quiz")
    assert set(ids) == {"quiz-1", "quiz-2"}, ids
    # без variant — все forms
    ids_all = _run(lib, "--type", "forms", "--niche", "generic")
    assert set(ids_all) == {"quiz-1", "email-1", "quiz-2"}


def test_quiz_role_finds_forms_quiz_blocks(tmp_path):
    blocks = [
        {"id": "ru-quiz-06-welcome-screen", "path": "quiz/ru-quiz-06-welcome-screen/",
         "category": "forms", "variant": "quiz"},
        {"id": "ru-quiz-01-step-card", "path": "quiz/ru-quiz-01-step-card/",
         "category": "forms", "variant": "quiz"},
    ]
    lib = _make_lib(tmp_path, blocks)
    ids = _run(lib, "--type", "quiz", "--niche", "generic", "--quiz-role", "welcome")
    assert ids and ids[0] == "ru-quiz-06-welcome-screen", ids
