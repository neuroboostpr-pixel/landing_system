#!/usr/bin/env python3
"""A2-гейт: поблочная сверка composed.html ↔ prototype.md действительно сделана.

Раньше гейт 07c проверял лишь НАЛИЧИЕ structure-check.md (type:file_exists) —
block-composer мог записать пустой файл и закрыть этап без реальной сверки.
Теперь требуется явный машинный вердикт.

Контракт structure-check.md (см. docs/standards/reference-driven-rules.md):
  - в конце файла строка `STRUCTURE_MATCH: PASS` (или `FAIL`);
  - PASS допустим только если нет нерешённых расхождений.

Exit: 0 — файл есть, вердикт PASS, есть содержательная сверка (таблица/строки);
      1 — файла нет / пустой / вердикт FAIL / вердикт отсутствует.

Usage: verify-structure-check.py <project-dir>
"""
import re
import sys
from pathlib import Path


def main(project_dir: Path) -> int:
    path = project_dir / "07b_COMPOSED" / "structure-check.md"
    if not path.exists():
        print(f"FAIL: нет {path} — block-composer обязан поблочно сверить "
              f"composed.html с prototype.md", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")
    if len(text.strip()) < 40:
        print("FAIL: structure-check.md пустой/заглушка — нет реальной сверки",
              file=sys.stderr)
        return 1
    m = re.search(r"STRUCTURE_MATCH:\s*(PASS|FAIL)", text, re.IGNORECASE)
    if not m:
        print("FAIL: в structure-check.md нет вердикта `STRUCTURE_MATCH: PASS|FAIL`. "
              "Допиши строку с явным результатом поблочной сверки.", file=sys.stderr)
        return 1
    if m.group(1).upper() != "PASS":
        print("FAIL: STRUCTURE_MATCH: FAIL — есть расхождения макета с прототипом. "
              "Почини composed.html до деплоя (raскладка/состав/порядок).",
              file=sys.stderr)
        return 1
    print("PASS: поблочная сверка пройдена (STRUCTURE_MATCH: PASS)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: verify-structure-check.py <project-dir>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
