"""Web scraper — pure-Python, no API keys.

Two strategies:
1. extract_static() — fast, uses trafilatura (Mozilla Readability port).
   Good for blogs, news, product pages with server-rendered HTML.
2. extract_dynamic() — uses Playwright headless Chromium.
   Good for SPAs (Я.Карты, 2GIS, Otzovik) where content is JS-loaded.
3. get_page_fonts() — uses Playwright + DOM CSS inspection to read the
   actual computed font-family used on a page. More accurate than image
   recognition for web references.

All three are deterministic, free, and don't require API keys.
"""
from typing import List, Dict, Any, Optional
import trafilatura


class ScrapeError(RuntimeError):
    pass


def extract_static(url: Optional[str] = None, html: Optional[str] = None) -> Dict[str, Any]:
    """Extract clean text+metadata from a static HTML page.

    Pass either `url` (will fetch) or `html` (already fetched).
    Returns {"text": str, "title": str, "raw_html": str}.
    """
    if url is None and html is None:
        raise ValueError("Pass either url= or html=")
    if url and not html:
        html = trafilatura.fetch_url(url)
        if html is None:
            raise ScrapeError(f"failed to fetch {url}")

    text = trafilatura.extract(html, include_comments=False, include_tables=True) or ""

    # Prefer <title> tag from raw HTML over trafilatura's h1 fallback (trafilatura 2.x
    # falls back to first <h1> when <title> is absent — risky for review pages).
    title = ""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
    except Exception:
        pass

    # Fall back to trafilatura metadata if no <title> found
    if not title:
        metadata = trafilatura.extract_metadata(html)
        if metadata and metadata.title:
            title = metadata.title

    return {"text": text, "title": title, "raw_html": html}


def _launch_chromium():
    """Lazy import + launch. Returns (playwright_instance, browser)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise ScrapeError(f"playwright not installed: {e}") from e
    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        return p, browser
    except Exception as e:
        raise ScrapeError(f"chromium launch failed: {e}") from e


def extract_dynamic(url: str, wait_for: Optional[str] = None,
                    timeout_ms: int = 30000) -> Dict[str, Any]:
    """Render `url` in headless Chromium and extract text via trafilatura on
    the rendered DOM.

    Args:
      url: page to load
      wait_for: optional CSS selector to wait for before extraction
        (e.g. ".review-card" for Я.Карты)
      timeout_ms: navigation timeout

    Returns same shape as extract_static.
    """
    p, browser = _launch_chromium()
    try:
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 14) AppleWebKit/605"
        )
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        if wait_for:
            page.wait_for_selector(wait_for, timeout=timeout_ms)
        rendered_html = page.content()
        return extract_static(html=rendered_html)
    finally:
        browser.close()
        p.stop()


def get_page_fonts(url: str, timeout_ms: int = 30000) -> List[str]:
    """Open `url` and return distinct font-family strings used on the page.

    Reads computed style of every visible element and returns unique
    font-family declarations sorted by frequency. This is more accurate than
    image-based detection for web references.
    """
    p, browser = _launch_chromium()
    try:
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        fonts = page.evaluate("""
        () => {
          const counts = new Map();
          document.querySelectorAll('*').forEach(el => {
            const cs = window.getComputedStyle(el);
            const ff = cs.fontFamily;
            if (ff && el.offsetParent !== null) {
              counts.set(ff, (counts.get(ff) || 0) + 1);
            }
          });
          return Array.from(counts.entries())
            .sort((a, b) => b[1] - a[1])
            .map(([family, _count]) => family);
        }
        """)
        return list(fonts)
    finally:
        browser.close()
        p.stop()
