"""Генератор dedup-report.html — группы дублей с чекбоксами и keep-list экспортом."""
from __future__ import annotations
import html
from pathlib import Path


def render_report(groups: dict[str, list[dict]], output: Path) -> None:
    """Сгенерировать интерактивный HTML-отчёт о дублях.
    groups: {signature: [block, ...]} — только группы с >1 блоком.
    Первый блок в группе по умолчанию НЕ отмечен на удаление.
    """
    cards = []
    for sig, blocks in groups.items():
        items = []
        for idx, b in enumerate(blocks):
            old_id = html.escape(b["old_id"])
            name = html.escape(b.get("display_name_ru", ""))
            preview = b.get("clean_html", "")
            checked = "" if idx == 0 else "checked"
            items.append(
                f'<div class="dup-item">'
                f'<label><input type="checkbox" class="rm" value="{old_id}" {checked}> '
                f'удалить <b>{old_id}</b></label>'
                f'<div class="dup-name">{name}</div>'
                f'<iframe class="dup-preview" srcdoc="{html.escape(preview, quote=True)}"></iframe>'
                f'</div>'
            )
        cards.append(
            f'<div class="dup-group"><div class="dup-sig">{html.escape(sig)}</div>'
            f'<div class="dup-items">{"".join(items)}</div></div>'
        )

    empty_note = "" if groups else "<p>Дублей не найдено 🎉</p>"

    page = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
<title>Дубли блоков</title><style>
body {{ font-family: system-ui, sans-serif; background: #f0f0f0; margin: 0; padding: 24px; }}
h1 {{ font-size: 1.4rem; }}
.dup-group {{ background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 20px; }}
.dup-sig {{ font-family: monospace; font-size: 12px; color: #888; margin-bottom: 12px; }}
.dup-items {{ display: flex; gap: 16px; flex-wrap: wrap; }}
.dup-item {{ flex: 1; min-width: 280px; border: 1px solid #ddd; border-radius: 6px; padding: 10px; }}
.dup-name {{ font-size: 13px; color: #555; margin: 6px 0; }}
.dup-preview {{ width: 100%; height: 200px; border: 1px solid #eee; transform: scale(1); }}
#save {{ position: fixed; bottom: 24px; right: 24px; background: #111; color: #fff;
  border: none; padding: 14px 28px; border-radius: 8px; font-size: 15px; cursor: pointer; }}
</style></head><body>
<h1>Дубли блоков — отметь что удалить, скачай keep-list.yaml</h1>
{empty_note}
{"".join(cards)}
<button id="save">Скачать keep-list.yaml</button>
<script>
document.getElementById('save').onclick = function() {{
  const removed = [...document.querySelectorAll('.rm:checked')].map(c => c.value);
  const kept = [...document.querySelectorAll('.rm:not(:checked)')].map(c => c.value);
  const yaml = 'removed:\\n' + removed.map(r => '  - ' + r).join('\\n') +
               '\\nkept:\\n' + kept.map(k => '  - ' + k).join('\\n') + '\\n';
  const blob = new Blob([yaml], {{type: 'text/yaml'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'keep-list.yaml'; a.click();
}};
</script></body></html>"""
    output.write_text(page, encoding="utf-8")
