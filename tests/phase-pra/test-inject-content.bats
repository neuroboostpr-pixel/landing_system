#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  INJECTOR="$ROOT/skills/block-composition/scripts/inject-content.py"
}

@test "substitutes headline into data-slot=headline element" {
  cat > "$BATS_TMPDIR/tmpl.html" <<EOF
<h1 data-slot="headline">[HEADLINE]</h1>
EOF
  cat > "$BATS_TMPDIR/proto.yaml" <<EOF
project: {slug: x, niche: services, source_file: x.pdf}
blocks:
  - position: 1
    type: hero
    headline: "Test headline"
    slots: []
EOF
  run python3 "$INJECTOR" \
      --template "$BATS_TMPDIR/tmpl.html" \
      --prototype "$BATS_TMPDIR/proto.yaml" \
      --position 1 \
      --output "$BATS_TMPDIR/out.html"
  [ "$status" -eq 0 ]
  grep -q "Test headline" "$BATS_TMPDIR/out.html"
  ! grep -q "\[HEADLINE\]" "$BATS_TMPDIR/out.html"
}

@test "substitutes cta text" {
  cat > "$BATS_TMPDIR/tmpl2.html" <<EOF
<a data-slot="primary-cta">[CTA]</a>
EOF
  cat > "$BATS_TMPDIR/proto2.yaml" <<EOF
project: {slug: x, niche: services, source_file: x.pdf}
blocks:
  - position: 1
    type: hero
    cta:
      text: "Buy now"
      action: ""
    slots: []
EOF
  python3 "$INJECTOR" --template "$BATS_TMPDIR/tmpl2.html" \
      --prototype "$BATS_TMPDIR/proto2.yaml" --position 1 --output "$BATS_TMPDIR/out2.html"
  grep -q "Buy now" "$BATS_TMPDIR/out2.html"
}

@test "leaves placeholder for missing slots" {
  cat > "$BATS_TMPDIR/tmpl3.html" <<EOF
<div data-slot="hero-bg"><span class="slot-label">photo</span></div>
EOF
  cat > "$BATS_TMPDIR/proto3.yaml" <<EOF
project: {slug: x, niche: services, source_file: x.pdf}
blocks:
  - position: 1
    type: hero
    slots:
      - {type: photo, name: hero-bg, hint: "интерьер до/после"}
EOF
  python3 "$INJECTOR" --template "$BATS_TMPDIR/tmpl3.html" \
      --prototype "$BATS_TMPDIR/proto3.yaml" --position 1 --output "$BATS_TMPDIR/out3.html"
  grep -q "интерьер до/после" "$BATS_TMPDIR/out3.html"
}
