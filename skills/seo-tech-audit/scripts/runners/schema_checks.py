"""Schema/microdata checks (S1-S5)."""
import json

from bs4 import BeautifulSoup

REQUIRED_OG = {"og:title", "og:description", "og:image", "og:type", "og:url"}
REQUIRED_TWITTER = {"twitter:card", "twitter:title", "twitter:image"}


def _result(check_id: str, passed: bool, evidence: str = "", **extra) -> dict:
    return {"id": check_id, "passed": passed, "evidence": evidence, **extra}


def check_schema(html: str, url: str) -> list[dict]:
    """Run 5 schema checks on HTML."""
    soup = BeautifulSoup(html, "lxml")
    out: list[dict] = []

    # S1: OG — all 5 required
    og_props = {m.get("property", ""): (m.get("content", "") or "").strip()
                for m in soup.find_all("meta", attrs={"property": True})}
    present = {k for k in REQUIRED_OG if og_props.get(k)}
    missing = REQUIRED_OG - present
    out.append(_result("S1", not missing,
                       f"present={len(present)}/5 missing={sorted(missing) if missing else 'none'}",
                       og_props=og_props))

    # S2: og:image valid (URL 200, >=1200x630) — without HTTP, verify URL format only
    og_image_url = og_props.get("og:image", "")
    out.append(_result("S2", bool(og_image_url) and og_image_url.startswith(("http://", "https://")),
                       f'url="{og_image_url}"'))

    # S3: Twitter Card — at least card/title/image
    tw_names = {m.get("name", ""): (m.get("content", "") or "").strip()
                for m in soup.find_all("meta", attrs={"name": True})
                if (m.get("name", "") or "").startswith("twitter:")}
    tw_present = {k for k in REQUIRED_TWITTER if tw_names.get(k)}
    tw_missing = REQUIRED_TWITTER - tw_present
    out.append(_result("S3", not tw_missing,
                       f"present={len(tw_present)}/3 missing={sorted(tw_missing) if tw_missing else 'none'}"))

    # S4: JSON-LD present and parses
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    parsed_count = 0
    parse_errors = []
    for s in scripts:
        try:
            json.loads(s.get_text(""))
            parsed_count += 1
        except json.JSONDecodeError as e:
            parse_errors.append(str(e)[:80])
    out.append(_result("S4", parsed_count > 0,
                       f"valid_json_ld={parsed_count}/{len(scripts)} errors={parse_errors[:2]}"))

    # S5: Favicon present (any size)
    favicon = soup.find("link", attrs={"rel": lambda r: r and (
        ("icon" in r.lower()) if isinstance(r, str) else any("icon" in x.lower() for x in (r or []))
    )})
    out.append(_result("S5", bool(favicon),
                       f"href={(favicon.get('href','') if favicon else '')}"))

    return out
