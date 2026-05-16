#!/usr/bin/env bash
# PR-L test helpers.

PR_L_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PR_L_REPO_ROOT

# Создать sandbox-репо, где scripts/ — это shim-скрипты, и записать в них желаемые exit-коды.
# args: exit_wiki exit_composed exit_content exit_photo exit_identity exit_visual
pr_l_make_sandbox() {
    local exit_wiki="${1:-0}"
    local exit_composed="${2:-0}"
    local exit_content="${3:-0}"
    local exit_photo="${4:-0}"
    local exit_identity="${5:-0}"
    local exit_visual="${6:-0}"

    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/scripts"

    # Скопировать реальный landing-final-check.sh
    cp "$PR_L_REPO_ROOT/scripts/landing-final-check.sh" "$tmpdir/scripts/landing-final-check.sh"
    chmod +x "$tmpdir/scripts/landing-final-check.sh"

    # Сгенерить shim-скрипты с заданными exit-кодами
    pr_l_make_shim "$tmpdir/scripts/check-wiki-sync.sh" "$exit_wiki" "wiki-sync output"
    pr_l_make_shim "$tmpdir/scripts/verify-composed-premium.sh" "$exit_composed" "composed-premium output"
    pr_l_make_shim "$tmpdir/scripts/verify-content-preserved.sh" "$exit_content" "content-preserved output"
    pr_l_make_shim "$tmpdir/scripts/verify-photo-pipeline.sh" "$exit_photo" "photo-pipeline output"
    pr_l_make_shim "$tmpdir/scripts/verify-identity-preserved.sh" "$exit_identity" "identity-preserved output"
    pr_l_make_shim "$tmpdir/scripts/verify-visual-qa.sh" "$exit_visual" "visual-qa output"

    echo "$tmpdir"
}

pr_l_make_shim() {
    local path="$1"
    local code="$2"
    local msg="$3"
    cat > "$path" <<EOF
#!/usr/bin/env bash
echo "$msg"
exit $code
EOF
    chmod +x "$path"
}

# Создать пустой project-skeleton
pr_l_make_project() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07b_COMPOSED" "$tmpdir/10_QA"
    echo "$tmpdir"
}
