"""B37 Фаза 2 — verify-prototype-fidelity: полнота + анти-галлюцинация."""
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "prototype-import" / "scripts" / "verify-prototype-fidelity.py"


def _run(src_txt: Path, proto: Path, report: Path, min_cov="0.9"):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--source-text", str(src_txt),
         "--prototype", str(proto), "--min-coverage", min_cov, "--report", str(report)],
        capture_output=True, text=True,
    )


def _write(p: Path, obj):
    p.write_text(yaml.dump(obj, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_full_coverage_passes(tmp_path):
    src = tmp_path / "src.txt"
    src.write_text(
        "Практический онлайн курс по ИИ визуалу\n"
        "Реальная цена тарифа сто тысяч рублей\n"
        "Кирилл Безиков автор книги Не Я а ИИ\n",
        encoding="utf-8",
    )
    proto = tmp_path / "p.yaml"
    _write(proto, {"sections": [
        {"id": "hero", "blocks": [{"type": "heading", "text": "Практический онлайн курс по ИИ визуалу"}]},
        {"id": "tariffs", "blocks": [{"type": "tariff_card", "price": "Реальная цена тарифа сто тысяч рублей"}]},
        {"id": "experts", "blocks": [{"type": "expert", "text": "Кирилл Безиков автор книги Не Я а ИИ"}]},
    ]})
    r = _run(src, proto, tmp_path / "rep.md")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout


def test_missing_content_fails(tmp_path):
    src = tmp_path / "src.txt"
    src.write_text(
        "Реальная цена тарифа сто тысяч девятьсот девяносто рублей\n"
        "Блок экспертов Кирилл Безиков и Никита Брусков биографии\n"
        "Рассрочка платите частями без переплат двадцать четыре месяца\n",
        encoding="utf-8",
    )
    proto = tmp_path / "p.yaml"
    # только первая строка дошла → ~33% покрытия
    _write(proto, {"sections": [
        {"id": "tariffs", "blocks": [{"type": "card", "text": "Реальная цена тарифа сто тысяч девятьсот девяносто рублей"}]},
    ]})
    r = _run(src, proto, tmp_path / "rep.md")
    assert r.returncode == 1
    assert "FAIL" in r.stdout


def test_hallucinated_menu_fails(tmp_path):
    src = tmp_path / "src.txt"
    src.write_text("Практический онлайн курс единственная строка контента тут\n", encoding="utf-8")
    proto = tmp_path / "p.yaml"
    _write(proto, {"sections": [
        {"id": "hero", "blocks": [{"type": "heading", "text": "Практический онлайн курс единственная строка контента тут"}]},
        {"id": "header", "blocks": [{"type": "menu", "items": ["Home", "About", "Services", "Contact"]}]},
    ]})
    r = _run(src, proto, tmp_path / "rep.md")
    assert r.returncode == 1
    assert "FAIL" in r.stdout
    rep = (tmp_path / "rep.md").read_text(encoding="utf-8")
    assert "menu" in rep.lower()


def test_fake_tariff_price_fails(tmp_path):
    src = tmp_path / "src.txt"
    src.write_text("Практический онлайн курс единственная строка контента здесь\n", encoding="utf-8")
    proto = tmp_path / "p.yaml"
    _write(proto, {"sections": [
        {"id": "hero", "blocks": [{"type": "heading", "text": "Практический онлайн курс единственная строка контента здесь"}]},
        {"id": "tariffs", "blocks": [{"type": "tariff_card", "price": "standard"}]},
    ]})
    r = _run(src, proto, tmp_path / "rep.md")
    assert r.returncode == 1


def test_real_vip_name_not_flagged(tmp_path):
    # «ВИП» как реальное название тарифа не должно считаться галлюцинацией
    src = tmp_path / "src.txt"
    src.write_text("Тариф ВИП двести одиннадцать тысяч рублей полный доступ\n", encoding="utf-8")
    proto = tmp_path / "p.yaml"
    _write(proto, {"sections": [
        {"id": "tariffs", "blocks": [{"type": "tariff_card", "name": "ВИП",
                                      "text": "Тариф ВИП двести одиннадцать тысяч рублей полный доступ"}]},
    ]})
    r = _run(src, proto, tmp_path / "rep.md")
    assert r.returncode == 0, r.stdout
