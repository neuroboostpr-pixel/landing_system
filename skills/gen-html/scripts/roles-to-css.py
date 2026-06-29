#!/usr/bin/env python3
"""gen-html — ДВИЖОК: objects.yaml (роли) → objects.css (CSS-классы).

Цель: gen-html НЕ выдумывает вид кнопки/фигуры/карточки. Базовый CSS каждой роли
генерится ДЕТЕРМИНИРОВАННО из `visual`/`size`/`type_props` роли — через токены.
Агент только РАСПОЛАГАЕТ (composition) и НАПОЛНЯЕТ (контент прототипа).
Это даёт соответствие ДС + переносимость: тот же objects.yaml на другой нише → тот же CSS.

Класс роли: `.lp-{role}` (напр. `.lp-cta-circle`, `.lp-figure-cutout`).
HTML агента вешает `.lp-{role}` на элемент роли + свой класс для расположения.

Извлекаются (надёжно парсимое):
  visual: bg/color/border/radius/shadow/opacity (+ ключи: КРУГ→50%, контур→border, СПЛОШНОЙ→fill,
          ВЫРЕЗ/cutout→object-fit:contain+drop-shadow, плашка/карточка→bg+radius)
  size:   w/h/padding/max_width/gap (токены или px)
  type_props: font/size/weight/case/line_height/letter_spacing/align

Usage:
  roles-to-css.py <moods_dir>            # сгенерить objects.css для всех мудов
  roles-to-css.py <moods_dir>/<mood>     # для одного мода
Выход: рядом с objects.yaml пишется objects.css.
"""
import re, sys
from pathlib import Path

TOKEN = re.compile(r'--[a-z0-9-]+')


def tok(val):
    """вернуть var(--token) если в строке есть токен, иначе сырое значение (px/число/слово)."""
    m = TOKEN.search(val)
    if m:
        return f'var({m.group(0)})'
    # сырое значение: px / rem / число / hex запрещён (вид только через токены) → пропускаем hex
    v = val.strip().strip('"').strip("'")
    if re.match(r'^[\d.]+(px|rem|em|%|ch)?$', v):
        return v
    return None


def field(block, key):
    """достать значение key: "..." из inline-словаря visual/size/type_props.
    (?<![\\w-]) — граница слева: ключ 'h' НЕ матчит 'widt-h:'/'max_widt-h:' (была причина height:40ch у subhead)."""
    b = r'(?<![\w-])'
    m = re.search(rf'{b}{key}:\s*"([^"]*)"', block) or re.search(rf'{b}{key}:\s*([^,}}\n]+)', block)
    if not m:
        return None
    v = m.group(1)
    v = re.sub(r'\s+#.*$', '', v)   # обрезать inline-комментарий YAML (#...) — иначе «row # ... column» ломает парс
    return v.strip()


