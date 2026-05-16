#!/usr/bin/env python3
"""Главный цикл Visual QA: screenshot → review → fix → repeat.

Использование:
  visual-qa-loop.py <project> [--strict] [--iterate] [--max-iterations 3]

Output:
  <project>/10_QA/visual-qa-report.md
  <project>/10_QA/screenshots/iter-N/{desktop,mobile}.png
  <project>/10_QA/screenshots/iter-N/{desktop,mobile}-review.json
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TAKE_SCREENSHOTS = SCRIPT_DIR / "take-screenshots.py"
CODEX_REVIEW = SCRIPT_DIR / "codex-review-screenshot.sh"
APPLY_FIX = SCRIPT_DIR / "apply-fix.py"


def take_shots(html: Path, out_dir: Path) -> dict[str, Path]:
    """Wrapper вокруг take-screenshots.py."""
    out_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["python3", str(TAKE_SCREENSHOTS), str(html), "--out", str(out_dir)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"take-screenshots failed: {result.stderr}")
    return {
        "desktop": out_dir / "desktop.png",
        "mobile": out_dir / "mobile.png",
    }


def review_screenshot(png: Path) -> dict:
    """Wrapper вокруг codex-review-screenshot.sh."""
    result = subprocess.run(
        ["bash", str(CODEX_REVIEW), str(png)],
        capture_output=True, text=True, timeout=180,
    )
    if result.returncode != 0:
        return {"issues": [], "summary": "ERROR", "error": result.stderr}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return {"issues": [], "summary": "PARSE_ERROR", "error": str(e)}


def apply_fix(html: Path, issue: dict) -> bool:
    """Wrapper вокруг apply-fix.py. Returns True if applied."""
    result = subprocess.run(
        ["python3", str(APPLY_FIX), str(html), "--issue", json.dumps(issue)],
        capture_output=True, text=True, timeout=60,
    )
    return result.returncode == 0


def iterate(project: Path, html: Path, max_iter: int, do_fix: bool) -> dict:
    qa_dir = project / "10_QA"
    qa_dir.mkdir(parents=True, exist_ok=True)
    history = []

    for i in range(1, max_iter + 1):
        iter_dir = qa_dir / "screenshots" / f"iter-{i}"
        shots = take_shots(html, iter_dir)
        iter_record = {"iteration": i, "screenshots": {}, "issues": []}

        for name, png in shots.items():
            review = review_screenshot(png)
            review_path = iter_dir / f"{name}-review.json"
            review_path.write_text(json.dumps(review, indent=2, ensure_ascii=False))
            iter_record["screenshots"][name] = str(png)
            iter_record["issues"].extend(review.get("issues", []))

        critical = [i for i in iter_record["issues"] if i.get("severity") == "critical"]
        history.append(iter_record)

        if not critical:
            break
        if not do_fix:
            break

        # Auto-fix
        for issue in critical:
            applied = apply_fix(html, issue)
            issue["fix_applied"] = applied

    return {"history": history, "final_iter": history[-1] if history else None}


def render_report(result: dict, out_path: Path) -> None:
    history = result["history"]
    final = result["final_iter"]
    all_issues = final["issues"] if final else []

    lines = [
        f"# Visual QA Report",
        f"",
        f"**Дата:** {datetime.now().isoformat()}",
        f"**Итераций:** {len(history)}",
        f"",
        f"## Финальное состояние",
        f"",
    ]
    for severity in ("critical", "warning", "info"):
        items = [i for i in all_issues if i.get("severity") == severity]
        if not items:
            continue
        lines.append(f"### {severity.upper()} ({len(items)})")
        for it in items:
            lines.append(f"- **[{it.get('type', '?')}]** {it.get('description', '')}")
            sel = it.get("selector")
            if sel:
                lines.append(f"  - selector: `{sel}`")
            hint = it.get("fix_hint")
            if hint:
                lines.append(f"  - fix_hint: {hint}")
        lines.append("")

    if not all_issues:
        lines.append("✅ Все проверки пройдены, видимых проблем нет.")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="Project root directory")
    parser.add_argument("--strict", action="store_true", help="Exit 1 если critical issues")
    parser.add_argument("--iterate", action="store_true", help="Запустить auto-fix цикл")
    parser.add_argument("--max-iterations", type=int, default=3)
    args = parser.parse_args()

    project = Path(args.project).resolve()
    composed = project / "07b_COMPOSED" / "composed.html"
    if not composed.exists():
        composed = project / "07f_COMPOSED_FINAL" / "composed.html"
    if not composed.exists():
        print(f"ERROR: composed.html не найден в {project}", file=sys.stderr)
        return 2

    print(f"🔍 Visual QA для {composed}")
    result = iterate(project, composed, args.max_iterations, args.iterate)

    report_path = project / "10_QA" / "visual-qa-report.md"
    render_report(result, report_path)
    print(f"📄 Отчёт: {report_path}")

    final = result["final_iter"]
    critical_count = len([i for i in final["issues"] if i.get("severity") == "critical"]) if final else 0

    if args.strict and critical_count > 0:
        print(f"❌ Strict mode: {critical_count} critical issues", file=sys.stderr)
        return 1
    print(f"✅ Visual QA завершён ({critical_count} critical осталось)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
