# -*- coding: utf-8 -*-
"""fresh-green рендерер — свежий светлый, волны-разделители, pink-CTA, italic-акцент,
круглые маски, золотой декор. Разметка СВОЯ под характер реф 29."""

WAVE = ('<div class="fg-wave{cls}" aria-hidden="true"><svg viewBox="0 0 1200 90" preserveAspectRatio="none">'
        '<path d="M0,40 C300,90 500,0 700,30 C900,60 1050,20 1200,50 L1200,90 L0,90 Z" fill="var(--lp-surface-2)"/></svg></div>')

def render(c):
    esc=c["esc"]
    def li_feat(): return "".join(f'<li><span class="fg-tick">✓</span>{esc(x)}</li>' for x in c["feats"]())
    def li_pain(): return "".join(f'<li><span class="fg-dot"></span>{esc(x)}</li>' for x in c["pains"]["items"])
    def li_gain(): return "".join(f'<li><span class="fg-tick">✓</span>{esc(x)}</li>' for x in c["gains"]["items"])
    def stat_cards():
        return "".join(f'<div class="fg-stat"><span class="fg-num">{esc(s["num"])}</span><span class="fg-stat-l">{esc(s["label"])}</span></div>' for s in c["stats"]())
    def fmt_cards():
        return "".join(
            f'<div class="fg-card"><span class="fg-fnum">{esc(f["num"])}</span><h3>{esc(f["title"])}</h3>'
            f'<p>{esc(f["text"])}</p><a href="#">{esc(f["cta"])} →</a></div>' for f in c["formats"]())
    def benefit_li():
        return "".join(f'<li><span class="fg-tick">✓</span>{esc(x)}</li>' for x in c["benefits"]["items"])
    def case_cards():
        out=[]
        for cs in c["cases"]():
            ba="".join(f'<span class="fg-ba-step">{esc(s)}</span>' for s in cs["before_after"])
            out.append(f'<div class="fg-card"><h3>{esc(cs["author"])}</h3><p class="fg-result">{esc(cs["result"])}</p>'
                       f'<div class="fg-ba">{ba}</div><a href="#">{esc(cs["cta"])} →</a></div>')
        return "".join(out)
    def reason_cards():
        return "".join(f'<div class="fg-card sm"><h4>{esc(r["title"])}</h4><p>{esc(r["text"])}</p></div>' for r in c["reasons"]())
    def chat_bubbles():
        return "".join(f'<div class="fg-chat"><p>{esc(ch["text"])}</p><span class="fg-time">{esc(ch["time"])}</span></div>' for ch in c["chats"]())
    def social_chips():
        return "".join(f'<a href="#" class="fg-social">{esc(s)}</a>' for s in c["socials"]())
    nav="".join(f'<a href="#">{esc(n)}</a>' for n in c["NAV"])
    q=c["CASE"]["quote"]

    html=f"""
<!-- ============ FRESH-GREEN ============ -->
<header class="fg-head"><div class="wrap">
  <div class="fg-logo"><b>{esc(c["LOGO"])}</b><span>{esc(c["LOGO_SUB"])}</span></div>
  <nav class="fg-nav">{nav}</nav>
  <button class="fg-cta sm">{esc(c["HEAD_CTA"])}</button>
</div></header>

<!-- HERO по Г1–Г5: левый текст-коридор (поток) + правый коридор фигура-в-маске. -->
<section class="section fg-hero" id="hero">
  <span class="fg-gold-dot" style="left:6%;top:18%"></span>
  <div class="fg-grid">
    <!-- ЛЕВЫЙ коридор — ПОТОК (Г3) -->
    <div class="fg-col fg-col-left reveal">
      <div class="fg-badges"><span>✓ Практический подход</span><span>• {esc(c["EYEBROW"])}</span></div>
      <h1>{esc(c["H1_PRE"])} <span class="fg-italic">{esc(c["H1_ACC"])}</span> {esc(c["H1_POST"])}</h1>
      <p class="fg-lead">{esc(c["SUBHEAD"])}</p>
      <ul class="fg-feats">{li_feat()}</ul>
      <div class="fg-cta-row"><button class="fg-cta">{esc(c["HERO_CTA"])}</button>
        <span class="fg-note">{esc(c["HERO_NOTE"])}</span></div>
    </div>
    <!-- ПРАВЫЙ коридор — фигура в маске (Г5) -->
    <div class="fg-col fg-col-fig reveal">
      <div class="fg-figwrap"><img src="{c["PHOTO"]}" alt="{esc(c["BADGE"])}"></div>
      <div class="fg-pill"><b>{esc(c["BADGE"])}</b><span>{esc(c["BADGE_SUB"])}</span></div>
    </div>
  </div>
</section>

{WAVE.format(cls="")}
<!-- STATS: green-zone -->
<section class="section fg-green-zone" id="stats" style="padding-top:20px">
  <span class="fg-gold-dot" style="left:8%;top:30%"></span>
  <div class="wrap fg-stats">{stat_cards()}</div>
</section>
{WAVE.format(cls=" flip")}

<!-- PROBLEM→SOLUTION: белые карточки, контраст pains/gains -->
<section class="section fg-problem fg-bg-surface" id="problem">
  <div class="wrap"><div class="fg-prob-grid">
    <div class="fg-card pains reveal"><h3>{esc(c["PROB"]["pains"]["label"])}</h3><ul>{li_pain()}</ul></div>
    <div class="fg-card gains reveal"><h3><span class="fg-italic">{esc(c["PROB"]["gains"]["label"])}</span></h3><ul>{li_gain()}</ul></div>
  </div>
  <div class="fg-cta-row center reveal"><button class="fg-cta">{esc(c["PROB_CTA"])}</button>
    <span class="fg-note">{esc(c["PROB_NOTE"])}</span></div>
</div></section>

<!-- PROCESS: 3 карточки + benefits -->
<section class="section fg-process fg-bg-bg reveal" id="process"><div class="wrap">
  <h2 class="fg-h2">{esc(c["PROC"]["section_title"]["text"])}</h2>
  <p class="fg-sub">{esc(c["PROC"]["subhead"]["text"])}</p>
  <div class="fg-cards3">{fmt_cards()}</div>
  <div class="fg-benefits"><h4>{esc(c["PROC"]["benefits"]["label"])}</h4><ul>{benefit_li()}</ul></div>
</div></section>

{WAVE.format(cls="")}
<!-- CASE-STUDY: green-zone, белые карточки + цитата -->
<section class="section fg-green-zone fg-cases reveal" id="cases" style="padding-top:20px">
  <div class="wrap">
  <h2 class="fg-h2 on-green">{esc(c["CASE"]["section_title"]["text"])}</h2>
  <div class="fg-cards2">{case_cards()}</div>
  <blockquote class="fg-quote">«{esc(q["quote_text"]["text"])}»<cite>{esc(q["author"]["text"])}</cite></blockquote>
</div></section>
{WAVE.format(cls=" flip")}

<!-- TRUST: 4 причины (круглые маски-иконки) + видео -->
<section class="section fg-trust fg-bg-surface reveal" id="trust"><div class="wrap">
  <h2 class="fg-h2">{esc(c["TRUST"]["section_title"]["text"])}</h2>
  <div class="fg-cards4">{reason_cards()}</div>
  <div class="fg-video"><span class="fg-play">▶</span>{esc(c["TRUST"]["video"]["text"])}</div>
</div></section>

<!-- TESTIMONIALS: чаты + соцсети -->
<section class="section fg-test fg-bg-bg reveal" id="testimonials"><div class="wrap">
  <h2 class="fg-h2">{esc(c["TEST"]["section_title"]["text"])}</h2>
  <div class="fg-chats">{chat_bubbles()}</div>
  <div class="fg-socials">{social_chips()}</div>
</div></section>
"""

    css="""
/* ============ FRESH-GREEN приёмы (recipes) ============ */
[data-mood="fresh-green"] body{background:var(--lp-bg)}
/* П4: шапка отделена от контента */
.fg-head{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--lp-border-strong);box-shadow:0 6px 24px rgba(43,80,30,.07)}
.fg-head .wrap{display:flex;align-items:center;justify-content:space-between;height:72px}
.fg-logo b{font-family:var(--lp-fh);font-weight:700;font-size:1.05rem;display:block;color:var(--lp-text)}
.fg-logo span{font-size:.7rem;color:var(--lp-text-muted)}
.fg-nav{display:flex;gap:26px}.fg-nav a{color:var(--lp-text);font-size:.9rem;font-weight:500;text-decoration:none}
.fg-nav a:hover{color:var(--lp-accent)}
@media(max-width:880px){.fg-nav{display:none}}
.fg-cta{background:var(--lp-cta);color:var(--lp-on-cta);font-family:var(--lp-fb);font-weight:700;font-size:1rem;border:none;border-radius:40px;padding:16px 34px;cursor:pointer;box-shadow:0 14px 30px rgba(224,55,154,.32);transition:.2s}
.fg-cta:hover{background:var(--lp-cta-2);transform:translateY(-2px)}
.fg-cta.sm{padding:11px 22px;font-size:.85rem}
.fg-note{font-size:.82rem;color:var(--lp-text-muted);max-width:17em;line-height:1.4}
.fg-cta-row{display:flex;align-items:center;gap:20px;flex-wrap:wrap;margin-top:8px}
.fg-cta-row.center{justify-content:center;margin-top:34px;text-align:center}
.fg-italic{font-family:var(--lp-fh);font-style:italic;font-weight:600;color:var(--lp-accent)}
.fg-tick{flex:none;width:24px;height:24px;border-radius:50%;background:var(--lp-accent-soft);display:grid;place-items:center;color:var(--lp-accent);font-size:.72rem;font-weight:800}
.fg-dot{flex:none;width:11px;height:11px;border-radius:50%;border:2px solid var(--lp-accent);margin-top:6px}
.fg-gold-dot{position:absolute;width:14px;height:14px;border-radius:50%;background:var(--lp-gold);opacity:.7;z-index:0}
.fg-wave{display:block;width:100%;height:90px;line-height:0}.fg-wave svg{display:block;width:100%;height:100%}
.fg-wave.flip{transform:rotate(180deg)}
/* П2: смена фона светлых секций */
.fg-bg-surface{background:var(--lp-surface)}
.fg-bg-bg{background:var(--lp-bg)}
/* hero по Г1–Г5: 2 коридора, левый поток, правый фигура-в-маске */
.fg-hero{background:radial-gradient(60% 50% at 88% 8%,var(--lp-accent-soft),transparent 60%),var(--lp-bg)}
/* Г6: сетка ограничена и центрирована — без провала между зонами */
.fg-grid{max-width:1200px;margin:0 auto;padding:0 32px;display:grid;grid-template-columns:1.15fr .85fr;gap:48px;align-items:center;position:relative;z-index:2;min-height:80vh}
.fg-col-left{display:flex;flex-direction:column;align-items:flex-start;gap:18px}
.fg-badges{display:flex;gap:10px;flex-wrap:wrap}
.fg-badges span{background:var(--lp-surface);border:1px solid var(--lp-border);border-radius:30px;padding:7px 15px;font-size:.78rem;font-weight:600}
.fg-hero h1{font-family:var(--lp-fh);font-size:clamp(2.3rem,5vw,4rem);font-weight:800;line-height:1.08;color:var(--lp-text);margin:0}
.fg-lead{font-size:1.12rem;color:var(--lp-text-muted);max-width:30em}
.fg-feats{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:12px 24px;max-width:32em}
.fg-feats li{display:flex;align-items:center;gap:11px;font-weight:500;font-size:.95rem}
.fg-col-fig{position:relative;justify-self:center}
.fg-figwrap{width:min(400px,80vw);aspect-ratio:4/5;overflow:hidden;border-radius:50% 50% 46% 46%/60% 60% 40% 40%;border:5px solid var(--lp-surface);box-shadow:0 30px 60px rgba(43,80,30,.18)}
.fg-figwrap img{display:block;width:100%;height:100%;object-fit:cover;object-position:top center}
.fg-pill{position:absolute;left:-10px;bottom:46px;background:var(--lp-surface);border-radius:18px;padding:12px 16px;max-width:210px;box-shadow:0 16px 36px rgba(43,80,30,.18)}
.fg-pill b{font-family:var(--lp-fh);font-style:italic;font-size:.95rem;color:var(--lp-text)}
.fg-pill span{display:block;font-size:.72rem;color:var(--lp-text-muted);margin-top:4px}
@media(max-width:900px){.fg-grid{grid-template-columns:1fr;min-height:auto}.fg-feats{grid-template-columns:1fr}.fg-col-fig{justify-self:start;margin-top:24px}}
/* green-zone */
.fg-green-zone{background:var(--lp-surface-2);color:var(--lp-text-on-dark);position:relative}
.fg-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;position:relative;z-index:2}
.fg-stat{background:var(--lp-overlay-2);border-radius:20px;padding:26px 22px;text-align:center;backdrop-filter:blur(2px)}
.fg-num{font-family:var(--lp-fh);font-weight:800;font-size:clamp(2.4rem,5vw,3.6rem);color:#fff;display:block;line-height:1}
.fg-stat-l{font-size:.84rem;color:rgba(255,255,255,.88);margin-top:10px;display:block;line-height:1.4}
@media(max-width:760px){.fg-stats{grid-template-columns:1fr 1fr}}
/* cards общие */
.fg-card{background:var(--lp-surface);border-radius:24px;box-shadow:0 18px 44px rgba(43,80,30,.10);padding:32px 28px}
.fg-card.sm{padding:24px 22px;text-align:center}
.fg-card h3{font-family:var(--lp-fh);font-size:1.5rem;font-weight:700;color:var(--lp-text);margin-bottom:18px}
.fg-card h4{font-family:var(--lp-fb);font-weight:600;color:var(--lp-text);margin-bottom:8px}
.fg-card p{color:var(--lp-text-muted);font-size:.95rem}
.fg-card ul{list-style:none}.fg-card li{display:flex;gap:13px;align-items:flex-start;padding:12px 0;border-bottom:1px solid var(--lp-border)}
.fg-card li:last-child{border-bottom:none}
.fg-card a{color:var(--lp-cta);font-weight:700;font-size:.9rem;display:inline-block;margin-top:14px;text-decoration:none}
/* problem */
.fg-prob-grid{display:grid;grid-template-columns:1fr 1fr;gap:26px}
.fg-card.gains{background:linear-gradient(165deg,var(--lp-accent-soft),var(--lp-surface) 70%)}
.fg-card.gains h3{color:var(--lp-accent-dark)}
@media(max-width:820px){.fg-prob-grid{grid-template-columns:1fr}}
/* process */
.fg-h2{font-family:var(--lp-fh);font-size:clamp(1.9rem,3.5vw,3rem);font-weight:800;color:var(--lp-text);text-align:center}
.fg-h2.on-green{color:#fff}
.fg-sub{text-align:center;color:var(--lp-text-muted);margin:10px 0 34px}
.fg-cards3{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.fg-fnum{font-family:var(--lp-fh);font-size:2.4rem;font-weight:800;color:var(--lp-accent);opacity:.55;display:block;margin-bottom:6px}
.fg-benefits{margin-top:34px;background:var(--lp-accent-soft);border-radius:20px;padding:26px 30px}
.fg-benefits h4{font-family:var(--lp-fb);font-weight:600;color:var(--lp-accent-dark);margin-bottom:14px}
.fg-benefits ul{list-style:none;display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.fg-benefits li{display:flex;gap:11px;color:var(--lp-text);font-size:.95rem}
@media(max-width:820px){.fg-cards3{grid-template-columns:1fr}.fg-benefits ul{grid-template-columns:1fr}}
/* cases */
.fg-cards2{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:30px}
.fg-result{color:var(--lp-accent-dark)!important;font-weight:700;margin:6px 0 14px}
.fg-ba{display:flex;flex-direction:column;gap:8px}
.fg-ba-step{font-size:.85rem;color:var(--lp-text-muted);padding-left:18px;position:relative}
.fg-ba-step:before{content:"›";position:absolute;left:0;color:var(--lp-accent);font-weight:800;top:0}
.fg-quote{font-family:var(--lp-fh);font-style:italic;font-size:1.5rem;color:#fff;text-align:center;max-width:30em;margin:36px auto 0;line-height:1.4}
.fg-quote cite{display:block;font-family:var(--lp-fb);font-style:normal;font-size:.9rem;color:var(--lp-gold-soft);margin-top:14px}
@media(max-width:820px){.fg-cards2{grid-template-columns:1fr}}
/* trust */
.fg-cards4{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:30px}
.fg-card.sm h4{margin-top:8px}
.fg-video{margin:34px auto 0;display:flex;align-items:center;gap:14px;justify-content:center;color:var(--lp-text)}
.fg-play{width:46px;height:46px;border-radius:50%;background:var(--lp-cta);color:#fff;display:grid;place-items:center;box-shadow:0 14px 30px rgba(224,55,154,.4)}
@media(max-width:820px){.fg-cards4{grid-template-columns:1fr 1fr}}
/* testimonials */
.fg-chats{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:30px}
.fg-chat{background:var(--lp-surface);border-radius:18px 18px 18px 4px;padding:20px 22px;box-shadow:0 12px 30px rgba(43,80,30,.08)}
.fg-chat p{color:var(--lp-text);font-size:.95rem}
.fg-time{display:block;text-align:right;font-size:.72rem;color:var(--lp-text-muted);margin-top:10px}
.fg-socials{display:flex;gap:12px;justify-content:center;margin-top:30px}
.fg-social{border:2px solid var(--lp-accent);color:var(--lp-accent);border-radius:30px;padding:9px 22px;font-weight:600;font-size:.9rem;text-decoration:none}
.fg-social:hover{background:var(--lp-accent);color:#fff}
@media(max-width:820px){.fg-chats{grid-template-columns:1fr}}
"""
    return html, css
