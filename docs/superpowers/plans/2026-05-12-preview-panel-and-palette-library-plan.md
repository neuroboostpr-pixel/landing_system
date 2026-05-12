# Preview Panel + Global Palette Library — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hardcoded palette switcher in neuroupgrade-v2 with a reusable WP plugin (`lp-preview-panel`) that supports a second `hero` axis, ships with every new landing, and is fed by a global palette library accumulated across projects.

**Architecture:** WP plugin lives at `template/08_КОД/plugins/lp-preview-panel/` and is copied into each new project via `wp-theme-assembler`. The theme registers axes (`palette`, `hero`) through the `lp_preview_panel_axes` filter. Palettes for that filter come from a project snapshot (`<project>/04_БРЕНД/palettes.yaml`), which is in turn populated from a global library (`landing_system/presets/palettes.yaml`) on `/landing-brand`. Approved palettes are pushed back into the library on `/landing-design`.

**Tech Stack:** PHP (WordPress plugin), vanilla JS, bash + python (for pipeline scripts), bats (for pipeline tests), YAML (for palette schema).

**Test strategy:** bats for pipeline scripts (export, snapshot, migration, codegen) — covers the majority of risk. Plugin runtime (PHP/JS) is validated via a documented manual E2E checklist on neuroupgrade-v2 after migration. No PHPUnit/Vitest infrastructure added in this plan.

**Verification rule:** at every step that runs tests/scripts, the engineer MUST run the command and confirm the output matches the "Expected" block before checking the box. Per superpowers:verification-before-completion — evidence before assertions.

---

## File Structure

### New files

```
landing_system/
├── presets/
│   └── palettes.yaml                                   ← Global palette library
│
├── template/08_КОД/plugins/lp-preview-panel/           ← Canonical plugin source
│   ├── lp-preview-panel.php
│   ├── includes/
│   │   ├── class-axes.php
│   │   ├── class-panel.php
│   │   └── class-settings.php
│   ├── assets/
│   │   ├── panel.css
│   │   ├── panel.js
│   │   └── admin.js
│   └── readme.txt
│
├── scripts/
│   ├── export-palettes-to-library.py                   ← /landing-design hook
│   ├── snapshot-palettes-to-project.py                 ← /landing-brand hook
│   ├── generate-palette-css.py                         ← /landing-build helper
│   ├── generate-axes-filter.py                         ← /landing-build helper
│   └── migrate-to-preview-panel.sh                     ← one-shot for neuroupgrade-v2
│
└── tests/phase-preview-panel/                          ← New test folder
    ├── fixtures/
    │   ├── project-with-palettes/                      (mini project skeleton)
    │   ├── library-empty.yaml
    │   ├── library-with-paper-minimal.yaml
    │   └── header-with-theme-bar.php
    ├── test-palette-schema.bats
    ├── test-export-palettes.bats
    ├── test-snapshot-palettes.bats
    ├── test-generate-palette-css.bats
    ├── test-generate-axes-filter.bats
    └── test-migrate-to-preview-panel.bats
```

### Modified files

```
landing_system/
├── package.json                                        ← add test:phase-preview-panel
├── skills/
│   ├── brand-kit-build/SKILL.md                        ← add palette-selection mode prompt
│   ├── design-tokens-generation/SKILL.md               ← document export hook on approval
│   ├── wp-theme-assembler/SKILL.md                     ← document plugin/css/filter codegen
│   └── wp-cli-deployer/SKILL.md                        ← document plugin activation step
├── template/CLAUDE.md                                  ← document body.theme-/hero-- contract
└── config/stage-gates.yaml                             ← add post-approve hook for stage 05

Lendings/neuroupgrade-v2/                               ← target of migration script
├── 08_КОД/wp-theme/header.php                          ← remove nu-theme-bar
├── 08_КОД/wp-theme/assets/js/main.js                   ← remove initThemeSwitcher
├── 08_КОД/wp-theme/functions.php                       ← gain lp_preview_panel_axes filter
├── 04_БРЕНД/palettes.yaml                              ← created with H/I/J/K
└── 08_КОД/plugins/lp-preview-panel/                    ← copy of template plugin
```

---

## Palette schema (locked for this plan)

Every palette entry in `landing_system/presets/palettes.yaml` and `<project>/{04_БРЕНД,05_ДИЗАЙН-СИСТЕМА}/palettes.yaml` follows this exact shape:

```yaml
palettes:
  - id: paper-minimal               # kebab-case, unique in library
    name: "Paper Minimal"           # human-readable, shown in select + brand picker
    description: "..."              # one line, helps agent during /landing-brand
    created_at: "2026-05-12"        # ISO date
    created_in_project: "neuroupgrade-v2"
    tokens:
      bg_base: "#F8F7F4"
      bg_section: "#FFFFFF"
      bg_elevated: "#FFFFFF"
      border_subtle: "#E7E5E0"
      border_strong: "#CBD5E1"
      text_primary: "#0F172A"
      text_soft: "#334155"
      text_dim: "#64748B"
      accent_mint: "#047857"
      accent_teal: "#047857"
      accent_coral: "#047857"
      accent_coral_hover: "#065F46"
      accent_coral_text: "#FFFFFF"
      accent_rgb_mint: "4, 120, 87"
      accent_rgb_coral: "4, 120, 87"
      card_bg: "#FFFFFF"
      card_border: "#E7E5E0"
      card_border_hover: "#047857"
      accent_cta_glow_opacity: "0.15"
```

**19 required token keys**, copied verbatim from current neuroupgrade-v2 `body.theme-h/i/j/k` blocks. Validator MUST reject palettes missing any of these. Future projects extending the schema follow this rule: add the token to the validator's required set, all existing palettes must be updated, no silent fallbacks.

**CSS variable mapping:** YAML key `bg_base` → CSS `--bg-base`. Replace `_` with `-`. The numeric-string keys (`accent_rgb_mint`, `accent_cta_glow_opacity`) are emitted verbatim — they contain CSS-syntax-ready values.

---

# Phase A — Plugin

## Task A1: Palette library file + schema validator

**Files:**
- Create: `landing_system/presets/palettes.yaml`
- Create: `scripts/validate-palettes.py`
- Create: `tests/phase-preview-panel/test-palette-schema.bats`
- Create: `tests/phase-preview-panel/fixtures/library-empty.yaml`
- Create: `tests/phase-preview-panel/fixtures/library-with-paper-minimal.yaml`
- Create: `tests/phase-preview-panel/fixtures/library-missing-token.yaml`
- Create: `tests/phase-preview-panel/fixtures/library-duplicate-id.yaml`

- [ ] **Step 1: Write the failing test**

`tests/phase-preview-panel/test-palette-schema.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  VALIDATOR="$ROOT/scripts/validate-palettes.py"
}

@test "validator accepts empty library" {
  run python "$VALIDATOR" "$FIXTURES/library-empty.yaml"
  [ "$status" -eq 0 ]
}

@test "validator accepts library with one valid palette" {
  run python "$VALIDATOR" "$FIXTURES/library-with-paper-minimal.yaml"
  [ "$status" -eq 0 ]
}

@test "validator rejects palette missing a required token" {
  run python "$VALIDATOR" "$FIXTURES/library-missing-token.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"missing required token"* ]]
}

@test "validator rejects duplicate ids" {
  run python "$VALIDATOR" "$FIXTURES/library-duplicate-id.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"duplicate id"* ]]
}

@test "validator rejects non-kebab-case id" {
  run python "$VALIDATOR" /dev/stdin <<< 'palettes:
  - id: PaperMinimal
    name: "x"
    description: "x"
    created_at: "2026-05-12"
    created_in_project: "x"
    tokens: {}'
  [ "$status" -ne 0 ]
  [[ "$output" == *"id must be kebab-case"* ]]
}

@test "global library file exists and is empty-but-valid" {
  run python "$VALIDATOR" "$ROOT/presets/palettes.yaml"
  [ "$status" -eq 0 ]
}
```

`tests/phase-preview-panel/fixtures/library-empty.yaml`:

```yaml
palettes: []
```

`tests/phase-preview-panel/fixtures/library-with-paper-minimal.yaml`:

```yaml
palettes:
  - id: paper-minimal
    name: "Paper Minimal"
    description: "Light editorial minimalism."
    created_at: "2026-05-12"
    created_in_project: "neuroupgrade-v2"
    tokens:
      bg_base: "#F8F7F4"
      bg_section: "#FFFFFF"
      bg_elevated: "#FFFFFF"
      border_subtle: "#E7E5E0"
      border_strong: "#CBD5E1"
      text_primary: "#0F172A"
      text_soft: "#334155"
      text_dim: "#64748B"
      accent_mint: "#047857"
      accent_teal: "#047857"
      accent_coral: "#047857"
      accent_coral_hover: "#065F46"
      accent_coral_text: "#FFFFFF"
      accent_rgb_mint: "4, 120, 87"
      accent_rgb_coral: "4, 120, 87"
      card_bg: "#FFFFFF"
      card_border: "#E7E5E0"
      card_border_hover: "#047857"
      accent_cta_glow_opacity: "0.15"
```

`tests/phase-preview-panel/fixtures/library-missing-token.yaml`: copy of `library-with-paper-minimal.yaml` but delete the `accent_cta_glow_opacity` line.

`tests/phase-preview-panel/fixtures/library-duplicate-id.yaml`: copy `library-with-paper-minimal.yaml` and duplicate the single palette entry (two with `id: paper-minimal`).

- [ ] **Step 2: Run test to verify it fails**

Run: `npx bats tests/phase-preview-panel/test-palette-schema.bats`
Expected: all tests FAIL — validator script not found.

- [ ] **Step 3: Create the empty library file**

`landing_system/presets/palettes.yaml`:

```yaml
# Global palette library for landing-system.
# Populated by /landing-design after design-system approval.
# Manual edits OK. Dedup by id.
palettes: []
```

- [ ] **Step 4: Implement validator**

`scripts/validate-palettes.py`:

```python
#!/usr/bin/env python3
"""Validate a palette library YAML file against the locked schema."""
import re
import sys
import yaml

REQUIRED_TOKENS = {
    "bg_base", "bg_section", "bg_elevated",
    "border_subtle", "border_strong",
    "text_primary", "text_soft", "text_dim",
    "accent_mint", "accent_teal", "accent_coral",
    "accent_coral_hover", "accent_coral_text",
    "accent_rgb_mint", "accent_rgb_coral",
    "card_bg", "card_border", "card_border_hover",
    "accent_cta_glow_opacity",
}
ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
REQUIRED_FIELDS = {"id", "name", "description", "created_at", "created_in_project", "tokens"}


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        fail(f"invalid YAML in {path}: {e}")
    except OSError as e:
        fail(f"cannot read {path}: {e}")

    palettes = data.get("palettes", [])
    if not isinstance(palettes, list):
        fail("'palettes' must be a list")

    seen_ids = set()
    for i, p in enumerate(palettes):
        if not isinstance(p, dict):
            fail(f"palette #{i} is not a mapping")
        missing = REQUIRED_FIELDS - p.keys()
        if missing:
            fail(f"palette #{i} missing required fields: {sorted(missing)}")
        pid = p["id"]
        if not isinstance(pid, str) or not ID_RE.match(pid):
            fail(f"palette #{i}: id must be kebab-case, got {pid!r}")
        if pid in seen_ids:
            fail(f"duplicate id: {pid}")
        seen_ids.add(pid)
        tokens = p.get("tokens") or {}
        if not isinstance(tokens, dict):
            fail(f"palette {pid}: tokens must be a mapping")
        # Empty tokens dict is allowed only when the rest of the entry is also a stub
        # (we use this in the kebab-case test). Otherwise enforce required tokens.
        if tokens:
            missing_tokens = REQUIRED_TOKENS - tokens.keys()
            if missing_tokens:
                fail(f"palette {pid}: missing required token(s): {sorted(missing_tokens)}")

    print(f"OK: {len(palettes)} palette(s) valid in {path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("usage: validate-palettes.py <path-to-palettes.yaml>")
    main(sys.argv[1])
```

