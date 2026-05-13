"""Tests for skills/photo-curation/scripts/intake.py"""
import shutil
from pathlib import Path

import yaml

from skills.photo_curation.scripts.intake import (
    run_intake,
    SUBFOLDER_TO_TAG,
    INTAKE_SUBFOLDERS,
)


FIXTURES = Path(__file__).parent / "fixtures"


def test_subfolder_constants_match_spec():
    # Per spec D10 + section "Дерево артефактов": 6 named subfolders + _свалка = 7 total
    assert len(INTAKE_SUBFOLDERS) == 7
    assert "_свалка" in INTAKE_SUBFOLDERS
    assert "портреты_и_команда" in INTAKE_SUBFOLDERS
    assert SUBFOLDER_TO_TAG["портреты_и_команда"] == ["portrait", "team"]


def test_intake_copies_subfolder_photo_with_folder_tag(tmp_path):
    src = tmp_path / "07c_PHOTOS"
    inbox = src / "inbox" / "портреты_и_команда"
    inbox.mkdir(parents=True)
    shutil.copy(FIXTURES / "red.jpg", inbox / "ceo.jpg")

    intake_dir = src / "intake"
    run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)

    # 1 file in intake/ (excluding thumbnails)
    jpgs = [p for p in intake_dir.glob("*.jpg") if not p.name.endswith(".thumb.jpg")]
    assert len(jpgs) == 1
    assert (intake_dir / "intake-report.yaml").exists()

    rpt = yaml.safe_load((intake_dir / "intake-report.yaml").read_text())
    assert len(rpt["photos"]) == 1
    photo = rpt["photos"][0]
    assert photo["original_name"] == "ceo.jpg"
    assert photo["folder_origin"] == "портреты_и_команда"
    assert photo["tag_source"] == "folder"
    assert sorted(photo["tags"]) == ["portrait", "team"]


def test_intake_dumps_unsorted_photo_as_pending_ai_classify(tmp_path):
    src = tmp_path / "07c_PHOTOS"
    inbox = src / "inbox" / "_свалка"
    inbox.mkdir(parents=True)
    shutil.copy(FIXTURES / "green.jpg", inbox / "random.jpg")

    intake_dir = src / "intake"
    run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)

    rpt = yaml.safe_load((intake_dir / "intake-report.yaml").read_text())
    photo = rpt["photos"][0]
    assert photo["folder_origin"] == "_свалка"
    assert photo["tag_source"] == "pending_ai_classify"
    assert photo["tags"] == []


def test_intake_dedupes_by_hash(tmp_path):
    src = tmp_path / "07c_PHOTOS"
    inbox = src / "inbox" / "_свалка"
    inbox.mkdir(parents=True)
    shutil.copy(FIXTURES / "red.jpg", inbox / "first.jpg")
    shutil.copy(FIXTURES / "red.jpg", inbox / "duplicate.jpg")
    shutil.copy(FIXTURES / "green.jpg", inbox / "unique.jpg")

    intake_dir = src / "intake"
    run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)

    rpt = yaml.safe_load((intake_dir / "intake-report.yaml").read_text())
    # 2 unique photos (red deduped)
    assert len(rpt["photos"]) == 2


def test_intake_creates_thumbnail(tmp_path):
    src = tmp_path / "07c_PHOTOS"
    inbox = src / "inbox" / "_свалка"
    inbox.mkdir(parents=True)
    shutil.copy(FIXTURES / "red.jpg", inbox / "x.jpg")

    intake_dir = src / "intake"
    run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)

    thumbs = list(intake_dir.glob("*.thumb.jpg"))
    assert len(thumbs) == 1
    from PIL import Image
    with Image.open(thumbs[0]) as img:
        assert max(img.size) == 256


def test_intake_idempotent(tmp_path):
    src = tmp_path / "07c_PHOTOS"
    inbox = src / "inbox" / "_свалка"
    inbox.mkdir(parents=True)
    shutil.copy(FIXTURES / "red.jpg", inbox / "x.jpg")

    intake_dir = src / "intake"
    run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)
    first_files = sorted(p.name for p in intake_dir.iterdir())

    run_intake(inbox_root=src / "inbox", intake_dir=intake_dir)
    second_files = sorted(p.name for p in intake_dir.iterdir())

    assert first_files == second_files
