#!/usr/bin/env bats

setup() {
  RULES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/positioning-modes.yaml"
  PY_RULES="$(cygpath -m "$RULES" 2>/dev/null || echo "$RULES" | sed 's|^/\([a-z]\)/|\1:/|')"
}

@test "positioning-modes.yaml exists" {
  [ -f "$RULES" ]
}

@test "positioning-modes.yaml is valid YAML" {
  python -c "import yaml; yaml.safe_load(open('$PY_RULES', encoding='utf-8'))"
}

@test "schema_version is 1" {
  python -c "import yaml; d=yaml.safe_load(open('$PY_RULES', encoding='utf-8')); assert d.get('schema_version') == 1"
}

@test "all 3 modes defined: rational, emotional_aspiration, trust_authority" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
required = {'rational', 'emotional_aspiration', 'trust_authority'}
got = set(d['modes'].keys())
assert required.issubset(got), f"missing modes: {required - got}"
EOF
}

@test "every mode has template_sections (min 4) and typical_categories" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
for name, mode in d['modes'].items():
    assert 'template_sections' in mode, f"{name}: missing template_sections"
    assert len(mode['template_sections']) >= 4, f"{name}: only {len(mode['template_sections'])} sections"
    assert 'typical_categories' in mode, f"{name}: missing typical_categories"
EOF
}

@test "mode_prediction_matrix has at least 5 rules" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
m = d.get('mode_prediction_matrix', [])
assert len(m) >= 5, f"need >=5 rules, got {len(m)}"
EOF
}

@test "brief_indicators has all 3 modes" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
ind = d.get('brief_indicators', {})
assert {'rational', 'emotional_aspiration', 'trust_authority'}.issubset(ind.keys())
for name, words in ind.items():
    assert len(words) >= 5, f"{name}: only {len(words)} indicator words"
EOF
}

@test "matrix predicts known cases correctly" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
matrix = d['mode_prediction_matrix']

def predict(tier, regulated, emotional_load=None):
    for rule in matrix:
        cond = rule['if']
        if tier not in cond.get('accessibility_tier', []):
            continue
        if 'regulated' in cond and cond['regulated'] != regulated:
            continue
        if 'emotional_load' in cond and cond['emotional_load'] != emotional_load:
            continue
        return rule['predict']
    return None

assert predict('premium', False) == 'emotional_aspiration', f"got {predict('premium', False)}"
assert predict('utility_essential', False) == 'rational', f"got {predict('utility_essential', False)}"
assert predict('mid_premium', True) == 'trust_authority', f"got {predict('mid_premium', True)}"
assert predict('premium', True) == 'hybrid:trust_authority+emotional_aspiration', f"got {predict('premium', True)}"
EOF
}