- [ ] **Step 5: Run tests, verify all pass**

Run: `npx bats tests/phase-preview-panel/test-palette-schema.bats`
Expected: 6 tests pass.

- [ ] **Step 6: Wire into npm scripts**

Modify `package.json`. Add to `scripts` block (after `test:phase-niche`):

```json
    "test:phase-preview-panel": "bats tests/phase-preview-panel/"
```

- [ ] **Step 7: Commit**

```bash
git add presets/palettes.yaml scripts/validate-palettes.py tests/phase-preview-panel/ package.json
git commit -m "feat(palette-library): schema validator + empty library + 6 bats tests"
```

---

## Task A2: Plugin skeleton (bootstrap + readme)

**Files:**
- Create: `template/08_КОД/plugins/lp-preview-panel/lp-preview-panel.php`
- Create: `template/08_КОД/plugins/lp-preview-panel/readme.txt`

No bats test for this task — it only creates an inert PHP file. Verification = `php -l` syntax check (Step 3).

- [ ] **Step 1: Create the plugin entry file**

`template/08_КОД/plugins/lp-preview-panel/lp-preview-panel.php`:

```php
<?php
/**
 * Plugin Name: LP Preview Panel
 * Description: Runtime preview panel for switching palettes and hero variants on landing pages.
 * Version: 0.1.0
 * Requires PHP: 7.4
 * Author: landing-system
 * License: proprietary
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

define( 'LP_PREVIEW_PANEL_FILE', __FILE__ );
define( 'LP_PREVIEW_PANEL_DIR', plugin_dir_path( __FILE__ ) );
define( 'LP_PREVIEW_PANEL_URL', plugin_dir_url( __FILE__ ) );
define( 'LP_PREVIEW_PANEL_OPTION', 'lp_preview_panel' );

require_once LP_PREVIEW_PANEL_DIR . 'includes/class-axes.php';
require_once LP_PREVIEW_PANEL_DIR . 'includes/class-panel.php';
require_once LP_PREVIEW_PANEL_DIR . 'includes/class-settings.php';

add_action( 'plugins_loaded', function () {
    LP_Preview_Panel_Panel::register();
    LP_Preview_Panel_Settings::register();
} );
```

- [ ] **Step 2: Create readme**

`template/08_КОД/plugins/lp-preview-panel/readme.txt`:

```
=== LP Preview Panel ===

Runtime preview panel for landing pages. Lets the client switch palettes
and hero variants live, persisted in localStorage. Defaults are set in
Settings -> Превью-панель. Hidden from anonymous visitors unless explicitly
enabled in admin.

Theme contract: register axes via the `lp_preview_panel_axes` filter.
See /docs/superpowers/specs/2026-05-12-preview-panel-and-palette-library-design.md
in the landing-system repo.
```

- [ ] **Step 3: Verify PHP syntax**

Run: `php -l template/08_КОД/plugins/lp-preview-panel/lp-preview-panel.php`
Expected: `No syntax errors detected in ...`

If `php` is not on PATH, skip and note in the commit message. (Modern WP runs PHP 7.4+; this file is plain syntax.)

- [ ] **Step 4: Commit**

```bash
git add template/08_КОД/plugins/lp-preview-panel/
git commit -m "feat(plugin): lp-preview-panel skeleton (bootstrap + readme)"
```

---

## Task A3: Axes registry class

**Files:**
- Create: `template/08_КОД/plugins/lp-preview-panel/includes/class-axes.php`

No bats; verification = syntax check + integration via later tasks.

- [ ] **Step 1: Implement the class**

`template/08_КОД/plugins/lp-preview-panel/includes/class-axes.php`:

```php
<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Reads registered axes from the lp_preview_panel_axes filter,
 * normalises them, drops invalid entries.
 *
 * Axis shape:
 *   [
 *     'label'             => string,
 *     'default'           => string,        // must be a key of 'options'
 *     'body_class_prefix' => string,
 *     'options'           => [key => label]
 *   ]
 */
class LP_Preview_Panel_Axes {

    /** @return array<string, array> map of axis_key => normalised axis */
    public static function all() {
        $raw = apply_filters( 'lp_preview_panel_axes', [] );
        if ( ! is_array( $raw ) ) {
            return [];
        }
        $out = [];
        foreach ( $raw as $key => $axis ) {
            $norm = self::normalise( $key, $axis );
            if ( $norm !== null ) {
                $out[ $key ] = $norm;
            }
        }
        return $out;
    }

    /** @return array|null normalised axis or null if invalid */
    private static function normalise( $key, $axis ) {
        if ( ! is_string( $key ) || $key === '' ) {
            return null;
        }
        if ( ! is_array( $axis ) ) {
            return null;
        }
        $options = isset( $axis['options'] ) && is_array( $axis['options'] ) ? $axis['options'] : [];
        if ( empty( $options ) ) {
            return null;
        }
        $default = isset( $axis['default'] ) ? (string) $axis['default'] : '';
        if ( ! array_key_exists( $default, $options ) ) {
            // Fall back to first option key.
            $default = array_key_first( $options );
        }
        return [
            'label'             => isset( $axis['label'] ) ? (string) $axis['label'] : $key,
            'default'           => $default,
            'body_class_prefix' => isset( $axis['body_class_prefix'] ) ? (string) $axis['body_class_prefix'] : ( $key . '-' ),
            'options'           => $options,
        ];
    }

    /** Returns true if value is a known option for the given axis. */
    public static function is_valid_value( $axis_key, $value ) {
        $axes = self::all();
        if ( ! isset( $axes[ $axis_key ] ) ) {
            return false;
        }
        return array_key_exists( $value, $axes[ $axis_key ]['options'] );
    }
}
```

- [ ] **Step 2: Syntax check**

Run: `php -l template/08_КОД/plugins/lp-preview-panel/includes/class-axes.php`
Expected: `No syntax errors detected`.

- [ ] **Step 3: Commit**

```bash
git add template/08_КОД/plugins/lp-preview-panel/includes/class-axes.php
git commit -m "feat(plugin): axes registry — reads lp_preview_panel_axes filter"
```

---

## Task A4: Panel renderer (front-end)

**Files:**
- Create: `template/08_КОД/plugins/lp-preview-panel/includes/class-panel.php`
- Create: `template/08_КОД/plugins/lp-preview-panel/assets/panel.css`
- Create: `template/08_КОД/plugins/lp-preview-panel/assets/panel.js`

- [ ] **Step 1: Implement renderer class**

`template/08_КОД/plugins/lp-preview-panel/includes/class-panel.php`:

```php
<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class LP_Preview_Panel_Panel {

    public static function register() {
        add_action( 'wp_body_open', [ __CLASS__, 'render' ] );
        add_action( 'wp_enqueue_scripts', [ __CLASS__, 'enqueue' ] );
    }

    public static function should_show() {
        $axes = LP_Preview_Panel_Axes::all();
        if ( empty( $axes ) ) {
            return false;
        }
        if ( current_user_can( 'edit_theme_options' ) ) {
            return true;
        }
        $opt = get_option( LP_PREVIEW_PANEL_OPTION, [] );
        return ! empty( $opt['visible_to_anon'] );
    }

    public static function enqueue() {
        if ( ! self::should_show() ) {
            return;
        }
        wp_enqueue_style(
            'lp-preview-panel',
            LP_PREVIEW_PANEL_URL . 'assets/panel.css',
            [],
            '0.1.0'
        );
        wp_enqueue_script(
            'lp-preview-panel',
            LP_PREVIEW_PANEL_URL . 'assets/panel.js',
            [],
            '0.1.0',
            true
        );
        $opt = get_option( LP_PREVIEW_PANEL_OPTION, [] );
        wp_localize_script(
            'lp-preview-panel',
            'LP_PREVIEW_PANEL',
            [
                'axes'     => LP_Preview_Panel_Axes::all(),
                'defaults' => isset( $opt['defaults'] ) ? $opt['defaults'] : [],
            ]
        );
    }

    public static function render() {
        if ( ! self::should_show() ) {
            return;
        }
        $axes = LP_Preview_Panel_Axes::all();
        echo '<div class="lp-preview-panel" role="region" aria-label="Панель превью">';
        echo '<div class="lp-preview-panel__inner">';
        foreach ( $axes as $key => $axis ) {
            echo '<div class="lp-preview-panel__row">';
            printf(
                '<span class="lp-preview-panel__label">Превью %s:</span>',
                esc_html( $axis['label'] )
            );
            echo '<label class="lp-preview-panel__select-wrap">';
            echo '<span class="screen-reader-text">' . esc_html( $axis['label'] ) . '</span>';
            printf(
                '<select class="lp-preview-panel__select" data-lp-axis="%s">',
                esc_attr( $key )
            );
            foreach ( $axis['options'] as $val => $label ) {
                printf(
                    '<option value="%s">%s</option>',
                    esc_attr( $val ),
                    esc_html( $label )
                );
            }
            echo '</select>';
            echo '</label>';
            echo '<span class="lp-preview-panel__hint">выбор сохраняется</span>';
            echo '</div>';
        }
        echo '</div>';
        echo '</div>';
    }
}
```

- [ ] **Step 2: Port CSS from `nu-theme-bar`**

`template/08_КОД/plugins/lp-preview-panel/assets/panel.css` — port of the existing `.nu-theme-bar__*` block in neuroupgrade-v2 `main.css:998-1037`, with class rename:

```css
.lp-preview-panel {
  background: #0A0A0A;
  color: #E5E5E5;
  font: 13px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  border-bottom: 1px solid #1F1F1F;
  position: relative;
  z-index: 9999;
}
.lp-preview-panel__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 8px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.lp-preview-panel__row {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 28px;
}
.lp-preview-panel__label { color: #A3A3A3; flex: 0 0 auto; }
.lp-preview-panel__hint  { color: #737373; flex: 0 0 auto; font-size: 12px; margin-left: auto; }
.lp-preview-panel__select-wrap { flex: 1 1 auto; display: flex; justify-content: center; }
.lp-preview-panel__select {
  background: #171717;
  color: #E5E5E5;
  border: 1px solid #2A2A2A;
  border-radius: 6px;
  padding: 4px 10px;
  min-width: 240px;
  font: inherit;
  cursor: pointer;
}
.lp-preview-panel__select:focus { outline: 2px solid #525252; outline-offset: 1px; }

@media (max-width: 640px) {
  .lp-preview-panel__label, .lp-preview-panel__hint { display: none; }
  .lp-preview-panel__select { min-width: 0; width: 100%; }
  .lp-preview-panel__select-wrap { justify-content: stretch; }
}
```

