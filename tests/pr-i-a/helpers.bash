#!/usr/bin/env bash
PR_I_A_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

make_project_with_placeholder() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07b_COMPOSED" "$tmpdir/07c_PHOTOS/processed"
    cat > "$tmpdir/07b_COMPOSED/composed.html" <<'HTML'
<!DOCTYPE html>
<html><body>
<section data-block="hero-1">
  <img src="placeholder-1920x1080.svg" alt="hero">
</section>
</body></html>
HTML
    echo "$tmpdir"
}

make_project_with_real_photos() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07b_COMPOSED" "$tmpdir/07c_PHOTOS/processed"
    # Создать dummy JPG 1x1
    python3 -c "
from PIL import Image
Image.new('RGB', (1920, 1080), (200, 200, 200)).save('$tmpdir/07c_PHOTOS/processed/hero-bg.jpg')
"
    cat > "$tmpdir/07b_COMPOSED/composed.html" <<'HTML'
<!DOCTYPE html>
<html><body>
<section data-block="hero-1">
  <img src="../07c_PHOTOS/processed/hero-bg.jpg" alt="hero">
</section>
</body></html>
HTML
    echo '{"hero-bg.jpg": {"slot": "hero-bg", "status": "processed"}}' > "$tmpdir/07c_PHOTOS/processed/manifest.json"
    echo "$tmpdir"
}

make_project_with_visual_assets_only() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07b_COMPOSED" "$tmpdir/07d_VISUALS/icons"
    cat > "$tmpdir/07b_COMPOSED/composed.html" <<'HTML'
<!DOCTYPE html>
<html><body>
<section data-block="hero-1">
  <img class="lp-icon" data-slot-type="icon" src="../07d_VISUALS/icons/feature-1.svg" alt="icon">
  <img data-slot="decor:page-sweep" src="../05_ДИЗАЙН-СИСТЕМА/moods/grooming/assets/decor/page-sweep.svg" alt="">
</section>
</body></html>
HTML
    echo "$tmpdir"
}
