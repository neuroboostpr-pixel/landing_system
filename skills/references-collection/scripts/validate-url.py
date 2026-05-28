"""Check whether a reference URL is accessible for content extraction.

CLI: python validate-url.py <url>
Returns exit 0 if accessible, exit 1 if blocked/inaccessible.
"""
import sys
import urllib.request
import urllib.error

KNOWN_BLOCKED_PLATFORMS = [
    "behance.net",
    "instagram.com",
    "tilda.cc",
    "dribbble.com",
    "pinterest.com",
    "figma.com",
]

MIN_CONTENT_LENGTH = 500


def is_known_blocked(url: str) -> bool:
    url_lower = url.lower()
    return any(platform in url_lower for platform in KNOWN_BLOCKED_PLATFORMS)


def check_url_accessible(url: str, timeout: int = 10) -> bool:
    if is_known_blocked(url):
        return False
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; landing-system/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return False
            content = resp.read(MIN_CONTENT_LENGTH * 2)
            return len(content) >= MIN_CONTENT_LENGTH
    except (urllib.error.URLError, OSError, TimeoutError):
        return False


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Usage: validate-url.py <url>", file=sys.stderr)
        return 2
    url = args[0]
    if check_url_accessible(url):
        print(f"OK: {url}")
        return 0
    else:
        blocked_note = " (known blocked platform)" if is_known_blocked(url) else ""
        print(f"BLOCKED: {url}{blocked_note}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