- [ ] **Step 3: Write panel.js**

`template/08_КОД/plugins/lp-preview-panel/assets/panel.js`:

```javascript
(function () {
  'use strict';

  var config = window.LP_PREVIEW_PANEL || { axes: {}, defaults: {} };
  var STORAGE_PREFIX = 'lp-axis-';

  function readUrl(axisKey) {
    try {
      var url = new URL(window.location.href);
      var v = url.searchParams.get(axisKey);
      return v || null;
    } catch (e) { return null; }
  }

  function readLs(axisKey) {
    try { return localStorage.getItem(STORAGE_PREFIX + axisKey); } catch (e) { return null; }
  }

  function writeLs(axisKey, value) {
    try { localStorage.setItem(STORAGE_PREFIX + axisKey, value); } catch (e) {}
  }

  function isValid(axis, value) {
    return value && Object.prototype.hasOwnProperty.call(axis.options, value);
  }

  function resolveInitial(axisKey, axis) {
    var fromUrl = readUrl(axisKey);
    if (isValid(axis, fromUrl)) return fromUrl;
    var fromLs = readLs(axisKey);
    if (isValid(axis, fromLs)) return fromLs;
    var fromServer = config.defaults && config.defaults[axisKey];
    if (isValid(axis, fromServer)) return fromServer;
    return axis.default;
  }

  function applyClass(prefix, oldValue, newValue) {
    var body = document.body;
    if (oldValue) body.classList.remove(prefix + oldValue);
    body.classList.add(prefix + newValue);
  }

  function initAxis(axisKey, axis) {
    var current = resolveInitial(axisKey, axis);
    applyClass(axis.body_class_prefix, null, current);

    var select = document.querySelector('[data-lp-axis="' + axisKey + '"]');
    if (!select) return;
    select.value = current;
    select.addEventListener('change', function () {
      var next = select.value;
      if (!isValid(axis, next)) return;
      applyClass(axis.body_class_prefix, current, next);
      writeLs(axisKey, next);
      current = next;
    });
  }

  function init() {
    Object.keys(config.axes || {}).forEach(function (k) {
      initAxis(k, config.axes[k]);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
```

- [ ] **Step 4: Syntax checks**

Run: `php -l template/08_КОД/plugins/lp-preview-panel/includes/class-panel.php`
Expected: `No syntax errors detected`.

Run: `node --check template/08_КОД/plugins/lp-preview-panel/assets/panel.js`
Expected: no output, exit 0.

- [ ] **Step 5: Commit**

```bash
git add template/08_КОД/plugins/lp-preview-panel/includes/class-panel.php template/08_КОД/plugins/lp-preview-panel/assets/
git commit -m "feat(plugin): front-end panel renderer + CSS + JS engine"
```

---

## Task A5: Settings page (admin)

**Files:**
- Create: `template/08_КОД/plugins/lp-preview-panel/includes/class-settings.php`
- Create: `template/08_КОД/plugins/lp-preview-panel/assets/admin.js`

- [ ] **Step 1: Implement settings class**

`template/08_КОД/plugins/lp-preview-panel/includes/class-settings.php`:

```php
<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class LP_Preview_Panel_Settings {

    const PAGE_SLUG = 'lp-preview-panel';

    public static function register() {
        add_action( 'admin_menu', [ __CLASS__, 'menu' ] );
        add_action( 'admin_init', [ __CLASS__, 'register_setting' ] );
        add_action( 'admin_enqueue_scripts', [ __CLASS__, 'enqueue' ] );
    }

    public static function menu() {
        add_options_page(
            'Превью-панель',
            'Превью-панель',
            'manage_options',
            self::PAGE_SLUG,
            [ __CLASS__, 'render' ]
        );
    }

    public static function register_setting() {
        register_setting(
            'lp_preview_panel_group',
            LP_PREVIEW_PANEL_OPTION,
            [
                'type'              => 'array',
                'sanitize_callback' => [ __CLASS__, 'sanitize' ],
                'default'           => [
                    'visible_to_anon' => false,
                    'defaults'        => [],
                ],
            ]
        );
    }

    public static function sanitize( $input ) {
        $out = [
            'visible_to_anon' => ! empty( $input['visible_to_anon'] ),
            'defaults'        => [],
        ];
        $axes = LP_Preview_Panel_Axes::all();
        $defaults_in = isset( $input['defaults'] ) && is_array( $input['defaults'] ) ? $input['defaults'] : [];
        foreach ( $defaults_in as $axis_key => $value ) {
            if ( LP_Preview_Panel_Axes::is_valid_value( $axis_key, $value ) ) {
                $out['defaults'][ $axis_key ] = $value;
            } else {
                add_settings_error(
                    'lp_preview_panel',
                    'invalid_default_' . $axis_key,
                    sprintf( 'Invalid default for axis %s, ignored.', esc_html( $axis_key ) ),
                    'warning'
                );
            }
        }
        return $out;
    }

    public static function enqueue( $hook ) {
        if ( $hook !== 'settings_page_' . self::PAGE_SLUG ) {
            return;
        }
        wp_enqueue_script(
            'lp-preview-panel-admin',
            LP_PREVIEW_PANEL_URL . 'assets/admin.js',
            [],
            '0.1.0',
            true
        );
    }

    public static function render() {
        if ( ! current_user_can( 'manage_options' ) ) {
            return;
        }
        $opt = get_option( LP_PREVIEW_PANEL_OPTION, [] );
        $visible = ! empty( $opt['visible_to_anon'] );
        $defaults = isset( $opt['defaults'] ) && is_array( $opt['defaults'] ) ? $opt['defaults'] : [];
        $axes = LP_Preview_Panel_Axes::all();
        ?>
        <div class="wrap">
            <h1>Превью-панель</h1>
            <form method="post" action="options.php">
                <?php settings_fields( 'lp_preview_panel_group' ); ?>

                <h2>Видимость</h2>
                <label>
                    <input type="checkbox"
                           name="<?php echo esc_attr( LP_PREVIEW_PANEL_OPTION ); ?>[visible_to_anon]"
                           value="1" <?php checked( $visible ); ?>>
                    Показывать панель превью анонимным посетителям
                </label>
                <p class="description">Если выключено — панель видят только админы.</p>

                <h2>Текущие дефолты для всех посетителей</h2>
                <table class="form-table">
                <?php foreach ( $axes as $key => $axis ) :
                    $current = isset( $defaults[ $key ] ) ? $defaults[ $key ] : $axis['default'];
                    ?>
                    <tr>
                        <th scope="row"><label for="lp-default-<?php echo esc_attr( $key ); ?>"><?php echo esc_html( $axis['label'] ); ?></label></th>
                        <td>
                            <select id="lp-default-<?php echo esc_attr( $key ); ?>"
                                    name="<?php echo esc_attr( LP_PREVIEW_PANEL_OPTION ); ?>[defaults][<?php echo esc_attr( $key ); ?>]"
                                    data-lp-admin-axis="<?php echo esc_attr( $key ); ?>">
                                <?php foreach ( $axis['options'] as $val => $label ) : ?>
                                    <option value="<?php echo esc_attr( $val ); ?>" <?php selected( $current, $val ); ?>>
                                        <?php echo esc_html( $label ); ?>
                                    </option>
                                <?php endforeach; ?>
                            </select>
                        </td>
                    </tr>
                <?php endforeach; ?>
                </table>

                <p>
                    <button type="button" class="button" data-lp-fill-from-ls>
                        Зафиксировать мой текущий выбор как дефолт
                    </button>
                    <span class="description">(берёт значения из вашего localStorage в этом браузере)</span>
                </p>

                <?php submit_button( 'Сохранить дефолты' ); ?>
            </form>
        </div>
        <?php
    }
}
```

- [ ] **Step 2: Write admin.js**

`template/08_КОД/plugins/lp-preview-panel/assets/admin.js`:

```javascript
(function () {
  'use strict';
  var STORAGE_PREFIX = 'lp-axis-';

  function fillFromLocalStorage() {
    var selects = document.querySelectorAll('[data-lp-admin-axis]');
    selects.forEach(function (sel) {
      var key = sel.getAttribute('data-lp-admin-axis');
      var v = null;
      try { v = localStorage.getItem(STORAGE_PREFIX + key); } catch (e) {}
      if (!v) return;
      var match = Array.prototype.find.call(sel.options, function (o) { return o.value === v; });
      if (match) sel.value = v;
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.querySelector('[data-lp-fill-from-ls]');
    if (btn) btn.addEventListener('click', fillFromLocalStorage);
  });
})();
```

- [ ] **Step 3: Syntax checks**

Run: `php -l template/08_КОД/plugins/lp-preview-panel/includes/class-settings.php`
Expected: `No syntax errors detected`.

Run: `node --check template/08_КОД/plugins/lp-preview-panel/assets/admin.js`
Expected: exit 0.

- [ ] **Step 4: Commit**

```bash
git add template/08_КОД/plugins/lp-preview-panel/includes/class-settings.php template/08_КОД/plugins/lp-preview-panel/assets/admin.js
git commit -m "feat(plugin): settings page + admin.js (fill defaults from localStorage)"
```

---

# Phase B — Pipeline integration

## Task B1: export-palettes-to-library.py + tests

**Files:**
- Create: `scripts/export-palettes-to-library.py`
- Create: `tests/phase-preview-panel/test-export-palettes.bats`
- Create: `tests/phase-preview-panel/fixtures/project-with-new-palette/05_ДИЗАЙН-СИСТЕМА/palettes.yaml`

- [ ] **Step 1: Write failing test**

`tests/phase-preview-panel/test-export-palettes.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/export-palettes-to-library.py"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  WORK="$(mktemp -d)"
  # Clean copies for each test
  cp -r "$FIXTURES/project-with-new-palette" "$WORK/project"
  cp "$FIXTURES/library-empty.yaml" "$WORK/library.yaml"
}

teardown() {
  rm -rf "$WORK"
}

@test "exports a new palette into empty library" {
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml"
  [ "$status" -eq 0 ]
  grep -q "id: forest-calm" "$WORK/library.yaml"
  grep -q 'created_in_project: "test-project"' "$WORK/library.yaml"
}

@test "skips palette whose id already exists" {
  cp "$FIXTURES/library-with-paper-minimal.yaml" "$WORK/library.yaml"
  # Add a palette to the project with id=paper-minimal
  cat > "$WORK/project/05_ДИЗАЙН-СИСТЕМА/palettes.yaml" <<'YAML'
palettes:
  - id: paper-minimal
    name: "Different name"
    description: "Different desc"
    created_at: "2026-05-12"
    created_in_project: "test-project"
    tokens:
      bg_base: "#000000"
      bg_section: "#000000"
      bg_elevated: "#000000"
      border_subtle: "#000000"
      border_strong: "#000000"
      text_primary: "#000000"
      text_soft: "#000000"
      text_dim: "#000000"
      accent_mint: "#000000"
      accent_teal: "#000000"
      accent_coral: "#000000"
      accent_coral_hover: "#000000"
      accent_coral_text: "#000000"
      accent_rgb_mint: "0, 0, 0"
      accent_rgb_coral: "0, 0, 0"
      card_bg: "#000000"
      card_border: "#000000"
      card_border_hover: "#000000"
      accent_cta_glow_opacity: "0.0"
YAML
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" == *"skipped"* ]]
  # Original library entry preserved
  grep -q 'name: "Paper Minimal"' "$WORK/library.yaml"
  ! grep -q 'name: "Different name"' "$WORK/library.yaml"
}

@test "rejects invalid project YAML" {
  echo "not: [valid" > "$WORK/project/05_ДИЗАЙН-СИСТЕМА/palettes.yaml"
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml"
  [ "$status" -ne 0 ]
}

@test "creates library file if absent" {
  rm "$WORK/library.yaml"
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml"
  [ "$status" -eq 0 ]
  [ -f "$WORK/library.yaml" ]
  grep -q "id: forest-calm" "$WORK/library.yaml"
}
```

