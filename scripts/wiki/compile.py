# scripts/wiki/compile.py
"""Wiki compiler CLI.

Три режима компиляции:
  --source-mode=system          компилит landing-system в landing-system/wiki/
  --source-mode=project-graph   компилит артефакты проекта в <project>/wiki/
                                требует --project=<slug>
  --source-mode=conversations   компилит daily logs сессий (coleam00 default)
                                требует --project=<slug>

В PR-F.1 — только скелет. Логика добавляется в PR-F.2 (system),
PR-F.3 (project-graph), PR-F.4 (conversations).
"""
import argparse
import sys

from scripts.wiki import config


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m scripts.wiki.compile",
        description="Wiki compiler — преобразует исходники в структурированную wiki.",
    )
    parser.add_argument(
        "--source-mode",
        required=True,
        choices=config.SOURCE_MODES,
        help="Что компилируем: system / project-graph / conversations",
    )
    parser.add_argument(
        "--project",
        help="Slug проекта (для project-graph и conversations)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Печатает план без записи файлов",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.source_mode in ("project-graph", "conversations") and not args.project:
        print(
            f"ERROR: --source-mode={args.source_mode} требует --project=<slug>",
            file=sys.stderr,
        )
        return 2

    if args.source_mode == "system":
        from scripts.wiki import system_compiler
        result = system_compiler.compile_system(
            repo_root=config.REPO_ROOT,
            wiki_dir=config.WIKI_DIR,
            sources=config.SYSTEM_SOURCES,
            dry_run=args.dry_run,
        )
        print(f"Compiled: {len(result['compiled'])}")
        print(f"Skipped: {len(result['skipped'])}")
        if result["errors"]:
            print(f"Errors: {len(result['errors'])}")
            for e in result["errors"]:
                print(f"  ! {e}", file=sys.stderr)
            return 1
        return 0

    if args.source_mode == "project-graph":
        from pathlib import Path
        from scripts.wiki import project_graph_compiler
        project_root = Path.home() / "Lendings" / args.project
        if not project_root.exists():
            print(f"ERROR: проект не найден: {project_root}", file=sys.stderr)
            return 2
        try:
            result = project_graph_compiler.compile_project(project_root=project_root)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        print(f"Project: {args.project}")
        print(f"Current stage: {result['current_stage']}")
        print(f"Wiki updated: {project_root / 'wiki'}")
        return 0

    if args.source_mode == "conversations":
        print(f"[PR-F.1] conversations mode для {args.project} (логика в PR-F.4, not implemented).")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
