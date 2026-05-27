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

# Источники для системного wiki — разделены на два уровня:
#
# CORE_SOURCES   — 6 основных категорий + catalog-entry блок-библиотеки.
#                  Только они компилируются при --source-mode=system.
# REFERENCE_SOURCES — всё остальное (спеки, планы, пресеты и т.д.).
#                  Зарезервированы для будущего use-case, не входят в CORE.
#
# Каждая запись: glob-паттерн относительно REPO_ROOT + папка концептов в wiki/.

CORE_SOURCES = [
    {"path": "agents/*.md", "concept_dir": "agents"},
    {"path": "skills/*/SKILL.md", "concept_dir": "skills"},
    {"path": "commands/*.md", "concept_dir": "commands"},
    {"path": "template/*/README.md", "concept_dir": "stages"},
    {"path": "docs/standards/*.md", "concept_dir": "rules"},
    # Catalog entry-point для блок-библиотеки (один файл, не полный обход)
    {"path": "block-library/README.md", "concept_dir": "catalogs"},
]

REFERENCE_SOURCES = [
    # PR-Q: блоки лежат на 2 уровнях вложенности — <category>/<block-id>/meta.yaml
    {"path": "block-library/*/*/meta.yaml", "concept_dir": "blocks"},
    # PR-S: расширенное покрытие
    {"path": "block-library/_patterns/*/meta.yaml", "concept_dir": "patterns"},
    {"path": "block-library/_styles/*/README.md", "concept_dir": "styles"},
    {"path": "config/*.yaml", "concept_dir": "config"},
    {"path": "docs/SETUP.md", "concept_dir": "docs"},
    # === PR-T: полное покрытие системы ===
    # Spec и plan документы (история разработки PR-F..PR-T)
    {"path": "docs/superpowers/specs/*.md", "concept_dir": "specs"},
    {"path": "docs/superpowers/plans/*.md", "concept_dir": "plans"},
    # Дополнительные doc файлы (планы доработок, dokrutka)
    {"path": "docs/ПЛАН-ДОРАБОТОК.md", "concept_dir": "docs"},
    {"path": "docs/BACKLOG.md", "concept_dir": "docs"},
    {"path": "docs/photo-selection-guide.md", "concept_dir": "docs"},
    {"path": "docs/superpowers/DOKRUTKA-system.md", "concept_dir": "docs"},
    {"path": "docs/superpowers/dokrutka*.md", "concept_dir": "docs"},
    # Тесты — README по группам PR-* и phase-*
    {"path": "tests/*/README.md", "concept_dir": "tests"},
    # Presets — все *.md и *.yaml на верхнем уровне
    {"path": "presets/*.md", "concept_dir": "presets"},
    {"path": "presets/*.yaml", "concept_dir": "presets"},
    # Auto-generated docs from scripts (см. scripts/generate-script-docs.py)
    {"path": "scripts/*.doc.md", "concept_dir": "scripts"},
    {"path": "scripts/*/*.doc.md", "concept_dir": "scripts"},
    {"path": "scripts/*/*/*.doc.md", "concept_dir": "scripts"},
]

# Back-compat alias — старый код, импортирующий SYSTEM_SOURCES, продолжает работать.
SYSTEM_SOURCES = CORE_SOURCES

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

# Модель по умолчанию — используется как fallback если CLAUDE_MODEL не задана в env.
# Обновлять при смене модели сессии.
DEFAULT_MODEL = "claude-sonnet-4-6"

# Паттерны путей которые считаются "source reads" (bypass wiki).
# transcript_parser.is_source_read() использует эти паттерны.
# При развёртывании на новом проекте — переопределить под свою структуру.
SOURCE_READ_PATTERNS: list[str] = [
    "agents/*.md",
    "skills/*/SKILL.md",
    "commands/*.md",
    "docs/standards/*.md",
]