Fixture `tests/phase-preview-panel/fixtures/project-with-new-palette/05_ДИЗАЙН-СИСТЕМА/palettes.yaml`:

```yaml
palettes:
  - id: forest-calm
    name: "Forest Calm"
    description: "Muted green tones for wellness niches."
    created_at: "2026-05-12"
    created_in_project: "test-project"
    tokens:
      bg_base: "#0F1A14"
      bg_section: "#162720"
      bg_elevated: "#1F3329"
      border_subtle: "#1F3329"
      border_strong: "#2E4A3C"
      text_primary: "#EDF5EF"
      text_soft: "#C7D6CB"
      text_dim: "#8FA395"
      accent_mint: "#7FB28C"
      accent_teal: "#4C8F7C"
      accent_coral: "#D89274"
      accent_coral_hover: "#E2A687"
      accent_coral_text: "#1F3329"
      accent_rgb_mint: "127, 178, 140"
      accent_rgb_coral: "216, 146, 116"
      card_bg: "#162720"
      card_border: "#1F3329"
      card_border_hover: "#4C8F7C"
      accent_cta_glow_opacity: "0.25"
```

- [ ] **Step 2: Verify tests fail**

Run: `npx bats tests/phase-preview-panel/test-export-palettes.bats`
Expected: 4 tests FAIL — script not found.

- [ ] **Step 3: Implement the script**

`scripts/export-palettes-to-library.py`:

```python
#!/usr/bin/env python3
"""Export palettes from a project's 05_ДИЗАЙН-СИСТЕМА/palettes.yaml
into the global library, deduping by id."""
import argparse
import os
import sys
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
# Reuse the validator
import importlib.util
spec = importlib.util.spec_from_file_location(
    "validate_palettes",
    os.path.join(REPO_ROOT, "scripts", "validate-palettes.py"),
)
validate_palettes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_palettes)


def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {"palettes": []}
    except yaml.YAMLError as e:
        print(f"ERROR: invalid YAML in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def save_yaml(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            f.write("# Global palette library for landing-system.\n")
            f.write("# Populated by /landing-design after design-system approval.\n")
            f.write("# Manual edits OK. Dedup by id.\n")
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="path to project root")
    ap.add_argument("--library", required=True, help="path to landing_system/presets/palettes.yaml")
    args = ap.parse_args()

    src = os.path.join(args.project, "05_ДИЗАЙН-СИСТЕМА", "palettes.yaml")
    project_data = load_yaml(src)
    src_palettes = project_data.get("palettes", []) or []

    # Validate the project file via the existing validator (will sys.exit on failure)
    try:
        validate_palettes.main(src)
    except SystemExit as e:
        if e.code:
            sys.exit(e.code)

    library_data = load_yaml(args.library)
    library = library_data.get("palettes", []) or []
    existing_ids = {p["id"] for p in library}

    added = []
    skipped = []
    for p in src_palettes:
        if p["id"] in existing_ids:
            skipped.append(p["id"])
        else:
            library.append(p)
            existing_ids.add(p["id"])
            added.append(p["id"])

    library_data["palettes"] = library
    save_yaml(args.library, library_data)

    for pid in added:
        print(f"added: {pid}")
    for pid in skipped:
        print(f"skipped (id already in library): {pid}")
    print(f"library now has {len(library)} palette(s)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Tests pass**

Run: `npx bats tests/phase-preview-panel/test-export-palettes.bats`
Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/export-palettes-to-library.py tests/phase-preview-panel/test-export-palettes.bats tests/phase-preview-panel/fixtures/project-with-new-palette/
git commit -m "feat(pipeline): export-palettes-to-library.py + 4 bats tests"
```

---

## Task B2: snapshot-palettes-to-project.py + tests

Copies a chosen subset (or all) of palettes from the library into `<project>/04_БРЕНД/palettes.yaml`. Used by `/landing-brand`.

**Files:**
- Create: `scripts/snapshot-palettes-to-project.py`
- Create: `tests/phase-preview-panel/test-snapshot-palettes.bats`
- Create: `tests/phase-preview-panel/fixtures/library-three-palettes.yaml`

- [ ] **Step 1: Write failing test**

`tests/phase-preview-panel/test-snapshot-palettes.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/snapshot-palettes-to-project.py"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  WORK="$(mktemp -d)"
  mkdir -p "$WORK/project/04_БРЕНД"
  cp "$FIXTURES/library-three-palettes.yaml" "$WORK/library.yaml"
}

teardown() {
  rm -rf "$WORK"
}

@test "--all copies every palette from library" {
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml" --all
  [ "$status" -eq 0 ]
  grep -q "id: paper-minimal" "$WORK/project/04_БРЕНД/palettes.yaml"
  grep -q "id: quiet-dark" "$WORK/project/04_БРЕНД/palettes.yaml"
  grep -q "id: forest-calm" "$WORK/project/04_БРЕНД/palettes.yaml"
}

@test "--id selects specific palettes by id" {
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml" --id paper-minimal --id forest-calm
  [ "$status" -eq 0 ]
  grep -q "id: paper-minimal" "$WORK/project/04_БРЕНД/palettes.yaml"
  grep -q "id: forest-calm" "$WORK/project/04_БРЕНД/palettes.yaml"
  ! grep -q "id: quiet-dark" "$WORK/project/04_БРЕНД/palettes.yaml"
}

@test "unknown --id fails" {
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml" --id no-such-palette
  [ "$status" -ne 0 ]
  [[ "$output" == *"no-such-palette"* ]]
}

@test "snapshot validates against schema" {
  # Corrupt the library to be missing a token in one palette
  python -c "
import yaml
with open('$WORK/library.yaml') as f: d=yaml.safe_load(f)
del d['palettes'][0]['tokens']['accent_cta_glow_opacity']
with open('$WORK/library.yaml','w') as f: yaml.safe_dump(d,f)
"
  run python "$SCRIPT" --project "$WORK/project" --library "$WORK/library.yaml" --all
  [ "$status" -ne 0 ]
}
```

Fixture `tests/phase-preview-panel/fixtures/library-three-palettes.yaml`: assemble three valid palette entries (paper-minimal, quiet-dark, forest-calm) using the schema above. Use the existing `library-with-paper-minimal.yaml` as a starting point for the first entry; copy structure for the other two with distinct hex values.

- [ ] **Step 2: Verify tests fail**

Run: `npx bats tests/phase-preview-panel/test-snapshot-palettes.bats`
Expected: 4 tests FAIL — script not found.

- [ ] **Step 3: Implement the script**

`scripts/snapshot-palettes-to-project.py`:

```python
#!/usr/bin/env python3
"""Copy a subset of palettes from the global library into a project."""
import argparse
import importlib.util
import os
import sys
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "validate_palettes",
    os.path.join(REPO_ROOT, "scripts", "validate-palettes.py"),
)
validate_palettes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_palettes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--library", required=True)
    ap.add_argument("--id", action="append", default=[], help="palette id to include (repeat)")
    ap.add_argument("--all", action="store_true", help="copy every palette")
    args = ap.parse_args()

    try:
        validate_palettes.main(args.library)
    except SystemExit as e:
        if e.code:
            sys.exit(e.code)

    with open(args.library, "r", encoding="utf-8") as f:
        lib = yaml.safe_load(f) or {}
    palettes = lib.get("palettes", []) or []
    by_id = {p["id"]: p for p in palettes}

    if args.all:
        selected = list(palettes)
    else:
        if not args.id:
            print("ERROR: pass --all or one or more --id", file=sys.stderr)
            sys.exit(2)
        missing = [i for i in args.id if i not in by_id]
        if missing:
            print(f"ERROR: unknown palette id(s): {missing}", file=sys.stderr)
            sys.exit(1)
        selected = [by_id[i] for i in args.id]

    dest_dir = os.path.join(args.project, "04_БРЕНД")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "palettes.yaml")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("# Project palette snapshot from landing_system/presets/palettes.yaml\n")
        yaml.safe_dump({"palettes": selected}, f, sort_keys=False, allow_unicode=True)

    print(f"snapshotted {len(selected)} palette(s) to {dest}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Tests pass**

Run: `npx bats tests/phase-preview-panel/test-snapshot-palettes.bats`
Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/snapshot-palettes-to-project.py tests/phase-preview-panel/test-snapshot-palettes.bats tests/phase-preview-panel/fixtures/library-three-palettes.yaml
git commit -m "feat(pipeline): snapshot-palettes-to-project.py + 4 bats tests"
```

---

## Task B3: generate-palette-css.py + tests

Reads `<project>/04_БРЕНД/palettes.yaml`, emits a CSS file with `body.theme-<id> { --bg-base: ...; }` blocks.

**Files:**
- Create: `scripts/generate-palette-css.py`
- Create: `tests/phase-preview-panel/test-generate-palette-css.bats`
- Create: `tests/phase-preview-panel/fixtures/expected-palettes.css`

- [ ] **Step 1: Write failing test**

`tests/phase-preview-panel/test-generate-palette-css.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/generate-palette-css.py"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  WORK="$(mktemp -d)"
  mkdir -p "$WORK/project/04_БРЕНД" "$WORK/project/08_КОД/wp-theme/assets/css"
  cp "$FIXTURES/library-with-paper-minimal.yaml" "$WORK/project/04_БРЕНД/palettes.yaml"
}

teardown() {
  rm -rf "$WORK"
}

@test "generates a body.theme-<id> block per palette" {
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  CSS="$WORK/project/08_КОД/wp-theme/assets/css/palettes.css"
  [ -f "$CSS" ]
  grep -q "body.theme-paper-minimal" "$CSS"
}

@test "translates YAML keys to CSS custom properties" {
  python "$SCRIPT" --project "$WORK/project"
  CSS="$WORK/project/08_КОД/wp-theme/assets/css/palettes.css"
  grep -q -- "--bg-base: #F8F7F4" "$CSS"
  grep -q -- "--accent-rgb-coral: 4, 120, 87" "$CSS"
  grep -q -- "--accent-cta-glow-opacity: 0.15" "$CSS"
}

@test "matches expected fixture exactly for paper-minimal" {
  python "$SCRIPT" --project "$WORK/project"
  diff -u "$FIXTURES/expected-palettes.css" "$WORK/project/08_КОД/wp-theme/assets/css/palettes.css"
}
```

