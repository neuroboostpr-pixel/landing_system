#!/usr/bin/env bash
PR_H_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

make_fake_project() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07_ПРОТОТИП" "$tmpdir/07b_COMPOSED"
    cat > "$tmpdir/07_ПРОТОТИП/prototype.yaml" <<'YAML'
blocks:
  - id: hero-1
    type: hero
    title: "Welcome to LiXiang"
    cta: "Request a test drive"
  - id: features-1
    type: features
    title: "World of comfort"
    items:
      - text: "Safety first"
      - text: "Quiet ride"
YAML
    cat > "$tmpdir/07b_COMPOSED/composed.html" <<'HTML'
<!DOCTYPE html>
<html><body>
<section data-block="hero-1">
  <h1>Welcome to LiXiang</h1>
  <button>Request a test drive</button>
</section>
<section data-block="features-1">
  <h2>World of comfort</h2>
  <ul><li>Safety first</li><li>Quiet ride</li></ul>
</section>
</body></html>
HTML
    echo "$tmpdir"
}
