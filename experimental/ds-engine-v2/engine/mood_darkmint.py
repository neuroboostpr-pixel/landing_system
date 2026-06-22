# -*- coding: utf-8 -*-
"""dark-mint рендерер — тёмный premium-коллаж (recipes: ромбы, контурный заголовок,
teal-зоны+glow, фигура-вырез, ромб-маркеры). Разметка СВОЯ под характер реф 02."""

def render(c):
    esc=c["esc"]
    def li_feat():  return "".join(f'<li><span class="dm-mark fill"></span>{esc(x)}</li>' for x in c["feats"]())
    def li_pain():  return "".join(f'<li><span class="dm-mark hollow"></span>{esc(x)}</li>' for x in c["pains"]["items"])
    def li_gain():  return "".join(f'<li><span class="dm-mark fill"></span>{esc(x)}</li>' for x in c["gains"]["items"])
    def stat_cards():
        return "".join(f'<div class="dm-stat"><span class="dm-num">{esc(s["num"])}</span><span class="dm-stat-l">{esc(s["label"])}</span></div>' for s in c["stats"]())
    def fmt_cards():
        return "".join(
            f'<div class="dm-card{" feat" if i==1 else ""}"><span class="dm-fnum">{esc(f["num"])}</span>'
            f'<h3>{esc(f["title"])}</h3><p>{esc(f["text"])}</p><a href="#">{esc(f["cta"])} →</a></div>'
            for i,f in enumerate(c["formats"]()))
    def benefit_li():
        return "".join(f'<li><span class="dm-mark fill"></span>{esc(x)}</li>' for x in c["benefits"]["items"])
    def case_cards():
        out=[]
        for cs in c["cases"]():
            ba="".join(f'<span class="dm-ba-step">{esc(s)}</span>' for s in cs["before_after"])
            out.append(f'<div class="dm-card"><h3>{esc(cs["author"])}</h3>'
                       f'<p class="dm-result">{esc(cs["result"])}</p><div class="dm-ba">{ba}</div>'
                       f'<a href="#">{esc(cs["cta"])} →</a></div>')
        return "".join(out)
    def reason_cards():
        return "".join(f'<div class="dm-card"><h4>{esc(r["title"])}</h4><p>{esc(r["text"])}</p></div>' for r in c["reasons"]())
    def chat_bubbles():
        return "".join(f'<div class="dm-chat"><p>{esc(ch["text"])}</p><span class="dm-time">{esc(ch["time"])}</span></div>' for ch in c["chats"]())
    def social_chips():
        return "".join(f'<a href="#" class="dm-social">{esc(s)}</a>' for s in c["socials"]())
    nav="".join(f'<a href="#">{esc(n)}</a>' for n in c["NAV"])
    q=c["CASE"]["quote"]

    html=f"""
<!-- ============ DARK-MINT ============ -->
<header class="dm-head"><div class="wrap">
  <div class="dm-logo"><b>{esc(c["LOGO"])}</b><span>{esc(c["LOGO_SUB"])}</span></div>
  <nav class="dm-nav">{nav}</nav>
  <button class="dm-cta sm">{esc(c["HEAD_CTA"])}</button>
</div></header>

<!-- HERO по Г1–Г4: 3 коридора скелетом (лево-текст/центр-фигура/право-текст),
     декор+контур-якорь — абсолютом. Текст в коридорах — ПОТОК. -->
<section class="section dm-hero" id="hero">
  <div class="dm-canvas">
    <!-- ДЕКОР (Г3 абсолют) -->
    <div class="dm-glow z-back" style="left:50%;top:6%"></div>
    <div class="dm-diamond z-back" style="right:8%;top:12%"></div>
    <div class="dm-diamond hollow sm z-back" style="left:31%;top:8%"></div>
    <div class="dm-bill z-back" style="right:4%;top:34%"></div>
    <div class="dm-bill z-back" style="right:13%;top:56%"></div>
    <div class="dm-diamond sm z-top" style="left:30%;bottom:10%"></div>

    <!-- СКЕЛЕТ: 3 коридора -->
    <div class="dm-grid">
      <!-- ЛЕВЫЙ коридор — ПОТОК (Г3) -->
      <div class="dm-col dm-col-left z-front">
        <div class="dm-badge-top"><span class="tick">✓</span>{esc(c["BADGE"])}</div>
        <div class="dm-script">{esc(c["EYEBROW"])}</div>
        <h1 class="dm-anchor-fill">{esc(c["H1_ACC"])}</h1>
        <p class="dm-h-rest">{esc(c["H1_ACTION"])}, {esc(c["H1_POST"])}</p>
        <div class="dm-cta-zone">
          <button class="dm-cta round">{esc(c["HERO_CTA"])}</button>
          <span class="dm-note">{esc(c["HERO_NOTE"])}</span>
        </div>
      </div>
      <!-- ЦЕНТР: фигура + контур-якорь ЗА ней (Г3) -->
      <div class="dm-col dm-col-fig z-fig">
        <div class="dm-anchor-outline">{esc(c["H1_QUALIFIER"])}</div>
        <div class="dm-fglow"></div>
        <img src="{c["PHOTO"]}" alt="{esc(c["BADGE"])}">
      </div>
      <!-- ПРАВЫЙ коридор — ПОТОК (Г3) -->
      <div class="dm-col dm-col-right z-front">
        <p class="dm-subhead">{esc(c["SUBHEAD"])}</p>
        <ul class="dm-feats">{li_feat()}</ul>
      </div>
    </div>
  </div>
</section>

<!-- STATS: тёмный провал, числа мятой -->
<section class="section dm-stats reveal" id="stats"><div class="wrap dm-stats-row">{stat_cards()}</div></section>

<!-- PROBLEM→SOLUTION: две тёмные панели, ромб-маркеры, teal-glow у выгод -->
<section class="section dm-problem" id="problem">
  <div class="dm-diamond hollow" style="left:3%;top:12%"></div>
  <div class="wrap">
    <div class="dm-prob-grid">
      <div class="dm-card pain reveal"><h3>{esc(c["PROB"]["pains"]["label"])}</h3><ul>{li_pain()}</ul></div>
      <div class="dm-card gain teal reveal"><h3>{esc(c["PROB"]["gains"]["label"])}</h3><ul>{li_gain()}</ul></div>
    </div>
    <div class="dm-cta-row center reveal"><button class="dm-cta">{esc(c["PROB_CTA"])}</button>
      <span class="dm-note">{esc(c["PROB_NOTE"])}</span></div>
  </div>
</section>

<!-- PROCESS: 3 нумерованные карточки + что получите -->
<section class="section dm-process dm-bg-deep reveal" id="process"><div class="wrap">
  <h2 class="dm-h2">{esc(c["PROC"]["section_title"]["text"])}</h2>
  <p class="dm-sub">{esc(c["PROC"]["subhead"]["text"])}</p>
  <div class="dm-cards3">{fmt_cards()}</div>
  <div class="dm-benefits"><h4>{esc(c["PROC"]["benefits"]["label"])}</h4><ul>{benefit_li()}</ul></div>
</div></section>

<!-- CASE-STUDY: teal-зона, карточки кейсов + цитата -->
<section class="section dm-cases teal-zone reveal" id="cases">
  <div class="dm-glow" style="right:8%;top:14%"></div>
  <div class="wrap">
  <h2 class="dm-h2">{esc(c["CASE"]["section_title"]["text"])}</h2>
  <div class="dm-cards2">{case_cards()}</div>
  <blockquote class="dm-quote">«{esc(q["quote_text"]["text"])}»<cite>{esc(q["author"]["text"])}</cite></blockquote>
</div></section>

<!-- TRUST: 4 причины + видео -->
<section class="section dm-trust teal-zone reveal" id="trust"><div class="wrap">
  <h2 class="dm-h2">{esc(c["TRUST"]["section_title"]["text"])}</h2>
  <div class="dm-cards4">{reason_cards()}</div>
  <div class="dm-video"><span class="dm-play">▶</span>{esc(c["TRUST"]["video"]["text"])}</div>
</div></section>

<!-- TESTIMONIALS: чаты-бабблы + соцсети -->
<section class="section dm-test dm-bg-deep reveal" id="testimonials"><div class="wrap">
  <h2 class="dm-h2">{esc(c["TEST"]["section_title"]["text"])}</h2>
  <div class="dm-chats">{chat_bubbles()}</div>
  <div class="dm-socials">{social_chips()}</div>
</div></section>
"""

    css="""
/* ============ DARK-MINT приёмы (recipes) ============ */
[data-mood="dark-mint"] body{background:var(--lp-bg)}
/* П4: шапка отделена от контента */
.dm-head{position:sticky;top:0;z-index:40;background:rgba(14,17,23,.88);backdrop-filter:blur(12px);border-bottom:1px solid var(--lp-border-strong);box-shadow:0 6px 24px rgba(0,0,0,.35)}
.dm-head .wrap{display:flex;align-items:center;justify-content:space-between;height:74px}
.dm-logo b{font-family:var(--lp-fh);font-weight:700;font-size:1.05rem;display:block;color:var(--lp-text)}
.dm-logo span{font-size:.7rem;color:var(--lp-text-muted)}
.dm-nav{display:flex;gap:28px}.dm-nav a{color:var(--lp-text-muted);font-size:.9rem;font-weight:500;text-decoration:none}
.dm-nav a:hover{color:var(--lp-accent)}
@media(max-width:880px){.dm-nav{display:none}}
.dm-cta{background:var(--lp-accent);color:var(--lp-on-accent);font-family:var(--lp-fb);font-weight:600;font-size:.98rem;border:none;border-radius:40px;padding:15px 30px;cursor:pointer;box-shadow:0 14px 34px rgba(1,212,154,.32);transition:.2s}
.dm-cta:hover{background:var(--lp-accent-2);transform:translateY(-2px)}
.dm-cta.sm{padding:11px 22px;font-size:.85rem}
.dm-note{font-size:.8rem;color:var(--lp-text-muted);max-width:18em;line-height:1.4}
.dm-cta-row{display:flex;align-items:center;gap:20px;flex-wrap:wrap;margin-top:8px}
.dm-cta-row.center{justify-content:center;margin-top:36px;text-align:center}
.dm-diamond{position:absolute;width:46px;height:46px;border-radius:10px;background:linear-gradient(135deg,var(--lp-accent),var(--lp-accent-dark));transform:rotate(45deg);box-shadow:0 18px 40px rgba(1,212,154,.25);z-index:1}
.dm-diamond.hollow{background:transparent;border:2px solid var(--lp-border-strong);box-shadow:none}
.dm-diamond.sm{width:26px;height:26px;border-radius:7px}
.dm-glow{position:absolute;width:520px;height:520px;border-radius:50%;background:var(--lp-accent);opacity:.16;filter:blur(80px);z-index:0;pointer-events:none}
/* ===== HERO по Г1–Г4: скелет-коридоры + поток, декор абсолютом ===== */
.dm-hero{padding:0;background:radial-gradient(110% 90% at 72% 34%,#1b3b34 0%,var(--lp-bg) 56%)}
.dm-canvas{position:relative;max-width:1240px;margin:0 auto;min-height:92vh;padding:40px 32px}
.z-back{z-index:1}.z-fig{z-index:2}.z-front{z-index:4}.z-top{z-index:5}
/* Г1: 3 коридора. Доли — частное мода (лево шире, центр под фигуру, право уже) */
/* Г6: 3 коридора собраны, без провалов */
.dm-grid{position:relative;z-index:3;display:grid;grid-template-columns:1fr 0.92fr 0.78fr;
  gap:20px;align-items:center;min-height:88vh}
/* Г3: левый коридор — ПОТОК сверху вниз */
.dm-col-left{display:flex;flex-direction:column;align-items:flex-start;gap:18px}
.dm-badge-top{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.06);
  border:1px solid var(--lp-border);border-radius:30px;padding:8px 16px;font-size:.78rem;color:var(--lp-text)}
.dm-badge-top .tick{color:var(--lp-accent);font-weight:800}
.dm-script{font-family:var(--lp-fscript,'Caveat',cursive);font-size:clamp(1.3rem,2.2vw,1.9rem);
  color:var(--lp-accent-2);transform:rotate(-4deg);margin-left:4px}
.dm-anchor-fill{font-family:var(--lp-fh);font-weight:800;font-size:clamp(2.8rem,6vw,5.2rem);
  line-height:.96;letter-spacing:-.03em;color:var(--lp-accent);margin:0}
.dm-h-rest{font-family:var(--lp-fb);font-size:clamp(1rem,1.5vw,1.2rem);font-weight:500;
  color:var(--lp-text);line-height:1.4;max-width:22em}
.dm-cta-zone{display:flex;align-items:center;gap:18px;margin-top:6px}
.dm-cta.round{width:124px;height:124px;border-radius:50%;padding:0;font-size:.88rem;line-height:1.2;text-align:center;flex:none}
.dm-note{font-size:.8rem;color:var(--lp-text-muted);max-width:16em;line-height:1.4}
/* центр: фигура-якорь (Г5: пропорции не ломаем) */
.dm-col-fig{position:relative;align-self:end;justify-self:center;width:100%;height:88vh;max-height:780px}
.dm-fglow{position:absolute;width:440px;height:440px;border-radius:50%;background:var(--lp-accent);opacity:.22;filter:blur(80px);left:50%;top:42%;transform:translate(-50%,-50%)}
.dm-col-fig img{position:relative;display:block;height:100%;width:100%;object-fit:contain;object-position:bottom center;filter:drop-shadow(0 30px 60px rgba(0,0,0,.55))}
/* anchor_outline (Г3: в ЦЕНТРАЛЬНОМ коридоре за фигурой, не в текст, не за край) */
.dm-col-fig .dm-anchor-outline{position:absolute;left:50%;top:36%;transform:translateX(-50%);
  font-family:var(--lp-fh);font-weight:800;font-size:clamp(3rem,7vw,6.5rem);line-height:.9;
  letter-spacing:.04em;text-transform:uppercase;white-space:nowrap;
  color:transparent;-webkit-text-stroke:1.3px var(--lp-text);opacity:.32;z-index:-1}
/* Г3: правый коридор — ПОТОК */
.dm-col-right{display:flex;flex-direction:column;gap:22px;align-items:flex-start}
.dm-subhead{font-size:1.02rem;color:var(--lp-text-muted);line-height:1.5;max-width:18em}
.dm-feats{list-style:none;display:flex;flex-direction:column;gap:12px}
.dm-feats li{display:flex;align-items:center;gap:11px;font-size:.95rem;color:var(--lp-text)}
.dm-mark{flex:none;width:13px;height:13px;border-radius:4px;transform:rotate(45deg)}
.dm-mark.fill{background:linear-gradient(135deg,var(--lp-accent),var(--lp-accent-dark));box-shadow:0 6px 16px rgba(1,212,154,.4)}
.dm-mark.hollow{background:transparent;border:1.5px solid var(--lp-text-muted)}
.dm-bill{position:absolute;width:62px;height:34px;border-radius:4px;background:linear-gradient(135deg,#1e5a4c,#0f3b32);border:1px solid var(--lp-border-strong);transform:rotate(-18deg);opacity:.8}
@media(max-width:900px){
  .dm-canvas{min-height:auto;padding:90px 24px 60px}
  .dm-grid{grid-template-columns:1fr;min-height:auto;gap:30px}
  .dm-col-fig{height:auto;order:5;align-self:start}.dm-col-fig img{height:auto;max-height:380px}
  .dm-anchor-fill{font-size:clamp(2.6rem,12vw,3.6rem)}
  .dm-anchor-outline{display:none}
}
/* stats */
.dm-stats{background:var(--lp-bg-deep);padding:clamp(44px,6vw,72px) 0}
.dm-stats-row{display:grid;grid-template-columns:repeat(4,1fr)}
.dm-stat{padding:14px 26px;border-left:1px solid var(--lp-border)}.dm-stat:first-child{border-left:none}
.dm-num{font-family:var(--lp-fh);font-weight:800;font-size:clamp(2.4rem,5vw,3.6rem);color:var(--lp-accent);display:block;line-height:1;margin-bottom:10px}
.dm-stat-l{font-size:.85rem;color:var(--lp-text-muted);line-height:1.4}
@media(max-width:760px){.dm-stats-row{grid-template-columns:1fr 1fr;gap:30px 0}.dm-stat:nth-child(odd){border-left:none}}
/* cards общие */
.dm-card{background:var(--lp-surface);border:1px solid var(--lp-border);border-radius:24px;padding:32px 28px}
.dm-card.feat,.dm-card.gain.teal{border-color:var(--lp-border-strong)}
.dm-card h3{font-family:var(--lp-fh);font-size:1.5rem;font-weight:700;color:var(--lp-text);margin-bottom:18px}
.dm-card h4{font-family:var(--lp-fb);font-size:1.1rem;font-weight:600;color:var(--lp-text);margin-bottom:10px}
.dm-card p{color:var(--lp-text-muted);font-size:.95rem}
.dm-card ul{list-style:none}.dm-card li{display:flex;gap:13px;align-items:flex-start;padding:11px 0;border-bottom:1px dashed var(--lp-border)}
.dm-card li:last-child{border-bottom:none}
.dm-card a{color:var(--lp-accent);font-weight:600;font-size:.9rem;display:inline-block;margin-top:14px;text-decoration:none}
/* problem */
.dm-problem{background:radial-gradient(70% 60% at 90% 85%,var(--lp-accent-soft),transparent 60%),var(--lp-bg)}
.dm-prob-grid{display:grid;grid-template-columns:1fr 1fr;gap:26px}
.dm-card.gain.teal{background:linear-gradient(160deg,rgba(18,90,78,.42),var(--lp-surface) 60%);position:relative;overflow:hidden}
.dm-card.gain.teal h3{color:var(--lp-accent-2)}
@media(max-width:820px){.dm-prob-grid{grid-template-columns:1fr}}
/* process */
.dm-h2{font-family:var(--lp-fh);font-size:clamp(2rem,4vw,3rem);font-weight:800;color:var(--lp-text);text-align:center}
.dm-sub{text-align:center;color:var(--lp-text-muted);margin:10px 0 36px}
.dm-cards3{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.dm-fnum{font-family:var(--lp-fh);font-size:2.6rem;font-weight:800;color:var(--lp-accent);opacity:.5;display:block;margin-bottom:8px}
.dm-card.feat{box-shadow:0 0 0 1px var(--lp-border-strong),0 20px 50px rgba(1,212,154,.12)}
.dm-benefits{margin-top:34px;background:var(--lp-surface);border:1px solid var(--lp-border);border-radius:20px;padding:26px 30px}
.dm-benefits h4{font-family:var(--lp-fb);font-weight:600;color:var(--lp-text);margin-bottom:14px}
.dm-benefits ul{list-style:none;display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.dm-benefits li{display:flex;gap:11px;color:var(--lp-text-muted);font-size:.95rem}
@media(max-width:820px){.dm-cards3{grid-template-columns:1fr}.dm-benefits ul{grid-template-columns:1fr}}
/* cases */
.dm-bg-deep{background:var(--lp-bg-deep)}
.dm-cases.teal-zone,.dm-trust.teal-zone{background:var(--lp-surface-2)}
.dm-trust.teal-zone .dm-card{background:rgba(14,17,23,.4)}
.dm-cases .dm-card{background:rgba(14,17,23,.4)}
.dm-cards2{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:30px}
.dm-result{color:var(--lp-accent-2)!important;font-weight:600;margin:6px 0 14px}
.dm-ba{display:flex;flex-direction:column;gap:8px}
.dm-ba-step{font-size:.85rem;color:var(--lp-text-muted);padding-left:18px;position:relative}
.dm-ba-step:before{content:"◆";position:absolute;left:0;color:var(--lp-accent);font-size:.6rem;top:3px}
.dm-quote{font-family:var(--lp-fh);font-style:italic;font-size:1.5rem;color:var(--lp-text);text-align:center;max-width:30em;margin:40px auto 0;line-height:1.4}
.dm-quote cite{display:block;font-family:var(--lp-fb);font-style:normal;font-size:.9rem;color:var(--lp-accent);margin-top:14px}
@media(max-width:820px){.dm-cards2{grid-template-columns:1fr}}
/* trust */
.dm-cards4{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:30px}
.dm-video{margin:34px auto 0;display:flex;align-items:center;gap:14px;justify-content:center;color:var(--lp-text)}
.dm-play{width:46px;height:46px;border-radius:50%;background:var(--lp-accent);color:var(--lp-on-accent);display:grid;place-items:center;box-shadow:0 14px 30px rgba(1,212,154,.4)}
@media(max-width:820px){.dm-cards4{grid-template-columns:1fr 1fr}}
/* testimonials */
.dm-chats{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:30px}
.dm-chat{background:var(--lp-surface);border:1px solid var(--lp-border);border-radius:18px 18px 18px 4px;padding:20px 22px}
.dm-chat p{color:var(--lp-text);font-size:.95rem}
.dm-time{display:block;text-align:right;font-size:.72rem;color:var(--lp-text-muted);margin-top:10px}
.dm-socials{display:flex;gap:12px;justify-content:center;margin-top:30px}
.dm-social{border:1px solid var(--lp-border-strong);color:var(--lp-accent);border-radius:30px;padding:10px 22px;font-weight:600;font-size:.9rem;text-decoration:none}
.dm-social:hover{background:var(--lp-accent-soft)}
@media(max-width:820px){.dm-chats{grid-template-columns:1fr}}
"""
    return html, css
