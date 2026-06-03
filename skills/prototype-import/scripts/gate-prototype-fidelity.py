#!/usr/bin/env python3
"""B37 Фаза 3 — gate-обёртка точности парсинга прототипа для stage-gate 07a.

Принимает папку проекта. Если в source/ есть .docx — извлекает эталонный текст
(extract-docx-text.py) и сверяет с prototype.yaml (verify-prototype-fidelity.py,
порог 90%). Если источник не .docx (.pdf/.md) — gate пропускается (extractor
поддерживает только docx; для остального полнота не проверяется в этой версии).

exit 0 — PASS / N/A, exit 1 — FAIL (потеря >10% или галлюцинации).

Использование (из stage-gates.yaml):
  gate-prototype-fidelity.py {project}
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTRACT = HERE / "extract-docx-text.py"
VERIFY = HERE / "verify-prototype-fidelity.py"


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: gate-prototype-fidelity.py <project_dir>", file=sys.stderr)
        sys.exit(2)
    project = Path(sys.argv[1])
    proto_dir = project / "07_ПРОТОТИП"
    yaml_path = proto_dir / "prototype.yaml"
    if not yaml_path.exists():
        print(f"FAIL: нет {yaml_path}", file=sys.stderr)
        sys.exit(1)

    # ищем .docx источник
    src_dir = proto_dir / "source"
    docx = next(iter(src_dir.glob("*.docx")), None) if src_dir.exists() else None
    if docx is None:
        print("N/A: источник не .docx — проверка полноты пропущена "
              "(поддерживается только docx)")
        sys.exit(0)

    extracted = proto_dir / "source-extracted"
    r1 = subprocess.run(
        [sys.executable, str(EXTRACT), "--source", str(docx), "--out", str(extracted)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if r1.returncode != 0:
        print(f"FAIL: экстрактор упал: {r1.stderr}", file=sys.stderr)
        sys.exit(1)

    r2 = subprocess.run(
        [sys.executable, str(VERIFY),
         "--source-text", str(extracted.with_suffix(".txt")),
         "--prototype", str(yaml_path),
         "--min-coverage", "0.9"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(r2.stdout.strip())
    if r2.returncode != 0:
        print(r2.stdout, file=sys.stderr)
    sys.exit(r2.returncode)


if __name__ == "__main__":
    main()
