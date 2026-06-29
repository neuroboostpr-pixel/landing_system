#!/usr/bin/env python3
"""gen-spec — гейт ТЗ (build-spec.md): mapping корректен, без хексов/размеров,
тексты не скопированы, ровно один active, разделы по мудам.

Проверки:
  STRUCT  : есть раздел «КОНТЕНТ ПРОТОТИПА» + ≥1 раздел «## МУД …» (по числу мудов).
  NO-HEX  : 0 прямых цветов (#hex / rgb()/rgba()) — они в ДС-токенах, не в ТЗ.
  NO-SIZE : 0 голых размеров (12px / 1.5rem / 2em) — кроме ссылок на токены var(--…)/`--…`.
  NO-COPY : длинные тексты активного прототипа (≥24 знаков) НЕ скопированы дословно в ТЗ
            (должны быть ССЫЛКОЙ на ключ). Заголовки-ярлыки (section_title коротк.) не считаем.
  ONE-ACTIVE: в папке прототипов ровно один meta.active:true.
  INSTR   : каждая block_instruction прототипа упомянута в ТЗ (перенесена как требование).

Отчёт → stdout. Отчётный .md (если --report) — во временную папку по умолчанию.
exit 0 PASS · 1 FAIL · 2 ошибка ввода.

Использование:
  python verify-spec.py --spec <build-spec.md> --prototype-dir <07_ПРОТОТИП/> \
         [--moods-dir <05_ДИЗАЙН-СИСТЕМА/moods/>] [--min-moods 1]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)")
SIZE_RE = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(px|rem|em)\b")


def _active_prototype(proto_dir: Path):
    actives = []
    for f in sorted(proto_dir.glob("prototype-*.yaml")):
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if (d.get("meta") or {}).get("active") is True:
            actives.append((f, d))
    return actives


def _strip_code_spans(line: str) -> str:
    """Убрать `…` (ссылки на токены/ключи) — в них px/hex легальны."""
    return re.sub(r"`[^`]*`", "", line)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--prototype-dir", required=True)
    ap.add_argument("--moods-dir", default="")
    ap.add_argument("--min-moods", type=int, default=1)
    args = ap.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.is_file():
        print(f"ERROR: нет файла ТЗ {spec_path}", file=sys.stderr)
        return 2
    spec = spec_path.read_text(encoding="utf-8")
    errors: list[str] = []

    # ── ONE-ACTIVE ──
    proto_dir = Path(args.prototype_dir)
    actives = _active_prototype(proto_dir)
    if len(actives) != 1:
        errors.append(f"ONE-ACTIVE: active=true у {len(actives)} прототипов "
                      f"{[f.name for f,_ in actives]} — должен быть РОВНО один")
        proto = actives[0][1] if actives else {}
    else:
        proto = actives[0][1]

    # ── STRUCT ──
    if "КОНТЕНТ ПРОТОТИПА" not in spec:
        errors.append("STRUCT: нет общего раздела «КОНТЕНТ ПРОТОТИПА»")
    n_mood_sections = len(re.findall(r"^##\s+МУД\b", spec, re.MULTILINE))
    expected = args.min_moods
    if args.moods_dir:
        md = Path(args.moods_dir)
        if md.is_dir():
            expected = len([p for p in md.iterdir()
                            if p.is_dir() and not p.name.startswith("_")])
    if n_mood_sections < expected:
        errors.append(f"STRUCT: разделов «## МУД» {n_mood_sections}, ожидалось ≥{expected}")

    # ── NO-HEX / NO-SIZE (вне code-spans) ──
    for i, line in enumerate(spec.splitlines(), 1):
        clean = _strip_code_spans(line)
        for m in COLOR_RE.finditer(clean):
            errors.append(f"NO-HEX: строка {i}: прямой цвет {m.group(0)} (→ в ДС-токены)")
        for m in SIZE_RE.finditer(clean):
            errors.append(f"NO-SIZE: строка {i}: размер {m.group(0)} (→ в metrics.css)")

    # ── NO-COPY: длинные тексты прототипа не скопированы дословно ──
    def _texts(node):
        out = []
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "text" and isinstance(v, str):
                    out.append(v)
                else:
                    out += _texts(v)
        elif isinstance(node, list):
            for v in node:
                out += _texts(v)
        return out

    # «Скопирован» = длинный текст прототипа встречается в ТЗ на строке БЕЗ
    # code-span ссылки (`blocks[...]`/`--токен`). Краткий ярлык-пояснение в «…»
    # РЯДОМ со ссылкой (Cn-таблица) — легально, не копия.
    spec_lines = spec.splitlines()
    copied = []
    for t in _texts(proto.get("blocks", [])):
        if len(t) < 24:
            continue
        for line in spec_lines:
            if t in line and "`" not in line:   # есть текст, но НЕТ ссылки на строке → копия
                copied.append(t)
                break
    for t in copied[:10]:
        errors.append(f"NO-COPY: текст прототипа скопирован в ТЗ дословно без ссылки: «{t[:50]}…»")

    # ── INSTR: block_instructions перенесены ──
    for bi in proto.get("block_instructions", []) or []:
        instr = bi.get("instruction", "") if isinstance(bi, dict) else str(bi)
        # ключевое слово инструкции (карусель/лестница/инфографика/до/после…)
        kw = re.findall(r"[А-Яа-яA-Za-z]{5,}", instr)
        if kw and not any(w.lower() in spec.lower() for w in kw[:3]):
            errors.append(f"INSTR: инструкция блока не перенесена в ТЗ: «{instr[:50]}…»")

    # ── вывод ──
    status = "PASS" if not errors else "FAIL"
    print(f"[{status}] ТЗ: мудов-разделов {n_mood_sections}, ошибок {len(errors)}")
    for e in errors[:40]:
        print(f"  {e}")
    if len(errors) > 40:
        print(f"  … ещё {len(errors)-40}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
