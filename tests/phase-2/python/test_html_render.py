from tools.html.render import render, get_env


def test_get_env_loads_templates_dir():
    env = get_env()
    # base.html.j2 should be loadable
    tmpl = env.get_template("base.html.j2")
    assert tmpl is not None


def test_render_base_with_blocks():
    # base alone renders empty heading
    out = render("base.html.j2", {})
    assert "<!DOCTYPE html>" in out
    assert "<title>Landing System Preview</title>" in out


def test_render_autoescapes_html_in_context():
    # Render via a tiny inline template — actually we test that
    # autoescape is enabled by checking base output for safety
    env = get_env()
    from jinja2 import DictLoader
    env.loader = DictLoader({"t.html.j2": "{{ value }}"})
    out = env.get_template("t.html.j2").render(value="<script>alert(1)</script>")
    assert "<script>" not in out
    assert "&lt;script&gt;" in out