def role_css(role, body):
    vis = (re.search(r'visual:\s*\{([^}]*)\}', body) or [None, ''])[1] if 'visual' in body else ''
    if not vis:
        vm = re.search(r'visual:\n((?:\s{6,}.*\n)+)', body)
        vis = vm.group(1) if vm else ''
    size = (re.search(r'size:\s*\{([^}]*)\}', body) or [None, ''])[1]
    tp = (re.search(r'type_props:\s*\{([^}]*)\}', body) or [None, ''])[1]
    decls = []

    # ── ГРУППА-ОБЪЕКТ: members_layout → flex-контейнер (члены внутри группы) ──
    ml = re.search(r'members_layout:\n((?:\s{6,}.*\n)+)', body)
    if ml:
        mlb = ml.group(1)
        flow = field(mlb, 'flow') or 'row'
        gap = tok(field(mlb, 'gap') or '') or '14px'
        decls.append('display:flex')
        decls.append('flex-direction:' + ('column' if 'column' in flow else 'row'))
        decls.append(f'gap:{gap}')
        ali = re.search(r'align:\s*\{([^}]*)\}', mlb)
        if ali:
            hm = {'start': 'flex-start', 'center': 'center', 'end': 'flex-end'}
            vm = {'top': 'flex-start', 'center': 'center', 'bottom': 'flex-end'}
            h = field(ali.group(1), 'h'); v = field(ali.group(1), 'v')
            # row: v→align-items, h→justify-content; column наоборот
            if 'column' in flow:
                if h in hm: decls.append(f'align-items:{hm[h]}')
                if v in vm: decls.append(f'justify-content:{vm[v]}')
            else:
                if v in vm: decls.append(f'align-items:{vm[v]}')
                if h in hm: decls.append(f'justify-content:{hm[h]}')
        # VISUAL группы (подложка-карточка: bg/radius/shadow/padding) — чтоб не сливалась с фоном
        gbg = field(vis, 'bg')
        if gbg and 'нет' not in gbg:
            gv = tok(gbg)
            if gv: decls.append(f'background:{gv}')
        grad = field(vis, 'radius')
        if grad:
            rv = tok(grad)
            if rv: decls.append(f'border-radius:{rv}')
        gsh = field(vis, 'shadow') or field(vis, 'glow')
        if gsh:
            sv = TOKEN.search(gsh)
            if sv: decls.append(f'box-shadow:var({sv.group(0)})')
        if decls and any(x.startswith('background') for x in decls):
            decls.append('padding:18px')   # карточка-подложка нуждается в внутр. отступе
        return f'.lp-{role}{{' + ';'.join(decls) + '}'

    # ── VISUAL ──
    bg = field(vis, 'bg')
    if bg and 'нет' not in bg and 'контур' not in bg:
        v = tok(bg)
        if v: decls.append(f'background:{v}')
    if bg and ('контур' in bg or 'нет' in bg):
        decls.append('background:transparent')
    color = field(vis, 'color')
    if color:
        v = tok(color)
        if v: decls.append(f'color:{v}')
    border = field(vis, 'border')
    if border and 'нет' not in border:
        bt = TOKEN.search(border)
        w = re.search(r'([\d.]+px)', border)
        if bt and w:
            decls.append(f'border:{w.group(1)} solid var({bt.group(0)})')
    radius = field(vis, 'radius')
    if radius:
        # КРУГ — только явный маркер: 50% или слово «круг» ОТДЕЛЬНО (не подстрока
        # «скруглённый/скругление» — там это про радиус-токен, не круглую форму).
        if '50%' in radius or 'КРУГ' in radius or re.search(r'\bкруг\b', radius):
            decls.append('border-radius:50%')
        else:
            v = tok(radius)
            if v: decls.append(f'border-radius:{v}')
    shadow = field(vis, 'shadow') or field(vis, 'glow')
    if shadow:
        v = TOKEN.search(shadow)
        if v: decls.append(f'box-shadow:var({v.group(0)})')
    opacity = field(vis, 'opacity')
    if opacity:
        o = re.search(r'([\d.]+)', opacity)
        if o: decls.append(f'opacity:{o.group(1)}')

    # cutout-фигура: ВЫРЕЗ → object-fit:contain + drop-shadow, НЕ cover/box
    if re.search(r'ВЫРЕЗ|cutout', body):
        decls.append('object-fit:contain')
        ds = re.search(r'drop-shadow\([^)]*\)', body)
        if ds: decls.append(f'filter:{ds.group(0)}')

    # ── SIZE ──
    for k, css in [('w', 'width'), ('h', 'height'), ('padding', 'padding'),
                   ('max_width', 'max-width'), ('gap', 'gap')]:
        val = field(size, k)
        if val:
            v = tok(val)
            if v: decls.append(f'{css}:{v}')

    # ── TYPE_PROPS ──
    f = field(tp, 'font')
    if f:
        v = TOKEN.search(f)
        if v: decls.append(f'font-family:var({v.group(0)})')
    s = field(tp, 'size')
    if s:
        v = tok(s)
        if v: decls.append(f'font-size:{v}')
    w = field(tp, 'weight')
    if w and w.strip('"').isdigit():
        decls.append(f'font-weight:{w.strip()}')
    case = field(tp, 'case')
    if case and 'uppercase' in case:
        decls.append('text-transform:uppercase')
    lh = field(tp, 'line_height')
    if lh:
        v = tok(lh)
        if v: decls.append(f'line-height:{v}')
    ls = field(tp, 'letter_spacing')
    if ls:
        v = tok(ls) or (re.search(r'([\d.]+em)', ls) or [None])[0]
        if v: decls.append(f'letter-spacing:{v}')
    align = field(tp, 'align')
    if align and 'center' in align:
        decls.append('text-align:center')

    if not decls:
        return None
    return f'.lp-{role}{{' + ';'.join(decls) + '}'


