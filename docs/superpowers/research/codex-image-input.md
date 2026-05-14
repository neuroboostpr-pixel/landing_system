# Codex CLI image input — research findings (2026-05-13)

## Environment

- codex --version: NOT INSTALLED on this machine at time of research
- OS: macOS Darwin 24.6.0
- Research method: source code analysis via GitHub API (`openai/codex` repo, HEAD as of 2026-05-13)
- npm registry: latest stable = `@openai/codex` v0.130.0; install via `npm i -g @openai/codex` or `brew install --cask codex`

---

## Help-text scan for image-related flags

### codex --help (top-level) — from source

Codex is not installed on this machine; flags were read directly from the Rust source:
`codex-rs/utils/cli/src/shared_options.rs` (commit HEAD, 2026-05-13).

```
--image <FILE>  (short: -i)
  Optional image(s) to attach to the initial prompt.
  value_delimiter = ','   ← comma-separated for multiple files
  num_args = 1..          ← one or more files accepted

Source: SharedCliOptions in codex-rs/utils/cli/src/shared_options.rs
This struct is shared (flattened) into BOTH the TUI interactive CLI and
the exec (non-interactive) CLI.
```

### codex exec --help — from source

`codex exec` delegates to `ExecSharedCliOptions`, which flattens `SharedCliOptions`:
```
Source: codex-rs/exec/src/cli.rs — ExecSharedCliOptions wraps SharedCliOptions
```

The `--image` / `-i` flag is therefore available on `codex exec` as well.
Confirmed in `codex-rs/exec/src/lib.rs`:
```
.map(|path| UserInput::LocalImage { path })
```
Images are passed as `UserInput::LocalImage` — the model receives them as vision inputs.

---

## Tested mechanisms

> NOTE: codex CLI is not installed on this machine, so tests A–C below
> could not be executed as live commands. All verdicts are based on source
> code inspection of the `openai/codex` GitHub repository (HEAD, 2026-05-13).

### Test A: --image / --attach flag

```bash
# Syntax confirmed from source (SharedCliOptions):
codex exec --skip-git-repo-check --image /tmp/test.jpg "Describe this image in one sentence"

# Multiple images (comma-separated):
codex exec --skip-git-repo-check --image /tmp/a.jpg,/tmp/b.jpg "Compare these images"

# Short form:
codex exec --skip-git-repo-check -i /tmp/test.jpg "Describe this image in one sentence"
```

Key source file: `codex-rs/utils/cli/src/shared_options.rs`
```rust
/// Optional image(s) to attach to the initial prompt.
#[arg(
    long = "image",
    short = 'i',
    value_name = "FILE",
    value_delimiter = ',',
    num_args = 1..
)]
pub images: Vec<PathBuf>,
```

`--attach` flag does NOT exist. Only `--image` / `-i`.

**Verdict: WORKS — natively supported in both interactive and exec (non-interactive) mode**

### Test B: filesystem read in prompt

```bash
codex exec --skip-git-repo-check \
  "Read the image file at /tmp/test.jpg using your read tool and describe it in one sentence"
```

This approach relies on codex's built-in `view_image` tool
(`codex-rs/core/src/tools/handlers/view_image.rs`), which exists in the codebase.
However, it is an indirect path: codex must decide to call the tool based on the
prompt text, rather than the image being explicitly attached to the initial message.

**Verdict: PARTIAL — view_image tool exists, but image arrives as tool-call result
not as first-class prompt attachment; less reliable for batch classification.**

### Test C: markdown image reference

```bash
codex exec --skip-git-repo-check \
  "Analyze this image: ![](/tmp/test.jpg). One sentence description."
```

No evidence in source that codex parses markdown image syntax into an actual
image attachment for the model. This would only work if codex invokes its
`view_image` tool on URLs/paths found in prompts — not a documented behavior.

**Verdict: NOT SUPPORTED — no source evidence for markdown image parsing in exec.**

---

## Decision

**Chosen mechanism for photo-classifier: Test A (`--image` / `-i` flag)**

**Rationale:**  
The `--image` / `-i` flag is a first-class, explicitly documented CLI option in
`SharedCliOptions`, which is flattened into the `codex exec` command. Images passed
via this flag become `UserInput::LocalImage` entries in the initial prompt message —
the model sees them as direct vision inputs alongside the text prompt. This is the
most reliable, most direct mechanism and requires no workarounds or tool-call
indirection. It is available in the same codex version (v0.130.0+) that the
project already requires for paralaximus (image_gen). There is no separate
Anthropic SDK dependency needed.

**Implication for Task 5 (codex wrappers):**
- `codex-classify.sh` will use mechanism: **A (`--image`)**
- Specific invocation pattern:
  ```bash
  codex exec \
    --skip-git-repo-check \
    --image "$PHOTO_PATH" \
    "$CLASSIFY_PROMPT"
  ```
  For batch (5 photos at a time per spec R2):
  ```bash
  # Comma-separated — all 5 photos in one codex exec call:
  codex exec \
    --skip-git-repo-check \
    --image "photo_001.jpg,photo_002.jpg,photo_003.jpg,photo_004.jpg,photo_005.jpg" \
    "$CLASSIFY_PROMPT_BATCH"
  ```
- SDK fallback (Task 5b): NOT needed. Mechanism A is confirmed supported natively.

---

## Sources

| Source | URL |
|---|---|
| `SharedCliOptions` (image flag definition) | `codex-rs/utils/cli/src/shared_options.rs` |
| `ExecSharedCliOptions` (exec uses SharedCliOptions) | `codex-rs/exec/src/cli.rs` |
| `UserInput::LocalImage` (images in exec lib) | `codex-rs/exec/src/lib.rs` |
| `view_image` tool handler | `codex-rs/core/src/tools/handlers/view_image.rs` |
| npm package info | `npm info @openai/codex` — latest v0.130.0 |
| Spec R1 reference | `docs/superpowers/specs/2026-05-13-photo-pipeline-design.md#R1` |

---

## Installation note

codex is NOT installed on this machine. Before running the photo-pipeline:
```bash
npm i -g @openai/codex
# OR
brew install --cask codex
```
Then authenticate:
```bash
codex login
```
