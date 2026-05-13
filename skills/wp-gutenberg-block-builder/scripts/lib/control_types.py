ALLOWED_CONTROL_TYPES = frozenset({
    "text", "textarea", "rich-text", "classic-editor", "code-editor",
    "number", "range", "url", "email", "password", "image", "gallery",
    "file", "inner-blocks", "select", "radio", "checkbox", "toggle",
    "color", "date-time", "repeater",
})

RESERVED_ATTRIBUTE_NAMES = frozenset({
    "anchor", "lazyblock", "className", "blockId", "blockUniqueClass",
    "ghostkitSpacings", "ghostkitSR",
})

ALLOWED_BLOCK_TYPES = frozenset({"single", "section-card"})
