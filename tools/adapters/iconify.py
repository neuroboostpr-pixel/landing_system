"""Iconify HTTP API — public, no key required."""
from typing import List, Dict, Any
import requests


class IconifyError(RuntimeError):
    pass


def search(query: str, limit: int = 32, prefix: str = "") -> List[Dict[str, Any]]:
    """Search icons across all Iconify icon sets.

    Args:
      query: search term (e.g. "arrow-right", "check")
      limit: max results
      prefix: optional icon set filter (e.g. "lucide", "phosphor")

    Returns list of {"prefix": str, "name": str, "id": str} dicts.
    """
    params = {"query": query, "limit": str(limit)}
    if prefix:
        params["prefixes"] = prefix
    try:
        resp = requests.get("https://api.iconify.design/search", params=params, timeout=10)
    except requests.RequestException as exc:
        raise IconifyError(f"network: {exc}") from exc
    if resp.status_code != 200:
        raise IconifyError(f"HTTP {resp.status_code}")
    payload = resp.json()
    results = []
    for full_id in payload.get("icons", []):
        # full_id format: "prefix:name"
        if ":" in full_id:
            pfx, name = full_id.split(":", 1)
            results.append({"prefix": pfx, "name": name, "id": full_id})
    return results
