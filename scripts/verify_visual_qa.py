#!/usr/bin/env python3
"""Проверяет наличие visual-qa-report.md и отсутствие critical issues.

Exit 0 — отчёт есть и нет critical
Exit 1 — есть critical
Exit 2 — отчёт не создан (visual-qa никогда не запускался)
"""
import sys
from pathlib import Path


def main(project: Path) -> int:
    report = project / "10_QA" / "visual-qa-report.md"
    if not report.exists():
        print(f"⚠ Visual QA report не создан. Запусти: /landing-qa {project.name}", file=sys.stderr)
        return 2

    text = report.read_text(encoding="utf-8")
    # Простой парсинг — ищем строку "CRITICAL"
    if "### CRITICAL" in text or "CRITICAL (" in text:
        print(f"❌ В visual-qa-report.md есть critical issues", file=sys.stderr)
        return 1

    print(f"✅ Visual QA: critical issues нет")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: verify_visual_qa.py <project>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
