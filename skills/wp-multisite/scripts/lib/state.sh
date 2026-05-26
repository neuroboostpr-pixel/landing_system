#!/usr/bin/env bash
# Read/write helpers for <project>/.landing-state.yaml
# Uses python+PyYAML (assumed installed; same as rest of landing-system).
#
# SECURITY: All user-supplied values (state path, slug, host, blog_id, field name)
# are passed to Python via os.environ, never interpolated into Python source code.

# Python helper invocation — handle Windows/Linux python binary name.

# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../../../scripts/lib/python-cmd.sh
. "$__SCRIPT_DIR__/../../../../scripts/lib/python-cmd.sh"
_state_py() {
    # Prefer $PYTHON_CMD only if it actually runs (Windows Store stub returns exit 49)
    if $PYTHON_CMD -c "import sys" >/dev/null 2>&1; then
        echo $PYTHON_CMD
    elif python -c "import sys" >/dev/null 2>&1; then
        echo python
    else
        echo $PYTHON_CMD  # fallback, will produce a useful error
    fi
}

state_get_field() {
    # state_get_field <state.yaml> <field-name> — print top-level field value
    local state="$1" field="$2"
    STATE_FILE="$state" STATE_FIELD="$field" \
    "$(_state_py)" -c '
import yaml, os, sys
state = os.environ["STATE_FILE"]
field = os.environ["STATE_FIELD"]
with open(state, encoding="utf-8") as f:
    d = yaml.safe_load(f) or {}
print(d.get(field, ""))
'
}

state_is_multisite() {
    # state_is_multisite <state.yaml> — exit 0 if multisite==true, 1 otherwise
    local state="$1"
    local result
    result=$(STATE_FILE="$state" "$(_state_py)" -c '
import yaml, os
state = os.environ["STATE_FILE"]
with open(state, encoding="utf-8") as f:
    d = yaml.safe_load(f) or {}
print("yes" if d.get("multisite") is True else "no")
')
    [ "$result" = "yes" ]
}

state_set_multisite_true() {
    # state_set_multisite_true <state.yaml> — flip flag, preserve other fields
    local state="$1"
    STATE_FILE="$state" "$(_state_py)" -c '
import yaml, os
state = os.environ["STATE_FILE"]
with open(state, encoding="utf-8") as f:
    d = yaml.safe_load(f) or {}
d["multisite"] = True
if "audience_segments" not in d:
    d["audience_segments"] = []
with open(state, "w", encoding="utf-8") as f:
    yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False)
'
}

state_add_segment() {
    # state_add_segment <state.yaml> <slug> <host> <blog_id>
    local state="$1" slug="$2" host="$3" blog_id="$4"
    STATE_FILE="$state" SEG_SLUG="$slug" SEG_HOST="$host" SEG_BLOG_ID="$blog_id" \
    "$(_state_py)" -c '
import yaml, os, datetime
state   = os.environ["STATE_FILE"]
slug    = os.environ["SEG_SLUG"]
host    = os.environ["SEG_HOST"]
blog_id = int(os.environ["SEG_BLOG_ID"])
with open(state, encoding="utf-8") as f:
    d = yaml.safe_load(f) or {}
d.setdefault("audience_segments", [])
d["audience_segments"].append({
    "slug":    slug,
    "host":    host,
    "blog_id": blog_id,
    "created": datetime.datetime.utcnow().isoformat() + "Z",
})
with open(state, "w", encoding="utf-8") as f:
    yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False)
'
}

state_segment_count() {
    # state_segment_count <state.yaml> — print number of audience_segments
    local state="$1"
    STATE_FILE="$state" "$(_state_py)" -c '
import yaml, os
state = os.environ["STATE_FILE"]
with open(state, encoding="utf-8") as f:
    d = yaml.safe_load(f) or {}
print(len(d.get("audience_segments", [])))
'
}

state_segment_exists() {
    # state_segment_exists <state.yaml> <slug> — exit 0 if found, 1 if not
    local state="$1" slug="$2"
    local found
    found=$(STATE_FILE="$state" SEG_SLUG="$slug" "$(_state_py)" -c '
import yaml, os
state = os.environ["STATE_FILE"]
slug  = os.environ["SEG_SLUG"]
with open(state, encoding="utf-8") as f:
    d = yaml.safe_load(f) or {}
print("yes" if any(s.get("slug") == slug for s in d.get("audience_segments", [])) else "no")
')
    [ "$found" = "yes" ]
}
