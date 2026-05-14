"""Tests for derive-landing-structure.py — prototype.yaml → landing-structure.md."""
import subprocess
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "derive-landing-structure.py"


def test_derives_structure_from_prototype(tmp_path):
    project = tmp_path / "test-project"
    proto_dir = project / "07_ПРОТОТИП"
    proto_dir.mkdir(parents=True)

    prototype = {
        "blocks": [
            {"id": "hero-1", "type": "hero", "title": "Главный экран"},
            {"id": "features-1", "type": "features", "title": "Что мы делаем"},
            {"id": "testimonials-1", "type": "social-proof", "title": "Отзывы"},
            {"id": "form-1", "type": "cta", "title": "Запрос расчёта"},
        ]
    }
    (proto_dir / "prototype.yaml").write_text(yaml.safe_dump(prototype, allow_unicode=True))

    result = subprocess.run(
        ["python3", str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"

    out_path = project / "01a_АНАЛИЗ_НИШИ" / "landing-structure.md"
    assert out_path.exists()

    body = out_path.read_text()
    assert "Контракт с wp-builder" in body
    assert "section-hero.php" in body
    assert "section-features.php" in body
    assert "section-form.php" in body or "section-cta.php" in body


def test_derive_handles_empty_prototype(tmp_path):
    project = tmp_path / "test-project"
    proto_dir = project / "07_ПРОТОТИП"
    proto_dir.mkdir(parents=True)
    (proto_dir / "prototype.yaml").write_text("blocks: []")

    result = subprocess.run(
        ["python3", str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0

    out_path = project / "01a_АНАЛИЗ_НИШИ" / "landing-structure.md"
    assert out_path.exists()
    assert "Контракт с wp-builder" in out_path.read_text()


def test_derive_dedupes_same_block_type(tmp_path):
    """Multiple blocks of same type → single template-part PHP file."""
    project = tmp_path / "test-project"
    proto_dir = project / "07_ПРОТОТИП"
    proto_dir.mkdir(parents=True)

    prototype = {
        "blocks": [
            {"id": "f1", "type": "features"},
            {"id": "f2", "type": "features"},  # second features block
        ]
    }
    (proto_dir / "prototype.yaml").write_text(yaml.safe_dump(prototype))

    subprocess.run(["python3", str(SCRIPT), "--project", str(project)], check=True)

    body = (project / "01a_АНАЛИЗ_НИШИ" / "landing-structure.md").read_text()
    # section-features.php should appear exactly once in the contract
    assert body.count("section-features.php") == 1


def test_derive_fails_if_no_prototype_yaml(tmp_path):
    project = tmp_path / "test-project"
    project.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
