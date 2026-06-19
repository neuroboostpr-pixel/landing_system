#!/usr/bin/env python3
"""rembg cutout — удаление фона с фото (студийные авто, портреты, продукты).

Обёртка над github.com/danielgatis/rembg (U2-Net / isnet-general-use). На вход —
один файл или папка; на выход — PNG с прозрачным фоном (alpha), опционально
autocrop по bbox объекта + контрольный preview на тёмной карточке.

Использование:
  python cutout.py <src.png|src_dir> --out <out_dir> [--model isnet-general-use]
                   [--no-crop] [--preview] [--webp]

Примеры:
  # один файл -> webp с прозрачностью + preview для оценки краёв
  python cutout.py photo.png --out ./cut --webp --preview
  # вся папка
  python cutout.py ./inbox --out ./cut --webp

Замечания:
  - Для машин на светлом студийном фоне лучше держит края, чем chroma-key.
  - Модель по умолчанию isnet-general-use (точнее краёв, чем u2net для авто).
    Первая загрузка модели качает веса (~170 МБ) в ~/.u2net — нужен интернет 1 раз.
  - webp сохраняет alpha; для дальнейшей вставки в карточку adapt см. T41 (оверлей mood).
"""
import argparse, os, sys
from PIL import Image


def cut_one(remove_fn, sess, src, out_dir, crop=True, preview=False, webp=False):
    name = os.path.splitext(os.path.basename(src))[0]
    im = Image.open(src).convert('RGBA')
    res = remove_fn(im, session=sess)
    if crop:
        bbox = res.getbbox()
        if bbox:
            res = res.crop(bbox)
    ext = 'webp' if webp else 'png'
    out = os.path.join(out_dir, name + '.' + ext)
    if webp:
        res.save(out, 'WEBP', quality=90, method=6)
    else:
        res.save(out)
    print('cut', os.path.basename(src), '->', os.path.basename(out), res.size)
    if preview:
        prev = Image.new('RGBA', res.size, (20, 20, 24, 255))
        prev.alpha_composite(res)
        p = os.path.join(out_dir, name + '-preview.png')
        prev.convert('RGB').save(p)
        print('   preview', os.path.basename(p))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', help='файл или папка с изображениями')
    ap.add_argument('--out', required=True, help='папка для результата')
    ap.add_argument('--model', default='isnet-general-use',
                    help='модель rembg (isnet-general-use|u2net|u2netp|...)')
    ap.add_argument('--no-crop', action='store_true', help='не обрезать по bbox')
    ap.add_argument('--preview', action='store_true', help='сохранить preview на тёмном фоне')
    ap.add_argument('--webp', action='store_true', help='сохранять webp (alpha) вместо png')
    a = ap.parse_args()

    from rembg import remove, new_session
    sess = new_session(a.model)
    os.makedirs(a.out, exist_ok=True)

    if os.path.isdir(a.src):
        files = sorted(f for f in os.listdir(a.src)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')))
        srcs = [os.path.join(a.src, f) for f in files]
    else:
        srcs = [a.src]

    for s in srcs:
        cut_one(remove, sess, s, a.out, crop=not a.no_crop, preview=a.preview, webp=a.webp)
    print('done:', len(srcs), 'file(s)')


if __name__ == '__main__':
    main()