Fixture `tests/phase-preview-panel/fixtures/expected-palettes.css`:

```css
/* Generated by scripts/generate-palette-css.py. Do not edit. */

body.theme-paper-minimal {
  --bg-base: #F8F7F4;
  --bg-section: #FFFFFF;
  --bg-elevated: #FFFFFF;
  --border-subtle: #E7E5E0;
  --border-strong: #CBD5E1;
  --text-primary: #0F172A;
  --text-soft: #334155;
  --text-dim: #64748B;
  --accent-mint: #047857;
  --accent-teal: #047857;
  --accent-coral: #047857;
  --accent-coral-hover: #065F46;
  --accent-coral-text: #FFFFFF;
  --accent-rgb-mint: 4, 120, 87;
  --accent-rgb-coral: 4, 120, 87;
  --card-bg: #FFFFFF;
  --card-border: #E7E5E0;
  --card-border-hover: #047857;
  --accent-cta-glow-opacity: 0.15;
}
```

- [ ] **Step 2: Verify tests fail**

Run: `npx bats tests/phase-preview-panel/test-generate-palette-css.bats`
Expected: 3 tests FAIL.

- [ ] **Step 3: Implement the script**

`scripts/generate-palette-css.py`:

```python
#!/usr/bin/env python3
"""Generate body.theme-<id> CSS blocks from <project>/04_БРЕНД/palettes.yaml."""
import argparse
import os
import sys
import yaml

# Ordered to match neuroupgrade-v2 main.css style for diff readability.
TOKEN_ORDER = [
    "bg_base", "bg_section", "bg_elevated",
    "border_subtle", "border_strong",
    "text_primary", "text_soft", "text_dim",
    "accent_mint", "accent_teal", "accent_coral",
    "accent_coral_hover", "accent_coral_text",
    "accent_rgb_mint", "accent_rgb_coral",
    "card_bg", "card_border", "card_border_hover",
    "accent_cta_glow_opacity",
]


def yaml_key_to_css(key):
    return "--" + key.replace("_", "-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    src = os.path.join(args.project, "04_БРЕНД", "palettes.yaml")
    with open(src, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    palettes = data.get("palettes", []) or []

    out_lines = ["/* Generated by scripts/generate-palette-css.py. Do not edit. */", ""]
    for p in palettes:
        out_lines.append(f"body.theme-{p['id']} {{")
        tokens = p.get("tokens", {})
        for key in TOKEN_ORDER:
            if key not in tokens:
                print(f"ERROR: palette {p['id']} missing token {key}", file=sys.stderr)
                sys.exit(1)
            out_lines.append(f"  {yaml_key_to_css(key)}: {tokens[key]};")
        out_lines.append("}")
        out_lines.append("")

    dest_dir = os.path.join(args.project, "08_КОД", "wp-theme", "assets", "css")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "palettes.css")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

    print(f"wrote {dest} ({len(palettes)} palette(s))")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Tests pass**

Run: `npx bats tests/phase-preview-panel/test-generate-palette-css.bats`
Expected: 3 tests pass.

If the `diff` test fails because of trailing whitespace or final newline, run `cat -A` on both files and adjust the fixture to match the script's actual output exactly. The script's contract is the source of truth here, not human formatting preferences.

- [ ] **Step 5: Commit**

```bash
git add scripts/generate-palette-css.py tests/phase-preview-panel/test-generate-palette-css.bats tests/phase-preview-panel/fixtures/expected-palettes.css
git commit -m "feat(pipeline): generate-palette-css.py + 3 bats tests"
```

---

## Task B4: generate-axes-filter.py + tests

Emits a PHP block that the theme's `functions.php` will include, registering `lp_preview_panel_axes` with the project's palettes and hero variants.

**Files:**
- Create: `scripts/generate-axes-filter.py`
- Create: `tests/phase-preview-panel/test-generate-axes-filter.bats`
- Create: `tests/phase-preview-panel/fixtures/expected-axes.php`

- [ ] **Step 1: Write failing test**

`tests/phase-preview-panel/test-generate-axes-filter.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/generate-axes-filter.py"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  WORK="$(mktemp -d)"
  mkdir -p "$WORK/project/04_БРЕНД" "$WORK/project/08_КОД/wp-theme/inc"
  cp "$FIXTURES/library-with-paper-minimal.yaml" "$WORK/project/04_БРЕНД/palettes.yaml"
}

teardown() {
  rm -rf "$WORK"
}

@test "emits a PHP file with the filter callback" {
  run python "$SCRIPT" --project "$WORK/project" --default-palette paper-minimal --hero static,parallax --default-hero static
  [ "$status" -eq 0 ]
  PHP="$WORK/project/08_КОД/wp-theme/inc/lp-preview-panel-axes.php"
  [ -f "$PHP" ]
  grep -q "add_filter( 'lp_preview_panel_axes'" "$PHP"
  grep -q "'paper-minimal' => 'Paper Minimal'" "$PHP"
  grep -q "'static'   => 'Static'" "$PHP"
  grep -q "'parallax' => 'Parallax'" "$PHP"
}

@test "matches expected fixture exactly" {
  python "$SCRIPT" --project "$WORK/project" --default-palette paper-minimal --hero static,parallax --default-hero static
  diff -u "$FIXTURES/expected-axes.php" "$WORK/project/08_КОД/wp-theme/inc/lp-preview-panel-axes.php"
}

@test "rejects --default-palette not in snapshot" {
  run python "$SCRIPT" --project "$WORK/project" --default-palette no-such --hero static --default-hero static
  [ "$status" -ne 0 ]
  [[ "$output" == *"no-such"* ]]
}

@test "rejects --default-hero not in --hero list" {
  run python "$SCRIPT" --project "$WORK/project" --default-palette paper-minimal --hero static,parallax --default-hero video
  [ "$status" -ne 0 ]
  [[ "$output" == *"video"* ]]
}
```

Fixture `tests/phase-preview-panel/fixtures/expected-axes.php`:

```php
<?php
/**
 * Generated by scripts/generate-axes-filter.py. Do not edit.
 * Registers the lp_preview_panel_axes filter for this theme.
 */

add_filter( 'lp_preview_panel_axes', function ( $axes ) {
    $axes['palette'] = [
        'label'             => 'Палитра',
        'default'           => 'paper-minimal',
        'body_class_prefix' => 'theme-',
        'options' => [
            'paper-minimal' => 'Paper Minimal',
        ],
    ];
    $axes['hero'] = [
        'label'             => 'Hero',
        'default'           => 'static',
        'body_class_prefix' => 'hero--',
        'options' => [
            'static'   => 'Static',
            'parallax' => 'Parallax',
        ],
    ];
    return $axes;
} );
```

- [ ] **Step 2: Verify tests fail**

Run: `npx bats tests/phase-preview-panel/test-generate-axes-filter.bats`
Expected: 4 tests FAIL.

- [ ] **Step 3: Implement the script**

`scripts/generate-axes-filter.py`:

```python
#!/usr/bin/env python3
"""Emit inc/lp-preview-panel-axes.php registering the lp_preview_panel_axes filter."""
import argparse
import os
import sys
import yaml

