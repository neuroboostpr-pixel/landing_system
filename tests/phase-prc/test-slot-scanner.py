"""Tests for slot-scanner.py — parses composed.html for visual slots."""
from pathlib import Path
import yaml

from skills.visual_generation.scripts.slot_scanner import scan_html


SAMPLE_HTML = """<!DOCTYPE html>
<html><body>
<section class="block" data-block-id="ru-features-01">
  <div data-slot="feature-1-icon" data-slot-type="icon" data-hint="shield"></div>
  <div data-slot="feature-2-icon" data-slot-type="icon"></div>
</section>
<section class="block" data-block-id="ru-stats-01">
  <div data-slot="kpi-clients" data-slot-type="infographic" data-chart-type="number"></div>
</section>
<section class="block" data-block-id="ru-hero-01">
  <div data-slot="hero-bg" data-slot-type="photo"></div>
  <h1 data-slot="headline">Test</h1>
</section>
</body></html>"""


def test_scan_finds_icon_and_infographic_slots(tmp_path):
    html_path = tmp_path / "composed.html"
    html_path.write_text(SAMPLE_HTML)

    result = scan_html(html_path)

    assert "icons" in result
    assert "infographics" in result
    assert len(result["icons"]) == 2
    assert len(result["infographics"]) == 1


def test_scan_captures_hints_and_block_ids(tmp_path):
    html_path = tmp_path / "composed.html"
    html_path.write_text(SAMPLE_HTML)

    result = scan_html(html_path)

    icon1 = result["icons"][0]
    assert icon1["slot_name"] == "feature-1-icon"
    assert icon1["block_id"] == "ru-features-01"
    assert icon1["hint"] == "shield"

    icon2 = result["icons"][1]
    assert icon2["hint"] == ""

    info1 = result["infographics"][0]
    assert info1["chart_type"] == "number"


def test_scan_ignores_photo_and_text_slots(tmp_path):
    html_path = tmp_path / "composed.html"
    html_path.write_text(SAMPLE_HTML)

    result = scan_html(html_path)

    all_slot_names = [s["slot_name"] for s in result["icons"]] + [s["slot_name"] for s in result["infographics"]]
    assert "hero-bg" not in all_slot_names
    assert "headline" not in all_slot_names


def test_scan_empty_html_returns_empty_lists(tmp_path):
    html_path = tmp_path / "composed.html"
    html_path.write_text("<html><body></body></html>")
    result = scan_html(html_path)
    assert result == {"icons": [], "infographics": []}


def test_scan_writes_yaml_output(tmp_path):
    from skills.visual_generation.scripts.slot_scanner import scan_and_write

    html_path = tmp_path / "composed.html"
    html_path.write_text(SAMPLE_HTML)
    out_path = tmp_path / "_slots.yaml"

    scan_and_write(html_path, out_path)

    data = yaml.safe_load(out_path.read_text())
    assert len(data["icons"]) == 2
    assert len(data["infographics"]) == 1
