#!/usr/bin/env bats
# Tests for render-gallery.py and the generated gallery.html

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  GALLERY_SCRIPT="$ROOT/skills/block-library-management/scripts/render-gallery.py"
  LIBRARY="$ROOT/block-library"
  GALLERY_OUT="$BATS_TMPDIR/gallery-$$.html"
}

@test "render-gallery.py script exists" {
  [ -f "$GALLERY_SCRIPT" ]
}

@test "render-gallery.py runs without error" {
  run python3 "$GALLERY_SCRIPT" --library "$LIBRARY" --output "$GALLERY_OUT"
  [ "$status" -eq 0 ]
  [[ "$output" == *"OK:"* ]]
}

@test "gallery.html is generated and non-empty" {
  python3 "$GALLERY_SCRIPT" --library "$LIBRARY" --output "$GALLERY_OUT"
  [ -f "$GALLERY_OUT" ]
  local size
  size=$(wc -c < "$GALLERY_OUT")
  [ "$size" -gt 10000 ]
}

@test "gallery.html contains every block id from catalog" {
  python3 "$GALLERY_SCRIPT" --library "$LIBRARY" --output "$GALLERY_OUT"
  run python3 -c "
import sys, yaml
lib = '$LIBRARY'
gallery_path = '$GALLERY_OUT'
cat = yaml.safe_load(open(f'{lib}/catalog.yaml'))
gallery = open(gallery_path).read()
missing = [b['id'] for b in cat['blocks'] if b['id'] not in gallery]
if missing:
    print('MISSING blocks in gallery:', missing)
    sys.exit(1)
print(f'All {len(cat[\"blocks\"])} blocks found in gallery')
"
  [ "$status" -eq 0 ]
}

@test "gallery.html has filter buttons for each category" {
  python3 "$GALLERY_SCRIPT" --library "$LIBRARY" --output "$GALLERY_OUT"
  run grep -c 'filter-btn' "$GALLERY_OUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 2 ]
}

@test "gallery.html has CSS-only :checked filter rules" {
  python3 "$GALLERY_SCRIPT" --library "$LIBRARY" --output "$GALLERY_OUT"
  run grep -c ':checked' "$GALLERY_OUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 5 ]
}

@test "gallery.html contains iframe thumbnail for each block" {
  python3 "$GALLERY_SCRIPT" --library "$LIBRARY" --output "$GALLERY_OUT"
  run grep -c 'gallery-card' "$GALLERY_OUT"
  [ "$status" -eq 0 ]
  # Should have at least 28 original blocks
  [ "$output" -ge 28 ]
}

@test "pre-built gallery.html exists in block-library/" {
  # The committed gallery should be fresh (generated during CI or manually)
  [ -f "$LIBRARY/gallery.html" ]
}

@test "pre-built gallery.html contains at least 35 blocks" {
  run python3 -c "
import sys, yaml
lib = '$LIBRARY'
cat = yaml.safe_load(open(f'{lib}/catalog.yaml'))
gallery = open(f'{lib}/gallery.html').read()
found = sum(1 for b in cat['blocks'] if b['id'] in gallery)
print(found)
if found < 35:
    sys.exit(1)
"
  [ "$status" -eq 0 ]
  [ "$output" -ge 35 ]
}
