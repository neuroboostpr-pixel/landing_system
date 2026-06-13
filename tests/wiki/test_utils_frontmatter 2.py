"""Tests for parse_frontmatter_full — extracts full card metadata."""
import pytest
from scripts.wiki import utils


def test_parse_frontmatter_full_extracts_all_known_fields():
    text = """---
slug: 08-kod
type: stage
stage: "08"
name: "Сборка"
tags: [wp, gutenberg]
triggers: [approve-07b]
inputs: [composed.html]
outputs: [wp-theme/]
gates: [composed_approved]
pre_reqs: [05-design]
related: [landing-build]
confidence:
  gates: low
---
body here
"""
    meta = utils.parse_frontmatter_full(text)
    assert meta["slug"] == "08-kod"
    assert meta["type"] == "stage"
    assert meta["stage"] == "08"
    assert meta["tags"] == ["wp", "gutenberg"]
    assert meta["triggers"] == ["approve-07b"]
    assert meta["inputs"] == ["composed.html"]
    assert meta["outputs"] == ["wp-theme/"]
    assert meta["gates"] == ["composed_approved"]
    assert meta["pre_reqs"] == ["05-design"]
    assert meta["related"] == ["landing-build"]
    assert meta["confidence"] == {"gates": "low"}


def test_parse_frontmatter_full_returns_empty_on_no_frontmatter():
    assert utils.parse_frontmatter_full("just body") == {}


def test_parse_frontmatter_full_returns_empty_on_malformed_yaml():
    text = "---\nslug: [unclosed\n---\nbody"
    assert utils.parse_frontmatter_full(text) == {}


def test_parse_frontmatter_full_unknown_fields_preserved():
    text = """---
slug: x
custom_field: value
---
body
"""
    meta = utils.parse_frontmatter_full(text)
    assert meta["custom_field"] == "value"
