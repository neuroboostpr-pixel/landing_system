# -*- coding: utf-8 -*-
"""grooming рендерер — editorial-воздушный, оранж точечно, тонкие дуги, фото-squircle,
оранжевый круг-подложка. Разметка СВОЯ под характер реф 01."""

ARC = ('<svg class="gr-arc" viewBox="0 0 200 200" fill="none" style="{style}">'
       '<circle cx="100" cy="100" r="98" stroke="var(--lp-accent)" stroke-width="1" opacity=".4"/></svg>')
# росчерк-подчёркивание под акцент-словом заголовка (реф 01/09)
SCRIBBLE = ('<svg class="gr-scribble" viewBox="0 0 200 24" fill="none" preserveAspectRatio="none">'
            '<path d="M4 16 C50 6, 150 6, 196 14" stroke="var(--lp-accent)" stroke-width="4" '
            'stroke-linecap="round" fill="none"/></svg>')
ARROW = '<a href="#" class="gr-arrow" aria-label="Подробнее">↗</a>'

def render(c):
    esc=c["esc"]
    def li_feat(): return "".join(f'<li><span class="gr-tick">✓</span>{esc(x)}</li>' for x in c["feats"]())
    def li_pain(): return "".join(f'<li><span class="gr-dot"></span>{esc(x)}</li>' for x in c["pains"]["items"])
    def li_gain(): return "".join(f'<li><span class="gr-tick">✓</span>{esc(x)}</li>' for x in c["gains"]["items"])
    # H2 с росчерком: последнее слово — акцент + кисть-подчёркивание
    def h2(text):
        words=esc(text).split(" ");
        if len(words)>1:
            words[-1]=f'<span class="gr-accent-word">{words[-1]}{SCRIBBLE}</span>'
        return " ".join(words)
    def stat_cards():
        # featured: одна карточка (i==1) оранжевая
        out=[]
        for i,s in enumerate(c["stats"]()):
            f=" featured" if i==1 else ""
            out.append(f'<div class="gr-card stat{f}"><span class="gr-num">{esc(s["num"])}</span><span class="gr-stat-l">{esc(s["label"])}</span></div>')
        return "".join(out)
    def fmt_cards():
        out=[]
        for i,f in enumerate(c["formats"]()):
            fe=" featured" if i==1 else ""
            out.append(f'<div class="gr-card{fe}"><span class="gr-fnum">{esc(f["num"])}</span><h3>{esc(f["title"])}</h3>'
                       f'<p>{esc(f["text"])}</p>{ARROW}</div>')
        return "".join(out)
    def benefit_li():
        return "".join(f'<li><span class="gr-tick">✓</span>{esc(x)}</li>' for x in c["benefits"]["items"])
    def case_cards():
        out=[]
        for i,cs in enumerate(c["cases"]()):
            fe=" featured" if i==0 else ""
            ba="".join(f'<span class="gr-ba-step">{esc(s)}</span>' for s in cs["before_after"])
            out.append(f'<div class="gr-card{fe}"><h3>{esc(cs["author"])}</h3><p class="gr-result">{esc(cs["result"])}</p>'
                       f'<div class="gr-ba">{ba}</div>{ARROW}</div>')
        return "".join(out)
    def reason_cards():
        out=[]
        for i,r in enumerate(c["reasons"]()):
            fe=" featured" if i==1 else ""
            out.append(f'<div class="gr-card sm{fe}"><h4>{esc(r["title"])}</h4><p>{esc(r["text"])}</p></div>')
        return "".join(out)
    def chat_bubbles():
        return "".join(f'<div class="gr-chat"><p>{esc(ch["text"])}</p><span class="gr-time">{esc(ch["time"])}</span></div>' for ch in c["chats"]())
    def social_chips():
        return "".join(f'<a href="#" class="gr-social">{esc(s)}</a>' for s in c["socials"]())
    nav="".join(f'<a href="#">{esc(n)}</a>' for n in c["NAV"])
    q=c["CASE"]["quote"]

    html=f"""
<!-- ============ GROOMING ============ -->
<header class="gr-head"><div class="wrap">
  <div class="gr-logo"><b>{esc(c["LOGO"])}</b><span>{esc(c["LOGO_SUB"])}</span></div>
  <nav class="gr-nav">{nav}</nav>
  <button class="gr-cta sm">{esc(c["HEAD_CTA"])}</button>
</div></header>

<!-- HERO по Г1–Г5: левый текст-коридор (поток) + правый коридор фигура-в-круге. Декор в границах зоны. -->
<section class="section gr-hero" id="hero">
  <div class="gr-grid">
    <!-- ЛЕВЫЙ коридор — ПОТОК (Г3) -->
    <div class="gr-col gr-col-left reveal">
      <div class="gr-eyebrow">{esc(c["EYEBROW"])}</div>
      <h1>{esc(c["H1_PRE"])} <span class="gr-accent">{esc(c["H1_ACC"])}</span> {esc(c["H1_POST"])}</h1>
      <p class="gr-lead">{esc(c["SUBHEAD"])}</p>
      <ul class="gr-feats">{li_feat()}</ul>
      <div class="gr-cta-row"><button class="gr-cta">{esc(c["HERO_CTA"])}</button>
        <span class="gr-note">{esc(c["HERO_NOTE"])}</span></div>
    </div>
    <!-- ПРАВЫЙ коридор — фигура в круге (Г5 без деформации) -->
    <div class="gr-col gr-col-fig reveal">
      {ARC.format(style="left:-50px;top:-20px;width:180px;height:180px")}
      <div class="gr-circle"></div>
      <div class="gr-photo"><img src="{c["PHOTO"]}" alt="{esc(c["BADGE"])}">
        <span class="gr-mark" style="left:14%;top:18%"></span><span class="gr-mark" style="right:18%;top:38%"></span></div>
      <div class="gr-pill"><b>{esc(c["BADGE"])}</b><span>{esc(c["BADGE_SUB"])}</span></div>
    </div>
  </div>
</section>

<!-- STATS: воздушный ряд цифр, тонкие разделители -->
<section class="section gr-stats gr-bg-surface reveal" id="stats"><div class="wrap gr-stats-row">{stat_cards()}</div></section>

<!-- PROBLEM→SOLUTION: белые воздушные карточки -->
<section class="section gr-problem gr-bg-bg" id="problem">
  {ARC.format(style="right:-90px;bottom:6%;width:200px;height:200px")}
  <div class="wrap"><div class="gr-prob-grid">
    <div class="gr-card pains reveal"><h3>{esc(c["PROB"]["pains"]["label"])}</h3><ul>{li_pain()}</ul></div>
    <div class="gr-card gains reveal"><h3>{esc(c["PROB"]["gains"]["label"])}</h3><ul>{li_gain()}</ul></div>
  </div>
  <div class="gr-cta-row center reveal"><button class="gr-cta">{esc(c["PROB_CTA"])}</button>
    <span class="gr-note">{esc(c["PROB_NOTE"])}</span></div>
</div></section>

<!-- PROCESS: 3 карточки с оранж-цифрой + benefits -->
<section class="section gr-process gr-bg-surface reveal" id="process">{ARC.format(style="right:-70px;top:8%;width:200px;height:200px")}<div class="wrap">
  <h2 class="gr-h2">{h2(c["PROC"]["section_title"]["text"])}</h2>
  <p class="gr-sub">{esc(c["PROC"]["subhead"]["text"])}</p>
  <div class="gr-cards3">{fmt_cards()}</div>
  <div class="gr-benefits"><h4>{esc(c["PROC"]["benefits"]["label"])}</h4><ul>{benefit_li()}</ul></div>
</div></section>

<!-- CASE-STUDY: карточки + цитата -->
<section class="section gr-cases gr-bg-soft reveal" id="cases">{ARC.format(style="left:-70px;bottom:10%;width:200px;height:200px")}<div class="wrap">
  <h2 class="gr-h2">{h2(c["CASE"]["section_title"]["text"])}</h2>
  <div class="gr-cards2">{case_cards()}</div>
  <blockquote class="gr-quote"><span class="gr-qmark">“</span>{esc(q["quote_text"]["text"])}<cite>{esc(q["author"]["text"])}</cite></blockquote>
</div></section>

<!-- TRUST: 4 причины + видео -->
<section class="section gr-trust gr-accent-band reveal" id="trust"><div class="wrap">
  <h2 class="gr-h2">{h2(c["TRUST"]["section_title"]["text"])}</h2>
  <div class="gr-cards4">{reason_cards()}</div>
  <div class="gr-video"><span class="gr-play">▶</span>{esc(c["TRUST"]["video"]["text"])}</div>
</div></section>

<!-- TESTIMONIALS: чаты + соцсети -->
<section class="section gr-test gr-bg-surface reveal" id="testimonials"><div class="wrap">
  <h2 class="gr-h2">{h2(c["TEST"]["section_title"]["text"])}</h2>
  <div class="gr-chats">{chat_bubbles()}</div>
  <div class="gr-socials">{social_chips()}</div>
</div></section>
"""

    css="""
/* ============ GROOMING приёмы (recipes) ============ */
[data-mood="grooming"] body{background:var(--lp-bg)}
/* П4: шапка отделена от контента — плотный фон + тень */
.gr-head{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--lp-border-strong);box-shadow:0 6px 24px rgba(50,44,40,.07)}
.gr-head .wrap{display:flex;align-items:center;justify-content:space-between;height:74px}
.gr-logo b{font-family:var(--lp-fh);font-weight:700;font-size:1.1rem;display:block;color:var(--lp-text)}
.gr-logo span{font-size:.7rem;color:var(--lp-text-muted)}
.gr-nav{display:flex;gap:26px}.gr-nav a{color:var(--lp-text);font-size:.9rem;font-weight:500;text-decoration:none}
.gr-nav a:hover{color:var(--lp-accent)}
@media(max-width:880px){.gr-nav{display:none}}
.gr-cta{background:var(--lp-accent);color:var(--lp-on-accent);font-family:var(--lp-fb);font-weight:600;font-size:1rem;border:none;border-radius:40px;padding:15px 32px;cursor:pointer;box-shadow:0 12px 28px rgba(223,107,44,.28);transition:.2s}
.gr-cta:hover{background:var(--lp-accent-dark);transform:translateY(-2px)}
.gr-cta.sm{padding:11px 22px;font-size:.85rem}
.gr-note{font-size:.82rem;color:var(--lp-text-muted);max-width:17em;line-height:1.4}
.gr-cta-row{display:flex;align-items:center;gap:20px;flex-wrap:wrap;margin-top:8px}
.gr-cta-row.center{justify-content:center;margin-top:34px;text-align:center}
.gr-accent{color:var(--lp-accent)}
.gr-arc{position:absolute;z-index:0;pointer-events:none}
.gr-dotdec{position:absolute;width:12px;height:12px;border-radius:50%;background:var(--lp-accent);opacity:.6;z-index:0}
.gr-tick{flex:none;width:22px;height:22px;border-radius:50%;background:var(--lp-accent-soft);display:grid;place-items:center;color:var(--lp-accent-dark);font-size:.7rem;font-weight:700}
.gr-dot{flex:none;width:9px;height:9px;border-radius:50%;background:var(--lp-accent);opacity:.6;margin-top:7px}
.gr-eyebrow{font-family:var(--lp-fb);font-size:.72rem;text-transform:uppercase;letter-spacing:.2em;font-weight:600;color:var(--lp-accent-dark);margin-bottom:14px}
/* П2: смена фона секций (ритм) */
.gr-bg-surface{background:var(--lp-surface)}
.gr-bg-bg{background:var(--lp-bg)}
.gr-bg-soft{background:var(--lp-surface-2)}
/* accent_band: полноширинная оранжевая зона-якорь */
.gr-accent-band{background:var(--lp-accent);color:#fff}
.gr-accent-band .gr-h2,.gr-accent-band h3,.gr-accent-band h4,.gr-accent-band p{color:#fff}
.gr-accent-band .gr-accent-word{color:#fff}
.gr-accent-band .gr-scribble path{stroke:#fff}
.gr-accent-band .gr-card,.gr-accent-band .gr-card.featured{background:rgba(255,255,255,.14);backdrop-filter:blur(2px)}
.gr-accent-band .gr-card.featured h4,.gr-accent-band .gr-card h4,.gr-accent-band .gr-card p{color:#fff!important}
.gr-accent-band .gr-play{background:#fff;color:var(--lp-accent)}
.gr-accent-band .gr-cta{background:#fff;color:var(--lp-accent)}
/* hero по Г1–Г5: 2 коридора, левый поток, правый фигура-в-круге */
.gr-hero{background:var(--lp-bg);overflow:hidden}
/* Г6: сетка ограничена и центрирована — без провала между зонами */
.gr-grid{max-width:1200px;margin:0 auto;padding:0 32px;display:grid;grid-template-columns:1.15fr .85fr;gap:48px;align-items:center;position:relative;z-index:2;min-height:80vh}
.gr-col-left{display:flex;flex-direction:column;align-items:flex-start;gap:18px}
.gr-hero h1{font-family:var(--lp-fh);font-size:clamp(2.4rem,5.5vw,4.4rem);font-weight:700;line-height:1.06;color:var(--lp-text);margin:0}
.gr-lead{font-size:1.12rem;color:var(--lp-text-muted);max-width:30em}
.gr-feats{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:12px 24px;max-width:32em}
.gr-feats li{display:flex;align-items:center;gap:11px;font-weight:500;font-size:.95rem}
/* правый коридор: фигура в круге, Г5 пропорции */
.gr-col-fig{position:relative;justify-self:center;width:min(440px,86vw)}
.gr-circle{position:absolute;right:-30px;top:8%;width:300px;height:300px;border-radius:50%;background:linear-gradient(150deg,var(--lp-accent),var(--lp-accent-2));z-index:0}
.gr-photo{position:relative;z-index:2;border-radius:36px;overflow:hidden;border:6px solid var(--lp-surface);box-shadow:0 30px 60px rgba(50,44,40,.16);aspect-ratio:4/5}
.gr-photo img{display:block;width:100%;height:100%;object-fit:cover;object-position:top center}
.gr-mark{position:absolute;width:18px;height:18px;border-radius:50%;background:var(--lp-surface);box-shadow:0 4px 10px rgba(0,0,0,.2);z-index:3}
.gr-pill{position:absolute;left:-14px;bottom:40px;background:var(--lp-surface);border-radius:18px;padding:12px 16px;max-width:210px;box-shadow:0 16px 36px rgba(50,44,40,.16);z-index:4}
.gr-pill b{font-family:var(--lp-fh);font-size:.98rem;color:var(--lp-text)}
.gr-pill span{display:block;font-size:.72rem;color:var(--lp-text-muted);margin-top:4px}
@media(max-width:900px){.gr-grid{grid-template-columns:1fr;min-height:auto}.gr-feats{grid-template-columns:1fr}.gr-col-fig{justify-self:start;margin-top:24px}}
/* stats */
.gr-stats-row{display:grid;grid-template-columns:repeat(4,1fr)}
.gr-stat{padding:14px 28px;border-left:1px solid var(--lp-border);text-align:left}.gr-stat:first-child{border-left:none}
.gr-num{font-family:var(--lp-fh);font-weight:700;font-size:clamp(2.4rem,5vw,3.6rem);color:var(--lp-accent);display:block;line-height:1;margin-bottom:8px}
.gr-stat-l{font-size:.85rem;color:var(--lp-text-muted);line-height:1.4}
@media(max-width:760px){.gr-stats-row{grid-template-columns:1fr 1fr;gap:28px 0}.gr-stat:nth-child(odd){border-left:none}}
/* П3: росчерк под акцент-словом заголовка */
.gr-accent-word{position:relative;color:var(--lp-accent);display:inline-block}
.gr-scribble{position:absolute;left:0;bottom:-.35em;width:100%;height:.4em;overflow:visible}
/* cards общие + featured (П3 акцент-карточка) + стрелка */
.gr-card{position:relative;background:var(--lp-surface);border-radius:26px;box-shadow:0 18px 44px rgba(50,44,40,.08);padding:32px 28px}
.gr-card.featured{background:var(--lp-accent)}
.gr-card.featured h3,.gr-card.featured h4,.gr-card.featured p,.gr-card.featured .gr-stat-l,.gr-card.featured .gr-num,.gr-card.featured .gr-result,.gr-card.featured .gr-ba-step{color:#fff!important}
.gr-card.featured .gr-fnum{background:rgba(255,255,255,.25);color:#fff}
.gr-card.featured .gr-ba-step:before{color:#fff}
.gr-arrow{position:absolute;right:22px;top:22px;width:40px;height:40px;border-radius:50%;background:var(--lp-accent);color:#fff;display:grid;place-items:center;text-decoration:none;font-size:1.1rem;box-shadow:0 8px 20px rgba(223,107,44,.3)}
.gr-card.featured .gr-arrow{background:#fff;color:var(--lp-accent)}
.gr-card.sm{padding:24px 22px}
.gr-card h3{font-family:var(--lp-fh);font-size:1.45rem;font-weight:600;color:var(--lp-text);margin-bottom:18px}
.gr-card h4{font-family:var(--lp-fh);font-size:1.1rem;font-weight:600;color:var(--lp-text);margin-bottom:8px}
.gr-card p{color:var(--lp-text-muted);font-size:.95rem}
.gr-card ul{list-style:none}.gr-card li{display:flex;gap:13px;align-items:flex-start;padding:12px 0;border-bottom:1px solid var(--lp-border)}
.gr-card li:last-child{border-bottom:none}
.gr-card a{color:var(--lp-accent);font-weight:600;font-size:.9rem;display:inline-block;margin-top:14px;text-decoration:none}
/* problem */
.gr-problem{position:relative;overflow:hidden}
.gr-prob-grid{display:grid;grid-template-columns:1fr 1fr;gap:26px}
.gr-card.gains{border:1.5px solid var(--lp-accent-soft)}
.gr-card.gains h3{color:var(--lp-accent-dark)}
@media(max-width:820px){.gr-prob-grid{grid-template-columns:1fr}}
/* process */
.gr-h2{font-family:var(--lp-fh);font-size:clamp(1.9rem,3.5vw,3rem);font-weight:700;color:var(--lp-text);text-align:center}
.gr-sub{text-align:center;color:var(--lp-text-muted);margin:10px 0 34px}
.gr-cards3{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.gr-fnum{display:inline-grid;place-items:center;width:46px;height:46px;border-radius:50%;background:var(--lp-accent-soft);color:var(--lp-accent-dark);font-family:var(--lp-fh);font-weight:700;font-size:1.2rem;margin-bottom:14px}
.gr-benefits{margin-top:34px;background:var(--lp-surface);border-radius:22px;box-shadow:0 14px 36px rgba(50,44,40,.07);padding:26px 30px}
.gr-benefits h4{font-family:var(--lp-fh);font-weight:600;color:var(--lp-text);margin-bottom:14px}
.gr-benefits ul{list-style:none;display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.gr-benefits li{display:flex;gap:11px;color:var(--lp-text-muted);font-size:.95rem}
@media(max-width:820px){.gr-cards3{grid-template-columns:1fr}.gr-benefits ul{grid-template-columns:1fr}}
/* cases */
.gr-cards2{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:30px}
.gr-result{color:var(--lp-accent-dark)!important;font-weight:600;margin:6px 0 14px}
.gr-ba{display:flex;flex-direction:column;gap:8px}
.gr-ba-step{font-size:.85rem;color:var(--lp-text-muted);padding-left:18px;position:relative}
.gr-ba-step:before{content:"›";position:absolute;left:0;color:var(--lp-accent);font-weight:800;top:0}
.gr-quote{font-family:var(--lp-fh);font-size:1.5rem;color:var(--lp-text);text-align:center;max-width:30em;margin:36px auto 0;line-height:1.45;position:relative}
.gr-qmark{font-family:var(--lp-fh);color:var(--lp-accent);font-size:2.4rem;display:block}
.gr-quote cite{display:block;font-family:var(--lp-fb);font-style:normal;font-size:.9rem;color:var(--lp-accent);margin-top:14px}
@media(max-width:820px){.gr-cards2{grid-template-columns:1fr}}
/* trust */
.gr-cards4{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:30px}
.gr-video{margin:34px auto 0;display:flex;align-items:center;gap:14px;justify-content:center;color:var(--lp-text)}
.gr-play{width:46px;height:46px;border-radius:50%;background:var(--lp-accent);color:#fff;display:grid;place-items:center;box-shadow:0 12px 28px rgba(223,107,44,.36)}
@media(max-width:820px){.gr-cards4{grid-template-columns:1fr 1fr}}
/* testimonials */
.gr-chats{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:30px}
.gr-chat{background:var(--lp-surface);border-radius:18px 18px 18px 4px;padding:20px 22px;box-shadow:0 12px 30px rgba(50,44,40,.07)}
.gr-chat p{color:var(--lp-text);font-size:.95rem}
.gr-time{display:block;text-align:right;font-size:.72rem;color:var(--lp-text-muted);margin-top:10px}
.gr-socials{display:flex;gap:12px;justify-content:center;margin-top:30px}
.gr-social{border:1.5px solid var(--lp-accent);color:var(--lp-accent);border-radius:30px;padding:9px 22px;font-weight:600;font-size:.9rem;text-decoration:none}
.gr-social:hover{background:var(--lp-accent);color:#fff}
@media(max-width:820px){.gr-chats{grid-template-columns:1fr}}
"""
    return html, css
