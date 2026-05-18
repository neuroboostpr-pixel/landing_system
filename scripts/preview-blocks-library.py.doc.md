---
type: script
name: preview-blocks-library
language: python
sources: ["scripts/preview-blocks-library.py"]
updated: 2026-05-18
---

# preview-blocks-library.py

Render ALL blocks from block-library/ into one HTML gallery.

Supports BOTH block formats:
  - NEW (imported / scaffolded): <block>/index.html + <block>/styles.css
    Uses {{slot:NAME}} text placeholders.
  - LEGACY (ru-*): <block>/assets/template.html
    Self-contained: <style> + HTML with data-slot attributes.

Each block gets dummy content substituted for slots so the rendered preview
makes visual sense.

Top of page has a sticky nav with category links + a radio filter:
  - Все
  - Только новые импортированные
  - Только legacy ru-*

Output: /tmp/block-library-gallery.html

Usage:
  python3 scripts/preview-blocks-library.py

## Источник

- `scripts/preview-blocks-library.py`
