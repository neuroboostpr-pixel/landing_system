"""HTML on-page checks (H1-H25). HTTP-based, returns list[dict]."""
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

# Allowed status: 200 = pass, other = fail for H1; non-fatal info for others
SOFT_REDIR_OK = {301, 302, 307, 308}


def _result(check_id: str, passed: bool, evidence: str = "", **extra) -> dict:
    return {"id": check_id, "passed": passed, "evidence": evidence, **extra}


def check_html(html: str, url: str, status_code: int = 200,
               response_time_ms: int = 0, content_size_bytes: int = 0) -> list[dict]:
    """Run 25 HTML on-page checks on parsed HTML.

    Args:
        html: response body
        url: canonical URL (for host comparison)
        status_code: HTTP status from response
        response_time_ms: TTFB ms (from response.elapsed)
        content_size_bytes: len(response.content) for H3
    """
    soup = BeautifulSoup(html, "lxml")
    out: list[dict] = []

    # H1: HTTP 200
    out.append(_result("H1", status_code == 200, f"status={status_code}"))

    # H2: TTFB
    out.append(_result("H2", response_time_ms <= 800, f"ttfb={response_time_ms}ms"))

    # H3: HTML size ≤150KB
    size_kb = content_size_bytes / 1024
    out.append(_result("H3", size_kb <= 150, f"size={size_kb:.1f}KB"))

    # H4: <title> present
    title = soup.find("title")
    title_text = title.get_text(strip=True) if title else ""
    out.append(_result("H4", bool(title_text), f'title="{title_text[:60]}"'))

    # H5: title length 30-80
    out.append(_result("H5", 30 <= len(title_text) <= 80, f"len={len(title_text)}"))

    # H6: meta description present
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc_text = (meta_desc.get("content", "") if meta_desc else "").strip()
    out.append(_result("H6", bool(desc_text), f"desc_len={len(desc_text)}"))

    # H7: description length 70-320
    out.append(_result("H7", 70 <= len(desc_text) <= 320, f"desc_len={len(desc_text)}"))

    # H8: exactly 1× <h1>
    h1_count = len(soup.find_all("h1"))
    out.append(_result("H8", h1_count == 1, f"h1_count={h1_count}"))

    # H9: heading hierarchy (no skips H2→H4 without H3)
    headings = [int(t.name[1]) for t in soup.find_all(re.compile(r"^h[1-6]$"))]
    skip_at = None
    for i, (prev, cur) in enumerate(zip(headings, headings[1:])):
        if cur > prev + 1:
            skip_at = (i + 1, prev, cur)
            break
    if skip_at is None:
        h9_evidence = f"{len(headings)} заголовков, иерархия корректна (без скачков уровней)"
    else:
        idx, prev, cur = skip_at
        seq = ",".join(f"H{n}" for n in headings[:idx + 2])
        h9_evidence = (
            f"скачок: H{prev}→H{cur} (через {cur - prev - 1} уровней) "
            f"на позиции #{idx}. Последовательность: {seq}..."
        )
    out.append(_result("H9", skip_at is None, h9_evidence))

    # H10: <html lang=...> present
    html_tag = soup.find("html")
    lang = (html_tag.get("lang", "") if html_tag else "").strip()
    out.append(_result("H10", bool(lang), f'lang="{lang}"'))

    # H11: UTF-8 declaration
    charset_tag = soup.find("meta", attrs={"charset": True})
    charset = (charset_tag.get("charset", "") if charset_tag else "").lower()
    is_utf8 = "utf-8" in charset or "utf8" in charset
    if not is_utf8:
        # check http-equiv variant
        equiv = soup.find("meta", attrs={"http-equiv": re.compile(r"content-type", re.I)})
        if equiv:
            content = equiv.get("content", "").lower()
            is_utf8 = "utf-8" in content or "utf8" in content
    out.append(_result("H11", is_utf8, f"charset={charset}"))

    # H12: <link rel=canonical> valid
    canonical = soup.find("link", attrs={"rel": "canonical"})
    canonical_href = (canonical.get("href", "") if canonical else "").strip()
    canonical_valid = bool(canonical_href) and canonical_href.startswith(("http://", "https://"))
    out.append(_result("H12", canonical_valid, f'href="{canonical_href}"'))

    # H13: hreflang (info if any) — soft, pass=true if not multilang
    hreflangs = soup.find_all("link", attrs={"rel": "alternate", "hreflang": True})
    out.append(_result("H13", True, f"hreflang_count={len(hreflangs)}"))

    # H14: meta robots — no unexpected noindex
    robots = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    robots_content = (robots.get("content", "") if robots else "").lower()
    has_noindex = "noindex" in robots_content
    out.append(_result("H14", not has_noindex, f'robots="{robots_content}"'))

    # H15: img alt ≥95%
    imgs = soup.find_all("img")
    img_with_alt = sum(1 for i in imgs if i.get("alt", "").strip())
    ratio_alt = img_with_alt / len(imgs) if imgs else 1.0
    out.append(_result("H15", ratio_alt >= 0.95, f"alt_ratio={ratio_alt:.2f} ({img_with_alt}/{len(imgs)})"))

    # H16: img loading=lazy ≥80% (skip if <3 images — no signal)
    lazy_count = sum(1 for i in imgs if i.get("loading", "").lower() == "lazy")
    ratio_lazy = lazy_count / len(imgs) if imgs else 1.0
    out.append(_result("H16", ratio_lazy >= 0.8 or len(imgs) < 3,
                       f"lazy_ratio={ratio_lazy:.2f} ({lazy_count}/{len(imgs)})"))

    # H17: img width/height ≥90%
    sized = sum(1 for i in imgs if i.get("width") and i.get("height"))
    ratio_sized = sized / len(imgs) if imgs else 1.0
    out.append(_result("H17", ratio_sized >= 0.9, f"sized_ratio={ratio_sized:.2f}"))

    # H18: modern formats (webp/avif) ≥50%
    modern = sum(1 for i in imgs if any(
        (i.get("src", "") or "").lower().endswith(ext) for ext in (".webp", ".avif")
    ))
    ratio_modern = modern / len(imgs) if imgs else 1.0
    out.append(_result(
        "H18", ratio_modern >= 0.5,
        f"WebP/AVIF: {ratio_modern:.0%} ({modern} из {len(imgs)} картинок); лимит ≥50%"
    ))

    # H19: inline CSS ≤10KB
    style_tags = soup.find_all("style")
    inline_css_size = sum(len(s.get_text("")) for s in style_tags)
    inline_css_kb = inline_css_size / 1024
    out.append(_result(
        "H19", inline_css_kb <= 10,
        f"inline CSS: {inline_css_kb:.1f}KB в {len(style_tags)} <style> тегах; лимит 10KB"
    ))

    # H20: render-blocking resources ≤3 (heuristic: <link rel=stylesheet> in head without media print)
    head = soup.find("head")
    rb = 0
    if head:
        for link in head.find_all("link", attrs={"rel": "stylesheet"}):
            media = (link.get("media", "") or "").lower()
            if "print" not in media:
                rb += 1
    out.append(_result(
        "H20", rb <= 3,
        f"render-blocking CSS файлов: {rb} в <head>; лимит 3"
    ))

    # H21: internal links ≥5
    host = urlparse(url).netloc
    internal = external = 0
    noopener_issues = []
    anchor_clicks = anchor_total = 0
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        anchor_text = a.get_text(strip=True).lower()
        if anchor_text:
            anchor_total += 1
            if anchor_text in ("click here", "тут", "сюда", "здесь"):
                anchor_clicks += 1
        parsed = urlparse(href)
        target_host = parsed.netloc
        is_external = target_host and target_host != host
        if is_external:
            external += 1
            rel = (a.get("rel") or [])
            if isinstance(rel, str):
                rel = rel.split()
            if "noopener" not in rel:
                noopener_issues.append(href)
        else:
            internal += 1
    out.append(_result(
        "H21", internal >= 5,
        f"внутренних ссылок: {internal} (внешних: {external}); минимум 5"
    ))

    # H22: external links → rel=noopener
    out.append(_result(
        "H22", not noopener_issues,
        f"внешних без rel=noopener: {len(noopener_issues)} (из {external} внешних)"
    ))

    # H23: «click here»/«тут» <5%
    click_ratio = anchor_clicks / anchor_total if anchor_total else 0
    out.append(_result(
        "H23", click_ratio < 0.05,
        f"обобщённых анкоров: {click_ratio:.0%} ({anchor_clicks} из {anchor_total}); лимит <5%"
    ))

    # H24: tel: links present
    has_tel = bool(soup.find("a", href=re.compile(r"^tel:")))
    out.append(_result(
        "H24", has_tel,
        "tel: ссылка найдена" if has_tel
        else "tel: ссылка не найдена — мобильные пользователи не могут позвонить в один клик"
    ))

    # H25: mailto: links if email in text
    body_text = soup.get_text(" ")
    has_email_in_text = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", body_text))
    has_mailto = bool(soup.find("a", href=re.compile(r"^mailto:")))
    if has_mailto:
        h25_evidence = "mailto: ссылка найдена"
    elif not has_email_in_text:
        h25_evidence = "email на странице не найден — mailto не требуется"
    else:
        h25_evidence = "email найден в тексте, но без <a href=mailto:> — кликнуть нельзя"
    out.append(_result("H25", has_mailto or not has_email_in_text, h25_evidence))

    return out
