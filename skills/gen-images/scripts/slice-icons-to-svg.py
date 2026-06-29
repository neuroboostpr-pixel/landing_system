#!/usr/bin/env python3
"""gen-images A2 — нарезка ЛИСТА с иконками (сетка на белом фоне) → отдельные PNG → SVG (vtracer).

Лист от codex: N иконок ч/б на белом, сеткой (строки×колонки). Скрипт:
  1. детектит bbox-ы каждой иконки (связные тёмные области на белом фоне),
  2. вырезает каждую в квадрат с полями,
  3. трассирует в SVG (vtracer),
  4. именует по порядку (icon-1.svg … icon-N.svg) — сопоставление концепция-i ↔ icon-i.

Usage:
  slice-icons-to-svg.py <sheet.png> --out <dir> [--expect N] [--concepts "a;b;c"]
  --expect N    ожидаемое число иконок (для сверки/упорядочивания по сетке)
  --concepts    через ';' — назвать файлы по концепциям (icon-1-{slug}.svg)
Выход: <out>/icon-*.png (вырезы) + <out>/icon-*.svg (трассировка) + manifest.json.
"""
import argparse, json, os, re, sys
from pathlib import Path
from PIL import Image


def find_icon_bboxes(im, white_thresh=235, min_area=400):
    """найти bbox-ы тёмных объектов на белом фоне. Возвращает список (x0,y0,x1,y1),
    упорядоченный по СЕТКЕ (сверху-вниз, слева-направо)."""
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    # маска: тёмное = объект
    visited = [[False] * w for _ in range(h)]
    boxes = []
    import collections
    for sy in range(h):
        for sx in range(w):
            if visited[sy][sx] or px[sx, sy] >= white_thresh:
                continue
            # BFS связной области
            q = collections.deque([(sx, sy)])
            visited[sy][sx] = True
            x0 = x1 = sx; y0 = y1 = sy; area = 0
            while q:
                cx, cy = q.popleft()
                area += 1
                x0, x1 = min(x0, cx), max(x1, cx)
                y0, y1 = min(y0, cy), max(y1, cy)
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
                    nx, ny = cx+dx, cy+dy
                    if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx] and px[nx, ny] < white_thresh:
                        visited[ny][nx] = True
                        q.append((nx, ny))
            if area >= min_area:
                boxes.append((x0, y0, x1+1, y1+1))
    # склеить близкие bbox-ы (части одной иконки) — по пересечению с расширением
    boxes = _merge_close(boxes, gap=max(w, h)//40)
    # упорядочить по сетке: кластеризовать по Y (строки), внутри строки по X
    boxes.sort(key=lambda b: (b[1], b[0]))
    rows, cur, last_y = [], [], None
    rowtol = max(h//12, 20)
    for b in boxes:
        if last_y is None or abs(b[1]-last_y) <= rowtol:
            cur.append(b)
        else:
            rows.append(sorted(cur, key=lambda x: x[0])); cur=[b]
        last_y = b[1]
    if cur: rows.append(sorted(cur, key=lambda x: x[0]))
    return [b for row in rows for b in row]


def _merge_close(boxes, gap):
    merged = True
    while merged:
        merged = False
        out = []
        used = [False]*len(boxes)
        for i in range(len(boxes)):
            if used[i]: continue
            x0,y0,x1,y1 = boxes[i]
            for j in range(i+1, len(boxes)):
                if used[j]: continue
                a0,b0,a1,b1 = boxes[j]
                if a0 <= x1+gap and x0 <= a1+gap and b0 <= y1+gap and y0 <= b1+gap:
                    x0,y0,x1,y1 = min(x0,a0),min(y0,b0),max(x1,a1),max(y1,b1)
                    used[j] = True; merged = True
            out.append((x0,y0,x1,y1)); used[i] = True
        boxes = out
    return boxes


def slugify(s):
    s = re.sub(r'[^a-z0-9а-я ]', '', s.lower()).strip()
    return re.sub(r'\s+', '-', s)[:30] or 'icon'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sheet')
    ap.add_argument('--out', required=True)
    ap.add_argument('--expect', type=int, default=0)
    ap.add_argument('--concepts', default='')
    ap.add_argument('--pad', type=int, default=24, help='поля вокруг иконки (px)')
    a = ap.parse_args()

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    im = Image.open(a.sheet).convert("RGB")
    boxes = find_icon_bboxes(im)
    if a.expect and len(boxes) != a.expect:
        print(f"⚠ найдено {len(boxes)} иконок, ожидалось {a.expect} — проверь сетку/пороги", file=sys.stderr)

    concepts = [c.strip() for c in a.concepts.split(';') if c.strip()] if a.concepts else []
    try:
        import vtracer
    except ImportError:
        print("vtracer не установлен (pip install vtracer)", file=sys.stderr); return 2

    manifest = []
    for i, (x0,y0,x1,y1) in enumerate(boxes, 1):
        crop = im.crop((max(0,x0-a.pad), max(0,y0-a.pad), x1+a.pad, y1+a.pad))
        # квадрат на белом
        side = max(crop.size)
        sq = Image.new("RGB", (side, side), (255,255,255))
        sq.paste(crop, ((side-crop.width)//2, (side-crop.height)//2))
        slug = slugify(concepts[i-1]) if i-1 < len(concepts) else ''
        base = f"icon-{i}" + (f"-{slug}" if slug else "")
        png = out / f"{base}.png"; svg = out / f"{base}.svg"
        sq.save(png)
        vtracer.convert_image_to_svg_py(str(png), str(svg), colormode='binary',
                                        filter_speckle=4, path_precision=6)
        manifest.append({"index": i, "concept": concepts[i-1] if i-1 < len(concepts) else None,
                         "png": png.name, "svg": svg.name, "bbox": [x0,y0,x1,y1]})
        print(f"icon-{i}: {png.name} → {svg.name}" + (f"  «{concepts[i-1]}»" if i-1 < len(concepts) else ""))

    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\ndone: {len(boxes)} иконок → {out}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
