# tests/phase-3/conftest.py
"""Pytest fixtures for Phase 3 tests."""
import yaml
from pathlib import Path
import pytest


@pytest.fixture
def brand_kit_project(tmp_path):
    """Project dir with 04_БРЕНД/brand-kit.md in Phase 2 format."""
    brand_dir = tmp_path / "04_БРЕНД"
    brand_dir.mkdir(parents=True)
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА").mkdir()

    brand_kit = {
        "brand_kit": {
            "meta": {
                "project": "test-project",
                "created": "2026-05-04",
                "references_used": 2,
            },
            "colors": {
                "primary": {
                    "hex": "#ff5733",
                    "role": "primary",
                    "source": "ref1.png@[10, 20]",
                    "extracted_by": "color-thief",
                },
                "secondary": {
                    "hex": "#33c1ff",
                    "role": "secondary",
                    "source": "ref1.png@[50, 50]",
                    "extracted_by": "color-thief",
                },
                "accent": {
                    "hex": "#2ecc71",
                    "role": "accent",
                    "source": "ref1.png@[80, 80]",
                    "extracted_by": "color-thief",
                },
            },
            "typography": {
                "display": {
                    "family": "Cabinet Grotesk",
                    "confidence": 0.9,
                    "source": "DOM computed style",
                },
                "body": {
                    "family": "Inter",
                    "confidence": 0.9,
                    "source": "DOM computed style",
                },
            },
            "icons": {
                "library": "lucide",
                "selected": [{"id": "lucide:check", "name": "check"}],
            },
            "motion": {"notes": "Subtle transitions, 200-400ms"},
            "grid": {"notes": "12-column grid, 24px gap, 1200px max-width"},
        }
    }

    yaml_block = yaml.dump(brand_kit, allow_unicode=True, default_flow_style=False)
    content = f"---\n{yaml_block}---\n\n# Brand Kit — test-project\n"
    (brand_dir / "brand-kit.md").write_text(content, encoding="utf-8")
    return tmp_path
