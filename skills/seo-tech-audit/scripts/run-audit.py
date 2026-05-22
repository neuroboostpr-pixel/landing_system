#!/usr/bin/env python3
"""seo-tech-audit CLI orchestrator (E1).

Usage:
    run-audit.py --url <url>                     # single ad-hoc URL
    run-audit.py --project <dir>                 # auto-discover hosts from .landing-state.yaml
    run-audit.py --project <dir> --site <host>   # only one host of a multisite project
    --out <dir>   override output dir (default: <project>/11_QA or ./11_QA)
    --json        suppress Markdown rendering (JSON only)

Exit codes:
    0 = all hard-gates pass on all sites
    1 = at least one hard-gate failed
    2 = system error (project not found, etc.)
"""
import argparse
import json
import sys
from pathlib import Path

# Make `lib.*` and `runners.*` importable
SKILL_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_SCRIPTS))

from lib.http_client import fetch
from lib.report import build_aggregate_report, build_site_report, render_markdown
from lib.site_discovery import discover_hosts
from lib.thresholds import load_thresholds
from runners.html_checks import check_html
from runners.network_checks import run_all as run_network_checks
from runners.schema_checks import check_schema


def audit_one_url(url: str) -> list[dict]:
    """Fetch URL once, run all 3 runner modules."""
    results: list[dict] = []
    try:
        resp = fetch(url)
        html = resp.text
        elapsed_ms = int(resp.elapsed.total_seconds() * 1000) if resp.elapsed else 0
        size = len(resp.content) if resp.content else 0
        results.extend(check_html(html, url,
                                   status_code=resp.status_code,
                                   response_time_ms=elapsed_ms,
                                   content_size_bytes=size))
        results.extend(check_schema(html, url))
    except Exception as e:
        # Network total failure — mark H1 as fail and proceed with network checks
        results.append({"id": "H1", "passed": False, "evidence": f"fetch_error: {e}"})
    # Network checks always run (they hit different endpoints)
    results.extend(run_network_checks(url))
    return results


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="run-audit.py")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--project", help="project root with .landing-state.yaml")
    g.add_argument("--url", help="single ad-hoc URL to audit")
    g.add_argument("--hosts-file", help="text file with URLs, one per line")
    p.add_argument("--site", help="filter: only this host (with --project)")
    p.add_argument("--out", help="output directory (default: <project>/11_QA or ./11_QA)")
    p.add_argument("--json", action="store_true", help="JSON only, skip Markdown")
    args = p.parse_args(argv[1:])

    # Resolve hosts
    if args.hosts_file:
        hosts_path = Path(args.hosts_file)
        if not hosts_path.exists():
            print(f"ERROR: hosts file not found: {hosts_path}", file=sys.stderr)
            return 2
        raw = hosts_path.read_text(encoding="utf-8").splitlines()
        hosts = [line.strip().rstrip("/") for line in raw if line.strip()]
        if not hosts:
            print(f"ERROR: hosts file is empty: {hosts_path}", file=sys.stderr)
            return 2
        out_root = Path(args.out) if args.out else Path("./11_QA")
    elif args.url:
        hosts = [args.url.rstrip("/")]
        out_root = Path(args.out) if args.out else Path("./11_QA")
    else:
        project = Path(args.project)
        state_path = project / ".landing-state.yaml"
        if not state_path.exists():
            print(f"ERROR: state file not found: {state_path}", file=sys.stderr)
            return 2
        try:
            hosts = discover_hosts(state_path, filter_host=args.site)
        except (FileNotFoundError, ValueError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        out_root = Path(args.out) if args.out else (project / "11_QA")

    out_root.mkdir(parents=True, exist_ok=True)
    per_site_dir = out_root / "per-site"
    per_site_dir.mkdir(exist_ok=True)

    # Load thresholds
    thresholds = load_thresholds()

    # Audit each host
    site_reports: list[dict] = []
    for host in hosts:
        print(f"▶ Auditing {host}", flush=True)
        results = audit_one_url(host)
        rep = build_site_report(host, results, thresholds)
        site_reports.append(rep)

        # Per-site JSON + MD
        host_key = host.replace("https://", "").replace("http://", "").rstrip("/")
        (per_site_dir / f"{host_key}.json").write_text(
            json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
        if not args.json:
            single_md = render_markdown([rep])
            (per_site_dir / f"{host_key}.md").write_text(single_md, encoding="utf-8")
        print(f"  {'PASS' if rep['passed'] else 'FAIL'} hard={rep['hard_passed']}/{rep['hard_total']} "
              f"soft={rep['soft_passed']}/{rep['soft_total']}", flush=True)

    # Aggregate
    agg = build_aggregate_report(site_reports)
    (out_root / "audit-report.json").write_text(
        json.dumps(agg, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.json:
        md = render_markdown(site_reports)
        (out_root / "audit-report.md").write_text(md, encoding="utf-8")

    print(f"\n{'PASS' if agg['overall_passed'] else 'FAIL'} "
          f"{agg['sites_passed']}/{agg['total_sites']} sites passed", flush=True)
    print(f"Reports: {out_root}", flush=True)

    return 0 if agg["overall_passed"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
