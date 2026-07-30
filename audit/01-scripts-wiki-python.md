# Code Review: scripts/wiki/ + scripts/*.py

## Summary
Code is overall clean, well-organized, with thoughtful separation between system/project/conversations compilers and good use of a SHA256 hash-cache for incremental builds. However, the SDK call path has **no caching of generated concepts on top of source-hash**, the source-glob loop does O(sources × concepts) re-globbing, and several issues silently swallow errors which can let the agent skip pipeline gates without noticing. A few security / robustness items in the `flush.py` background path also need fixing.

**Verdict: Request Changes.**

---

## Critical (must fix)

### 1. `scripts/wiki/system_compiler.py:139–147` — bootstrap-rehash visits every source twice
Before the main compile loop runs, the function globs every `SYSTEM_SOURCES` pattern and computes `compute_hash(source_path)` for every existing concept (regardless of whether the cache already knows about it correctly). With 473 concepts and most of `docs/**`, this means hundreds of full-file `read_bytes()` calls just to "pre-populate" the cache. Then the main loop globs the same patterns AGAIN.

```python
# Current — extra full pass over the whole repo on every invoke
if not dry_run:
    for source_def in sources:
        for source_path in sorted(repo_root.glob(source_def["path"])):
            rel_key = source_path.relative_to(repo_root).as_posix()
            slug = _slug_for_source(source_path)
            concept_path = wiki_dir / "concepts" / source_def["concept_dir"] / f"{slug}.md"
            if concept_path.exists() and rel_key not in cache:
                cache[rel_key] = hash_cache.compute_hash(source_path)
    hash_cache.save_cache(cache_path, cache)
```

Fix: merge the bootstrap into the main loop. Inside the main loop, when `rel_key not in cache` AND `concept_path.exists()`, compute hash once, set cache, and `continue` as skipped. This removes one full sweep and ~halves IO on cold-warm runs.

### 2. `scripts/wiki/system_compiler.py:194–198` — `save_cache` called inside the per-file loop
`hash_cache.save_cache` rewrites the **entire** `.cache.json` (~62 KB on disk today, ~473 keys) on every single successfully compiled concept. If the compiler ever processes a sizeable batch (e.g., 50 changes), that's 50 full JSON serializations + atomic-replace operations of the whole cache. The final `save_cache` on line 217 already persists the cache after the loop.

```python
# Current — write entire cache after every concept
if not dry_run:
    utils.atomic_write(concept_path, content)
    cache[rel_key] = hash_cache.compute_hash(source_path)
    hash_cache.save_cache(cache_path, cache)   # <-- O(N²) over batch
```

Fix: remove the inner `save_cache` call. The one at line 217 (and 147 bootstrap save) is sufficient. If you want crash-resilience, save every N items (e.g., every 25) instead of every item.

### 3. `scripts/wiki/system_compiler.py:179–183` — SDK errors are stored but the cache is NOT updated, so each subsequent run **retries the SDK call for the same broken file forever**
```python
try:
    content = _compile_concept(source_path, repo_root)
except sdk_client.SDKError as e:
    errors.append(f"{rel_key}: {e}")
    continue
```
If the SDK returns empty (very common when sonnet hits a content filter or the input is malformed), the file's hash is never written, so next invocation re-globs it and re-calls the SDK — **token leak on every git commit** via the post-commit hook. The whole point of the hash cache (per CLAUDE.md: "~0 сек если ничего не менялось") is defeated when even one file fails persistently.

Fix: distinguish "transient" vs "persistent" errors, or write the source hash with a negative-cache marker (e.g., a separate `.cache.errors.json` keyed on `(hash, error_count)`). Minimum viable fix: track failures, and after N consecutive failures for the same hash, persist the hash so the file is treated as "skip until source changes".

### 4. `scripts/wiki/flush.py:88–89` — silent SDK swallow loses every flush failure
```python
try:
    lessons = sdk_client.generate(system=prompt, user=text)
except sdk_client.SDKError:
    return  # silent — мы в фоне, не пугаем юзера
```
The hook runs detached at SessionEnd/PreCompact. If the SDK is misconfigured, has no auth, or always errors, the user gets **zero feedback** — they think memory is being captured but no daily log is ever written. Combined with `subprocess.Popen(..., stderr=DEVNULL)` in the hooks, debugging this is impossible.

