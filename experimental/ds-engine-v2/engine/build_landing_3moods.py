#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор полного лендинга (8 блоков) с переключателем 3 модов.

ПРИНЦИП: не «придумывает» раскладку — собирает то, что заложено по recipes.yaml
каждого мода (вид снят глазами с рефов 01/02/29, приёмы в recipes.yaml).
У каждого мода — СВОЯ разметка/раскладка блоков (как в старых composed).

Поток согласования: показать клиенту все 3 → выбрать → удалить лишние → один для 08.
08-формат: реальный текст в семантических тегах (h1/p/li/a), <section class="lp-...">.

Тексты — из prototype-01.yaml (активный, Екатерина Безикова). Дословно.
"""
import html, pathlib, yaml, argparse, sys

# --- путь к проекту: --project <путь>, иначе автопоиск (если движок лежит в <project>/07b_COMPOSED) ---
def _resolve_project():
    ap = argparse.ArgumentParser(description="DS-Engine v2 — собрать composed-3moods.html по проекту")
    ap.add_argument("--project", help="путь к проекту-лендингу (папка с 05_ДИЗАЙН-СИСТЕМА/, 07_ПРОТОТИП/)")
    ap.add_argument("--prototype", default=None, help="имя файла прототипа в 07_ПРОТОТИП/ (по умолчанию активный/первый)")
    args, _ = ap.parse_known_args()
    if args.project:
        root = pathlib.Path(args.project).expanduser().resolve()
    else:
        # fallback: движок внутри <project>/07b_COMPOSED → проект на уровень выше
        root = pathlib.Path(__file__).resolve().parents[1]
    if not (root / "05_ДИЗАЙН-СИСТЕМА" / "moods").exists():
        sys.exit(f"[ОШИБКА] не нашёл 05_ДИЗАЙН-СИСТЕМА/moods в {root}\n"
                 f"Укажи проект: python build_landing_3moods.py --project <путь-к-проекту>")
    return root, args.prototype

ROOT, _PROTO_NAME = _resolve_project()
MOODS = ROOT / "05_ДИЗАЙН-СИСТЕМА" / "moods"

# прототип: явный --prototype, иначе активный (meta.active), иначе prototype-01/первый
def _find_proto():
    pdir = ROOT / "07_ПРОТОТИП"
    if _PROTO_NAME:
        return pdir / _PROTO_NAME
    cands = sorted(pdir.glob("prototype*.yaml"))
    for c in cands:
        try:
            if yaml.safe_load(open(c, encoding="utf-8")).get("meta", {}).get("active"):
                return c
        except Exception:
            pass
    if (pdir / "prototype-01.yaml").exists():
        return pdir / "prototype-01.yaml"
    if cands:
        return cands[0]
    sys.exit(f"[ОШИБКА] не нашёл prototype*.yaml в {pdir}")

PROTO = _find_proto()
OUT = ROOT / "07b_COMPOSED" / "composed-3moods.html"
PHOTO = "../07c_PHOTOS/photo.png"

def esc(s): return html.escape(str(s), quote=True)

def esc(s): return html.escape(str(s), quote=True)

# Т3: неразрывный пробел (U+00A0) после коротких служебных слов
NBSP=" "
_SHORT={"в","и","с","к","за","по","не","на","о","об","от","до","из","у","а","но","я","мы","вы","да","же","ли","бы","то","во","со","ко","изо"}
def nbsp(s):
    if not s: return s
    words=str(s).split(" ")
    res=""
    for i,w in enumerate(words):
        res+=w
        if i<len(words)-1:
            res += NBSP if w.lower().strip(".,;:!?—") in _SHORT else " "
    return res

# ─────────────────────────── ДАННЫЕ ПРОТОТИПА ───────────────────────────
P = yaml.safe_load(open(PROTO, encoding="utf-8"))
B = {b["type"]: b for b in P["blocks"]}

def feats():   return B["hero"]["features"]["items"]
def stats():   return B["stats"]["items"]["items"]
def pains():   return B["problem-solution"]["pains"]
def gains():   return B["problem-solution"]["gains"]
def formats(): return B["process"]["formats"]["items"]
def benefits():return B["process"]["benefits"]
def cases():   return B["case-study"]["cases"]["items"]
def reasons(): return B["trust"]["reasons"]["items"]
def chats():   return B["testimonials"]["chats"]["items"]
def socials(): return B["testimonials"]["socials"]["items"]

HERO  = B["hero"]; HEAD = B["header"]; PROB = B["problem-solution"]
PROC  = B["process"]; CASE = B["case-study"]; TRUST = B["trust"]; TEST = B["testimonials"]

H1_PRE, H1_ACC = "Наведите", HERO["headline"]["accent_word"]
H1_POST = "за 5 дней — закройте первые долги и начните копить без стресса"
# смысловые единицы H1 для hero_layout (см. _REFERENCE-ANALYSIS-LOGIC.md):
H1_ACTION    = H1_PRE                 # глагол-призыв «Наведите»
H1_QUALIFIER = "5 дней"               # срок — отдельная единица, НЕ часть accent_word
# anchor_outline = qualifier (не пересекается с accent_word «порядок в деньгах»)
EYEBROW = HERO["eyebrow"]["text"]
SUBHEAD = HERO["subhead"]["text"]
HERO_CTA = HERO["cta"]["button"]["text"]
HERO_NOTE = HERO["cta"]["note"]["text"]
BADGE = HERO["badge"]["text"]
BADGE_SUB = HERO["expert_intro"]["text"]["text"]
HEAD_CTA = HEAD["cta"]["button"]["text"]
NAV = HEAD["nav"]["items"]
LOGO = HEAD["logo"]["text"]; LOGO_SUB = HEAD["logo"]["sub"]
PROB_CTA = PROB["cta"]["button"]["text"]; PROB_NOTE = PROB["cta"]["note"]["text"]

def read_css(mood, *files):
    out = []
    for f in files:
        p = MOODS / mood / f
        if p.exists(): out.append(p.read_text(encoding="utf-8"))
    return "\n".join(out)

# ═══════════════════════════════════════════════════════════════════════
#  Каждый мод = модуль с функцией render() → HTML восьми блоков + его CSS.
#  Разметка РАЗНАЯ под характер (recipes этого мода).
# ═══════════════════════════════════════════════════════════════════════

# импортируем три рендерера
import mood_darkmint, mood_freshgreen, mood_grooming

RENDERERS = {
    "dark-mint":   mood_darkmint,
    "fresh-green": mood_freshgreen,
    "grooming":    mood_grooming,
}
LABELS = {"dark-mint":"Dark-mint (деньги PRO)", "fresh-green":"Fresh-green (нутрициология)", "grooming":"Grooming (editorial)"}
DEFAULT = "dark-mint"

ctx = dict(
    PHOTO=PHOTO, esc=esc,
    H1_PRE=H1_PRE, H1_ACC=H1_ACC, H1_POST=nbsp(H1_POST), EYEBROW=EYEBROW, SUBHEAD=nbsp(SUBHEAD),
    H1_ACTION=H1_ACTION, H1_QUALIFIER=H1_QUALIFIER,
    HERO_CTA=HERO_CTA, HERO_NOTE=nbsp(HERO_NOTE), BADGE=BADGE, BADGE_SUB=nbsp(BADGE_SUB),
    HEAD_CTA=HEAD_CTA, NAV=NAV, LOGO=LOGO, LOGO_SUB=LOGO_SUB,
    PROB_CTA=PROB_CTA, PROB_NOTE=nbsp(PROB_NOTE),
    feats=feats, stats=stats, pains=pains(), gains=gains(), formats=formats,
    benefits=benefits(), cases=cases, reasons=reasons, chats=chats, socials=socials,
    PROB=PROB, PROC=PROC, CASE=CASE, TRUST=TRUST, TEST=TEST, HERO=HERO,
)

# собрать секции CSS токенов всех модов
tokens_css = "\n".join(read_css(m, "palette.css", "typography.css", "metrics.css", "motion.css") for m in RENDERERS)

# собрать тело: для каждого мода — обёртка .mood-stage[data-stage=mood]
bodies = []
mood_css = []
for m, mod in RENDERERS.items():
    html_body, css = mod.render(ctx)
    # Г8: сквозной декор-слой (page-level) — тонкая дуга-нить через весь лендинг
    sweep = ('<svg class="page-sweep" aria-hidden="true" preserveAspectRatio="none" viewBox="0 0 100 1000">'
             '<path d="M 8 0 C 60 200, -10 420, 50 620 C 95 780, 20 900, 70 1000" '
             'fill="none" stroke="var(--lp-accent)" stroke-width="0.4" opacity="0.18"/></svg>')
    bodies.append(f'<div class="mood-stage" data-stage="{m}" {"data-active" if m==DEFAULT else ""}>\n{sweep}\n{html_body}\n</div>')
    mood_css.append(css)

switcher = "".join(
    f'<button class="ms-tab{" on" if m==DEFAULT else ""}" data-mood="{m}">{esc(LABELS[m])}</button>'
    for m in RENDERERS
)

PAGE = f"""<!DOCTYPE html>
<html lang="ru" data-mood="{DEFAULT}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Екатерина Безикова — лендинг · 3 мода (примерка)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,500;1,600&family=Montserrat:wght@300;400;500;600;700;800&family=Caveat:wght@500;600&family=El+Messiri:wght@400;500;600;700&family=Raleway:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ===== ТОКЕНЫ ВСЕХ 3 МОДОВ (palette/typography/metrics/motion) ===== */
{tokens_css}

