# scripts/wiki/query.py

Pure-Python filter over `wiki/index.yaml`. No SDK calls. <100ms for any query.

## CLI Usage

```bash
# Filter by stage
python -m scripts.wiki.query --stage=08

# Filter by type
python -m scripts.wiki.query --type=agent

# Filter by tag
python -m scripts.wiki.query --tag=gutenberg

# Filter by trigger event
python -m scripts.wiki.query --trigger=landing-build

# Look up specific concept
python -m scripts.wiki.query --slug=block-composer

# Full-text search across slug/name/tags/triggers
python -m scripts.wiki.query --grep=gutenberg

# Combine filters (AND)
python -m scripts.wiki.query --stage=08 --type=agent

# Output formats: compact (default), cards, slugs, json
python -m scripts.wiki.query --slug=block-composer --format=cards

# Custom wiki directory
python -m scripts.wiki.query --wiki=/path/to/wiki --type=stage
```

## Python API

```python
from scripts.wiki import query
from pathlib import Path

wiki_dir = Path("wiki")
concepts = query.filter_concepts(wiki_dir, stage="08", type_="agent")
print(query.format_output(wiki_dir, concepts, fmt="compact"))
```
