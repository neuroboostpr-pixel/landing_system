import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "experimental" / "ds-engine-v2" / "engine"
PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def make_project(tmp_path: Path) -> Path:
    project = tmp_path / "project with spaces"
    mood = project / "05_ДИЗАЙН-СИСТЕМА" / "moods" / "grooming"
    mood.mkdir(parents=True)
    (project / "07_ПРОТОТИП").mkdir(parents=True)
    (project / "07c_PHOTOS").mkdir(parents=True)
    (mood / "recipes.yaml").write_text("meta:\n  mood: grooming\nrecipes: []\n", encoding="utf-8")
    manifest = {
        "meta": {"mood": "grooming"},
        "assets": [
            {
                "id": "page-bg",
                "нужен": True,
                "роль_где": "фон страницы",
                "источник": "снят-с-рефа 01/01 -> CSS",
                "формат": "CSS",
                "слот": "var(--lp-bg)",
                "статус": "готов",
                "режим": "-",
            },
            {
                "id": "page-sweep",
                "нужен": True,
                "роль_где": "сквозная линия",
                "источник": "снят-с-рефа 01/03",
                "формат": "SVG",
                "слот": "{{decor:page-sweep}}",
                "статус": "заглушка",
                "режим": "single",
                "промпт": "Одна тонкая линия, прозрачный фон, без цвета.",
            },
        ],
        "to_generate": [{"id": "page-sweep", "режим": "single", "формат": "SVG"}],
    }
    (mood / "assets-manifest.yaml").write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return project


def run_script(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(ENGINE / script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_gen_assets_report_creates_plan_pack(tmp_path):
    project = make_project(tmp_path)

    result = run_script("gen_assets_report.py", "grooming", "--project", str(project))

    assert result.returncode == 0, result.stderr
    mood = project / "05_ДИЗАЙН-СИСТЕМА" / "moods" / "grooming"
    todo = mood / "ASSETS-TODO.md"
    pack = mood / "asset-pack.yaml"
    assert todo.exists()
    assert pack.exists()
    assert "Полный пакет для верстки" in todo.read_text(encoding="utf-8")
    assert "preview-desktop.png" in todo.read_text(encoding="utf-8")
    assert (mood / "assets" / "prompts.md").exists()
    assert (mood / "assets" / "source-rules.md").exists()

    verify = run_script("verify_ds_asset_pack.py", "--project", str(project), "--mode", "plan")
    assert verify.returncode == 0, verify.stderr


def test_ready_mode_fails_without_real_files(tmp_path):
    project = make_project(tmp_path)
    assert run_script("gen_assets_report.py", "grooming", "--project", str(project)).returncode == 0

    verify = run_script("verify_ds_asset_pack.py", "--project", str(project), "--mode", "ready")

    assert verify.returncode == 1
    assert "нет файлов полного пакета" in verify.stderr


def test_ready_mode_accepts_real_delivery_files(tmp_path):
    project = make_project(tmp_path)
    assert run_script("gen_assets_report.py", "grooming", "--project", str(project)).returncode == 0
    mood = project / "05_ДИЗАЙН-СИСТЕМА" / "moods" / "grooming"
    assets = mood / "assets"

    (assets / "previews" / "preview-desktop.png").write_bytes(PNG_1X1)
    (assets / "previews" / "preview-mobile.png").write_bytes(PNG_1X1)
    (assets / "layers" / "layers.svg").write_text("<svg viewBox='0 0 1 1'></svg>", encoding="utf-8")
    (assets / "canvas" / "canvas-file.md").write_text("Canvas export link or embedded file note.", encoding="utf-8")
    (assets / "decor" / "page-sweep.svg").write_text("<svg viewBox='0 0 1 1'></svg>", encoding="utf-8")

    verify = run_script("verify_ds_asset_pack.py", "--project", str(project), "--mode", "ready")

    assert verify.returncode == 0, verify.stderr
