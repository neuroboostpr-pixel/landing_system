#!/usr/bin/env python3
"""Inject Yandex Metrika + Google Tag Manager into functions.php.

CLI: python3 generate-analytics.py <project-dir>
Reads: 00_БРИФ/brief.md for YM counter ID and GTM container ID.
Modifies: 08_КОД/wp-theme/functions.php — replaces // [YM_COUNTER] placeholder.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success, warn


def _parse_analytics(brief_text: str) -> tuple:
    ym = ""
    gtm = ""
    m = re.search(r"YM\s*счётчик[:\s]+(\d{6,10})", brief_text, re.IGNORECASE)
    if m:
        ym = m.group(1)
    m2 = re.search(r"GTM\s*(?:контейнер)?[:\s]+(GTM-[A-Z0-9]+)", brief_text, re.IGNORECASE)
    if m2:
        gtm = m2.group(1)
    return ym, gtm


def _ym_code(counter_id: str) -> str:
    return (
        f"// Yandex Metrika — counter {counter_id}\n"
        "add_action('wp_head', function () { ?>\n"
        "<script>\n"
        "(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};\n"
        "m[i].l=1*new Date();\n"
        "for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}\n"
        "k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}\n"
        f")(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js', 'ym');\n"
        f"ym({counter_id}, 'init', {{ clickmap:true, trackLinks:true, accurateTrackBounce:true, webvisor:true }});\n"
        "// Цель: отправка формы\n"
        f"// ym({counter_id}, 'reachGoal', 'form_submit');\n"
        "</script>\n"
        f"<noscript><div><img src='https://mc.yandex.ru/watch/{counter_id}' style='position:absolute; left:-9999px;' alt='' /></div></noscript>\n"
        "<?php }, 1);\n\n"
        "// Хелпер для отправки целей ЯМ из PHP\n"
        f"function lp_ym_goal(string $goal): void {{\n"
        f"    echo \"<script>ym({counter_id}, 'reachGoal', '\" . esc_js($goal) . \"');</script>\";\n"
        "}\n"
    )


def _gtm_head_code(container_id: str) -> str:
    return (
        f"// Google Tag Manager — {container_id}\n"
        "add_action('wp_head', function () { ?>\n"
        f"<!-- Google Tag Manager -->\n"
        f"<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});\n"
        f"var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';\n"
        f"j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;\n"
        f"f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{container_id}');</script>\n"
        f"<!-- End Google Tag Manager -->\n"
        "<?php }, 2);\n\n"
        "// GTM noscript (body)\n"
        "add_action('wp_body_open', function () { ?>\n"
        f"<!-- Google Tag Manager (noscript) -->\n"
        f"<noscript><iframe src='https://www.googletagmanager.com/ns.html?id={container_id}'\n"
        f"height='0' width='0' style='display:none;visibility:hidden'></iframe></noscript>\n"
        f"<!-- End Google Tag Manager (noscript) -->\n"
        "<?php });\n"
    )


def main(argv: list) -> int:
    if len(argv) < 2:
        error("Usage: generate-analytics.py <project-dir>")
        return 1
    try:
        start = Path(argv[1])
        fp = start / "08_КОД" / "wp-theme" / "functions.php"
        if not fp.exists():
            raise FileNotFoundError("functions.php not found — run /landing-build first")
        project = start

        brief_path = project / "00_БРИФ" / "brief.md"
        brief_text = brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""
        ym_id, gtm_id = _parse_analytics(brief_text)

        current = fp.read_text(encoding="utf-8")

        if ym_id:
            current = current.replace("// [YM_COUNTER] — Yandex Metrika (analytics-engineer)", _ym_code(ym_id))
            current = current.replace("// [YM_COUNTER]", _ym_code(ym_id))
        else:
            warn("YM счётчик не найден в brief.md — пропускаю")

        if gtm_id and "googletagmanager.com" not in current:
            current += "\n" + _gtm_head_code(gtm_id)
        else:
            warn("GTM контейнер не найден в brief.md — пропускаю")

        fp.write_text(current, encoding="utf-8")
        success(f"Analytics injected → {fp}")
        return 0
    except FileNotFoundError as exc:
        error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