Fix: log to a rotating file under `memory/.flush-errors.log` instead of returning silently. Cheap, two lines:
```python
except sdk_client.SDKError as e:
    err_log = (memory_dir / ".flush-errors.log")
    err_log.parent.mkdir(parents=True, exist_ok=True)
    err_log.open("a", encoding="utf-8").write(f"{date.today().isoformat()} {e}\n")
    return
```

### 5. `scripts/wiki/sdk_client.py:52` — `max_turns=50` is excessive for one-shot generation
The wiki concept prompt is single-turn: system + user → assistant text. There is no tool-use loop, no agentic flow. `max_turns=50` lets the SDK keep iterating; on a hung or runaway invocation this could burn a large number of turns before the user notices.

```python
options = ClaudeAgentOptions(
    system_prompt=system,
    model=DEFAULT_MODEL,
    permission_mode="bypassPermissions",
    max_turns=50,
)
```
Fix: `max_turns=1`. For wiki concept gen and conversation flush and query, one round-trip is the entire contract.

### 6. `scripts/wiki/lint.py:62–64` and `91–106` — reads every concept file twice
```python
for name, path in concepts.items():
    text = path.read_text(encoding="utf-8")   # read #1
    _, body = utils.parse_frontmatter(text)
    bodies[name] = body
    links_from[name] = _wikilinks_in(body)

# later, in the stale check:
for name, path in concepts.items():
    text = path.read_text(encoding="utf-8")   # read #2 — same file
    meta, _ = utils.parse_frontmatter(text)
    updated = meta.get("updated")
```
With 473 concepts that's 946 file reads instead of 473. Fix: cache both `meta` and `body` in the first pass.

```python
metas: dict[str, dict] = {}
for name, path in concepts.items():
    text = path.read_text(encoding="utf-8")
    meta, body = utils.parse_frontmatter(text)
    metas[name] = meta
    bodies[name] = body
    links_from[name] = _wikilinks_in(body)
```

### 7. `scripts/wiki/lint.py:121–139` — LLM contradiction check sends EVERY concept body into one prompt
```python
combined = "\n\n---\n\n".join(
    f"# {n}\n\n{bodies[n][:500]}" for n in concepts
)
```
With 473 concepts × 500 chars = ~235K chars input every time `--llm-check` is used. There is no chunking, no cache, no skip-if-unchanged. This is the single largest token-cost path in the codebase. Even with sonnet, this is ~60K input tokens per run.

Fix: hash the concatenated input and cache the result keyed on hash in `wiki/.lint-cache.json`. Re-run only if input hash changes. Also chunk: 50 concepts per request is sufficient for cross-comparison; do pair-wise comparisons within chunks.

---

## Major (should fix — token leak / perf / design)

