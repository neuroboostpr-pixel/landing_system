#!/usr/bin/env bats
load 'helpers.bash'

# Проверяем что повторный classify не зовёт codex для тех же файлов
# (hash-cache работает). Мокаем codex через CODEX_CLASSIFY_MOCK.

setup() {
    PROJECT_DIR="$(pr_k_make_project)"
    INBOX="$PROJECT_DIR/07c_PHOTOS/inbox"
    pr_k_make_jpg "$INBOX/team-photo-1.jpg" 1920 1080
}

teardown() {
    rm -rf "$PROJECT_DIR"
}

@test "classify-photos: первый прогон — заполняет .classifications.json" {
    run env CODEX_CLASSIFY_MOCK="team" \
        python3 "$PR_K_REPO_ROOT/skills/photo-curation/scripts/classify-photos.py" \
        "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    [ -f "$INBOX/.classifications.json" ]
    run python3 -c "
import json
d = json.load(open('$INBOX/.classifications.json'))
assert d['team-photo-1.jpg']['type'] == 'team', d
assert 'hash' in d['team-photo-1.jpg'], d
print('OK')
"
    [ "$status" -eq 0 ]
}

@test "classify-photos: повторный прогон — НЕ зовёт codex (cache hit)" {
    # Первый прогон с моком "team"
    env CODEX_CLASSIFY_MOCK="team" \
        python3 "$PR_K_REPO_ROOT/skills/photo-curation/scripts/classify-photos.py" \
        "$PROJECT_DIR" >/dev/null 2>&1

    # Второй прогон с моком "hero" — должен НЕ переопределить,
    # потому что hash совпадает (cache hit).
    run env CODEX_CLASSIFY_MOCK="hero" \
        python3 "$PR_K_REPO_ROOT/skills/photo-curation/scripts/classify-photos.py" \
        "$PROJECT_DIR"
    [ "$status" -eq 0 ]

    run python3 -c "
import json
d = json.load(open('$INBOX/.classifications.json'))
assert d['team-photo-1.jpg']['type'] == 'team', \
    f'cache miss! got {d[\"team-photo-1.jpg\"]}'
print('cache hit OK')
"
    [ "$status" -eq 0 ]
}

@test "classify-photos: меняем файл → cache invalidates (новый hash)" {
    env CODEX_CLASSIFY_MOCK="team" \
        python3 "$PR_K_REPO_ROOT/skills/photo-curation/scripts/classify-photos.py" \
        "$PROJECT_DIR" >/dev/null 2>&1

    # Заменяем содержимое файла — должен пересчитаться
    pr_k_make_jpg "$INBOX/team-photo-1.jpg" 1000 1000

    run env CODEX_CLASSIFY_MOCK="hero" \
        python3 "$PR_K_REPO_ROOT/skills/photo-curation/scripts/classify-photos.py" \
        "$PROJECT_DIR"
    [ "$status" -eq 0 ]

    run python3 -c "
import json
d = json.load(open('$INBOX/.classifications.json'))
assert d['team-photo-1.jpg']['type'] == 'hero', \
    f'cache should have invalidated, got {d[\"team-photo-1.jpg\"]}'
print('invalidate OK')
"
    [ "$status" -eq 0 ]
}
