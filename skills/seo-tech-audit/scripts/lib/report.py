"""Build site + aggregate reports; render Markdown."""
from datetime import datetime


def build_site_report(host: str, results: list[dict], thresholds: dict) -> dict:
    """Aggregate one site's results with hard/soft split."""
    hard_total = hard_passed = soft_total = soft_passed = 0
    fails: list[dict] = []
    for r in results:
        check_id = r["id"]
        threshold = thresholds.get(check_id, {})
        is_hard = bool(threshold.get("hard", False))
        if is_hard:
            hard_total += 1
            if r["passed"]:
                hard_passed += 1
            else:
                fails.append({**r, "desc": threshold.get("desc", ""), "severity": "hard"})
        else:
            soft_total += 1
            if r["passed"]:
                soft_passed += 1
            elif not r["passed"]:
                fails.append({**r, "desc": threshold.get("desc", ""), "severity": "soft"})
    return {
        "host": host,
        "checked_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "all_total": len(results),
        "hard_total": hard_total,
        "hard_passed": hard_passed,
        "soft_total": soft_total,
        "soft_passed": soft_passed,
        "passed": hard_passed == hard_total,
        "results": results,
        "failures": fails,
    }


def build_aggregate_report(site_reports: list[dict]) -> dict:
    """Combine per-site reports into an aggregate."""
    total = len(site_reports)
    passed = sum(1 for s in site_reports if s["passed"])
    return {
        "checked_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "total_sites": total,
        "sites_passed": passed,
        "overall_passed": passed == total,
        "sites": site_reports,
    }


def render_markdown(site_reports: list[dict]) -> str:
    """Render Markdown report covering one OR many sites."""
    lines: list[str] = []
    lines.append("# Audit Report")
    lines.append("")
    lines.append(f"**Date:** {datetime.utcnow().isoformat(timespec='seconds')}Z")
    lines.append("")

    if len(site_reports) > 1:
        agg = build_aggregate_report(site_reports)
        status = "✅ PASS" if agg["overall_passed"] else "❌ FAIL"
        lines.append(f"**Overall:** {status} ({agg['sites_passed']}/{agg['total_sites']} sites passed)")
        lines.append("")
        lines.append("## Сводная таблица")
        lines.append("")
        lines.append("| Host | Status | Hard gates | Soft gates |")
        lines.append("|---|---|---|---|")
        for s in site_reports:
            icon = "✅" if s["passed"] else "❌"
            lines.append(f"| {s['host']} | {icon} | {s['hard_passed']}/{s['hard_total']} | {s['soft_passed']}/{s['soft_total']} |")
        lines.append("")

    for s in site_reports:
        status = "✅ PASS" if s["passed"] else "❌ FAIL"
        lines.append(f"## {s['host']} — {status}")
        lines.append("")
        lines.append(f"- Hard gates: **{s['hard_passed']}/{s['hard_total']}**")
        lines.append(f"- Soft gates: {s['soft_passed']}/{s['soft_total']}")
        lines.append("")
        if s["failures"]:
            lines.append("### Failed checks")
            lines.append("")
            lines.append("| ID | Severity | Desc | Evidence |")
            lines.append("|---|---|---|---|")
            for f in s["failures"]:
                sev_icon = "🔴" if f["severity"] == "hard" else "🟡"
                ev = (f.get("evidence", "") or "")[:120].replace("|", "\\|").replace("\n", " ")
                lines.append(f"| {f['id']} | {sev_icon} {f['severity']} | {f.get('desc', '')} | {ev} |")
            lines.append("")
        else:
            lines.append("Все проверки пройдены.")
            lines.append("")

    return "\n".join(lines) + "\n"
