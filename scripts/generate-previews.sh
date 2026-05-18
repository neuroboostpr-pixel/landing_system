#!/usr/bin/env bash
# scripts/generate-previews.sh — генерирует desktop/mobile/responsive preview обёртки.
set -uo pipefail

PROJECT="${1:?ERROR: project required}"
COMPOSED_DIR="$PROJECT/07b_COMPOSED"
SRC="$COMPOSED_DIR/composed.html"
[ -f "$SRC" ] || { echo "ERROR: $SRC not found" >&2; exit 2; }

generate_preview() {
    local NAME="$1" WIDTH="$2" HEIGHT="$3" OUT="$4"
    cat > "$OUT" <<HTML
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>$NAME preview</title>
<style>
  body { margin: 0; background: #f0f0f0; font-family: -apple-system, sans-serif; display: flex; flex-direction: column; align-items: center; padding: 20px; }
  .label { font-size: 14px; color: #555; margin-bottom: 12px; }
  .frame { background: #1a1a1a; padding: 8px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.15); }
  iframe { display: block; width: ${WIDTH}px; height: ${HEIGHT}px; border: 0; border-radius: 4px; background: white; }
</style>
</head>
<body>
<div class="label">$NAME — ${WIDTH}×${HEIGHT}</div>
<div class="frame"><iframe src="composed.html" loading="eager"></iframe></div>
</body>
</html>
HTML
    echo "  ✓ $OUT"
}

generate_preview "Desktop" 1280 800 "$COMPOSED_DIR/composed-desktop-preview.html"
generate_preview "Mobile (iPhone 14)" 375 812 "$COMPOSED_DIR/composed-mobile-preview.html"

# Index с переключателем
cat > "$COMPOSED_DIR/composed-previews-index.html" <<'HTML'
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Previews — все устройства</title>
<style>
  body { margin: 0; background: #fafafa; font-family: -apple-system, sans-serif; }
  header { background: #1a1a1a; color: white; padding: 16px 24px; display: flex; gap: 12px; align-items: center; }
  header h1 { font-size: 16px; margin: 0; flex: 1; }
  button { background: transparent; color: white; border: 1px solid #555; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 13px; }
  button.active { background: #d4af37; color: #1a1a1a; border-color: #d4af37; }
  main { padding: 24px; display: flex; justify-content: center; }
  .frame { background: #1a1a1a; padding: 8px; border-radius: 8px; box-shadow: 0 12px 32px rgba(0,0,0,0.18); transition: width 0.3s, height 0.3s; }
  iframe { display: block; width: 100%; height: 100%; border: 0; border-radius: 4px; background: white; }
</style>
</head>
<body>
<header>
<h1>Previews — composed.html на разных устройствах</h1>
<button data-w="375"  data-h="812" class="active">📱 Mobile 375</button>
<button data-w="768"  data-h="1024">📲 Tablet 768</button>
<button data-w="1280" data-h="800">💻 Desktop 1280</button>
<button data-w="1920" data-h="1080">🖥 Wide 1920</button>
</header>
<main>
<div class="frame" id="frame" style="width:391px;height:828px"><iframe src="composed.html"></iframe></div>
</main>
<script>
const frame = document.getElementById('frame');
document.querySelectorAll('button[data-w]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    frame.style.width  = (parseInt(btn.dataset.w) + 16) + 'px';
    frame.style.height = (parseInt(btn.dataset.h) + 16) + 'px';
  });
});
</script>
</body>
</html>
HTML

echo "  ✓ $COMPOSED_DIR/composed-previews-index.html"
echo ""
echo "✅ Previews generated. Open:"
echo "   $COMPOSED_DIR/composed-previews-index.html"
