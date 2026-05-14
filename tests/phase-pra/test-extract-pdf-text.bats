#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  EXTRACT="$ROOT/skills/prototype-import/scripts/extract-pdf-text.py"

  if python3 -c "import reportlab" 2>/dev/null; then
    python3 <<PY > /dev/null
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
c = canvas.Canvas("$BATS_TMPDIR/sample.pdf", pagesize=A4)
c.drawString(100, 750, "Hero block")
c.drawString(100, 720, "Headline: Test landing")
c.drawString(100, 690, "CTA: Get started")
c.save()
PY
  fi
}

@test "extract text from a simple text PDF" {
  if [ ! -f "$BATS_TMPDIR/sample.pdf" ]; then skip "reportlab not installed"; fi
  run python3 "$EXTRACT" "$BATS_TMPDIR/sample.pdf"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Hero block"* ]]
  [[ "$output" == *"Test landing"* ]]
}

@test "non-existent file exits non-zero" {
  run python3 "$EXTRACT" "$BATS_TMPDIR/does-not-exist.pdf"
  [ "$status" -ne 0 ]
}

@test "exit non-zero if file is empty" {
  touch "$BATS_TMPDIR/empty.pdf"
  run python3 "$EXTRACT" "$BATS_TMPDIR/empty.pdf"
  [ "$status" -ne 0 ]
}