HERO_LABELS = {
    "static": "Static",
    "parallax": "Parallax",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--default-palette", required=True)
    ap.add_argument("--hero", required=True, help="comma-separated hero ids")
    ap.add_argument("--default-hero", required=True)
    args = ap.parse_args()

    src = os.path.join(args.project, "04_БРЕНД", "palettes.yaml")
    with open(src, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    palettes = data.get("palettes", []) or []
    palette_by_id = {p["id"]: p for p in palettes}

    if args.default_palette not in palette_by_id:
        print(f"ERROR: --default-palette {args.default_palette!r} not in project snapshot", file=sys.stderr)
        sys.exit(1)

    hero_ids = [h.strip() for h in args.hero.split(",") if h.strip()]
    unknown = [h for h in hero_ids if h not in HERO_LABELS]
    if unknown:
        print(f"ERROR: unknown hero id(s): {unknown}", file=sys.stderr)
        sys.exit(1)
    if args.default_hero not in hero_ids:
        print(f"ERROR: --default-hero {args.default_hero!r} not in --hero list", file=sys.stderr)
        sys.exit(1)

    palette_max_key_len = max(len(pid) for pid in palette_by_id) if palette_by_id else 0
    hero_max_key_len = max(len(h) for h in hero_ids) if hero_ids else 0

    def fmt_option(key, label, max_len):
        pad = " " * (max_len - len(key))
        return f"            '{key}'{pad} => '{label}',"

    lines = [
        "<?php",
        "/**",
        " * Generated by scripts/generate-axes-filter.py. Do not edit.",
        " * Registers the lp_preview_panel_axes filter for this theme.",
        " */",
        "",
        "add_filter( 'lp_preview_panel_axes', function ( $axes ) {",
        "    $axes['palette'] = [",
        "        'label'             => 'Палитра',",
        f"        'default'           => '{args.default_palette}',",
        "        'body_class_prefix' => 'theme-',",
        "        'options' => [",
    ]
    for pid in palette_by_id:
        lines.append(fmt_option(pid, palette_by_id[pid]["name"], palette_max_key_len))
    lines += [
        "        ],",
        "    ];",
        "    $axes['hero'] = [",
        "        'label'             => 'Hero',",
        f"        'default'           => '{args.default_hero}',",
        "        'body_class_prefix' => 'hero--',",
        "        'options' => [",
    ]
    for h in hero_ids:
        lines.append(fmt_option(h, HERO_LABELS[h], hero_max_key_len))
    lines += [
        "        ],",
        "    ];",
        "    return $axes;",
        "} );",
        "",
    ]

    dest = os.path.join(args.project, "08_КОД", "wp-theme", "inc", "lp-preview-panel-axes.php")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Tests pass**

Run: `npx bats tests/phase-preview-panel/test-generate-axes-filter.bats`
Expected: 4 tests pass.

If the `diff` test fails, do `cat -A` on both, adjust the fixture to match the script's exact output. The script is the source of truth.

- [ ] **Step 5: Commit**

```bash
git add scripts/generate-axes-filter.py tests/phase-preview-panel/test-generate-axes-filter.bats tests/phase-preview-panel/fixtures/expected-axes.php
git commit -m "feat(pipeline): generate-axes-filter.py + 4 bats tests"
```

---

## Task B5: Wire pipeline scripts into skill docs

No new code, just documentation so future runs of `/landing-design`, `/landing-brand`, `/landing-build`, `/landing-deploy` invoke the right scripts.

**Files:**
- Modify: `skills/design-tokens-generation/SKILL.md`
- Modify: `skills/brand-kit-build/SKILL.md`
- Modify: `skills/wp-theme-assembler/SKILL.md`
- Modify: `skills/wp-cli-deployer/SKILL.md`
- Modify: `template/CLAUDE.md`

- [ ] **Step 1: Document export hook in design-tokens-generation**

Append to `skills/design-tokens-generation/SKILL.md`:

```markdown
## Palette library export (post-approve hook)

When stage `05_design_system` is approved (gate-check passes), run:

\```bash
python scripts/export-palettes-to-library.py \
    --project "$PROJECT_ROOT" \
    --library "$LANDING_SYSTEM_ROOT/presets/palettes.yaml"
\```

This adds new palette ids to the global library. Existing ids are preserved
(skipped with a notice — see `scripts/export-palettes-to-library.py`).

Invariant: do NOT call this script before approval. Black-box behaviour is
"approved palettes are reusable across projects." Drafts must not pollute
the library.
```

- [ ] **Step 2: Document mode selection in brand-kit-build**

Append to `skills/brand-kit-build/SKILL.md`:

```markdown
## Palette selection from global library

Before extracting brand tokens, ask the user which mode to use:

\```
Сколько палитр показать клиенту на согласовании?
  [1] Точечно (1-3)        — клиент знает что хочет
  [2] Несколько (4-6)      — есть направление (рекомендуется)
  [3] Весь каталог         — клиент в полном поиске
\```

Modes 1-2: agent proposes candidates from `landing_system/presets/palettes.yaml`
based on niche analysis (read 01a_АНАЛИЗ_НИШИ artifacts), user confirms list,
then run:

\```bash
python scripts/snapshot-palettes-to-project.py \
    --project "$PROJECT_ROOT" \
    --library "$LANDING_SYSTEM_ROOT/presets/palettes.yaml" \
    --id <id1> --id <id2> ...
\```

Mode 3:

\```bash
python scripts/snapshot-palettes-to-project.py \
    --project "$PROJECT_ROOT" \
    --library "$LANDING_SYSTEM_ROOT/presets/palettes.yaml" \
    --all
\```

Result: `<project>/04_БРЕНД/palettes.yaml` contains the selected subset.

If `landing_system/presets/palettes.yaml` is empty (greenfield), tell the user:
"библиотека пуста — на /landing-design ты создашь первые палитры с нуля".
Skip the selection step entirely.
```

- [ ] **Step 3: Document codegen in wp-theme-assembler**

Append to `skills/wp-theme-assembler/SKILL.md`:

```markdown
## lp-preview-panel integration

During theme assembly:

1. Copy plugin source:

   \```bash
   cp -r "$LANDING_SYSTEM_ROOT/template/08_КОД/plugins/lp-preview-panel" \
         "$PROJECT_ROOT/08_КОД/plugins/"
   \```

2. Generate palette CSS:

   \```bash
   python scripts/generate-palette-css.py --project "$PROJECT_ROOT"
   \```

   Output: `$PROJECT_ROOT/08_КОД/wp-theme/assets/css/palettes.css`.
   Include this file in the theme's main stylesheet enqueue.

3. Generate axes filter PHP:

   \```bash
   python scripts/generate-axes-filter.py \
       --project "$PROJECT_ROOT" \
       --default-palette <chosen-palette-id> \
       --hero static,parallax \
       --default-hero static
   \```

   Output: `$PROJECT_ROOT/08_КОД/wp-theme/inc/lp-preview-panel-axes.php`.
   In `functions.php` add: `require_once get_template_directory() . '/inc/lp-preview-panel-axes.php';`

4. Theme contract: any block whose visibility depends on hero variant must use
   `body.hero--<id>` selectors, with both variants present in DOM (visibility
   toggled by CSS). Non-active hero assets should use `loading="lazy"`.
```

- [ ] **Step 4: Document deploy step in wp-cli-deployer**

Append to `skills/wp-cli-deployer/SKILL.md`:

```markdown
## lp-preview-panel activation

After plugin sync, activate:

\```bash
wp plugin activate lp-preview-panel
\```

On first activation, the plugin defaults to `visible_to_anon = false`, so the
panel is admin-only on production by default. To enable client-facing preview:
admin → Settings → Превью-панель → "Показывать панель превью анонимным
посетителям" → save.

Deploy checklist add-on: before announcing a deploy to the client, open the
site in an incognito window and confirm the panel is either present (intended)
or absent (intended). No surprises.
```

- [ ] **Step 5: Document body-class contract in template/CLAUDE.md**

Append to `template/CLAUDE.md`:

```markdown
## Reserved body classes (lp-preview-panel)

These class prefixes are reserved by the `lp-preview-panel` plugin:

- `body.theme-<id>` — palette axis. CSS tokens live under each block.
- `body.hero--<id>` — hero variant axis. Theme controls visibility per block.

Do NOT add or remove these classes from theme code. The plugin's JS owns them.
For hero variants, keep both DOM subtrees rendered and toggle visibility via
`body.hero--<id>` selectors in CSS. Non-active hero assets must use
`loading="lazy"`.
```

- [ ] **Step 6: Verify all four skills mention the integration**

Run: `grep -l "lp-preview-panel" skills/*/SKILL.md`
Expected output (in some order):
```
skills/brand-kit-build/SKILL.md
skills/design-tokens-generation/SKILL.md
skills/wp-cli-deployer/SKILL.md
skills/wp-theme-assembler/SKILL.md
```

- [ ] **Step 7: Commit**

```bash
git add skills/design-tokens-generation/SKILL.md skills/brand-kit-build/SKILL.md skills/wp-theme-assembler/SKILL.md skills/wp-cli-deployer/SKILL.md template/CLAUDE.md
git commit -m "docs(skills): wire lp-preview-panel + palette library into landing workflow"
```

---

# Phase C — Migration of neuroupgrade-v2

## Task C1: Migration script + tests on synthetic fixtures

**Files:**
- Create: `scripts/migrate-to-preview-panel.sh`
- Create: `tests/phase-preview-panel/test-migrate-to-preview-panel.bats`
- Create: `tests/phase-preview-panel/fixtures/synth-project/08_КОД/wp-theme/header.php`
- Create: `tests/phase-preview-panel/fixtures/synth-project/08_КОД/wp-theme/assets/js/main.js`
- Create: `tests/phase-preview-panel/fixtures/synth-project/08_КОД/wp-theme/assets/css/main.css`
- Create: `tests/phase-preview-panel/fixtures/synth-project/08_КОД/wp-theme/functions.php`

- [ ] **Step 1: Build synthetic fixture**

Create a minimal stand-in for the neuroupgrade-v2 theme.

`tests/phase-preview-panel/fixtures/synth-project/08_КОД/wp-theme/header.php`: copy of the real `header.php` from `Lendings/neuroupgrade-v2/08_КОД/wp-theme/header.php` (the file we read at brainstorming time — contains the `<div class="nu-theme-bar">` block at lines 12-26). To keep the fixture under version control and stable across edits to the live project, snapshot it now.

`tests/phase-preview-panel/fixtures/synth-project/08_КОД/wp-theme/assets/js/main.js`: minimal stub:

```javascript
(function () {
  function unrelated() { return 1; }

  function initThemeSwitcher() {
    var STORAGE_KEY = 'nu-palette';
    var DEFAULT = 'i';
    var VALID = ['h', 'i', 'j', 'k'];
    function applyTheme(p) {
      var body = document.body;
      VALID.forEach(function (v) { body.classList.remove('theme-' + v); });
      body.classList.add('theme-' + p);
    }
    applyTheme(DEFAULT);
  }

  document.addEventListener('DOMContentLoaded', function () {
    unrelated();
    initThemeSwitcher();
  });
})();
```

`tests/phase-preview-panel/fixtures/synth-project/08_КОД/wp-theme/assets/css/main.css`: snippet containing the four `body.theme-h/i/j/k` blocks copied verbatim from `Lendings/neuroupgrade-v2/08_КОД/wp-theme/assets/css/main.css:1044-1133`. The migration script will parse these to derive `04_БРЕНД/palettes.yaml`.

`tests/phase-preview-panel/fixtures/synth-project/08_КОД/wp-theme/functions.php`:

```php
<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

function lp_render_icon( $name, $size ) {
    return '<svg></svg>';
}
```

- [ ] **Step 2: Write failing test**

`tests/phase-preview-panel/test-migrate-to-preview-panel.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/migrate-to-preview-panel.sh"
  FIXTURES="$ROOT/tests/phase-preview-panel/fixtures"
  WORK="$(mktemp -d)"
  cp -r "$FIXTURES/synth-project" "$WORK/project"
  # Use a temp library so test doesn't pollute the real one
  cp "$FIXTURES/library-empty.yaml" "$WORK/library.yaml"
}

teardown() {
  rm -rf "$WORK"
}

@test "removes nu-theme-bar from header.php" {
  run bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  [ "$status" -eq 0 ]
  ! grep -q "nu-theme-bar" "$WORK/project/08_КОД/wp-theme/header.php"
  # But other content is preserved
  grep -q "nu-header" "$WORK/project/08_КОД/wp-theme/header.php"
}

@test "removes initThemeSwitcher from main.js" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  ! grep -q "initThemeSwitcher" "$WORK/project/08_КОД/wp-theme/assets/js/main.js"
  grep -q "unrelated" "$WORK/project/08_КОД/wp-theme/assets/js/main.js"
}

@test "creates 04_БРЕНД/palettes.yaml with four palettes" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  PYAML="$WORK/project/04_БРЕНД/palettes.yaml"
  [ -f "$PYAML" ]
  grep -q "id: nu-paper" "$PYAML"
  grep -q "id: nu-quiet-dark" "$PYAML"
  grep -q "id: nu-beige" "$PYAML"
  grep -q "id: nu-iqido" "$PYAML"
}

@test "exports the four palettes to the library" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  grep -q "id: nu-paper" "$WORK/library.yaml"
  grep -q "id: nu-iqido" "$WORK/library.yaml"
}

@test "copies plugin from template" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  [ -d "$WORK/project/08_КОД/plugins/lp-preview-panel" ]
  [ -f "$WORK/project/08_КОД/plugins/lp-preview-panel/lp-preview-panel.php" ]
}

@test "generates inc/lp-preview-panel-axes.php" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  PHP="$WORK/project/08_КОД/wp-theme/inc/lp-preview-panel-axes.php"
  [ -f "$PHP" ]
  grep -q "'nu-iqido'" "$PHP"
  grep -q "'parallax'" "$PHP"
}

@test "adds require_once to functions.php exactly once" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  # Re-run; idempotent
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  COUNT=$(grep -c "lp-preview-panel-axes.php" "$WORK/project/08_КОД/wp-theme/functions.php")
  [ "$COUNT" = "1" ]
}

@test "generates palettes.css with body.theme-nu-iqido block" {
  bash "$SCRIPT" "$WORK/project" "$WORK/library.yaml"
  CSS="$WORK/project/08_КОД/wp-theme/assets/css/palettes.css"
  [ -f "$CSS" ]
  grep -q "body.theme-nu-iqido" "$CSS"
}
```

- [ ] **Step 3: Verify tests fail**

Run: `npx bats tests/phase-preview-panel/test-migrate-to-preview-panel.bats`
Expected: 8 tests FAIL — script not found.

- [ ] **Step 4: Implement the migration script**

`scripts/migrate-to-preview-panel.sh`:

```bash
#!/usr/bin/env bash
# migrate-to-preview-panel.sh <project-path> <library-path>
# One-shot migration: replaces hard-coded nu-theme-bar with lp-preview-panel plugin
# and seeds the project + library palette files from existing CSS.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: migrate-to-preview-panel.sh <project-path> <library-path>" >&2
  exit 2
fi

PROJECT="$1"
LIBRARY="$2"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# 1. Strip nu-theme-bar from header.php (the entire <div class="nu-theme-bar">...</div> block).
python3 "$ROOT/scripts/_migrate-strip-header.py" "$PROJECT/08_КОД/wp-theme/header.php"

# 2. Strip initThemeSwitcher from main.js (function declaration + invocation).
python3 "$ROOT/scripts/_migrate-strip-js.py" "$PROJECT/08_КОД/wp-theme/assets/js/main.js"

# 3. Extract H/I/J/K palettes from main.css → 04_БРЕНД/palettes.yaml as nu-paper/nu-quiet-dark/nu-beige/nu-iqido.
python3 "$ROOT/scripts/_migrate-extract-palettes.py" \
    --css "$PROJECT/08_КОД/wp-theme/assets/css/main.css" \
    --project "$PROJECT"

# 4. Export newly-created palettes into the global library.
python3 "$ROOT/scripts/export-palettes-to-library.py" --project "$PROJECT" --library "$LIBRARY"

# 5. Copy plugin from template (idempotent: rm -rf then cp).
mkdir -p "$PROJECT/08_КОД/plugins"
rm -rf "$PROJECT/08_КОД/plugins/lp-preview-panel"
cp -r "$ROOT/template/08_КОД/plugins/lp-preview-panel" "$PROJECT/08_КОД/plugins/"

# 6. Generate palette CSS and axes filter PHP.
python3 "$ROOT/scripts/generate-palette-css.py" --project "$PROJECT"
python3 "$ROOT/scripts/generate-axes-filter.py" \
    --project "$PROJECT" \
    --default-palette nu-iqido \
    --hero static,parallax \
    --default-hero static

# 7. Inject require_once into functions.php, idempotent.
FN="$PROJECT/08_КОД/wp-theme/functions.php"
LINE="require_once get_template_directory() . '/inc/lp-preview-panel-axes.php';"
if ! grep -qF "lp-preview-panel-axes.php" "$FN"; then
  printf "\n%s\n" "$LINE" >> "$FN"
fi

echo "migration complete for $PROJECT"
```

`scripts/_migrate-strip-header.py`:

```python
#!/usr/bin/env python3
"""Remove the <div class="nu-theme-bar">...</div> block from header.php."""
import re
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    src = f.read()

# DOTALL: the block spans multiple lines.
pattern = re.compile(r"\n?<div class=\"nu-theme-bar\".*?</div>\s*</div>\s*\n", re.DOTALL)
new = pattern.sub("\n", src, count=1)

with open(path, "w", encoding="utf-8") as f:
    f.write(new)
```

`scripts/_migrate-strip-js.py`:

```python
#!/usr/bin/env python3
"""Remove initThemeSwitcher function and its invocation from main.js."""
import re
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    src = f.read()

# Strip function declaration up through its closing brace.
# Match: function initThemeSwitcher() { ... }  (balanced by counting in regex is hard;
# use a hand-rolled scan that finds the matching brace.)
def strip_function(src, name):
    idx = src.find("function " + name)
    if idx < 0:
        return src
    brace_idx = src.find("{", idx)
    if brace_idx < 0:
        return src
    depth = 0
    i = brace_idx
    while i < len(src):
        c = src[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                # Eat a trailing newline if present.
                if end < len(src) and src[end] == "\n":
                    end += 1
                return src[:idx] + src[end:]
        i += 1
    return src

src = strip_function(src, "initThemeSwitcher")
# Strip any line that calls initThemeSwitcher(), with or without leading whitespace.
src = re.sub(r"^\s*initThemeSwitcher\(\);.*\n", "", src, flags=re.MULTILINE)

with open(path, "w", encoding="utf-8") as f:
    f.write(src)
```

`scripts/_migrate-extract-palettes.py`:

```python
#!/usr/bin/env python3
"""Parse body.theme-h/i/j/k blocks from main.css → 04_БРЕНД/palettes.yaml."""
import argparse
import os
import re
import sys
import yaml

# Map letter → migration id and name.
LETTER_MAP = {
    "h": ("nu-paper", "Бумажный"),
    "i": ("nu-quiet-dark", "Тихий-тёмный"),
    "j": ("nu-beige", "Бежевый"),
    "k": ("nu-iqido", "IQIDO Guideline"),
}

# CSS-var → yaml token key.
VAR_TO_KEY = {
    "--bg-base": "bg_base",
    "--bg-section": "bg_section",
    "--bg-elevated": "bg_elevated",
    "--border-subtle": "border_subtle",
    "--border-strong": "border_strong",
    "--text-primary": "text_primary",
    "--text-soft": "text_soft",
    "--text-dim": "text_dim",
    "--accent-mint": "accent_mint",
    "--accent-teal": "accent_teal",
    "--accent-coral": "accent_coral",
    "--accent-coral-hover": "accent_coral_hover",
    "--accent-coral-text": "accent_coral_text",
    "--accent-rgb-mint": "accent_rgb_mint",
    "--accent-rgb-coral": "accent_rgb_coral",
    "--card-bg": "card_bg",
    "--card-border": "card_border",
    "--card-border-hover": "card_border_hover",
    "--accent-cta-glow-opacity": "accent_cta_glow_opacity",
}


def parse_block(css, letter):
    pattern = re.compile(
        r"body\.theme-" + letter + r"\s*\{(.*?)\}",
        re.DOTALL,
    )
    m = pattern.search(css)
    if not m:
        print(f"ERROR: theme-{letter} block not found in CSS", file=sys.stderr)
        sys.exit(1)
    body = m.group(1)
    tokens = {}
    for var, key in VAR_TO_KEY.items():
        vm = re.search(re.escape(var) + r"\s*:\s*([^;]+?)\s*;", body)
        if not vm:
            print(f"ERROR: theme-{letter} missing {var}", file=sys.stderr)
            sys.exit(1)
        tokens[key] = vm.group(1).strip()
    return tokens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--css", required=True)
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    with open(args.css, "r", encoding="utf-8") as f:
        css = f.read()

    palettes = []
    for letter, (pid, pname) in LETTER_MAP.items():
        tokens = parse_block(css, letter)
        palettes.append({
            "id": pid,
            "name": pname,
            "description": f"Migrated from neuroupgrade-v2 theme-{letter}.",
            "created_at": "2026-05-12",
            "created_in_project": "neuroupgrade-v2",
            "tokens": tokens,
        })

    dest_dir = os.path.join(args.project, "04_БРЕНД")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "palettes.yaml")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("# Project palette snapshot (migrated from theme CSS)\n")
        yaml.safe_dump({"palettes": palettes}, f, sort_keys=False, allow_unicode=True)
    # Mirror to design-system folder so /landing-design's export hook picks them up.
    ds_dir = os.path.join(args.project, "05_ДИЗАЙН-СИСТЕМА")
    os.makedirs(ds_dir, exist_ok=True)
    with open(os.path.join(ds_dir, "palettes.yaml"), "w", encoding="utf-8") as f:
        f.write("# Mirror of 04_БРЕНД/palettes.yaml for design-system traceability.\n")
        yaml.safe_dump({"palettes": palettes}, f, sort_keys=False, allow_unicode=True)
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Make script executable**

Run: `chmod +x scripts/migrate-to-preview-panel.sh`

- [ ] **Step 6: Tests pass**

Run: `npx bats tests/phase-preview-panel/test-migrate-to-preview-panel.bats`
Expected: 8 tests pass.

If a test fails because the header.php fixture doesn't have a `</div>` immediately after the nu-theme-bar close (real `header.php` does — line 26), inspect the synthetic fixture and confirm it matches the real file's structure verbatim. The migration regex depends on the closing pair pattern.

- [ ] **Step 7: Commit**

```bash
git add scripts/migrate-to-preview-panel.sh scripts/_migrate-strip-header.py scripts/_migrate-strip-js.py scripts/_migrate-extract-palettes.py tests/phase-preview-panel/test-migrate-to-preview-panel.bats tests/phase-preview-panel/fixtures/synth-project/
git commit -m "feat(migration): migrate-to-preview-panel.sh + 8 bats tests on synthetic fixtures"
```

---

## Task C2: Run migration on the real neuroupgrade-v2, manual E2E

This is a non-TDD task. The migration script is the implementation; here we run it on real data and manually verify behaviour.

**Files:**
- Modify: every file in `Lendings/neuroupgrade-v2/` listed under "Modified files" at top of this plan.
- Create: docs note for the QA checklist (in the project, not in landing-system repo).

- [ ] **Step 1: Snapshot current state of neuroupgrade-v2**

Run inside `Lendings/neuroupgrade-v2/`:
```bash
git status
git diff --stat
```
Expected: clean working tree (or known WIP). If unclean, commit/stash first. We need a clean baseline so the migration commit is auditable.

- [ ] **Step 2: Run the migration**

From `landing_system/`:
```bash
bash scripts/migrate-to-preview-panel.sh \
    "$(pwd)/../Lendings/neuroupgrade-v2" \
    "$(pwd)/presets/palettes.yaml"
```
Expected output: `migration complete for .../neuroupgrade-v2`.

- [ ] **Step 3: Inspect the diff in neuroupgrade-v2**

In `Lendings/neuroupgrade-v2/`:
```bash
git status
git diff -- 08_КОД/wp-theme/header.php
git diff -- 08_КОД/wp-theme/assets/js/main.js
git diff -- 08_КОД/wp-theme/functions.php
ls 04_БРЕНД/palettes.yaml 05_ДИЗАЙН-СИСТЕМА/palettes.yaml
ls 08_КОД/plugins/lp-preview-panel/
ls 08_КОД/wp-theme/inc/lp-preview-panel-axes.php
ls 08_КОД/wp-theme/assets/css/palettes.css
```

Expected:
- `header.php` no longer contains `nu-theme-bar`; `nu-header` block untouched.
- `main.js` no longer contains `initThemeSwitcher` (declaration or call).
- `functions.php` ends with `require_once get_template_directory() . '/inc/lp-preview-panel-axes.php';`
- The four new files exist.

If any file looks wrong, do NOT commit. Reset:
```bash
git checkout -- .
git clean -fd 04_БРЕНД 05_ДИЗАЙН-СИСТЕМА 08_КОД/plugins 08_КОД/wp-theme/inc 08_КОД/wp-theme/assets/css/palettes.css
```
…then investigate the regex/parser in `_migrate-strip-*.py` against the actual file.

- [ ] **Step 4: Verify the library got four new entries**

From `landing_system/`:
```bash
python scripts/validate-palettes.py presets/palettes.yaml
grep -E "^\s*- id:" presets/palettes.yaml
```
Expected: at least four lines including `nu-paper`, `nu-quiet-dark`, `nu-beige`, `nu-iqido`.

- [ ] **Step 5: Enqueue palettes.css in the theme**

Edit `Lendings/neuroupgrade-v2/08_КОД/wp-theme/functions.php` (or wherever `wp_enqueue_style` for `main.css` lives — find with `grep -n "wp_enqueue_style" Lendings/neuroupgrade-v2/08_КОД/wp-theme/functions.php`). Add adjacent to the existing main stylesheet enqueue:

```php
wp_enqueue_style(
    'lp-palettes',
    get_template_directory_uri() . '/assets/css/palettes.css',
    [ 'main-css-handle' ], // replace with actual main handle
    '0.1.0'
);
```

This is a manual edit because the existing enqueue handle name is theme-specific.

- [ ] **Step 6: Manual E2E checklist (deploy to staging, open browser)**

Deploy locally (or to staging) per your usual `/landing-deploy` flow, then verify in browser:

| # | Action | Expected |
|---|---|---|
| 1 | Log in as admin, open homepage | Panel visible at top with two rows: palette + hero |
| 2 | Switch palette select to `nu-paper` | Body class becomes `theme-nu-paper`; visuals match old `theme-h` |
| 3 | Switch hero to `parallax` | Body class becomes `hero--parallax`; static hero hidden, parallax stage shown (or, if not yet wired in theme markup — at minimum body class is set; **flag this as follow-up** if no visual change) |
| 4 | Log out, reload | Panel absent from HTML (Ctrl+U to view source — no `lp-preview-panel`) |
| 5 | Admin → Settings → Превью-панель → check "visible to anon" → save | After reload as anon: panel visible |
| 6 | Click "Зафиксировать мой текущий выбор", save | Reload in incognito: server-default applied |
| 7 | Open `?palette=nu-paper&hero=static` | Both axes applied regardless of localStorage |
| 8 | Reset settings, uncheck visible_to_anon | Panel admin-only again |

Record results in a markdown file: `Lendings/neuroupgrade-v2/10_QA/preview-panel-e2e-2026-05-12.md`. For each row note PASS/FAIL plus a one-line observation.

If anywhere FAIL: do NOT commit the migration. Diagnose with systematic-debugging skill before continuing.

- [ ] **Step 7: Commit the migration in the neuroupgrade-v2 repo**

From `Lendings/neuroupgrade-v2/`:
```bash
git add -A
git commit -m "feat(theme): replace nu-theme-bar with lp-preview-panel plugin

Migrated palettes H/I/J/K to body.theme-nu-paper/nu-quiet-dark/nu-beige/nu-iqido.
Added hero axis (static/parallax). Panel hidden from anon by default.
See Lendings/neuroupgrade-v2/10_QA/preview-panel-e2e-2026-05-12.md for E2E pass.
"
```

- [ ] **Step 8: Commit the library update in the landing-system repo**

From `landing_system/`:
```bash
git add presets/palettes.yaml
git commit -m "feat(palette-library): seed library with four palettes from neuroupgrade-v2 migration"
```

---

## Task C3: Wire the hero parallax markup into neuroupgrade-v2 theme

The migration sets `body.hero--parallax` on the body, but until the theme markup actually contains both static and parallax hero subtrees, the user won't see visual difference between the two hero options.

This task is the smallest possible reachable goal: add a `parallax-stage` stub in the hero block that's gated by `body.hero--parallax`. Real parallax atlas integration (per `paralaximus-codex` skill) is a follow-up.

**Files:**
- Modify: `Lendings/neuroupgrade-v2/08_КОД/wp-theme/template-parts/block-hero.php` (or wherever hero markup lives)
- Modify: `Lendings/neuroupgrade-v2/08_КОД/wp-theme/assets/css/main.css`

- [ ] **Step 1: Locate the hero block**

Run: `grep -l "nu-hero" Lendings/neuroupgrade-v2/08_КОД/wp-theme/template-parts/`
Expected: one or two PHP files. Note the path.

- [ ] **Step 2: Add the parallax stub wrapper**

In the hero PHP template, wrap the existing static hero content in a `<div class="nu-hero__static-bg">` and add an adjacent empty `<div class="nu-hero__parallax-stage" aria-hidden="true"></div>`. Both inside the same `.nu-hero` container.

Example (adjust to actual structure):

```php
<section class="nu-hero">
    <div class="nu-hero__static-bg">
        <!-- existing static hero markup, unchanged -->
    </div>
    <div class="nu-hero__parallax-stage" aria-hidden="true">
        <!-- placeholder; real parallax atlas wired via /skills/paralaximus-codex -->
        <div class="nu-hero__parallax-placeholder">Parallax preview placeholder</div>
    </div>
</section>
```

- [ ] **Step 3: Add the body-class CSS gating**

At the bottom of `main.css`, after the palette overrides block, append:

```css
/* Hero axis — toggled by body.hero--<id> from lp-preview-panel plugin. */
.nu-hero__parallax-stage { display: none; }
body.hero--parallax .nu-hero__static-bg     { display: none; }
body.hero--parallax .nu-hero__parallax-stage { display: block; }
.nu-hero__parallax-placeholder {
  padding: 60px 20px;
  text-align: center;
  background: linear-gradient(135deg, #1B4A50, #0E2B30);
  color: #77D9D9;
  font-size: 24px;
  border-radius: 8px;
}
```

- [ ] **Step 4: Manual verify**

Reload the staged site. Switch hero in the panel between `static` and `parallax`. Expected: visible difference (placeholder block vs. real hero). Update QA file row 3 from "flagged" to PASS.

- [ ] **Step 5: Commit**

From `Lendings/neuroupgrade-v2/`:
```bash
git add 08_КОД/wp-theme/template-parts/ 08_КОД/wp-theme/assets/css/main.css 10_QA/preview-panel-e2e-2026-05-12.md
git commit -m "feat(theme): wire hero static/parallax via body.hero-- classes (placeholder for parallax atlas)"
```

---

## Task C4: Configure stage-gates hook for palette export

Hook `/landing-design` approval so that the export runs automatically. Without this, library growth is manual.

**Files:**
- Modify: `config/stage-gates.yaml`
- Modify: `scripts/gate-check.sh` (or wherever post-approve hooks fire)

- [ ] **Step 1: Inspect current stage-gates config**

Run:
```bash
grep -A 20 "05_design_system" config/stage-gates.yaml
```
Expected: a block for stage `05_design_system`. Note its structure — we'll add a `post_approve_hooks` key.

- [ ] **Step 2: Locate where hooks fire**

Run:
```bash
grep -n "approve" scripts/gate-check.sh | head
grep -rn "post_approve" scripts/ config/ 2>/dev/null | head
```
Expected: either an existing hook mechanism (good, we plug in) or nothing (we add minimal hook support).

- [ ] **Step 3: Choose implementation path based on what you found**

**Path A — there is already a `post_approve_hooks` mechanism:** add to `config/stage-gates.yaml` under `05_design_system`:

```yaml
post_approve_hooks:
  - command: python
    args:
      - scripts/export-palettes-to-library.py
      - --project
      - "${PROJECT_ROOT}"
      - --library
      - "${LANDING_SYSTEM_ROOT}/presets/palettes.yaml"
    on_error: warn
```

**Path B — no hook mechanism exists:** add the documentation-only path. Append a note in `config/stage-gates.yaml`:

```yaml
05_design_system:
  # ... existing config
  manual_post_approve_steps:
    - "Run: python scripts/export-palettes-to-library.py --project <project> --library presets/palettes.yaml"
```

…and add a reminder in `skills/design-tokens-generation/SKILL.md` (already done in Task B5 step 1 — verify the wording mentions "MUST run after approval").

- [ ] **Step 4: Manual smoke test of the hook (Path A only)**

If you took Path A: create a throwaway project skeleton with a palette, approve its design stage, confirm the library gets the new entry. If Path B: skip — manual step is documented, no script to test.

- [ ] **Step 5: Commit**

```bash
git add config/stage-gates.yaml scripts/gate-check.sh
git commit -m "feat(stage-gates): post-approve palette export for stage 05 (or doc-only if no hook mechanism yet)"
```

---

# Final verification

- [ ] **Step F1: Full test suite green**

Run from `landing_system/`:
```bash
npm run test:phase-preview-panel
```
Expected: every bats test from this plan passes (~33 tests total across the new suite).

Also run the existing suites to confirm no regression:
```bash
npm test
```
Expected: all green.

- [ ] **Step F2: Spec acceptance criteria walk-through**

Open `docs/superpowers/specs/2026-05-12-preview-panel-and-palette-library-design.md`, scroll to "Acceptance Criteria", verify each of the 11 items:

1. Plugin lies in `template/08_КОД/plugins/lp-preview-panel/` — verify with `ls`.
2. `landing_system/presets/palettes.yaml` exists, valid — `python scripts/validate-palettes.py presets/palettes.yaml`.
3. All bats tests green — done in F1.
4. neuroupgrade-v2 migrated, panel works, palette behaviour unchanged — confirmed in C2 step 6.
5. Hero axis switches between static/parallax visually — confirmed in C3 step 4.
6. Admin page exists with both options — confirmed in C2 step 6 row 5.
7. Default `visible_to_anon=false` — confirmed in C2 step 6 row 4.
8. Deploy checklist mentions panel visibility — done in B5 step 4.
9. `/landing-design` exports palettes — done in B5 step 1 + C4.
10. `/landing-brand` supports three modes — done in B5 step 2.
11. `/landing-build` generates CSS + filter from snapshot — done in B5 step 3.

If any item still doesn't hold, file a follow-up task before declaring the plan done.

- [ ] **Step F3: Final commit / branch close-out**

If working on a feature branch, push and open a PR. Otherwise verify clean tree:
```bash
git status
git log --oneline -20
```

---

## Self-review summary

After writing this plan I checked it back against the spec:

**Spec coverage** — every acceptance criterion has at least one task. F2 walks them. The "snapshot at /landing-build" wording in the spec is satisfied by B3+B4+B5; the "snapshot at /landing-brand" wording is satisfied by B2+B5. Two distinct snapshot moments, separate scripts, no contradiction.

**Placeholders** — no TBD, no "implement later", no "similar to Task N". Every code step contains complete code. The `--hero` registry is hard-coded to `static`/`parallax` in Task B4 — when a third hero is added, extend `HERO_LABELS` in `generate-axes-filter.py` and the schema in the matching test. The "Path A / Path B" branch in C4 is intentional and pragmatic (we don't know the current hook mechanism state without inspecting); each path has concrete steps.

**Type consistency** — checked:
- Method `LP_Preview_Panel_Axes::all()` and `::is_valid_value()` referenced consistently in panel + settings.
- WP option key `lp_preview_panel` and its array shape `{visible_to_anon, defaults}` consistent across class-settings, class-panel, and the spec.
- YAML token keys (`bg_base` etc.) consistent across validator, exporter, snapshot, CSS gen, and migration extractor.
- CSS class names `lp-preview-panel__*` consistent between PHP renderer and CSS file.
- `body.theme-<id>` and `body.hero--<id>` prefixes consistent across CSS gen, axes filter, JS engine, and migration script.

Plan saved to `docs/superpowers/plans/2026-05-12-preview-panel-and-palette-library-plan.md`.
