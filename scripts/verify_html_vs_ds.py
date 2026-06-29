#!/usr/bin/env python3
"""verify_html_vs_ds — проверка соответствия composed.html дизайн-системе (ДС).

Архитектура «один факт — одно место» (2026-06-20): objects.yaml = вид через токены,
metrics.css = токены размеров, composition = ref+расположение. HTML обязан использовать
ТОКЕНЫ (var()), а не голые значения, и реализовать роли из composition.

Этот гейт ловит РАССИНХРОН HTML↔ДС, который verify_tokens (цвета) и premium (эффекты) не видят:
  1. КАЖДЫЙ токен размера из {mood}/metrics.css ДОЛЖЕН использоваться в HTML через var(--token).
     Токен объявлен, но не использован → размер где-то захардкожен → рассинхрон. (FAIL)
  2. КАЖДАЯ роль из {mood}/compositions/*.yaml с `ref:` должна иметь след в HTML
     (класс/элемент по имени роли или её алиасу). Роль в композиции есть, в HTML нет → расположение
     не реализовано. (WARN — имя класса может не совпадать с ролью, поэтому не hard.)
  3. Голые размеры рядом с токенизируемым свойством (width/height: NNNpx) в hero-блоках, когда
     для них есть токен в metrics.css → подозрение на хардкод. (WARN)

Usage: verify_html_vs_ds.py <project_dir>
Exit: 0 PASS · 1 FAIL · 2 нет файлов.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

# токены, которые НЕ обязаны быть в hero composed (служебные/для др. секций) — не фейлим за них
OPTIONAL_TOKENS = {
    "--header-h",      # шапка может верстаться без явного var (high-level)
    "--plate-w", "--plate-radius",  # плашка — могут быть в фоне; warn не fail
    "--logo-size", "--logo-sub-size",
}


def find_metrics_tokens(mood_dir: Path) -> set[str]:
    f = mood_dir / "metrics.css"
    if not f.exists():
        return set()
    return set(re.findall(r"(--[a-z0-9-]+)\s*:", f.read_text(encoding="utf-8")))


def find_composition_refs(mood_dir: Path) -> set[str]:
    refs: set[str] = set()
    comp = mood_dir / "compositions"
    if not comp.is_dir():
        return refs
    for y in comp.glob("*.yaml"):
        txt = y.read_text(encoding="utf-8")
        # ref: role  ИЛИ  ref: [role1, role2]
        for m in re.findall(r"ref:\s*\[([^\]]+)\]", txt):
            refs.update(r.strip() for r in m.split(","))
        for m in re.findall(r"ref:\s*([a-z][a-z0-9-]+)\s*$", txt, re.MULTILINE):
            refs.add(m.strip())
    return refs


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: verify_html_vs_ds.py <project_dir>", file=sys.stderr)
        return 2
    proj = Path(sys.argv[1])
    html = proj / "07b_COMPOSED" / "composed.html"
    moods_dir = proj / "05_ДИЗАЙН-СИСТЕМА" / "moods"

    # 0) активный прототип определяется ФЛАГОМ meta.active: true (ровно один), не именем файла
    proto_dir = proj / "07_ПРОТОТИП"
    if proto_dir.is_dir():
        actives = [p.name for p in proto_dir.glob("prototype-*.yaml")
                   if re.search(r"active:\s*true", p.read_text(encoding="utf-8"))]
        if len(actives) == 0:
            print("FAIL: ни один prototype-*.yaml не помечен `meta.active: true` — флоу не знает, какой прототип брать.", file=sys.stderr)
            return 1
        if len(actives) > 1:
            print(f"FAIL: несколько активных прототипов ({', '.join(actives)}) — `active: true` должен быть РОВНО у одного.", file=sys.stderr)
            return 1
    if not html.exists():
        print(f"нет файла: {html}", file=sys.stderr)
        return 2
    if not moods_dir.is_dir():
        print("нет папки moods/ — ДС не настроена, пропуск (fallback reference-driven)", file=sys.stderr)
        return 0

    html_txt = html.read_text(encoding="utf-8")
    used_vars = set(re.findall(r"var\((--[a-z0-9-]+)", html_txt))

    fails: list[str] = []
    warns: list[str] = []

    for mood_dir in sorted(p for p in moods_dir.iterdir() if p.is_dir()):
        mood = mood_dir.name
        # 1) токены metrics → должны использоваться
        tokens = find_metrics_tokens(mood_dir)
        for t in sorted(tokens):
            if t in used_vars:
                continue
            if t in OPTIONAL_TOKENS:
                warns.append(f"[{mood}] токен {t} объявлен в metrics.css, но не используется в HTML (опционально)")
            else:
                fails.append(f"[{mood}] токен размера {t} НЕ используется в HTML через var() — размер захардкожен (рассинхрон ДС↔HTML)")
        # 2) роли composition → след в HTML (по имени роли/частям/алиасам)
        # алиасы: имя класса в HTML может не совпадать с ролью (figure-center → .hm-center img)
        ROLE_ALIASES = {
            "figure-center": ["center", "cutout", "img"],
            "figure-cutout": ["cutout", "figure", "img"],
            "diamond-decor": ["dmd", "diamond"],
            "announcement-bar": ["ann-bar", "ann"],
            "caption-eyebrow": ["eyebrow"],
            "cta-circle": ["cta"],
            "cta-note": ["cta-note", "note"],
            "trust-item": ["trust"],
            "feature": ["feat"],
            "logo-text": ["logo"],
            "nav-menu": ["menu", "nav"],
            "head-cta": ["head-cta"],
            "brand-scribble": ["scribble", "acc"],
            "hotspot-marker": ["marker"],
            "stat-card": ["stat"],
            "bg-grain": ["grain"],
            "section-bg": ["hero", "nav"],
        }
        refs = find_composition_refs(mood_dir)
        for role in sorted(refs):
            stem = role.split("-")[0]
            aliases = ROLE_ALIASES.get(role, []) + [role, stem]
            if any(re.search(r'class="[^"]*' + re.escape(a), html_txt) for a in aliases) or role in html_txt:
                continue
            warns.append(f"[{mood}] роль '{role}' есть в composition, но не найдена в HTML (проверь реализацию расположения)")

    # 3) пустые placeholder/иконки на финале = дефект (читается как «дёшево/плоско»)
    PLACEHOLDER_PAT = [
        (r'>\s*фото\s+эксперт', "текстовый placeholder «фото эксперта» вместо реального фото/выреза"),
        (r'>\s*\[SLOT[: ]', "незаполненный [SLOT: …] (gen-images не отработал)"),
        (r'>\s*placeholder\s*<', "литеральный placeholder в контенте"),
    ]
    for pat, msg in PLACEHOLDER_PAT:
        if re.search(pat, html_txt, re.IGNORECASE):
            fails.append(f"placeholder: {msg} — вставить фото/иконку через gen-images ДО закрытия этапа")
    # пустые иконки-слоты: <span class="...ic|icon|penta..."></span> без вложенного <svg>/<img>/символа.
    # Иконка фиши/маркера должна нести SVG по смыслу, а не быть голым цветным кружком.
    empty_icons = re.findall(r'<(?:span|i|div)\s+class="[^"]*\b(?:ic|icon|feat-ic|penta)\b[^"]*"\s*>\s*</(?:span|i|div)>', html_txt)
    if len(empty_icons) >= 3:
        fails.append(f"пустые иконки: {len(empty_icons)} иконок-слотов без <svg> (голые кружки/фигуры) — "
                     f"вставить SVG ПО СМЫСЛУ через gen-images (пустой кружок = «дёшево»)")
    # счётчик inline-svg: на лендинг с иконками-фишами должно быть достаточно реальных SVG
    svg_count = len(re.findall(r'<svg', html_txt))
    if svg_count == 0 and empty_icons:
        fails.append("0 inline <svg> при наличии иконочных слотов — иконки не сгенерированы (gen-images пропущен).")

    # .ph placeholder-плашки на финале (До/После, видео, круг-фото) — должны быть заполнены или стилизованы
    ph_blocks = re.findall(r'class="ph\b[^"]*"', html_txt)
    if len(ph_blocks) >= 3:
        fails.append(f".ph placeholder: {len(ph_blocks)} плашек-заглушек на финале — заполнить визуалом (gen-images) "
                     f"или стилизовать (силуэт/градиент), не серая пустая плашка.")

    # cutout-фигура в object-fit:cover = обрезана в бокс вместо выреза с наездом.
    # если фигура — прозрачный PNG (cutout/figure в классе), cover её «запирает» в прямоугольник.
    for nm, body in re.findall(r'\.([a-z0-9-]*(?:figure|cutout)[a-z0-9-]*)\s*\{([^}]*)\}', html_txt):
        if re.search(r'object-fit:\s*cover', body):
            fails.append(f"фигура .{nm}: object-fit:cover обрезает вырез в прямоугольный бокс — для cutout-PNG "
                         f"нужен object-fit:contain + drop-shadow + наезд (как figure-cutout в ДС).")

    # h1-гигант на длинный текст = «стена текста». Кегль ≥5rem + длинный H1 = warning.
    for tdir in [p for p in (moods_dir.iterdir() if moods_dir.is_dir() else [])]:
        typ = tdir / "typography.css"
        if not typ.is_dir() and typ.exists():
            mm = re.search(r'--fs-h1:\s*clamp\([^,]+,[^,]+,\s*([\d.]+)rem', typ.read_text(encoding="utf-8"))
            if mm and float(mm.group(1)) >= 5:
                # есть ли длинный H1 (>40 симв) в HTML?
                h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', html_txt, re.DOTALL)
                long_h1 = any(len(re.sub(r'<[^>]+>', '', h)) > 40 for h in h1s)
                if long_h1:
                    warns.append(f"[{tdir.name}] --fs-h1 до {mm.group(1)}rem (гигант) + длинный заголовок (>40 симв) = "
                                 f"риск «стена текста». Гигант-дисплей — для коротких/расколотых слов.")

    # 4) ВСЕ объекты СТРОГО по visual роли objects.yaml (не только кнопки).
    #    Для каждой роли с visual → найти её CSS-класс(ы) в HTML и сверить ПРОВЕРЯЕМЫЕ признаки вида:
    #    контур vs заливка · круг/pill (radius) · наличие тени/glow · фон-плашка.
    #    Эвристика (нельзя сверить всё), но грубые расхождения ДС↔HTML ловит.
    for mood_dir in sorted(p for p in moods_dir.iterdir() if p.is_dir()):
        obj = mood_dir / "objects.yaml"
        if not obj.exists():
            continue
        otext = obj.read_text(encoding="utf-8")
        mood = mood_dir.name
        # все роли верхнего уровня (2 пробела отступ) с их телом
        roles = re.findall(r'^  ([a-z][a-z0-9-]+):\n(.*?)(?=^  [a-z]|\Z)', otext, re.DOTALL | re.MULTILINE)
        for role, body in roles:
            vm = re.search(r'visual:\s*\{([^}]*)\}', body) or re.search(r'visual:\n((?:\s{6}.*\n)+)', body)
            if not vm:
                continue
            vis = vm.group(1)
            aliases = ROLE_ALIASES.get(role, []) + [role, role.split("-")[0]]
            # собрать CSS-тело классов HTML, относящихся к роли (по алиасам, default-состояние)
            css_bodies = []
            for a in aliases:
                for nm, cb in re.findall(r'\.([a-z0-9-]*' + re.escape(a) + r'[a-z0-9-]*)\s*\{([^}]*)\}', html_txt):
                    if ':hover' in nm or ':' in nm:
                        continue
                    css_bodies.append((nm, cb))
            if not css_bodies:
                continue
            css_all = " ".join(cb for _, cb in css_bodies)
            # тело СТРОГО правила .lp-<role> (точное имя роли) — для проверки заливки контура.
            # (css_all по широким алиасам ловит чужие классы → ложные срабатывания, напр.
            #  circle-photo с bg:accent приписывался cta-outline.)
            exact = [cb for nm, cb in css_bodies if nm == f'lp-{role}']
            css_exact = " ".join(exact)
            # признак: роль КОНТУРНАЯ (bg нет + border) → в HTML не должно быть background:accent (default)
            is_outline = bool(re.search(r'(контур|bg:\s*"?нет)', vis)) and 'border' in vis
            if is_outline and re.search(r'background:\s*var\(--lp-accent\)(?!-)', css_exact):
                fails.append(f"[{mood}] роль '{role}' в ДС КОНТУРНАЯ (bg нет, border), а в HTML ЗАЛИВАЕТСЯ accent — вид не соответствует ДС.")
            # признак: КНОПКА со сплошной заливкой accent → в HTML фон accent (не прозрачный).
            #   Только для ролей-кнопок и точного --lp-accent СПЛОШНОЙ (не accent-soft).
            is_button = bool(re.search(r'type:\s*\[[^\]]*кнопка', body))
            wants_fill = is_button and bool(re.search(r'bg:\s*"?--lp-accent\s+СПЛОШН|bg:\s*"?--lp-accent\s*\(зел|bg:\s*"?--lp-accent СПЛОШНОЙ', vis))
            if wants_fill and css_bodies and not re.search(r'background:\s*var\(--lp-accent\)(?!-)', css_all):
                fails.append(f"[{mood}] кнопка '{role}' в ДС со СПЛОШНОЙ заливкой accent, а в HTML фон не accent — вид не соответствует ДС.")
            # признак: роль-КРУГ (radius 50%) → в HTML border-radius:50%
            wants_circle = bool(re.search(r'radius:\s*"?50%|КРУГ', vis))
            if wants_circle and css_bodies and not re.search(r'border-radius:\s*50%', css_all):
                fails.append(f"[{mood}] роль '{role}' в ДС = КРУГ (radius 50%), а в HTML не круглая — вид не соответствует ДС.")

    print("── verify_html_vs_ds ──")
    for w in warns:
        print(f"  ⚠  {w}")
    for f in fails:
        print(f"  ✗  {f}")
    if not fails:
        print(f"PASS: HTML соответствует ДС (токены используются). warns: {len(warns)}")
        return 0
    print(f"\nFAIL: {len(fails)} рассинхрон(ов) ДС↔HTML. Размеры брать из metrics.css через var(), не хардкодить.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
