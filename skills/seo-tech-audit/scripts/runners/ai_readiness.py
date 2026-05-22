"""AI readiness checks (AI1-AI3)."""
import json
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from lib.http_client import fetch

# Types that satisfy AI2 — at least one must be present in JSON-LD blocks
AI2_TYPES = {"Organization", "LocalBusiness", "Product", "FAQPage"}

# Threshold for AI3 sufficient render — body text (after stripping script/style)
AI3_MIN_BODY_BYTES = 1024


def _result(check_id, passed, evidence="", **extra):
    return {"id": check_id, "passed": passed, "evidence": evidence, **extra}


def check_llms_txt(url):
    """AI1: /llms.txt valid per llmstxt.org spec.

    Pass: 200 OK AND content has `# <h1>` AND at least one `[label](url)` link.
    """
    target = urljoin(url, "/llms.txt")
    try:
        resp = fetch(target)
    except Exception as e:
        return _result("AI1", False, f"fetch_error: {e.__class__.__name__}")
    if resp.status_code != 200:
        return _result("AI1", False, f"status={resp.status_code}")
    text = resp.text or ""
    has_h1 = bool(re.search(r"^#\s+\S+", text, re.MULTILINE))
    has_link = bool(re.search(r"\[[^\]]+\]\([^)]+\)", text))
    passed = has_h1 and has_link
    return _result(
        "AI1", passed,
        f"size={len(text)}B has_h1={has_h1} has_link={has_link}"
    )


def check_schema_org_types(html, url):
    """AI2: at least one JSON-LD block with @type in AI2_TYPES."""
    soup = BeautifulSoup(html, "lxml")
    blocks = soup.find_all("script", attrs={"type": "application/ld+json"})
    found_types = []
    for b in blocks:
        try:
            raw = (b.get_text("") or "").strip().lstrip("﻿")
            if not raw:
                continue
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        # JSON-LD can be a single object or a list
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            t = item.get("@type")
            if isinstance(t, list):
                found_types.extend(t)
            elif isinstance(t, str):
                found_types.append(t)
    matched = [t for t in found_types if t in AI2_TYPES]
    return _result(
        "AI2", bool(matched),
        f"found_types={found_types} matched={matched}"
    )


def check_no_js_render(html, url):
    """AI3: body has ≥1KB of text content (or noscript fallback)."""
    soup = BeautifulSoup(html, "lxml")
    # Strip script/style — those don't count as visible content
    for tag in soup(["script", "style"]):
        tag.decompose()
    body = soup.body
    if body is None:
        return _result("AI3", False, "no_body")
    text = body.get_text(" ", strip=True)
    size = len(text.encode("utf-8"))
    passed = size >= AI3_MIN_BODY_BYTES
    return _result("AI3", passed, f"body_text={size}B threshold={AI3_MIN_BODY_BYTES}B")


def run_all(url, html):
    """Run AI1+AI2+AI3. html is already-fetched body for AI2/AI3."""
    return [
        check_llms_txt(url),
        check_schema_org_types(html, url),
        check_no_js_render(html, url),
    ]
