"""Parse legal: section from brand-kit.md.

The legal section is a YAML block inside a markdown ## Legal heading:

    ## Legal
    ```yaml
    company_name: '...'
    entity_type: 'ООО'
    inn: '...'
    ogrn: '...'
    legal_address: '...'
    contact_email: '...'
    dpo_email: '...'
    ```

Returns dict on success or None if section missing/malformed.
Sets result['_incomplete'] = True if any required field is the literal 'TODO_LEGAL'.
"""
import re
import yaml
from pathlib import Path


LEGAL_SECTION_RE = re.compile(
    r'^##\s+Legal\s*$\n+```yaml\n(.*?)\n```',
    re.MULTILINE | re.DOTALL
)

REQUIRED_FIELDS = ['company_name', 'entity_type', 'inn', 'ogrn',
                   'legal_address', 'contact_email', 'dpo_email']


def parse_legal_from_brand_kit(path):
    """Parse the legal: section from a brand-kit.md file.

    Args:
        path: path to brand-kit.md (str or Path).

    Returns:
        dict with legal fields + '_incomplete' flag, or None if missing/malformed.

    Raises:
        FileNotFoundError: if path does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"brand-kit.md not found: {path}")

    content = p.read_text(encoding='utf-8')
    m = LEGAL_SECTION_RE.search(content)
    if not m:
        return None

    yaml_block = m.group(1)
    try:
        data = yaml.safe_load(yaml_block)
    except yaml.YAMLError as e:
        import sys
        print(f"[parse_legal] warning: malformed YAML in Legal section: {e}", file=sys.stderr)
        return None

    if not isinstance(data, dict):
        return None

    # Detect TODO_LEGAL placeholders
    incomplete = any(
        str(data.get(f, '')).strip() == 'TODO_LEGAL'
        for f in REQUIRED_FIELDS
    )
    data['_incomplete'] = incomplete

    return data
