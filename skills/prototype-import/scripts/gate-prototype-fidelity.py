#!/usr/bin/env python3
"""Gate точности парсинга прототипа для stage-gate 07a (B37 + A1).

A1 (спека reference-driven flow §2.1):
  - Канон этапа — prototype.md (fallback: prototype.yaml).
  - Проверка полноты работает на ВСЕХ форматах источника:
      .docx           → extract-docx-text.py (параграфы + таблицы)
      .pdf            → extract-pdf-text.py (текстовый слой)
      .md / .txt      → текст источника напрямую
      .png/.jpg/...   → OCR (pytesseract), если установлен
  - Если текст извлечь нельзя (скан без OCR) — гейт НЕ падает, но пишет
    ЯВНОЕ предупреждение в stdout и fidelity-report.md («полнота НЕ
    проверена»). Молчаливый pass — дефект.

exit 0 — PASS / explicit-N/A, exit 1 — FAIL (потеря >10% или галлюцинации).

Использование (из stage-gates.yaml):
  gate-prototype-fidelity.py {project}
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTRACT_DOCX = HERE / "extract-docx-text.py"
EXTRACT_PDF = HERE / "extract-pdf-text.py"
VERIFY = HERE / "verify-prototype-fidelity.py"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}


def _find_source(src_dir: Path) -> Path | None:
    """Источник по приоритету: docx > pdf > md/txt > картинка."""
    if not src_dir.exists():
        return None
    for pattern in ("*.docx", "*.pdf", "*.md", "*.txt"):
        found = sorted(src_dir.glob(pattern))
        if found:
            return found[0]
    images = sorted(p for p in src_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    return images[0] if images else None


def _ocr_image(image: Path) -> str | None:
    """OCR картинки; None если pytesseract/tesseract недоступны."""
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore
    except ImportError:
        return None
    try:
        return pytesseract.image_to_string(Image.open(image), lang="rus+eng")
    except Exception:
        return None


def _unverified_pass(proto_dir: Path, reason: str) -> None:
    """Явный N/A: полнота не проверена — предупреждение, не молчание."""
    report = proto_dir / "fidelity-report.md"
    report.write_text(
        "# Fidelity-отчёт парсинга прототипа\n\n"
        f"⚠️ **Полнота НЕ проверена**: {reason}\n\n"
        "Сверь prototype.md с источником вручную: каждый текст, кнопка и "
        "комментарий клиента должны быть перенесены 1:1.\n",
        encoding="utf-8",
    )
    print(f"⚠️ N/A: полнота НЕ проверена — {reason}. "
          f"Отчёт: {report}. Сверь prototype.md с источником вручную.")
    sys.exit(0)


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: gate-prototype-fidelity.py <project_dir>", file=sys.stderr)
        sys.exit(2)
    project = Path(sys.argv[1])
    proto_dir = project / "07_ПРОТОТИП"

    # A1: канон — prototype.md, fallback prototype.yaml
    target = proto_dir / "prototype.md"
    if not target.exists():
        target = proto_dir / "prototype.yaml"
    if not target.exists():
        print(f"FAIL: нет ни prototype.md, ни prototype.yaml в {proto_dir}",
              file=sys.stderr)
        sys.exit(1)

    source = _find_source(proto_dir / "source")
    if source is None:
        _unverified_pass(proto_dir, "в source/ нет файла-источника")
        return

    ext = source.suffix.lower()
    source_text_path = proto_dir / "source-extracted.txt"

    if ext == ".docx":
        extracted = proto_dir / "source-extracted"
        r1 = subprocess.run(
            [sys.executable, str(EXTRACT_DOCX), "--source", str(source),
             "--out", str(extracted)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r1.returncode != 0:
            print(f"FAIL: docx-экстрактор упал: {r1.stderr}", file=sys.stderr)
            sys.exit(1)
        source_text_path = extracted.with_suffix(".txt")
    elif ext == ".pdf":
        r1 = subprocess.run(
            [sys.executable, str(EXTRACT_PDF), str(source)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r1.returncode != 0 or not r1.stdout.strip():
            # сканированный PDF без текстового слоя — честно сообщаем,
            # что полнота не проверена (OCR для PDF не настроен).
            _unverified_pass(
                proto_dir,
                "PDF без текстового слоя (скан); OCR для PDF не настроен")
            return
        source_text_path.write_text(r1.stdout, encoding="utf-8")
    elif ext in (".md", ".txt"):
        source_text_path.write_text(
            source.read_text(encoding="utf-8"), encoding="utf-8")
    elif ext in IMAGE_EXTS:
        text = _ocr_image(source)
        if not text or not text.strip():
            _unverified_pass(
                proto_dir,
                "источник — картинка, OCR недоступен (установи pytesseract + tesseract)")
            return
        source_text_path.write_text(text, encoding="utf-8")
    else:
        _unverified_pass(proto_dir, f"неизвестный формат источника {ext}")
        return

    r2 = subprocess.run(
        [sys.executable, str(VERIFY),
         "--source-text", str(source_text_path),
         "--prototype", str(target),
         "--min-coverage", "0.9"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(r2.stdout.strip())
    if r2.returncode != 0:
        print(r2.stdout, file=sys.stderr)
    sys.exit(r2.returncode)


if __name__ == "__main__":
    main()
