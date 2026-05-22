"""Network/Infra checks (N1-N13). HTTP/SSL/Whois-based."""
import socket
import ssl
import uuid
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

from lib.http_client import fetch, make_session

SECURITY_HEADER_KEYS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def _result(check_id: str, passed: bool, evidence: str = "", **extra) -> dict:
    return {"id": check_id, "passed": passed, "evidence": evidence, **extra}


def check_ssl_valid(url: str) -> dict:
    """N1+N3: SSL valid + ≥7 days to expiry."""
    host = urlparse(url).netloc
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
        not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days = (not_after - datetime.now(timezone.utc)).days
        return _result("N1", days > 0, f"expires_in_days={days}", days=days)
    except Exception as e:
        return _result("N1", False, f"error={e.__class__.__name__}")


def check_ssl_critical(url: str) -> dict:
    """N3 explicit: ≥7 days. Calls check_ssl_valid for days."""
    base = check_ssl_valid(url)
    days = base.get("days", -1)
    return _result("N3", days >= 7, f"expires_in_days={days}")


def check_ssl_soon_warning(url: str) -> dict:
    """N2 (soft): ≥30 days."""
    base = check_ssl_valid(url)
    days = base.get("days", -1)
    return _result("N2", days >= 30, f"expires_in_days={days}")


def check_http_version(url: str) -> dict:
    """N4: HTTP/2 or HTTP/3."""
    try:
        resp = fetch(url, method="HEAD")
        # requests doesn't expose protocol version directly — check via raw
        version = "HTTP/" + str(resp.raw.version / 10) if hasattr(resp.raw, "version") else "HTTP/?"
        # version 11 = HTTP/1.1, 20 = HTTP/2 (rare to get via requests)
        is_modern = "/2" in version or "/3" in version
        return _result("N4", is_modern, f"version={version}")
    except Exception as e:
        return _result("N4", False, f"error={e.__class__.__name__}")


def check_security_headers(url: str) -> dict:
    """N5: ≥3 of 4 security headers."""
    try:
        resp = fetch(url, method="HEAD")
    except Exception as e:
        return _result("N5", False, f"error={e.__class__.__name__}")
    present = [h for h in SECURITY_HEADER_KEYS if h in resp.headers]
    return _result("N5", len(present) >= 3, f"present={len(present)}/4: {present}")


def check_server_header_no_version(url: str) -> dict:
    """N6: Server header doesn't expose version."""
    try:
        resp = fetch(url, method="HEAD")
    except Exception as e:
        return _result("N6", False, f"error={e.__class__.__name__}")
    server = resp.headers.get("Server", "")
    # heuristic: digits in server string = version disclosure
    has_version = any(c.isdigit() for c in server)
    return _result("N6", not has_version, f'server="{server}"')


def check_www_redirect(url: str) -> dict:
    """N7: www/non-www → 301 to canonical (without loop)."""
    parsed = urlparse(url)
    host = parsed.netloc
    if host.startswith("www."):
        other_host = host[4:]
    else:
        other_host = "www." + host
    other_url = parsed._replace(netloc=other_host).geturl()
    try:
        resp = fetch(other_url)
    except Exception as e:
        return _result("N7", False, f"error={e.__class__.__name__}")
    # Should land on canonical (any 200 after redirect is OK)
    final_host = urlparse(resp.url).netloc
    redirected_correctly = (final_host == host and len(resp.history) > 0)
    return _result("N7", redirected_correctly,
                   f"history_len={len(resp.history)} final={final_host}")


def check_robots_txt(url: str) -> dict:
    """N8: robots.txt exists and parses."""
    robots_url = urljoin(url, "/robots.txt")
    try:
        resp = fetch(robots_url)
    except Exception as e:
        return _result("N8", False, f"error={e.__class__.__name__}")
    if resp.status_code != 200:
        return _result("N8", False, f"status={resp.status_code}")
    # minimal validity: contains "User-agent" directive
    valid = "user-agent" in resp.text.lower()
    return _result("N8", valid, f"size={len(resp.text)}B valid={valid}",
                   robots_text=resp.text)


def check_sitemap_xml(url: str, robots_text: str = "") -> dict:
    """N9: sitemap.xml exists, valid XML, referenced in robots.txt."""
    sitemap_url = urljoin(url, "/sitemap.xml")
    try:
        resp = fetch(sitemap_url)
    except Exception as e:
        return _result("N9", False, f"error={e.__class__.__name__}")
    if resp.status_code != 200:
        return _result("N9", False, f"status={resp.status_code}")
    try:
        ET.fromstring(resp.text)
    except ET.ParseError as e:
        return _result("N9", False, f"invalid XML: {e}")
    in_robots = "sitemap" in robots_text.lower() and "sitemap.xml" in robots_text.lower()
    return _result("N9", in_robots,
                   f"valid_xml=true in_robots={in_robots}",
                   in_robots=in_robots)


def check_llms_txt(url: str) -> dict:
    """N10: llms.txt (AI standard)."""
    try:
        resp = fetch(urljoin(url, "/llms.txt"))
    except Exception:
        return _result("N10", False, "fetch error")
    return _result("N10", resp.status_code == 200, f"status={resp.status_code}")


def check_404_status(url: str) -> dict:
    """N11: random /404-test-xyz returns 404 (not soft 200)."""
    test_url = urljoin(url, f"/test-404-{uuid.uuid4().hex[:8]}")
    try:
        resp = fetch(test_url)
    except Exception as e:
        return _result("N11", False, f"error={e.__class__.__name__}")
    return _result("N11", resp.status_code == 404, f"status={resp.status_code}")


def check_404_has_nav(url: str) -> dict:
    """N12: 404 page contains navigation (link to home)."""
    test_url = urljoin(url, f"/test-404-{uuid.uuid4().hex[:8]}")
    try:
        resp = fetch(test_url)
    except Exception:
        return _result("N12", False, "fetch error")
    has_home_link = bool(resp.text) and ('href="/"' in resp.text or "href='/'" in resp.text)
    return _result("N12", has_home_link, f"has_home_link={has_home_link}")


def check_whois(url: str) -> dict:
    """N13: Whois — info-only. Always passes; embeds data."""
    try:
        import whois  # python-whois
    except ImportError:
        return _result("N13", True, "python-whois not installed (info skipped)")
    host = urlparse(url).netloc.replace("www.", "")
    try:
        w = whois.whois(host)
        created = str(w.creation_date)[:10] if w.creation_date else "?"
        expires = str(w.expiration_date)[:10] if w.expiration_date else "?"
        return _result("N13", True, f"created={created} expires={expires}")
    except Exception as e:
        return _result("N13", True, f"whois error: {e.__class__.__name__}")


def run_all(url: str) -> list[dict]:
    """Run all N1-N13. Order matters: robots.txt result is reused for sitemap."""
    out: list[dict] = []
    out.append(check_ssl_valid(url))
    out.append(check_ssl_soon_warning(url))
    out.append(check_ssl_critical(url))
    out.append(check_http_version(url))
    out.append(check_security_headers(url))
    out.append(check_server_header_no_version(url))
    out.append(check_www_redirect(url))
    robots_res = check_robots_txt(url)
    out.append(robots_res)
    out.append(check_sitemap_xml(url, robots_text=robots_res.get("robots_text", "")))
    out.append(check_llms_txt(url))
    out.append(check_404_status(url))
    out.append(check_404_has_nav(url))
    out.append(check_whois(url))
    return out
