# tests/phase-5/python/test_generate_integrations.py
import importlib.util
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parents[3] / "skills/wp-gutenberg-block-builder/scripts/generate-integrations.py"


def _load():
    spec = importlib.util.spec_from_file_location("generate_integrations", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert SCRIPT.exists()


def test_main_returns_zero(wp_built_project):
    mod = _load()
    assert mod.main(["generate-integrations.py", str(wp_built_project)]) == 0


def test_fluent_webhook_placeholder_replaced(wp_built_project):
    mod = _load()
    mod.main(["generate-integrations.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "// [FLUENT_WEBHOOK]" not in fp
    assert "fluentform/submission_inserted" in fp


def test_telegram_code_injected_when_enabled(wp_built_project):
    mod = _load()
    mod.main(["generate-integrations.py", str(wp_built_project)])
    fp = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert "TG_BOT_TOKEN" in fp
    assert "api.telegram.org" in fp


def test_amocrm_instruction_created(wp_built_project):
    mod = _load()
    mod.main(["generate-integrations.py", str(wp_built_project)])
    inst = wp_built_project / "08_КОД" / "integrations" / "amocrm-setup.md"
    assert inst.exists()
    assert "AmoCRM" in inst.read_text(encoding="utf-8")


def test_telegram_instruction_created(wp_built_project):
    mod = _load()
    mod.main(["generate-integrations.py", str(wp_built_project)])
    inst = wp_built_project / "08_КОД" / "integrations" / "telegram-setup.md"
    assert inst.exists()


def test_fluent_webhook_not_doubled_on_rerun(wp_built_project):
    mod = _load()
    mod.main(["generate-integrations.py", str(wp_built_project)])
    mod.main(["generate-integrations.py", str(wp_built_project)])
    content = (wp_built_project / "08_КОД" / "wp-theme" / "functions.php").read_text(encoding="utf-8")
    assert content.count("fluentform/submission_inserted") == 1


def test_parse_integrations_from_brief():
    mod = _load()
    brief = "## Интеграции\n- CRM: AmoCRM\n- Telegram уведомления: да\n- Попапы: да\n"
    result = mod._parse_integrations(brief)
    assert result["crm"] == "amocrm"
    assert result["telegram"] is True


def test_missing_functions_php_returns_one(tmp_path):
    mod = _load()
    assert mod.main(["generate-integrations.py", str(tmp_path)]) == 1
