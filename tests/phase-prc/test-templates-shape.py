"""Validate the 2 codex prompt templates have the required structure."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TEMPLATES = REPO / "skills" / "visual-generation" / "templates"

REQUIRED_SECTIONS = ["## How to use", "## Placeholders", "## Prompt body", "## Filled example"]


def test_icon_template_has_all_sections():
    body = (TEMPLATES / "icon-prompt.md").read_text()
    for s in REQUIRED_SECTIONS:
        assert s in body, f"icon-prompt.md missing: {s}"


def test_infographic_template_has_all_sections():
    body = (TEMPLATES / "infographic-prompt.md").read_text()
    for s in REQUIRED_SECTIONS:
        assert s in body, f"infographic-prompt.md missing: {s}"


def test_icon_template_forbids_text_and_faces():
    body = (TEMPLATES / "icon-prompt.md").read_text()
    assert "No text" in body or "no text" in body.lower()
    assert "No photoreal human faces" in body or "no photoreal" in body.lower()


def test_skill_md_exists():
    p = REPO / "skills" / "visual-generation" / "SKILL.md"
    assert p.exists()
    body = p.read_text()
    assert body.startswith("---")
    assert "name: visual-generation" in body
