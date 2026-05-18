#!/usr/bin/env bats
load 'helpers.bash'

# Фикстура: 3 фото (hero, team, product) → правильный greedy mapping
# к слотам ru-hero-01-services-calc (требует hero-bg, photo).

setup() {
    PROJECT_DIR="$(pr_k_make_project)"
    INBOX="$PROJECT_DIR/07c_PHOTOS/inbox"

    # 3 фото с разными ratio
    pr_k_make_jpg "$INBOX/big-cinematic.jpg"  1920 1080  # 16:9 (hero)
    pr_k_make_jpg "$INBOX/team-shot.jpg"      1200 800   # 3:2 (team)
    pr_k_make_jpg "$INBOX/product-1.jpg"      1000 1000  # 1:1 (product)

    pr_k_write_classifications "$INBOX" '{
        "big-cinematic.jpg": {"type": "hero",    "ratio": "16:9", "size": "1920x1080", "hash": "h1"},
        "team-shot.jpg":     {"type": "team",    "ratio": "3:2",  "size": "1200x800",  "hash": "h2"},
        "product-1.jpg":     {"type": "product", "ratio": "1:1",  "size": "1000x1000", "hash": "h3"}
    }'

    # composed.html с тремя блоками: один hero, один team, один product
    cat > "$PROJECT_DIR/07b_COMPOSED/composed.html" <<'HTML'
<!doctype html>
<html><body>
<section data-block="ru-hero-01-services-calc"></section>
</body></html>
HTML
}

teardown() {
    rm -rf "$PROJECT_DIR"
}

@test "match-photos: hero-bg слот получает hero-тип фото (greedy)" {
    run python3 "$PR_K_REPO_ROOT/skills/photo-curation/scripts/match-photos-to-slots.py" \
        "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    [ -f "$PROJECT_DIR/07c_PHOTOS/selections.suggested.yaml" ]

    run python3 -c "
import yaml
d = yaml.safe_load(open('$PROJECT_DIR/07c_PHOTOS/selections.suggested.yaml'))
hero_block = next(b for b in d['blocks'] if b['block_id'] == 'ru-hero-01-services-calc')
assert hero_block['slots']['hero-bg'] == 'big-cinematic.jpg', \
    f'expected big-cinematic.jpg for hero-bg, got {hero_block[\"slots\"]}'
print('hero match OK')
"
    [ "$status" -eq 0 ]
}

@test "match-photos: needs_generation для слотов без подходящих типов" {
    # Подменим — оставим только product
    pr_k_write_classifications "$INBOX" '{
        "product-1.jpg": {"type": "product", "ratio": "1:1", "size": "1000x1000", "hash": "h3"}
    }'

    run python3 "$PR_K_REPO_ROOT/skills/photo-curation/scripts/match-photos-to-slots.py" \
        "$PROJECT_DIR"
    [ "$status" -eq 0 ]

    # hero-bg слот не должен закрыться (product не в hero prefs)
    run python3 -c "
import yaml
d = yaml.safe_load(open('$PROJECT_DIR/07c_PHOTOS/selections.suggested.yaml'))
hero_block = next(b for b in d['blocks'] if b['block_id'] == 'ru-hero-01-services-calc')
assert hero_block['slots']['hero-bg'] == '__NEEDS_GENERATION__', \
    f'should need gen, got {hero_block[\"slots\"]}'
assert any(g['slot'] == 'hero-bg' for g in d['needs_generation']), \
    f'needs_generation missing hero-bg: {d[\"needs_generation\"]}'
print('needs_gen OK')
"
    [ "$status" -eq 0 ]
}

@test "match-photos: каждое фото используется не более одного раза" {
    # Добавим второй hero-блок чтобы был conflict
    cat > "$PROJECT_DIR/07b_COMPOSED/composed.html" <<'HTML'
<!doctype html>
<html><body>
<section data-block="ru-hero-01-services-calc"></section>
<section data-block="ru-hero-02-b2c-expert"></section>
</body></html>
HTML

    run python3 "$PR_K_REPO_ROOT/skills/photo-curation/scripts/match-photos-to-slots.py" \
        "$PROJECT_DIR"
    [ "$status" -eq 0 ]

    run python3 -c "
import yaml
d = yaml.safe_load(open('$PROJECT_DIR/07c_PHOTOS/selections.suggested.yaml'))
used = []
for block in d['blocks']:
    for slot, fname in block['slots'].items():
        if fname != '__NEEDS_GENERATION__':
            used.append(fname)
assert len(used) == len(set(used)), f'duplicates! {used}'
print('no dupes OK')
"
    [ "$status" -eq 0 ]
}
