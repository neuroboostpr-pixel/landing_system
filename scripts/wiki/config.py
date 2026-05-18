# scripts/wiki/config.py
"""Конфигурация wiki-компайлера.

Определяет источники для трёх режимов компиляции:
- system: компилит landing-system/{agents,skills,commands,template,docs/standards}
- project-graph: компилит артефакты конкретного лендинга (~/Lendings/<slug>/)
- conversations: компилит daily logs сессий в knowledge базу (coleam00 default)
"""
from pathlib import Path

# Корень landing-system — рассчитывается от расположения этого файла.
# scripts/wiki/config.py → корень = parents[2]
REPO_ROOT = Path(__file__).resolve().parents[2]

# Папка системного wiki внутри landing-system.
WIKI_DIR = REPO_ROOT / "wiki"

# Три режима компиляции.
SOURCE_MODES = ("system", "project-graph", "conversations")

# Источники для системного wiki.
# Каждая запись: glob-паттерн относительно REPO_ROOT + папка концептов в wiki/.
SYSTEM_SOURCES = [
    {"path": "agents/*.md", "concept_dir": "agents"},
    {"path": "skills/*/SKILL.md", "concept_dir": "skills"},
    {"path": "commands/*.md", "concept_dir": "commands"},
    {"path": "template/*/README.md", "concept_dir": "stages"},
    {"path": "docs/standards/*.md", "concept_dir": "rules"},
    # PR-Q: блоки лежат на 2 уровнях вложенности — <category>/<block-id>/meta.yaml
    {"path": "block-library/*/*/meta.yaml", "concept_dir": "blocks"},
    # PR-S: расширенное покрытие
    {"path": "block-library/_patterns/*/meta.yaml", "concept_dir": "patterns"},
    {"path": "block-library/_styles/*/README.md", "concept_dir": "styles"},
    {"path": "config/*.yaml", "concept_dir": "config"},
    {"path": "docs/SETUP.md", "concept_dir": "docs"},
]

# Источники для графа конкретного проекта (~/Lendings/<slug>/).
# Пути относительно корня проекта.
PROJECT_SOURCES = [
    {"path": ".landing-state.yaml", "concept": "stage-current.md"},
    {"path": "07_ПРОТОТИП/prototype.md", "concept": "prototype.md"},
    {"path": "07a_WIREFRAME/selections.yaml", "concept": "blocks.md"},
    {"path": "07b_COMPOSED/composed.html", "concept": "blocks.md"},
    {"path": "07c_PHOTOS/selections.yaml", "concept": "photos.md"},
    {"path": "04_БРЕНД/tokens.json", "concept": "brand.md"},
    {"path": "04_БРЕНД/brand-kit.md", "concept": "brand.md"},
]
