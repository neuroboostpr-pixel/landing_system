#!/usr/bin/env python3
"""Append stage decisions to <project>/decisions.log.md.

CLI:
  python scripts/log-decisions.py --project <path> --stage 04_brand
  python scripts/log-decisions.py --project <path> --stage 04_brand \
    --decisions-file <project>/.stage-decisions/04_brand.md
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path


LOG_FILENAME = "decisions.log.md"
HEADER = "# Decisions Log\n\nЖурнал самостоятельных решений агентов.\nФиксируется только то, что не было задано в visual-concept.yaml явно.\n\n"


def append_decisions(project: str, stage: str, decisions_file: str | None) -> None:
    project_path = Path(project)
    log_path = project_path / LOG_FILENAME

    # Create log with header if missing
    if not log_path.exists():
        log_path.write_text(HEADER, encoding="utf-8")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if decisions_file and Path(decisions_file).exists():
        content = Path(decisions_file).read_text(encoding="utf-8").strip()
        entry = f"\n## {stage} — {timestamp}\n\n{content}\n"
        Path(decisions_file).unlink()
    else:
        entry = f"\n## {stage} — {timestamp}\n\n_(нет отклонений)_\n"

    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--decisions-file", default=None, dest="decisions_file")
    ns = p.parse_args(args)
    append_decisions(ns.project, ns.stage, ns.decisions_file)
    print(f"OK: logged decisions for {ns.stage}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
