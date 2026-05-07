#!/usr/bin/env bats

setup() {
  RULES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/niche-visual-rules.yaml"
  # Convert MSYS-style path (/d/...) to native (D:/...) for Python on Windows
  PY_RULES="$(cygpath -m "$RULES" 2>/dev/null || echo "$RULES" | sed 's|^/\([a-z]\)/|\1:/|')"
}

@test "niche-visual-rules.yaml exists" {
  [ -f "$RULES" ]
}

@test "niche-visual-rules.yaml is valid YAML" {
  python -c "import yaml; yaml.safe_load(open('$PY_RULES', encoding='utf-8'))"
}

@test "rules has 4 MVP categories plus default" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
required = {'premium_automotive', 'local_services', 'professional_services', 'b2c_consumer', 'default'}
got = set(d['categories'].keys())
assert required.issubset(got), f"missing: {required - got}"
EOF
}

@test "every category has minimum required fields" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
required = {'description', 'hero_focal', 'hero_composition', 'photography',
            'people', 'product_treatment', 'background_allowed',
            'universal_red_flags', 'universal_preferences'}
for name, cat in d['categories'].items():
    missing = required - set(cat.keys())
    assert not missing, f"category {name} missing: {missing}"
EOF
}

@test "every category has at least 3 red flags and 3 preferences" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
for name, cat in d['categories'].items():
    rf = cat.get('universal_red_flags', [])
    prefs = cat.get('universal_preferences', [])
    assert len(rf) >= 3, f"category {name}: only {len(rf)} red_flags"
    assert len(prefs) >= 3, f"category {name}: only {len(prefs)} preferences"
EOF
}

@test "schema_version is 1" {
  python -c "import yaml; d=yaml.safe_load(open('$PY_RULES', encoding='utf-8')); assert d.get('schema_version') == 1"
}

@test "every category has default_positioning_mode" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
valid_modes = {'rational', 'emotional_aspiration', 'trust_authority',
               'hybrid:emotional_aspiration+trust_authority',
               'hybrid:trust_authority+emotional_aspiration',
               'hybrid:emotional_aspiration+rational',
               'hybrid:trust_authority+rational'}
for name, cat in d['categories'].items():
    mode = cat.get('default_positioning_mode')
    assert mode is not None, f"{name}: no default_positioning_mode"
    assert mode in valid_modes, f"{name}: invalid mode '{mode}'"
EOF
}
