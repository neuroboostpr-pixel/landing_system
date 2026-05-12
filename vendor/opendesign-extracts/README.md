# OpenDesign Extracts

Copy-only extraction. We do NOT vendor the full repo or use git-submodules.

## How to refresh

1. Clone OpenDesign locally: `git clone https://github.com/nexu-io/open-design /tmp/od`
2. Note the commit hash: `git -C /tmp/od rev-parse HEAD`
3. Copy needed files (see `ATTRIBUTION.md` table) with header comment:
   ```
   <!-- Source: github.com/nexu-io/open-design @ <commit-hash> | Licensed: Apache-2.0 -->
   ```
4. Update `ATTRIBUTION.md` `Pinned commit` field.
5. Commit.

## Do not

- Edit copied files. If a file needs changes — fork it into the target location (e.g. `block-library/`) with adapted comment header.
- Add upstream dependencies. Each extract must be standalone (no imports from siblings unless documented).
