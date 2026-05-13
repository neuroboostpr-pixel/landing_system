"""Validate the 3 codex prompt templates have the required structure."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TEMPLATES = REPO / "skills" / "photo-curation" / "templates"

REQUIRED_SECTIONS = ["## How to use", "## Placeholders", "## Prompt body", "## Filled example"]


def test_classify_template_has_all_sections():
    body = (TEMPLATES / "classify-prompt.md").read_text()
    for s in REQUIRED_SECTIONS:
        assert s in body, f"classify-prompt.md missing section: {s}"


def test_match_template_has_all_sections():
    body = (TEMPLATES / "match-prompt.md").read_text()
    for s in REQUIRED_SECTIONS:
        assert s in body, f"match-prompt.md missing section: {s}"


def test_generate_fallback_has_all_sections():
    body = (TEMPLATES / "generate-fallback.md").read_text()
    for s in REQUIRED_SECTIONS:
        assert s in body, f"generate-fallback.md missing section: {s}"


def test_generate_fallback_includes_anti_patterns_from_open_design():
    body = (TEMPLATES / "generate-fallback.md").read_text()
    for phrase in ["No lens flare", "No glitch", "No AI watermarks", "No surreal"]:
        assert phrase in body, f"generate-fallback.md missing anti-pattern: {phrase}"


def test_identity_safe_md_exists():
    p = REPO / "skills" / "photo-curation" / "IDENTITY_SAFE.md"
    assert p.exists()
    body = p.read_text()
    for phrase in ["NEVER alter the face", "NEVER AI-repaint", "ai_approved_by_user"]:
        assert phrase in body


def test_skill_md_exists_with_frontmatter():
    p = REPO / "skills" / "photo-curation" / "SKILL.md"
    assert p.exists()
    body = p.read_text()
    assert body.startswith("---")
    assert "name: photo-curation" in body
    assert "description:" in body
