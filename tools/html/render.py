"""Jinja2 setup for HTML preview generators."""
from pathlib import Path
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape


_TEMPLATES_DIR = Path(__file__).parent / "templates"


def get_env() -> Environment:
    """Return a configured Jinja2 environment."""
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render(template_name: str, context: Dict[str, Any]) -> str:
    """Render a template by name with the given context."""
    env = get_env()
    tmpl = env.get_template(template_name)
    return tmpl.render(**context)
