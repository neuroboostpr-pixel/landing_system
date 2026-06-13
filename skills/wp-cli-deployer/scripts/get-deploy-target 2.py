#!/usr/bin/env python3
# skills/wp-cli-deployer/scripts/get-deploy-target.py
# Read deploy-targets.yaml and print shell exports for the requested env.
# Usage: python get-deploy-target.py <deploy-targets.yaml> <staging|prod>
# Output:  BEGET_USER=...  BEGET_HOST=...  BEGET_PATH=...  (one per line, eval-safe)
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed", file=sys.stderr)
    sys.exit(1)

REQUIRED_KEYS = ("beget_user", "beget_host", "beget_path")


def get_target(targets_path: str, env: str) -> dict:
    """Return target dict for the given env. Raises SystemExit on error."""
    path = Path(targets_path)
    if not path.is_file():
        print(f"ERROR: deploy-targets.yaml not found: {targets_path}", file=sys.stderr)
        sys.exit(1)

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"ERROR: invalid YAML: {exc}", file=sys.stderr)
        sys.exit(1)

    if env not in data:
        available = ", ".join(data.keys()) if data else "(none)"
        print(f"ERROR: env '{env}' not found in deploy-targets.yaml. Available: {available}", file=sys.stderr)
        sys.exit(1)

    target = data[env]
    missing = [k for k in REQUIRED_KEYS if not target.get(k)]
    if missing:
        print(f"ERROR: env '{env}' missing required keys: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    return {k: str(target[k]) for k in REQUIRED_KEYS}


def format_env_exports(target: dict) -> list:
    """Return list of shell export lines for eval."""
    mapping = {
        "beget_user": "BEGET_USER",
        "beget_host": "BEGET_HOST",
        "beget_path": "BEGET_PATH",
    }
    return [f"{mapping[k]}={v!r}" for k, v in target.items()]


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: get-deploy-target.py <deploy-targets.yaml> <env>", file=sys.stderr)
        return 1
    target = get_target(sys.argv[1], sys.argv[2])
    for line in format_env_exports(target):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
