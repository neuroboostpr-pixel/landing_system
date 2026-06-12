#!/usr/bin/env python3
# skills/seo-optimizer/scripts/generate-sitemap.py
# Generate a static sitemap.xml for the main page + legal pages.
# Usage: python generate-sitemap.py <base_url> <output_path> [--legal /policy /consent ...]
import argparse
import sys
from datetime import date
from urllib.parse import urljoin
import xml.etree.ElementTree as ET


SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def generate_sitemap(base_url: str, legal_paths: list, output_path: str) -> int:
    """Write sitemap.xml to output_path. Returns 0 on success, 1 on error."""
    if not base_url.endswith("/"):
        base_url += "/"

    seen = set()
    urls = []

    def add(path: str, priority: str, changefreq: str, add_trailing: bool = False) -> None:
        if not path.strip("/"):
            loc = base_url
        else:
            loc = base_url.rstrip("/") + "/" + path.lstrip("/")
            if add_trailing and not loc.endswith("/"):
                loc += "/"
        if loc in seen:
            return
        seen.add(loc)
        urls.append({"loc": loc, "priority": priority, "changefreq": changefreq})

    add("/", "1.0", "weekly")
    for path in legal_paths:
        add(path, "0.3", "yearly", add_trailing=False)

    ET.register_namespace("", SITEMAP_NS)
    root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    today = date.today().isoformat()
    for entry in urls:
        url_el = ET.SubElement(root, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(url_el, f"{{{SITEMAP_NS}}}loc").text = entry["loc"]
        ET.SubElement(url_el, f"{{{SITEMAP_NS}}}lastmod").text = today
        ET.SubElement(url_el, f"{{{SITEMAP_NS}}}changefreq").text = entry["changefreq"]
        ET.SubElement(url_el, f"{{{SITEMAP_NS}}}priority").text = entry["priority"]

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    try:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            tree.write(fh, encoding="unicode", xml_declaration=False)
        return 0
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate sitemap.xml")
    parser.add_argument("base_url", help="Base URL of the site (e.g. https://example.com)")
    parser.add_argument("output", help="Output file path for sitemap.xml")
    parser.add_argument(
        "--legal",
        nargs="*",
        default=["/policy", "/consent"],
        help="Legal page paths to include (default: /policy /consent)",
    )
    args = parser.parse_args()
    return generate_sitemap(args.base_url, args.legal, args.output)


if __name__ == "__main__":
    sys.exit(main())