/* ===== БАЗА ===== */
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{background:var(--lp-bg);color:var(--lp-text);font-family:var(--lp-fb);line-height:1.65;overflow-x:hidden}}
.wrap{{max-width:1200px;margin:0 auto;padding:0 32px}}
.section{{position:relative;padding:clamp(56px,8vw,108px) 0}}
img{{max-width:100%}}

/* Т1: заголовки переносятся по смыслу, не рвутся; Т2: текст не обрезается */
h1,h2,h3{{text-wrap:balance;overflow-wrap:break-word}}
p,blockquote,.dm-quote,.gr-quote,.fg-quote{{text-wrap:pretty;overflow:visible;max-height:none}}
blockquote,.dm-quote,.gr-quote,.fg-quote{{height:auto}}

/* показываем только активную сцену мода (примерка) */
.mood-stage{{display:none}}
.mood-stage[data-active]{{display:block;position:relative}}
/* Г8: сквозной декор-слой — нить через весь лендинг, под контентом, не ловит клики */
.page-sweep{{position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none}}
.mood-stage[data-active]>*:not(.page-sweep){{position:relative;z-index:1}}

/* ===== ПАНЕЛЬ-ПЕРЕКЛЮЧАТЕЛЬ МУДОВ ===== */
.mood-switcher{{position:fixed;left:50%;transform:translateX(-50%);bottom:18px;z-index:100;
  display:flex;gap:6px;background:rgba(20,20,20,.86);backdrop-filter:blur(10px);
  padding:7px;border-radius:40px;box-shadow:0 16px 40px rgba(0,0,0,.35)}}
