"""Render legal HTML pages by substituting reqs into templates."""
import re
from pathlib import Path

# Path to templates dir (relative to landing-system root)
TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / 'template' / '08_КОД' / 'legal-pages'

PLACEHOLDER_RE = re.compile(r'\{\{(\w+)\}\}')


def render_template(tpl_string, legal):
    """Substitute {{key}} placeholders with legal[key] values.

    Raises RuntimeError if legal['_incomplete'] is True.
    Raises KeyError if template references a key not in legal.
    """
    if legal.get('_incomplete'):
        raise RuntimeError(
            "Legal data is incomplete (TODO_LEGAL detected). "
            "Заполни 04_БРЕНД/extracted/legal.yaml и перезапусти build.py."
        )

    def _replace(m):
        key = m.group(1)
        if key not in legal:
            raise KeyError(f"Template references unknown key: {key!r}")
        return str(legal[key])

    return PLACEHOLDER_RE.sub(_replace, tpl_string)


def render_policy(legal):
    tpl_path = TEMPLATES_DIR / 'policy.html.template'
    return render_template(tpl_path.read_text(encoding='utf-8'), legal)


def render_consent(legal):
    tpl_path = TEMPLATES_DIR / 'consent.html.template'
    return render_template(tpl_path.read_text(encoding='utf-8'), legal)
