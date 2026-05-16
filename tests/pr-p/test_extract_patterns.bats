#!/usr/bin/env bats
# PR-P: extract-patterns.py грепает CSS-фикстуру и возвращает JSON
# со всеми ожидаемыми ключами (@keyframes, hover, backdrop-filter и т.д.).

PR_P_REPO_ROOT="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
EXTRACT="$PR_P_REPO_ROOT/scripts/extract-effects/extract-patterns.py"

setup() {
    TMP="$(mktemp -d)"
    SCRAPED="$TMP/scraped"
    mkdir -p "$SCRAPED"

    # CSS-фикстура с премиум-эффектами
    cat > "$SCRAPED/inline.css" <<'CSS'
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 10px rgba(255,200,100,0.5); }
  50% { box-shadow: 0 0 30px rgba(255,200,100,0.9); }
}

.btn-primary {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%);
}

.btn-primary:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 12px 40px rgba(255, 107, 107, 0.4);
}

.nav-glass {
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
}

.angled {
  clip-path: polygon(0 0, 100% 0, 100% 90%, 0 100%);
}

.text-overlay {
  mix-blend-mode: difference;
}

.grid-features {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

@media (prefers-reduced-motion: no-preference) {
  .reveal { transition: opacity 0.7s ease; }
}
CSS
}

teardown() {
    rm -rf "$TMP"
}

@test "extract-patterns: возвращает валидный JSON" {
    run python3 "$EXTRACT" "$SCRAPED"
    [ "$status" -eq 0 ]
    echo "$output" | python3 -c "import json, sys; json.loads(sys.stdin.read())"
}

@test "extract-patterns: находит keyframes" {
    run python3 "$EXTRACT" "$SCRAPED"
    [ "$status" -eq 0 ]
    echo "$output" | python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
assert 'keyframes' in d, f'keyframes missing: {list(d.keys())}'
assert any('fadeIn' in str(k) or 'pulseGlow' in str(k) for k in d['keyframes']), d['keyframes']
"
}

@test "extract-patterns: находит hover_states" {
    run python3 "$EXTRACT" "$SCRAPED"
    [ "$status" -eq 0 ]
    echo "$output" | python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
assert 'hover_states' in d and len(d['hover_states']) > 0, d
"
}

@test "extract-patterns: находит backdrop-filter и clip-path" {
    run python3 "$EXTRACT" "$SCRAPED"
    [ "$status" -eq 0 ]
    echo "$output" | python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
for key in ('backdrop_filter', 'clip_path', 'mix_blend', 'motion_safe', 'grid_auto'):
    assert key in d and len(d[key]) > 0, f'{key} missing from {list(d.keys())}'
"
}

@test "extract-patterns: транзишены и transform_3d найдены" {
    run python3 "$EXTRACT" "$SCRAPED"
    [ "$status" -eq 0 ]
    echo "$output" | python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
assert 'transitions' in d and len(d['transitions']) > 0
assert 'transform_3d' in d and len(d['transform_3d']) > 0
"
}