def gen_one(mood_dir):
    obj = mood_dir / 'objects.yaml'
    if not obj.exists():
        return
    text = obj.read_text(encoding='utf-8')
    roles = re.findall(r'^  ([a-z][a-z0-9-]+):\n(.*?)(?=^  [a-z]|\Z)', text, re.DOTALL | re.M)
    lines = [f'/* AUTO-GENERATED от objects.yaml движком roles-to-css.py — НЕ редактировать руками.',
             f' * Базовый вид каждой роли (.lp-<role>). gen-html добавляет ТОЛЬКО расположение. */',
             f'html[data-mood="{mood_dir.name}"] :where(/* scope */){{}}']
    out = []
    for role, body in roles:
        css = role_css(role, body)
        if css:
            out.append(f'html[data-mood="{mood_dir.name}"] ' + css)

    # ── PER-BLOCK переопределение групп (placements[block].members_layout) ──
    # надёжно через yaml.safe_load (regex по вложенному yaml хрупок). Класс .lp-{role}--{block}.
    try:
        import yaml
        data = yaml.safe_load(text) or {}
        for role, b in (data.get('roles') or {}).items():
            if not isinstance(b, dict) or 'members_layout' not in b:
                continue
            for block, pl in (b.get('placements') or {}).items():
                ml = (pl or {}).get('members_layout') if isinstance(pl, dict) else None
                if not isinstance(ml, dict):
                    continue
                d2 = []
                fl = str(ml.get('flow', '')).strip()
                if fl:
                    d2.append('flex-direction:' + ('column' if fl == 'column' else 'row'))
                a = ml.get('align') or {}
                hm = {'start': 'flex-start', 'center': 'center', 'end': 'flex-end'}
                vm = {'top': 'flex-start', 'center': 'center', 'bottom': 'flex-end'}
                if fl == 'column':
                    if a.get('h') in hm: d2.append(f'align-items:{hm[a["h"]]}')
                else:
                    if a.get('v') in vm: d2.append(f'align-items:{vm[a["v"]]}')
                if d2:
                    out.append(f'html[data-mood="{mood_dir.name}"] .lp-{role}--{block}{{' + ';'.join(d2) + '}')
    except Exception as e:
        print(f'  warn: per-block groups skipped: {e}', file=sys.stderr)

    (mood_dir / 'objects.css').write_text('\n'.join(lines[:2] + out) + '\n', encoding='utf-8')
    print(f'{mood_dir.name}: {len(out)} ролей/правил → objects.css')


def main():
    if len(sys.argv) < 2:
        print('usage: roles-to-css.py <moods_dir|mood_dir>', file=sys.stderr); return 2
    p = Path(sys.argv[1])
    if (p / 'objects.yaml').exists():
        gen_one(p)
    else:
        for d in sorted(x for x in p.iterdir() if x.is_dir() and (x / 'objects.yaml').exists()):
            gen_one(d)
    return 0


if __name__ == '__main__':
    sys.exit(main())
