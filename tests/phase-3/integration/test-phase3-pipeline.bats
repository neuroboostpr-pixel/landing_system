#!/usr/bin/env bats
# tests/phase-3/integration/test-phase3-pipeline.bats

load '../../helpers/test_helpers'

BUILD_SCRIPT="$LANDING_SYSTEM_ROOT/skills/design-tokens-generation/scripts/build-tokens.py"
RENDER_SCRIPT="$LANDING_SYSTEM_ROOT/skills/design-tokens-generation/scripts/render-preview.py"

setup() {
  PROJECT_DIR="$(mktemp -d)"
  mkdir -p "$PROJECT_DIR/04_БРЕНД" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА"

  python3 -c "
import yaml, pathlib
brand_kit = {
    'brand_kit': {
        'meta': {'project': 'test', 'created': '2026-05-04', 'references_used': 1},
        'colors': {
            'primary': {'hex': '#ff5733', 'role': 'primary', 'source': 'ref1.png'},
            'secondary': {'hex': '#33c1ff', 'role': 'secondary', 'source': 'ref1.png'},
            'accent': {'hex': '#2ecc71', 'role': 'accent', 'source': 'ref1.png'},
        },
        'typography': {
            'display': {'family': 'Cabinet Grotesk', 'confidence': 0.9, 'source': 'DOM'},
            'body': {'family': 'Inter', 'confidence': 0.9, 'source': 'DOM'},
        },
        'icons': {'library': 'lucide', 'selected': [{'id': 'lucide:check', 'name': 'check'}]},
        'motion': {'notes': 'Subtle transitions, 200-400ms'},
        'grid': {'notes': '12-column grid, 24px gap'},
    }
}
yaml_block = yaml.dump(brand_kit, allow_unicode=True, default_flow_style=False)
content = f'---\n{yaml_block}---\n\n# Brand Kit\n'
pathlib.Path('$PROJECT_DIR/04_БРЕНД/brand-kit.md').write_text(content, encoding='utf-8')
"
}

teardown() {
  rm -rf "$PROJECT_DIR"
}

@test "phase3 integration: build-tokens.py produces DESIGN.md" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  [ -f "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/DESIGN.md" ]
}

@test "phase3 integration: DESIGN.md has YAML frontmatter" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  grep -q "^---" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"
  grep -q "tokens:" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"
}

@test "phase3 integration: tokens.json is valid JSON" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  python3 -c "import json; json.load(open('$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/tokens.json', encoding='utf-8'))"
}

@test "phase3 integration: render-preview.py produces design-preview.html" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  python3 "$RENDER_SCRIPT" "$PROJECT_DIR"
  [ -f "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/design-preview.html" ]
}

@test "phase3 integration: design-preview.html contains color swatch" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  python3 "$RENDER_SCRIPT" "$PROJECT_DIR"
  grep -q "#ff5733" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/design-preview.html"
}

@test "phase3 integration: design-preview.html contains font specimen" {
  python3 "$BUILD_SCRIPT" "$PROJECT_DIR"
  python3 "$RENDER_SCRIPT" "$PROJECT_DIR"
  grep -q "Cabinet Grotesk" "$PROJECT_DIR/05_ДИЗАЙН-СИСТЕМА/design-preview.html"
}
