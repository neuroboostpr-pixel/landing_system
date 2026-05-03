#!/usr/bin/env python3
"""Maintain 03_РЕФЕРЕНСЫ/index.yaml — references with statuses.

CLI:
  python3 index.py add <refs-dir> <ref> [--type url|file] [--status candidate|approved|rejected]
  python3 index.py update <refs-dir> <ref-id> --status <new>
  python3 index.py list <refs-dir> [--status <filter>]
  python3 index.py show <refs-dir> <ref-id>
  python3 index.py remove <refs-dir> <ref-id>
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


VALID_STATUSES = {"candidate", "approved", "rejected", "needs_user_review"}


def _load(refs_dir: Path) -> Dict[str, Any]:
    idx = refs_dir / "index.yaml"
    if not idx.exists():
        return {"references": []}
    return yaml.safe_load(idx.read_text(encoding="utf-8")) or {"references": []}


def _save(refs_dir: Path, data: Dict[str, Any]) -> None:
    idx = refs_dir / "index.yaml"
    idx.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _ref_id(ref: str) -> str:
    return hashlib.sha1(ref.encode("utf-8")).hexdigest()[:8]


def add_ref(refs_dir: str, ref: str, ref_type: str = "url", status: str = "candidate") -> Dict[str, Any]:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {status}")
    refs = Path(refs_dir)
    refs.mkdir(parents=True, exist_ok=True)
    data = _load(refs)

    new_id = _ref_id(ref)

    # Check if already exists — return existing entry unchanged
    for existing in data["references"]:
        if existing["id"] == new_id:
            return existing  # Return what's actually in the file

    # New entry
    entry = {
        "id": new_id,
        "value": ref,
        "type": ref_type,
        "status": status,
        "added_at": datetime.now(timezone.utc).isoformat(),
    }
    data["references"].append(entry)
    _save(refs, data)
    return entry


def update_status(refs_dir: str, ref_id: str, new_status: str) -> None:
    if new_status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {new_status}")
    refs = Path(refs_dir)
    data = _load(refs)
    for r in data["references"]:
        if r["id"] == ref_id:
            r["status"] = new_status
            r["updated_at"] = datetime.now(timezone.utc).isoformat()
            _save(refs, data)
            return
    raise KeyError(f"ref {ref_id} not found")


def list_refs(refs_dir: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    refs = Path(refs_dir)
    data = _load(refs)
    if status:
        return [r for r in data["references"] if r["status"] == status]
    return data["references"]


def show_ref(refs_dir: str, ref_id: str) -> Dict[str, Any]:
    refs = Path(refs_dir)
    data = _load(refs)
    for r in data["references"]:
        if r["id"] == ref_id:
            return r
    raise KeyError(f"ref {ref_id} not found")


def remove_ref(refs_dir: str, ref_id: str) -> None:
    refs = Path(refs_dir)
    data = _load(refs)
    original_count = len(data["references"])
    data["references"] = [r for r in data["references"] if r["id"] != ref_id]
    if len(data["references"]) == original_count:
        raise KeyError(f"ref {ref_id} not found")
    _save(refs, data)


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("add")
    add.add_argument("refs_dir")
    add.add_argument("ref")
    add.add_argument("--type", default="url")
    add.add_argument("--status", default="candidate")

    upd = sub.add_parser("update")
    upd.add_argument("refs_dir")
    upd.add_argument("ref_id")
    upd.add_argument("--status", required=True)

    lst = sub.add_parser("list")
    lst.add_argument("refs_dir")
    lst.add_argument("--status")

    shw = sub.add_parser("show")
    shw.add_argument("refs_dir")
    shw.add_argument("ref_id")

    rem = sub.add_parser("remove")
    rem.add_argument("refs_dir")
    rem.add_argument("ref_id")

    args = p.parse_args(argv[1:])
    try:
        if args.cmd == "add":
            entry = add_ref(args.refs_dir, args.ref, args.type, args.status)
            print(entry["id"])
        elif args.cmd == "update":
            update_status(args.refs_dir, args.ref_id, args.status)
        elif args.cmd == "list":
            for r in list_refs(args.refs_dir, args.status):
                print(f"{r['id']}\t{r['status']}\t{r['value']}")
        elif args.cmd == "show":
            r = show_ref(args.refs_dir, args.ref_id)
            print(json.dumps(r, ensure_ascii=False, indent=2))
        elif args.cmd == "remove":
            remove_ref(args.refs_dir, args.ref_id)
        return 0
    except (ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