### 8. `scripts/wiki/system_compiler.py:154–157` — sorted glob inside nested loop on every run
```python
for source_def in sources:
    pattern = source_def["path"]
    concept_dir = source_def["concept_dir"]
    for source_path in sorted(repo_root.glob(pattern)):
```
Each source pattern is globbed and sorted at every invocation. Several patterns like `block-library/*/*/meta.yaml` walk every block category. This is fine in isolation, but combined with the bootstrap pass above (issue #1) you walk the tree twice. After fixing #1, this becomes acceptable.

### 9. `scripts/wiki/query.py:34–42` — no cache on Q&A and no `max_tokens` limit
Every `python -m scripts.wiki.query "..."` does a full SDK round trip including potentially `2 * 6000` chars of index plus question. No caching of recent questions, no rate guard. Users may invoke the same question repeatedly (especially in tests). Even a simple `(question + sorted(wiki_dirs))` hash → file lookup in `~/.cache/landing-system-wiki/qa/` would eliminate duplicate token usage.

### 10. `scripts/wiki/sdk_client.py:67–77` — no retry on transient errors and no token-usage logging
`generate()` raises immediately on empty content. There is no retry on transient network errors (the SDK will raise its own type) and **no log of how many tokens were spent**. For a system the user complains about as "token-leaky", at minimum log `len(system)`, `len(user)`, `len(content)` to a usage file. This is the first piece of evidence you'll need when deciding where to cut.

### 11. `scripts/wiki/system_compiler.py:71–107` — `_build_index` rebuilds from scratch even on no changes
On every invocation `_build_index` is called and `index.md` is rewritten (line 201–205) even if `compiled` is empty (no changes). `git` will still record a no-op write, and the `concepts_summary` list is built regardless.

```python
if concepts_summary:   # always true when wiki has any concepts
    index_content = _build_index(concepts_summary)
    if not dry_run:
        utils.atomic_write(wiki_dir / "index.md", index_content)
```
Fix: skip the write if `not compiled and not errors` (i.e., everything was skipped from cache).

### 12. `scripts/wiki/system_compiler.py:25` — `GENERIC_STEMS` mixes case sensitivity inconsistently
```python
GENERIC_STEMS = {"SKILL", "README", "readme", "meta", "META", "index"}
```
A `Path("SKILL.MD").stem` would yield `"SKILL"`, but `Path("Readme.md").stem` is `"Readme"` and would not match. Fix:
```python
GENERIC_STEMS = {"skill", "readme", "meta", "index"}
# ...
if path.stem.lower() in GENERIC_STEMS:
```

### 13. `scripts/wiki/lint.py:107–111` — "missing backlinks" is noise, not a problem
The lint flags every directional link as a "missing backlink". In a wiki, hierarchical references (e.g., command → skill, but not skill → command) are normal. With ~500 concepts this generates hundreds of false positives that obscure real issues. Either remove this check or make it opt-in.

### 14. `scripts/wiki/conversations_compiler.py:31–36` — `combined` has no size cap
```python
combined = "\n\n".join(
    f"## {f.stem}\n\n{f.read_text(encoding='utf-8')}" for f in files
)
```
Daily logs grow unboundedly. After 6 months of use, `combined` could be megabytes shipped into a single SDK call. Fix: cap to recent N days (e.g., 7) or recent K chars (e.g., 50_000). Same problem flagged in flush.py at the message level (it caps at last 30 messages — but conversations_compiler does not).

### 15. `scripts/wiki/flush.py:80–83` — `format_transcript` runs twice when `len(msgs) > 30`
```python
text = format_transcript(msgs)           # full run
if len(msgs) > 30:
    text = format_transcript(msgs[-30:]) # discard first, re-format
```
Fix:
```python
trimmed = msgs[-30:] if len(msgs) > 30 else msgs
text = format_transcript(trimmed)
```

### 16. `scripts/wiki/hash_cache.py:18` — `load_cache` doesn't pass `encoding="utf-8"`
```python
return json.loads(cache_path.read_text())
```
On macOS the default is usually utf-8 but not guaranteed (e.g., POSIX locale). Wiki concept paths are kebab-case ascii, but `compute_hash` writes `relative_to(repo_root).as_posix()` keys that include Cyrillic for `04_БРЕНД`, `07_ПРОТОТИП`, etc.
Fix: `cache_path.read_text(encoding="utf-8")` and add `encoding="utf-8"` to `write_text` in `save_cache` as well.

### 17. `scripts/wiki/hash_cache.py:19` — exception swallow loses real cache corruption
```python
except (json.JSONDecodeError, OSError):
    return {}
```
If `.cache.json` becomes corrupted, the whole wiki silently re-compiles (token cost: every concept goes back through the SDK). Fix: rename the broken cache to `.cache.json.broken-YYYY-MM-DD` and log a warning to stderr so the user sees the regression.

### 18. `scripts/wiki/lint.py:83–88` — `stale_threshold` only works if frontmatter has `updated:` set
Most concepts written by `system_compiler` have no `updated` field (look at `_build_index`/`_compile_concept` — they delegate that to the SDK prompt, which is unreliable). Net result: the "stale" check finds nothing useful. Either set `updated` deterministically when writing the concept (good) or remove the check (better than a check that never fires).

### 19. `scripts/wiki/system_compiler.py:96–106` — index loops sort concepts on `file_stem` but allows `None`
```python
for c in sorted(groups[type_], key=lambda x: x.get("file_stem", "")):
```
If `file_stem` is ever missing or None, comparing None vs str raises. Cheap defensive fix:
```python
key=lambda x: (x.get("file_stem") or "")
```

### 20. `scripts/verify_photo_pipeline.py:57–66` — `_find_block_meta` re-walks `block-library` on every `<img>`
```python
for img in soup.find_all("img"):
    ...
issues.extend(_check_hero_no_crop(soup, project_dir, repo_root))
```
`_check_hero_no_crop` loops hero imgs and calls `_find_block_meta` for each `bid`. `_find_block_meta` itself iterates `library_root.iterdir()` and probes each `cat_dir / block_id / "meta.yaml"`. For a project with 10 hero blocks across a 200+ block library, this is 10 × ~30 stat calls. Easy fix: cache `meta` by `block_id` once at the start of `_check_hero_no_crop`.

### 21. `scripts/wiki/cleanup_broken_links.py:42–44` — non-atomic write to wiki concept files
```python
new_text = WIKILINK_RE.sub(replace, text)
if fixed > 0 and not dry_run:
    path.write_text(new_text, encoding="utf-8")
```
If the script is interrupted, the file is left partially written. Reuse `utils.atomic_write` for consistency with the rest of the package.

### 22. `scripts/wiki/preview.py:30` — `body.strip()[:3000]` silently truncates concepts
This is fine for a preview but should be documented in the rendered HTML (e.g., add "[truncated]" suffix). Currently a user reviewing the preview won't know they're seeing a partial concept.

### 23. `scripts/wiki/hooks/session_end.py:32` and `pre_compact.py:32` — subprocess with no path escaping
```python
subprocess.Popen(
    ["python3", str(FLUSH), "--transcript", transcript, "--cwd", cwd, ...]
)
```
The arguments are passed as a list (good — no shell injection), but `transcript` comes from `payload.get("transcript_path", "")` (untrusted JSON from stdin). The downstream `flush.py` then `Path(args.transcript).read_text(...)`. If a malicious harness payload supplies a path like `/etc/shadow`, `read_text` will error harmlessly, but it does read any path the user has access to. Document this trust boundary, and add an explicit check that the transcript path lives under `~/.claude/projects/` (the only legitimate source).

```python
if not Path(transcript).resolve().is_relative_to(Path.home() / ".claude"):
    return 0
```

### 24. `scripts/wiki/system_compiler.py:139–147` — bootstrap blindly trusts existing concept files
The bootstrap pre-populates cache for any existing concept file regardless of whether the concept actually corresponds to the current source. If a source file was deleted but the concept file remains, the cache key `rel_key` is never added (since `repo_root.glob(...)` won't yield deleted files), so this is fine in that direction. But if a concept was generated from an older version of a source file and the source was edited externally without invalidating cache, the bootstrap rewrites the cache to the **current** source hash, freezing the stale concept in place. The behaviour is "resume bootstrap after crash" per comment, but the side effect on edited-but-not-detected sources is real.

Fix: scope bootstrap to "concept file exists, source hash key missing, AND concept frontmatter shows it was generated from this source recently". Or document this trade-off explicitly.

---

## Minor (nice to have)

### 25. `scripts/wiki/utils.py:21–26` — `slugify` truncates "ё" via the map but loses "ж" → "zh" length info on long Russian titles
Functionally fine, but consider adding a `max_len` parameter (currently `query.py:67` slices `[:60]` externally, magic number leaks across files).

### 26. `scripts/wiki/lint.py:24` — `STALE_DAYS = 30` and `MIN_WORDS = 50` are magic numbers
Move to `scripts/wiki/config.py` so the threshold is discoverable.

### 27. `scripts/wiki/system_compiler.py:60–67` — `STATUS_EMOJI` for stages exists in `project_graph_compiler.py:116–122` too. Duplicated definition.
Move to `config.py` or a small `presentation.py`.

### 28. `scripts/wiki/compile.py:70–96` — import-inside-branch pattern is fine but suspiciously asymmetric
`Path` is imported inside both branches; pull it to the top. Cosmetic.

### 29. `scripts/wiki/preview.py:42` — `defaultdict(list)` is built and then `dict(groups)` is passed to the template
Just pass the defaultdict — Jinja iterates it the same way. Net cost: one extra dict copy on every preview.

### 30. `scripts/verify_visual_qa.py:20` — substring "CRITICAL" check is fragile
A concept body that mentions "### CRITICAL paths" in a positive sentence would false-positive. Use a structured marker (e.g., parse a frontmatter `critical_count: 0`). The script is small enough that this is a real concern.

### 31. `scripts/wiki/sdk_client.py:67` — `generate()` strips content but loses leading frontmatter `---`
`.strip()` will remove leading newlines before `---\n` if the SDK puts whitespace in front. Later `parse_frontmatter` requires `text.startswith("---\n")` (utils.py:35). On rare SDK outputs this drops the meta. Use `.strip("\n").strip()` or, better, leave content alone and only check `if not response.content.strip(): raise SDKError(...)`.

### 32. `scripts/wiki/conversations_compiler.py:48` — `meta.get("name") or "concept"` silently merges all unnamed chunks into one file
If the SDK returns 3 unnamed concepts in one batch, they all write to `concepts/concept.md` and the last one wins. Append an index suffix instead.

### 33. `scripts/wiki/flush.py:71` — mutable default-ish: `memory_dir: Path = None` then immediately reassigned. Use `Optional[Path] = None` and type-check properly.

### 34. `scripts/wizard-check-materials.py:124` — reads full `index.yaml` into memory to find one non-empty non-comment line
Fine for small files but could short-circuit by streaming `with open(...) as f: for line in f:`.

### 35. `scripts/wiki/hash_cache.py` — no test for atomic write of cache
`save_cache` uses plain `cache_path.write_text(...)`, not `utils.atomic_write`. If interrupted mid-write, the cache becomes corrupted JSON (which `load_cache` then silently discards per issue #17). Fix: use `utils.atomic_write` here too.

### 36. `scripts/wiki/parsers/state_yaml.py:7` — no exception handling for malformed YAML
`yaml.safe_load(...)` can raise `yaml.YAMLError`. The caller (`project_graph_compiler`) doesn't catch it. A malformed `.landing-state.yaml` will crash the whole wiki compile rather than producing a useful error.

### 37. `scripts/wiki/parsers/composed_html.py` — reads `composed.html` synchronously and parses with `html.parser`. For >1MB composed files this could be slow. Consider `lxml` for production.

---

## Positive (keep this)

- **`scripts/wiki/utils.py:atomic_write`** — proper temp-file-+-rename pattern. Used consistently across the codebase. Good defensive design.
- **`scripts/wiki/hash_cache.py`** — clean, focused module. Right size, right responsibilities. Just needs the bug fixes above.
- **`scripts/wiki/_build_index` stub replacing SDK** (`system_compiler.py:71–107` and `project_graph_compiler.py:125–172`) — excellent decision documented in the docstrings ("SDK для index выдавал мусор"). Trading determinism + zero tokens for slightly less polished output is exactly the right call.
- **`scripts/wiki/parsers/`** — small, single-purpose modules, no over-abstraction. Good shape.
- **`scripts/wiki/sdk_client.py`** — `_sdk_query` separated from `generate` makes mocking trivial in tests. Right factoring.
- **`scripts/verify_photo_pipeline.py`** — domain logic (HERO_RATIO_TOLERANCE, three resolution strategies for hero images) is well-commented and clearly traces back to PR-K hard gate requirements. The error messages tell the user exactly what to fix.
- **`scripts/wizard-check-materials.py`** — clean JSON contract, neat status taxonomy (`pass`/`warn`/`fail`). Exit code maps to "agent can continue" correctly.
- **`scripts/wiki/compile.py`** — readable CLI dispatcher, late imports keep startup fast for each branch.
- **Source-mode pattern in `config.py`** — declarative `SYSTEM_SOURCES` list is much easier to extend than a switch statement. Good.

---

## Token-leak priority ranking (top 5 to fix first)

1. **`system_compiler.py:197`** — remove per-iteration `save_cache` (cheap; ~10x faster cold builds).
2. **`system_compiler.py:179–183`** — negative-cache SDK failures so the same broken file doesn't re-call SDK on every hook trigger.
3. **`lint.py:121–139`** — add cache for `--llm-check` keyed on input hash. This is the single biggest per-invocation token cost.
4. **`sdk_client.py:52`** — `max_turns=50` → `max_turns=1`. Insurance against runaway.
5. **`query.py`** — add Q&A cache. Repeat questions cost nothing.

After those 5: `system_compiler.py` bootstrap merge (#1), and `lint.py` double-read fix (#6). Together these should cut the post-commit-hook wall-time and token cost dramatically.

---

## Verdict
**Request Changes** — issues #1, #2, #3, #5, #7 are token-leak bugs that match the user's stated top priority. Issues #4, #16, #17, #23 are correctness/safety. The rest can land incrementally.
