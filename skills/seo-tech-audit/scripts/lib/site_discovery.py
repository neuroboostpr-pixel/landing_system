"""Discover hosts to audit from .landing-state.yaml."""
from pathlib import Path
import yaml


def discover_hosts(state_path: Path, filter_host: str | None = None) -> list[str]:
    """Return list of https://<host> URLs to audit.

    - multisite=true → primary_domain + each segment.host
    - multisite=false (or missing) → only primary_domain
    - filter_host → return only matching host (with leading https://); raise ValueError if unknown
    """
    state_path = Path(state_path)
    if not state_path.exists():
        raise FileNotFoundError(f"state file not found: {state_path}")

    data = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}

    # Support two schemas:
    #   new:  project: {primary_domain: "...", slug: "..."}
    #   old:  project: "slug"  (primary_domain at top level or absent)
    project_val = data.get("project")
    if isinstance(project_val, dict):
        primary = (project_val.get("primary_domain") or "").strip()
    else:
        primary = (data.get("primary_domain") or "").strip()

    if not primary:
        raise ValueError(
            f"primary_domain missing in {state_path}. "
            "Use --url <https://your-domain.com> to audit directly."
        )

    is_multisite = bool(data.get("multisite"))
    hosts = [primary]
    if is_multisite:
        for seg in data.get("audience_segments") or []:
            host = (seg.get("host") or "").strip()
            if host and host not in hosts:
                hosts.append(host)

    if filter_host:
        matched = [h for h in hosts if h == filter_host]
        if not matched:
            raise ValueError(f"host {filter_host!r} not found in state. Known: {hosts}")
        hosts = matched

    return [f"https://{h}" for h in hosts]
