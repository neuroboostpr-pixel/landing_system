#!/usr/bin/env python3
"""gen-images — вырез фона (rembg) + FEATHER краёв (обязательный шаг).

Резкий край rembg = видимая «вырезанность» + остатки фона по контуру. Feather убирает их:
  alpha → эрозия (срез каймы) → порог (убрать полупрозрачную кайму) → gaussian-blur (мягкий край).
RGB не трогаем — только alpha.

Использование:
  python cutout-feather.py <src.png|dir> --out <out_dir> [--no-feather] [--preview] [--webp]
  python cutout-feather.py inbox/ --out processed/ --preview

Параметры feather (по умолчанию — «широкий», убирает остатки фона):
  erode_size=7   (MinFilter, ≈ срез 3px)
  alpha_floor=40 (отсечь полупрозрачную кайму)
  blur_radius=3.0 (мягкость края)
"""
import argparse, os, sys
from PIL import Image, ImageFilter


def feather_edges(im, radius=3.0, erode_size=7, alpha_floor=40):
    """Сглаживание края выреза. Только alpha; RGB не трогаем."""
    im = im.convert('RGBA')
    r, g, b, a = im.split()
    if erode_size and erode_size >= 3:
        a = a.filter(ImageFilter.MinFilter(erode_size))     # срезать кайму фона
    if alpha_floor:
        a = a.point(lambda v: 0 if v < alpha_floor else v)  # убрать полупрозрачную кайму
    a = a.filter(ImageFilter.GaussianBlur(radius))          # feather
    im.putalpha(a)
    return im


def cut_one(remove_fn, sess, src, out_dir, crop=True, feather=True, preview=False, webp=False):
    name = os.path.splitext(os.path.basename(src))[0]
    im = Image.open(src).convert('RGBA')
    res = remove_fn(im, session=sess)
    if feather:
        res = feather_edges(res)
    if crop:
        bbox = res.getbbox()
        if bbox:
            res = res.crop(bbox)
    ext = 'webp' if webp else 'png'
    out = os.path.join(out_dir, name + '.' + ext)
    res.save(out, 'WEBP', quality=90, method=6) if webp else res.save(out)
    print('cut', os.path.basename(src), '->', os.path.basename(out), res.size,
          '(feathered)' if feather else '(sharp)')
    if preview:
        for bg, tag in [((240, 240, 240, 255), 'light'), ((20, 24, 29, 255), 'dark')]:
            c = Image.new('RGBA', res.size, bg); c.alpha_composite(res)
            p = os.path.join(out_dir, name + '-preview-' + tag + '.png')
            c.convert('RGB').save(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', help='файл или папка')
    ap.add_argument('--out', required=True)
    ap.add_argument('--model', default='isnet-general-use')
    ap.add_argument('--no-crop', action='store_true')
    ap.add_argument('--no-feather', action='store_true', help='НЕ сглаживать края (по умолчанию feather вкл)')
    ap.add_argument('--preview', action='store_true', help='preview на тёмном+светлом фоне (оценка краёв)')
    ap.add_argument('--webp', action='store_true')
    a = ap.parse_args()

    from rembg import remove, new_session
    sess = new_session(a.model)
    os.makedirs(a.out, exist_ok=True)

    if os.path.isdir(a.src):
        files = sorted(f for f in os.listdir(a.src) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')))
        srcs = [os.path.join(a.src, f) for f in files]
    else:
        srcs = [a.src]

    for s in srcs:
        cut_one(remove, sess, s, a.out, crop=not a.no_crop, feather=not a.no_feather,
                preview=a.preview, webp=a.webp)
    print('done:', len(srcs), 'file(s)')


if __name__ == '__main__':
    main()
