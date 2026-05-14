#!/usr/bin/env bash
# codex-mock — captures arguments, prints canned response based on env $CODEX_MOCK_RESPONSE
echo "MOCK_CODEX_CALLED" >&2
echo "ARGS: $*" >&2
if [ -n "${CODEX_MOCK_RESPONSE:-}" ]; then
    echo "$CODEX_MOCK_RESPONSE"
else
    echo "tags: [portrait]"
    echo "caption: \"Mock photo description\""
    echo "face_count: 1"
fi
exit 0
