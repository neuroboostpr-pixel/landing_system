#!/usr/bin/env bats
load 'helpers.bash'

# composed.html с hero <img>, чей ratio расходится со slot.ratio >5% →
# verify_photo_pipeline.py exit 1 с сообщением «hero не должен обрезаться».

setup() {
    PROJECT_DIR="$(pr_k_make_project)"
    mkdir -p "$PROJECT_DIR/07c_PHOTOS/processed"
    echo '{}' > "$PROJECT_DIR/07c_PHOTOS/processed/manifest.json"
}

teardown() {
    rm -rf "$PROJECT_DIR"
}

@test "verify_photo_pipeline: hero ratio мismatch >5% → exit 1" {
    # block ru-hero-01-services-calc требует hero-bg: 16:9 (~1.778).
    # Кладём фото 1:1 (=1.0) — отклонение ~44%.
    pr_k_make_jpg "$PROJECT_DIR/07c_PHOTOS/processed/hero-1x1.jpg" 1000 1000

    cat > "$PROJECT_DIR/07b_COMPOSED/composed.html" <<'HTML'
<!doctype html>
<html><body>
<section data-block="ru-hero-01-services-calc">
  <img src="../07c_PHOTOS/processed/hero-1x1.jpg" data-slot="hero-bg" alt="">
</section>
</body></html>
HTML

    run python3 "$PR_K_REPO_ROOT/scripts/verify_photo_pipeline.py" "$PROJECT_DIR"
    [ "$status" -eq 1 ]
    [[ "$output" == *"hero не должен обрезаться"* ]]
}

@test "verify_photo_pipeline: hero ratio match — OK" {
    # 16:9 фото для 16:9 слота
    pr_k_make_jpg "$PROJECT_DIR/07c_PHOTOS/processed/hero-16x9.jpg" 1920 1080

    cat > "$PROJECT_DIR/07b_COMPOSED/composed.html" <<'HTML'
<!doctype html>
<html><body>
<section data-block="ru-hero-01-services-calc">
  <img src="../07c_PHOTOS/processed/hero-16x9.jpg" data-slot="hero-bg" alt="">
</section>
</body></html>
HTML

    run python3 "$PR_K_REPO_ROOT/scripts/verify_photo_pipeline.py" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
}

@test "verify_photo_pipeline: hero ratio в пределах 5% — OK (1900x1080 ≈ 16:9)" {
    # 1900/1080 = 1.759, 16/9 = 1.778, dev = 1.05% < 5%
    pr_k_make_jpg "$PROJECT_DIR/07c_PHOTOS/processed/hero-close.jpg" 1900 1080

    cat > "$PROJECT_DIR/07b_COMPOSED/composed.html" <<'HTML'
<!doctype html>
<html><body>
<section data-block="ru-hero-01-services-calc">
  <img src="../07c_PHOTOS/processed/hero-close.jpg" data-slot="hero-bg" alt="">
</section>
</body></html>
HTML

    run python3 "$PR_K_REPO_ROOT/scripts/verify_photo_pipeline.py" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
}