.ms-tab{{font-family:'Montserrat',sans-serif;font-size:.82rem;font-weight:600;color:#ddd;
  background:transparent;border:none;cursor:pointer;padding:9px 18px;border-radius:30px;transition:.2s}}
.ms-tab:hover{{color:#fff}}
.ms-tab.on{{background:#fff;color:#111}}

/* ===== CSS ПРИЁМОВ КАЖДОГО МОДА (recipes) ===== */
{"".join(mood_css)}

@media(prefers-reduced-motion:no-preference){{
  .reveal{{opacity:0;transform:translateY(24px);transition:.7s ease}}.reveal.in{{opacity:1;transform:none}}}}
/* Г8: декор СТАБИЛЕН — не участвует в reveal, всегда видим (не мигает) */
.page-sweep,.gr-arc,.gr-scribble,.gr-circle,.dm-anchor-outline,.dm-glow,.dm-fglow,
.dm-diamond,.dm-bill,.gr-dotdec,.fg-gold-dot,.fg-wave,.gr-mark{{opacity:1!important;transform:none!important;transition:none!important}}
.dm-glow,.dm-fglow{{opacity:.2!important}}.dm-anchor-outline{{opacity:.32!important}}
.page-sweep{{opacity:.18!important}}.gr-arc circle{{opacity:.4}}
</style>
</head>
<body>

<nav class="mood-switcher" aria-label="Переключатель дизайн-систем">{switcher}</nav>

{"".join(bodies)}

<script>
// переключатель: меняет data-mood на <html> и активную сцену
const tabs=document.querySelectorAll('.ms-tab');
function setMood(m){{
  document.documentElement.setAttribute('data-mood',m);
  document.querySelectorAll('.mood-stage').forEach(s=>{{
    if(s.dataset.stage===m) s.setAttribute('data-active',''); else s.removeAttribute('data-active');
  }});
  tabs.forEach(t=>t.classList.toggle('on',t.dataset.mood===m));
  reobserve();
}}
tabs.forEach(t=>t.addEventListener('click',()=>setMood(t.dataset.mood)));

// reveal
let io;
function reobserve(){{
  if(io) io.disconnect();
  io=new IntersectionObserver((es)=>es.forEach(e=>{{if(e.isIntersecting){{e.target.classList.add('in')}}}}),{{threshold:.12}});
  // не сбрасываем уже показанные (Г8: без мигания при переключении мода)
  document.querySelectorAll('.mood-stage[data-active] .reveal:not(.in)').forEach(el=>io.observe(el));
}}
reobserve();
</script>
</body>
</html>
"""

OUT.write_text(PAGE, encoding="utf-8")
print(f"OK → {OUT}  ({len(PAGE.splitlines())} строк)")
