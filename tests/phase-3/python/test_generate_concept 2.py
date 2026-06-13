import importlib.util
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "visual-concept-generator" / "scripts" / "generate-concept.py"

def _load():
    spec = importlib.util.spec_from_file_location("generate_concept", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _make_brief(tmp_path, goal="Продать премиум EV в Dubai", audience="Состоятельные экспаты 35-55"):
    brief = tmp_path / "00_БРИФ" / "brief.md"
    brief.parent.mkdir(parents=True)
    brief.write_text(f"# Бриф\n\n## Цель\n{goal}\n\n## Аудитория\n{audience}\n", encoding="utf-8")
    return brief

def _make_prototype(tmp_path):
    proto = tmp_path / "07_ПРОТОТИП" / "prototype.yaml"
    proto.parent.mkdir(parents=True)
    data = {"blocks": [
        {"position": 1, "type": "hero", "content": {"headline": "Premium SUVs"}},
        {"position": 2, "type": "trust", "content": {"headline": "Why LiXiang"}},
    ]}
    proto.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return proto

def test_generate_returns_list_of_concepts(tmp_path):
    mod = _load()
    brief = _make_brief(tmp_path)
    proto = _make_prototype(tmp_path)
    concepts = mod.generate_concepts(str(brief), str(proto), [])
    assert isinstance(concepts, list)
    assert 2 <= len(concepts) <= 3

def test_each_concept_has_required_fields(tmp_path):
    mod = _load()
    brief = _make_brief(tmp_path)
    proto = _make_prototype(tmp_path)
    concepts = mod.generate_concepts(str(brief), str(proto), [])
    for c in concepts:
        assert "name" in c
        assert "emotional_goal" in c
        assert "palette" in c
        assert "bg" in c["palette"]
        assert "accent" in c["palette"]
        assert "text" in c["palette"]
        assert "mood" in c

def test_save_concept_writes_yaml(tmp_path):
    mod = _load()
    concept = {
        "name": "Доверие через статус",
        "emotional_goal": "Снять барьер недоверия",
        "palette": {"bg": "#0A0A0A", "accent": "#C9A84C", "text": "#FFFFFF", "surface": "#161616"},
        "typography_direction": "Inter 700",
        "mood": ["cinematic", "luxury"],
        "approved_by_manager": True,
    }
    out = tmp_path / "visual-concept.yaml"
    mod.save_concept(concept, str(out))
    assert out.exists()
    loaded = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert loaded["name"] == "Доверие через статус"
    assert loaded["approved_by_manager"] is True

def test_generate_with_palette_context(tmp_path):
    mod = _load()
    brief = _make_brief(tmp_path)
    proto = _make_prototype(tmp_path)
    palette_context = [{"hex": "#2B72B8", "role": "background", "label": "синий"}]
    concepts = mod.generate_concepts(str(brief), str(proto), palette_context)
    assert len(concepts) >= 2
