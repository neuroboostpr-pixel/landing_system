#!/usr/bin/env python3
"""
Quick wireframe generator — reads prototype.yaml and catalog.yaml,
generates wireframe.html with ALL matching block candidates (no Python version issues).

Usage: python3 quick-wireframe-gen.py <project_dir>
"""

import sys
import yaml
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 quick-wireframe-gen.py <project_dir>")
        sys.exit(1)

    project = Path(sys.argv[1]).resolve()
    proto_path = project / "07_ПРОТОТИП" / "prototype.yaml"
    catalog_path = project.parent.parent / "landing_system" / "block-library" / "catalog.yaml"

    if not proto_path.exists():
        print(f"❌ prototype.yaml not found: {proto_path}")
        sys.exit(1)

    if not catalog_path.exists():
        print(f"❌ catalog.yaml not found: {catalog_path}")
        sys.exit(1)

    # Load
    with open(proto_path) as f:
        proto = yaml.safe_load(f)

    with open(catalog_path) as f:
        catalog_data = yaml.safe_load(f)

    blocks = catalog_data.get('blocks', [])
    print(f"📦 Loaded {len(blocks)} blocks from catalog", file=sys.stderr)

    # Index blocks by type
    by_type = {}
    for b in blocks:
        btype = b.get('type', '').lower()
        if btype not in by_type:
            by_type[btype] = []
        by_type[btype].append(b)

    print(f"📁 Indexed {len(by_type)} block types", file=sys.stderr)

    # Generate HTML
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wireframe Selector — НЕЙРОКРЕАТОР</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root { --primary: #FFA500; --text: #333; --bg: #f5f5f5; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); padding: 40px 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { font-size: 36px; margin-bottom: 10px; text-align: center; }
        .subtitle { text-align: center; color: #666; margin-bottom: 40px; }
        .section { background: white; border-radius: 8px; padding: 32px; margin-bottom: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .section-title { font-size: 20px; font-weight: 700; border-bottom: 3px solid var(--primary); padding-bottom: 12px; margin-bottom: 20px; }
        .section-num { display: inline-block; background: var(--primary); color: white; width: 28px; height: 28px; border-radius: 50%; text-align: center; line-height: 28px; font-weight: 700; margin-right: 12px; }
        .blocks-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
        .block-card { border: 2px solid #ddd; border-radius: 6px; padding: 14px; cursor: pointer; transition: all 200ms; }
        .block-card:hover { border-color: var(--primary); box-shadow: 0 4px 12px rgba(255,165,0,0.2); }
        .block-card input { margin-right: 8px; cursor: pointer; }
        .block-card label { display: flex; align-items: center; cursor: pointer; font-weight: 500; }
        .block-card input:checked + label { color: var(--primary); font-weight: 700; }
        .block-card.selected { border-color: var(--primary); background: rgba(255,165,0,0.05); }
        .block-info { margin-top: 12px; padding: 12px; background: #f9f9f9; border-radius: 4px; border-left: 3px solid var(--primary); font-size: 12px; line-height: 1.5; color: #666; }
        .badge { background: var(--primary); color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; margin-left: 8px; }
        .buttons { display: flex; gap: 12px; justify-content: center; margin-top: 40px; }
        button { padding: 12px 32px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 14px; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:hover { background: #ff9500; }
        .success { display: none; background: #4CAF50; color: white; padding: 16px; border-radius: 6px; margin-top: 16px; text-align: center; }
        .success.show { display: block; }
        .footer { text-align: center; padding: 40px 20px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Selector макета</h1>
        <p class="subtitle">Выбери блоки для каждой секции. Первый (выделен жёлтым) — рекомендуется.</p>

        <form id="form">
"""

    section_num = 0
    for section in proto.get('sections', []):
        section_num += 1
        section_name = section.get('name', f'Section {section_num}')
        section_id = section.get('id', f'section_{section_num}')

        html += f"""
            <div class="section">
                <h2 class="section-title">
                    <span class="section-num">{section_num}</span>{section_name}
                </h2>
                <div class="blocks-grid">
"""

        for block_idx, block in enumerate(section.get('blocks', [])):
            btype = block.get('type', 'unknown').lower()
            block_label = block.get('label', btype)
            block_id_full = f"{section_id}_{block_idx}"

            # Find matching blocks from catalog
            candidates = by_type.get(btype, [])

            if not candidates:
                html += f"""
                    <div class="block-card">
                        <p style="color: #d9534f; font-weight: 600;">⚠️ No blocks for "{btype}"</p>
                        <p style="font-size: 11px; color: #999; margin-top: 8px;">No matching candidates in block-library</p>
                    </div>
"""
                continue

            # Show all candidates
            for cand_idx, cand in enumerate(candidates[:8]):  # Max 8 per block
                is_first = (cand_idx == 0)
                radio_id = f"r_{block_id_full}_{cand_idx}"
                radio_name = f"block_{block_id_full}"
                radio_value = cand['id']

                selected_class = "selected" if is_first else ""
                badge_html = '<span class="badge">Рекомендуется</span>' if is_first else ''

                layout = cand.get('layout_pattern', '')
                cat = cand.get('category', '')
                meta_str = f"{cat} • {layout}" if layout else cat

                html += f"""
                    <div class="block-card {selected_class}">
                        <input type="radio" id="{radio_id}" name="{radio_name}" value="{radio_value}" {'checked' if is_first else ''}>
                        <label for="{radio_id}">{cand['display_name_ru']} {badge_html}</label>
                        <div class="block-info">
                            <strong>Блок:</strong> {block_label}<br>
                            <strong>ID:</strong> <code>{cand['id']}</code><br>
                            <strong>Макет:</strong> {layout or 'standard'}<br>
                            <strong>Категория:</strong> {cat}
                        </div>
                    </div>
"""

        html += """
                </div>
            </div>
"""

    html += """
        <div class="buttons">
            <button type="button" class="btn-primary" onclick="downloadSelections()">
                ✅ Подтвердить и скачать selections.yaml
            </button>
        </div>

        <div id="success" class="success">
            ✅ Скачано! Положи файл в 07a_WIREFRAME/selections.yaml
        </div>
        </form>
    </div>

    <div class="footer">
        <p>НЕЙРОКРЕАТОР | Stage 07b_wireframe</p>
    </div>

    <script>
        function downloadSelections() {
            const form = document.getElementById('form');
            const data = new FormData(form);

            let yaml = '# Wireframe Selections\\n';
            yaml += '# ' + new Date().toISOString() + '\\n\\n';
            yaml += 'selections:\\n';

            for (const [key, value] of data) {
                yaml += `  ${key}: "${value}"\\n`;
            }
            yaml += '\\nstatus: pending_compose\\n';

            const blob = new Blob([yaml], {type: 'text/yaml'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'selections.yaml';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            document.getElementById('success').classList.add('show');
        }
    </script>
</body>
</html>
"""

    # Write output
    out_file = project / "07a_WIREFRAME" / "wireframe.html"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html, encoding='utf-8')

    print(f"✅ Generated: {out_file}", file=sys.stderr)
    print(f"📂 Open in browser: file://{out_file}", file=sys.stderr)

if __name__ == '__main__':
    main()
