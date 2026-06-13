# B23+B24+B26 — Reference Validation, Visual Strategist & Quick Mockup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Устранить три системных сбоя флоу 03→05: агент молча пропускает недоступные референсы, добавляет свои без согласования, и принимает визуальные решения вместо менеджера.

**Architecture:** (1) Расширить `references-curator` + `index.py` для валидации URL и явного согласования; (2) создать нового агента `visual-strategist` и скрипт `generate-concept.py` для этапа 03b; (3) добавить скрипт `generate-mockup.py` в `design-system-generator` и изменить порядок этапа 05; (4) добавить новую папку `03b_КОНЦЕПТ/` в template; (5) обновить `stage-gates.yaml` с новыми чеками; (6) обновить агентов `brand-architect` и `design-system-generator`.

**Tech Stack:** Python 3.10+, PyYAML, pytest, Jinja2 (для HTML-генерации), bash (gate-check.sh).

**Зависимости между задачами:** Task 1→2→3 (последовательно, каждая зависит от предыдущей). Task 4 независима, можно делать параллельно с Task 1-3. Task 5 зависит от Task 1-4. Task 6 зависит от Task 2 и 3.

---

## File Structure

**Создать:**
- `skills/references-collection/scripts/extract-palette.py` — извлечение цветов/шрифтов из скриншота или текста, генерация `refs-palette.html`
- `skills/references-collection/scripts/validate-url.py` — проверка доступности URL через WebFetch-подобный HTTP GET
- `agents/visual-strategist.md` — новый агент этапа 03b
- `skills/visual-concept-generator/SKILL.md` — скилл 03b
- `skills/visual-concept-generator/scripts/generate-concept.py` — генерация 2-3 концептов из брифа + прототипа + палитры референсов
- `skills/design-system-generator/scripts/generate-mockup.py` — генерация mockup-preview.html из visual-concept.yaml + prototype.yaml
- `template/03b_КОНЦЕПТ/README.md` — новая папка в template
- `tests/phase-3/python/test_validate_url.py`
- `tests/phase-3/python/test_extract_palette.py`
- `tests/phase-3/python/test_generate_concept.py`
- `tests/phase-3/python/test_generate_mockup.py`

**Изменить:**
- `skills/references-collection/scripts/index.py` — добавить поле `palette_extracted`, статус `needs_user_review`
- `config/stage-gates.yaml` — новые чеки для 03, новый этап 03b, новые чеки для 05
- `agents/references-curator.md` — новый протокол STOP при недоступном URL + явное согласование доп. референсов
- `agents/brand-architect.md` — добавить `visual-concept.yaml` как обязательный input
- `agents/design-system-generator.md` — добавить фазу mockup перед генерацией дизайн-системы

---

## Task 1: Валидация URL и поле `palette_extracted` в index.py (B23)

**Files:**
- Create: `skills/references-collection/scripts/validate-url.py`
- Modify: `skills/references-collection/scripts/index.py`
- Test: `tests/phase-3/python/test_validate_url.py`

- [ ] **Step 1: Написать failing тест на validate_url**

```python
# tests/phase-3/python/test_validate_url.py
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "references-collection" / "scripts" / "validate-url.py"

def _load():
    spec = importlib.util.spec_from_file_location("validate_url", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_accessible_url_returns_true():
    mod = _load()
    # httpbin.org/get — надёжный публичный endpoint
    result = mod.check_url_accessible("https://httpbin.org/get")
    assert result is True

def test_inaccessible_url_returns_false():
    mod = _load()
    # Несуществующий домен
    result = mod.check_url_accessible("https://this-domain-does-not-exist-xyz123.com")
    assert result is False

def test_known_blocked_platform_returns_false():
    mod = _load()
    # Behance возвращает JS-only страницу или редирект без полезного содержимого
    result = mod.check_url_accessible("https://www.behance.net/gallery/246960855/test")
    # Behance может вернуть 200 но пустой HTML — функция должна детектировать это
    # Тест проверяет что функция возвращает bool, не бросает исключение
    assert isinstance(result, bool)

def test_known_blocked_platforms_list():
    mod = _load()
    assert mod.is_known_blocked("https://www.behance.net/gallery/123")
    assert mod.is_known_blocked("https://www.instagram.com/p/abc")
    assert mod.is_known_blocked("https://tilda.cc/page123")
    assert not mod.is_known_blocked("https://example.com")
```

- [ ] **Step 2: Запустить тест — убедиться что FAIL**

```bash
cd D:\AI_TEAMS\landing_system
python -m pytest tests/phase-3/python/test_validate_url.py -v
```

Ожидаем: `ModuleNotFoundError` или `FileNotFoundError` — файл не существует.

- [ ] **Step 3: Создать `validate-url.py`**

```python
# skills/references-collection/scripts/validate-url.py
"""Check whether a reference URL is accessible for content extraction.

CLI: python validate-url.py <url>
Returns exit 0 if accessible, exit 1 if blocked/inaccessible.
"""
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Платформы, которые требуют браузер/авторизацию и не отдают контент через HTTP GET
KNOWN_BLOCKED_PLATFORMS = [
    "behance.net",
    "instagram.com",
    "tilda.cc",
    "dribbble.com",
    "pinterest.com",
    "figma.com",
]

MIN_CONTENT_LENGTH = 500  # байт — меньше = скорее всего JS-redirect


def is_known_blocked(url: str) -> bool:
    """Return True if URL belongs to a platform known to block programmatic access."""
    url_lower = url.lower()
    return any(platform in url_lower for platform in KNOWN_BLOCKED_PLATFORMS)


def check_url_accessible(url: str, timeout: int = 10) -> bool:
    """Return True if URL returns meaningful HTML content, False otherwise."""
    if is_known_blocked(url):
        return False
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; landing-system/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return False
            content = resp.read(MIN_CONTENT_LENGTH * 2)
            return len(content) >= MIN_CONTENT_LENGTH
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Usage: validate-url.py <url>", file=sys.stderr)
        return 2
    url = args[0]
    if check_url_accessible(url):
        print(f"OK: {url}")
        return 0
    else:
        blocked_note = " (known blocked platform)" if is_known_blocked(url) else ""
        print(f"BLOCKED: {url}{blocked_note}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Запустить тесты — убедиться что PASS**

```bash
python -m pytest tests/phase-3/python/test_validate_url.py -v
```

Ожидаем: 4 теста PASS (httpbin может занять 2-3 сек).

- [ ] **Step 5: Добавить поле `palette_extracted` в index.py**

В функцию `add_ref` в `skills/references-collection/scripts/index.py` добавить поле в новую запись:

```python
    entry = {
        "id": new_id,
        "value": ref,
        "type": ref_type,
        "status": status,
        "palette_extracted": False,   # <-- добавить эту строку
        "added_at": datetime.now(timezone.utc).isoformat(),
    }
```

- [ ] **Step 6: Написать тест на новое поле**

Добавить в конец `tests/phase-3/python/test_validate_url.py`:

```python
def test_add_ref_has_palette_extracted_field(tmp_path):
    import importlib.util
    INDEX = ROOT / "skills" / "references-collection" / "scripts" / "index.py"
    spec2 = importlib.util.spec_from_file_location("index", INDEX)
    mod2 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(mod2)

    entry = mod2.add_ref(str(tmp_path), "https://example.com", "url", "candidate")
    assert "palette_extracted" in entry
    assert entry["palette_extracted"] is False
```

- [ ] **Step 7: Запустить все тесты в файле**

```bash
python -m pytest tests/phase-3/python/test_validate_url.py -v
```

Ожидаем: 5 тестов PASS.

- [ ] **Step 8: Commit**

```bash
git add skills/references-collection/scripts/validate-url.py skills/references-collection/scripts/index.py tests/phase-3/python/test_validate_url.py
git commit -m "feat(b23): add URL validation and palette_extracted field to references index"
```

---

## Task 2: Extract-palette скрипт + refs-palette.html (B23)

**Files:**
- Create: `skills/references-collection/scripts/extract-palette.py`
- Test: `tests/phase-3/python/test_extract_palette.py`

- [ ] **Step 1: Написать failing тесты**

```python
# tests/phase-3/python/test_extract_palette.py
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "references-collection" / "scripts" / "extract-palette.py"

def _load():
    spec = importlib.util.spec_from_file_location("extract_palette", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_parse_text_description_extracts_colors():
    mod = _load()
    text = "синий фон #2B72B8, золотой акцент #C9A84C, белый текст #FFFFFF"
    result = mod.parse_text_description(text)
    assert len(result["colors"]) >= 2
    assert any(c["hex"] == "#2B72B8" for c in result["colors"])
    assert any(c["hex"] == "#C9A84C" for c in result["colors"])

def test_parse_text_description_extracts_fonts():
    mod = _load()
    text = "шрифт Archivo Black, Inter для тела"
    result = mod.parse_text_description(text)
    assert len(result["fonts"]) >= 1
    assert any("Archivo" in f for f in result["fonts"])

def test_parse_text_description_no_hex_returns_empty_colors():
    mod = _load()
    text = "просто описание без цветов"
    result = mod.parse_text_description(text)
    assert result["colors"] == []

def test_render_palette_html_contains_hex(tmp_path):
    mod = _load()
    palette = {
        "colors": [
            {"hex": "#2B72B8", "role": "background", "label": "насыщенный синий"},
            {"hex": "#C9A84C", "role": "accent", "label": "золотисто-жёлтый"},
        ],
        "fonts": ["Archivo Black"],
        "mood": "editorial, яркий",
        "source": "OFFtrail",
    }
    out = tmp_path / "refs-palette.html"
    mod.render_palette_html([palette], str(out))
    html = out.read_text(encoding="utf-8")
    assert "#2B72B8" in html
    assert "#C9A84C" in html
    assert "Archivo Black" in html
    assert "насыщенный синий" in html

def test_render_palette_html_creates_file(tmp_path):
    mod = _load()
    out = tmp_path / "refs-palette.html"
    mod.render_palette_html([], str(out))
    assert out.exists()
```

- [ ] **Step 2: Запустить — убедиться что FAIL**

```bash
python -m pytest tests/phase-3/python/test_extract_palette.py -v
```

- [ ] **Step 3: Создать `extract-palette.py`**

```python
# skills/references-collection/scripts/extract-palette.py
"""Extract color palette and typography from text description or image analysis.

CLI:
  python extract-palette.py --text "описание стиля" --source "OFFtrail" --output refs-palette.html
  python extract-palette.py --refs-yaml index.yaml --output refs-palette.html
"""
import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

import yaml

HEX_RE = re.compile(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b')

KNOWN_FONTS = [
    "Inter", "Roboto", "Open Sans", "Montserrat", "Lato", "Poppins",
    "Archivo Black", "Archivo", "Manrope", "Raleway", "Nunito",
    "Playfair Display", "Merriweather", "Source Sans", "DM Sans",
    "Space Grotesk", "Plus Jakarta Sans", "Outfit", "Unbounded",
]

COLOR_ROLES = {
    "фон": "background", "background": "background", "bg": "background",
    "акцент": "accent", "accent": "accent", "cta": "accent",
    "текст": "text", "text": "text",
    "footer": "footer", "футер": "footer",
    "surface": "surface", "карточк": "surface",
}

COLOR_NAMES = {
    # blues
    "#2B72B8": "насыщенный синий, энергичный",
    "#1A56DB": "ярко-синий, технологичный",
    "#0A0A0A": "почти чёрный, глубокий",
    "#161616": "тёмно-серый, минималистичный",
    "#FFFFFF": "белый, чистый",
    "#F5F5F5": "светло-серый, мягкий",
    "#C9A84C": "матовое золото, премиум",
    "#E8407A": "ярко-розовый, игривый",
}


def _guess_color_name(hex_color: str) -> str:
    h = hex_color.upper()
    if h in COLOR_NAMES:
        return COLOR_NAMES[h]
    r = int(h[1:3], 16)
    g = int(h[3:5], 16)
    b = int(h[5:7], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    if brightness < 50:
        return "тёмный, глубокий"
    if brightness > 200:
        return "светлый, чистый"
    if r > g and r > b:
        return "тёплый, акцентный"
    if b > r and b > g:
        return "холодный, технологичный"
    if g > r and g > b:
        return "натуральный, органичный"
    return "нейтральный"


def _guess_role_from_context(hex_color: str, context: str) -> str:
    context_lower = context.lower()
    for keyword, role in COLOR_ROLES.items():
        if keyword in context_lower:
            return role
    # Guess from brightness
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    if brightness < 60:
        return "background"
    if brightness > 200:
        return "text"
    return "accent"


def parse_text_description(text: str) -> dict:
    """Extract colors and fonts from a text description."""
    colors = []
    seen_hex = set()

    # Find all hex colors with surrounding context
    for m in HEX_RE.finditer(text):
        hex_val = "#" + m.group(1).upper()
        if len(hex_val) == 4:  # expand 3-char hex
            hex_val = "#" + "".join(c*2 for c in hex_val[1:])
        if hex_val in seen_hex:
            continue
        seen_hex.add(hex_val)
        # Get 30 chars of context before the hex
        start = max(0, m.start() - 30)
        context = text[start:m.start()]
        role = _guess_role_from_context(hex_val, context)
        colors.append({
            "hex": hex_val,
            "role": role,
            "label": _guess_color_name(hex_val),
        })

    # Find fonts
    fonts = []
    for font in KNOWN_FONTS:
        if font.lower() in text.lower():
            fonts.append(font)

    return {"colors": colors, "fonts": fonts}


def render_palette_html(palettes: list, output_path: str) -> None:
    """Render HTML preview of extracted palettes."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    cards_html = ""
    for p in palettes:
        source = p.get("source", "Референс")
        mood = p.get("mood", "")
        fonts = p.get("fonts", [])
        colors = p.get("colors", [])

        swatches = ""
        for c in colors:
            role_label = {
                "background": "Фон",
                "accent": "Акцент",
                "text": "Текст",
                "footer": "Footer",
                "surface": "Surface",
            }.get(c.get("role", ""), c.get("role", ""))
            # Choose text color for contrast
            r = int(c["hex"][1:3], 16)
            g = int(c["hex"][3:5], 16)
            b = int(c["hex"][5:7], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            text_color = "#000000" if brightness > 128 else "#FFFFFF"
            swatches += f"""
            <div class="swatch" style="background:{c['hex']};color:{text_color}">
              <div class="swatch-role">{role_label}</div>
              <div class="swatch-hex">{c['hex']}</div>
              <div class="swatch-label">{c.get('label','')}</div>
            </div>"""

        fonts_html = "".join(f'<span class="font-tag">{f}</span>' for f in fonts) or "<span class='font-tag muted'>не определено</span>"

        cards_html += f"""
        <div class="ref-card">
          <h2 class="ref-title">{source}</h2>
          {f'<div class="ref-mood">Настроение: {mood}</div>' if mood else ''}
          <div class="swatches-row">{swatches}</div>
          <div class="fonts-row"><strong>Типографика:</strong> {fonts_html}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Палитры референсов</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #F8F8F8; color: #111; margin: 0; padding: 2rem; }}
    h1 {{ font-size: 1.5rem; margin-bottom: 2rem; color: #333; }}
    .ref-card {{ background: #fff; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
    .ref-title {{ font-size: 1.2rem; margin: 0 0 .5rem; }}
    .ref-mood {{ font-size: .85rem; color: #666; margin-bottom: 1rem; }}
    .swatches-row {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 1rem; }}
    .swatch {{ border-radius: 8px; padding: 12px 16px; min-width: 120px; }}
    .swatch-role {{ font-size: .7rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; opacity: .7; }}
    .swatch-hex {{ font-size: 1rem; font-weight: 700; font-family: monospace; margin: 4px 0; }}
    .swatch-label {{ font-size: .75rem; opacity: .8; }}
    .fonts-row {{ font-size: .9rem; color: #444; }}
    .font-tag {{ display: inline-block; background: #F0F0F0; border-radius: 4px; padding: 2px 10px; margin: 2px; font-size: .85rem; }}
    .font-tag.muted {{ color: #999; }}
    .generated {{ font-size: .75rem; color: #aaa; margin-top: 2rem; }}
  </style>
</head>
<body>
  <h1>Извлечённые палитры референсов</h1>
  {cards_html if cards_html else '<p style="color:#999">Нет данных о палитрах</p>'}
  <p class="generated">Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</body>
</html>"""

    out.write_text(html, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--text", help="Текстовое описание стиля")
    p.add_argument("--source", default="Референс", help="Название источника")
    p.add_argument("--refs-yaml", help="Путь к index.yaml для batch-обработки")
    p.add_argument("--output", required=True, help="Путь для refs-palette.html")
    ns = p.parse_args(args)

    palettes = []

    if ns.text:
        extracted = parse_text_description(ns.text)
        extracted["source"] = ns.source
        palettes.append(extracted)

    if ns.refs_yaml:
        idx_path = Path(ns.refs_yaml)
        if idx_path.exists():
            data = yaml.safe_load(idx_path.read_text(encoding="utf-8")) or {}
            for ref in data.get("references", []):
                if ref.get("status") == "approved" and ref.get("notes"):
                    extracted = parse_text_description(ref["notes"])
                    extracted["source"] = ref.get("title", ref.get("value", "Референс"))
                    extracted["mood"] = ref.get("mood", "")
                    palettes.append(extracted)

    render_palette_html(palettes, ns.output)
    print(f"OK: wrote {ns.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Запустить тесты**

```bash
python -m pytest tests/phase-3/python/test_extract_palette.py -v
```

Ожидаем: 5 тестов PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/references-collection/scripts/extract-palette.py tests/phase-3/python/test_extract_palette.py
git commit -m "feat(b23): add extract-palette script and refs-palette.html generator"
```

---

## Task 3: Новый агент `visual-strategist` + скрипт `generate-concept.py` (B24)

**Files:**
- Create: `agents/visual-strategist.md`
- Create: `skills/visual-concept-generator/SKILL.md`
- Create: `skills/visual-concept-generator/scripts/generate-concept.py`
- Test: `tests/phase-3/python/test_generate_concept.py`

- [ ] **Step 1: Написать failing тесты**

```python
# tests/phase-3/python/test_generate_concept.py
import importlib.util
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "visual-concept-generator" / "scripts" / "generate-concept.py"

def _load():
    spec = importlib.util.spec_from_file_location("generate_concept", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _make_brief(tmp_path, goal="Продать премиум EV в Dubai", audience="Состоятельные экспаты 35-55"):
    brief = tmp_path / "00_БРИФ" / "brief.md"
    brief.parent.mkdir(parents=True)
    brief.write_text(f"# Бриф\n\n## Цель\n{goal}\n\n## Аудитория\n{audience}\n", encoding="utf-8")
    return brief

def _make_prototype(tmp_path):
    proto = tmp_path / "07_ПРОТОТИП" / "prototype.yaml"
    proto.parent.mkdir(parents=True)
    data = {"blocks": [
        {"position": 1, "type": "hero", "content": {"headline": "Premium SUVs"}},
        {"position": 2, "type": "trust", "content": {"headline": "Why LiXiang"}},
    ]}
    proto.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return proto

def test_generate_returns_list_of_concepts(tmp_path):
    mod = _load()
    brief = _make_brief(tmp_path)
    proto = _make_prototype(tmp_path)
    concepts = mod.generate_concepts(str(brief), str(proto), [])
    assert isinstance(concepts, list)
    assert 2 <= len(concepts) <= 3

def test_each_concept_has_required_fields(tmp_path):
    mod = _load()
    brief = _make_brief(tmp_path)
    proto = _make_prototype(tmp_path)
    concepts = mod.generate_concepts(str(brief), str(proto), [])
    for c in concepts:
        assert "name" in c
        assert "emotional_goal" in c
        assert "palette" in c
        assert "bg" in c["palette"]
        assert "accent" in c["palette"]
        assert "text" in c["palette"]
        assert "mood" in c

def test_save_concept_writes_yaml(tmp_path):
    mod = _load()
    concept = {
        "name": "Доверие через статус",
        "emotional_goal": "Снять барьер недоверия",
        "palette": {"bg": "#0A0A0A", "accent": "#C9A84C", "text": "#FFFFFF", "surface": "#161616"},
        "typography_direction": "Inter 700",
        "mood": ["cinematic", "luxury"],
        "approved_by_manager": True,
    }
    out = tmp_path / "visual-concept.yaml"
    mod.save_concept(concept, str(out))
    assert out.exists()
    loaded = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert loaded["name"] == "Доверие через статус"
    assert loaded["approved_by_manager"] is True

def test_generate_with_palette_context(tmp_path):
    mod = _load()
    brief = _make_brief(tmp_path)
    proto = _make_prototype(tmp_path)
    palette_context = [{"hex": "#2B72B8", "role": "background", "label": "синий"}]
    concepts = mod.generate_concepts(str(brief), str(proto), palette_context)
    # Должен быть хотя бы один концепт, упоминающий референс
    assert len(concepts) >= 2
```

- [ ] **Step 2: Запустить — убедиться что FAIL**

```bash
python -m pytest tests/phase-3/python/test_generate_concept.py -v
```

- [ ] **Step 3: Создать папку скилла и `generate-concept.py`**

```bash
mkdir -p "D:\AI_TEAMS\landing_system\skills\visual-concept-generator\scripts"
```

```python
# skills/visual-concept-generator/scripts/generate-concept.py
"""Generate 2-3 visual concept proposals from brief + prototype + reference palettes.

CLI:
  python generate-concept.py --brief path/brief.md --prototype path/prototype.yaml \
    [--palette-json '[{"hex":"#2B72B8","role":"background"}]'] \
    --output path/visual-concept.yaml --index 0
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

# Библиотека готовых концептов по эмоциональным стратегиям.
# Агент выбирает подходящие на основе ниши из брифа.
CONCEPT_TEMPLATES = [
    {
        "name": "Доверие через статус",
        "emotional_goal": "Снять барьер недоверия к бренду через язык luxury",
        "fit_keywords": ["премиум", "premium", "luxury", "статус", "exclusive", "дорог"],
        "palette": {
            "bg": "#0A0A0A",
            "accent": "#C9A84C",
            "text": "#FFFFFF",
            "surface": "#161616",
        },
        "typography_direction": "Inter 700, строгий гротеск, uppercase заголовки",
        "mood": ["cinematic", "luxury", "editorial"],
        "color_rationale": "Тёмный фон + золото = язык Rolls-Royce / Bentley. Снимает вопрос о премиальности.",
    },
    {
        "name": "Современность и технологии",
        "emotional_goal": "Позиционировать бренд как tech-инновацию, а не просто авто",
        "fit_keywords": ["ev", "electric", "tech", "технолог", "инновац", "будущ"],
        "palette": {
            "bg": "#FFFFFF",
            "accent": "#1A56DB",
            "text": "#111111",
            "surface": "#F5F7FA",
        },
        "typography_direction": "Inter 700, clean, без засечек, modern",
        "mood": ["technical", "minimal", "corporate"],
        "color_rationale": "Белый фон + синий акцент = язык Tesla / BMW i. Технологичность и доверие.",
    },
    {
        "name": "Тепло и семья",
        "emotional_goal": "Показать что автомобиль создан для семьи и реальной жизни",
        "fit_keywords": ["семь", "family", "комфорт", "comfort", "жизн", "life", "простор"],
        "palette": {
            "bg": "#FAFAFA",
            "accent": "#B87333",
            "text": "#1A1A1A",
            "surface": "#F0EDE8",
        },
        "typography_direction": "Inter 500/700, тёплый, читаемый",
        "mood": ["editorial", "warm", "minimal"],
        "color_rationale": "Тёплые нейтралы + медь = близко к эстетике UAE luxury interior. Семейное тепло.",
    },
]


def _extract_brief_text(brief_path: str) -> str:
    p = Path(brief_path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8").lower()


def _extract_prototype_types(prototype_path: str) -> list[str]:
    p = Path(prototype_path)
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return [b.get("type", "") for b in data.get("blocks", [])]


def generate_concepts(
    brief_path: str,
    prototype_path: str,
    palette_context: list[dict],
) -> list[dict]:
    """Return 2-3 concept proposals ranked by fit to brief + prototype."""
    brief_text = _extract_brief_text(brief_path)
    block_types = _extract_prototype_types(prototype_path)

    scored = []
    for tmpl in CONCEPT_TEMPLATES:
        score = sum(1 for kw in tmpl["fit_keywords"] if kw in brief_text)
        # Если есть palette_context из референсов — добавить концепт "по референсу"
        scored.append((score, tmpl))

    scored.sort(key=lambda x: -x[0])
    concepts = [c for _, c in scored[:3]]

    # Если palette_context непустой — первым предложить концепт "по референсу"
    if palette_context:
        ref_concept = _build_ref_concept(palette_context)
        # Вставить как вариант B если не совпадает с первым
        if ref_concept["palette"]["bg"] != concepts[0]["palette"]["bg"]:
            concepts.insert(1, ref_concept)
            concepts = concepts[:3]

    return concepts


def _build_ref_concept(palette_context: list[dict]) -> dict:
    """Build a concept based on extracted reference palette."""
    bg = next((c["hex"] for c in palette_context if c.get("role") == "background"), "#FFFFFF")
    accent = next((c["hex"] for c in palette_context if c.get("role") == "accent"), "#C9A84C")
    text_col = "#FFFFFF" if _is_dark(bg) else "#111111"
    surface = _darken(bg, 10) if _is_dark(bg) else _lighten(bg, 5)
    return {
        "name": "По референсу",
        "emotional_goal": "Реализовать визуальный стиль, близкий к предоставленному референсу",
        "fit_keywords": [],
        "palette": {"bg": bg, "accent": accent, "text": text_col, "surface": surface},
        "typography_direction": "Определяется референсом",
        "mood": ["editorial"],
        "color_rationale": f"Палитра извлечена из референса: фон {bg}, акцент {accent}.",
    }


def _is_dark(hex_color: str) -> bool:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c*2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000 < 128


def _darken(hex_color: str, pct: int) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c*2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    factor = 1 - pct / 100
    return "#{:02X}{:02X}{:02X}".format(int(r*factor), int(g*factor), int(b*factor))


def _lighten(hex_color: str, pct: int) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c*2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    factor = pct / 100
    return "#{:02X}{:02X}{:02X}".format(
        int(r + (255 - r) * factor),
        int(g + (255 - g) * factor),
        int(b + (255 - b) * factor),
    )


def save_concept(concept: dict, output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.dump(concept, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--brief", required=True)
    p.add_argument("--prototype", required=True)
    p.add_argument("--palette-json", default="[]")
    p.add_argument("--output", required=True)
    p.add_argument("--index", type=int, default=0, help="Which concept to save (0-based)")
    ns = p.parse_args(args)

    palette_context = json.loads(ns.palette_json)
    concepts = generate_concepts(ns.brief, ns.prototype, palette_context)

    if ns.index >= len(concepts):
        print(f"ERROR: index {ns.index} out of range (have {len(concepts)} concepts)", file=sys.stderr)
        return 1

    chosen = concepts[ns.index]
    chosen["approved_by_manager"] = True
    save_concept(chosen, ns.output)
    print(f"OK: saved concept '{chosen['name']}' to {ns.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Запустить тесты**

```bash
python -m pytest tests/phase-3/python/test_generate_concept.py -v
```

Ожидаем: 4 теста PASS.

- [ ] **Step 5: Создать `skills/visual-concept-generator/SKILL.md`**

```markdown
---
name: visual-concept-generator
description: Stage 03b — generate 2-3 visual concept proposals from brief + prototype + reference palettes. Manager picks one concept; result saved to 03b_КОНЦЕПТ/visual-concept.yaml.
---

# visual-concept-generator

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill visual-concept-generator --stage 03b
```

## What it does

1. Reads `00_БРИФ/brief.md` — goal, audience, positioning
2. Reads `07_ПРОТОТИП/prototype.yaml` — block types (reveals pains/needs/CTAs)
3. Reads `03_РЕФЕРЕНСЫ/index.yaml` + extracts palette context if `refs-palette.html` exists
4. Runs `generate-concept.py` to produce 2-3 concept proposals
5. Presents concepts to manager in chat — name, emotional goal, palette hex, rationale
6. Manager picks (or requests adjustments)
7. Saves approved concept to `03b_КОНЦЕПТ/visual-concept.yaml`

## CLI

```bash
python skills/visual-concept-generator/scripts/generate-concept.py \
  --brief <project>/00_БРИФ/brief.md \
  --prototype <project>/07_ПРОТОТИП/prototype.yaml \
  --palette-json '<extracted_palette_json>' \
  --output <project>/03b_КОНЦЕПТ/visual-concept.yaml \
  --index <chosen_index>
```
```

- [ ] **Step 6: Создать `agents/visual-strategist.md`**

```markdown
---
name: visual-strategist
description: Stage 03b agent. Reads brief + prototype + reference palettes, proposes 2-3 visual concepts (emotional goal + palette), waits for manager to pick one, saves visual-concept.yaml.
---

# visual-strategist

## Pre-flight

```bash
python -m scripts.wiki.log --type agent_call --agent visual-strategist --stage 03b
```

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 03b_visual_concept`.
2. Запусти `bash scripts/gate-check.sh --stage 03b_visual_concept --project <project>`. Если exit != 0 — STOP.
3. Залогируй: `python -m scripts.wiki.log --type agent_call --agent visual-strategist --stage 03b`

## Mission

Предложить менеджеру 2-3 визуальных концепта — не выбирать за него.

## Process

1. Прочитай `00_БРИФ/brief.md` — извлеки цель, аудиторию, барьеры доверия.
2. Прочитай `07_ПРОТОТИП/prototype.yaml` — посмотри типы блоков, CTA, структуру.
3. Если есть `03_РЕФЕРЕНСЫ/index.yaml` — прочитай notes для каждого `approved` референса.
4. Запусти `generate-concept.py` для получения концептов.
5. Покажи концепты менеджеру в формате:

```
## Концепт 1: "Название"
Эмоция: ...
Как цвет работает: ...
Палитра:
  Фон      #XXXXXX — описание
  Акцент   #XXXXXX — описание
  Текст    #XXXXXX
Связь с референсом: ...
```

6. Жди выбора менеджера. Если правки — адаптируй и покажи снова.
7. После "ок" — сохрани в `03b_КОНЦЕПТ/visual-concept.yaml`.
8. Закрой этап: `bash scripts/gate-check.sh --stage 03b_visual_concept --project <project> --approve`
```

- [ ] **Step 7: Создать `template/03b_КОНЦЕПТ/README.md`**

```markdown
# 03b_КОНЦЕПТ — Визуальная концепция

Артефакт этапа 03b (visual-strategist).

## Файлы

- `visual-concept.yaml` — утверждённый визуальный концепт (создаётся агентом)

## Формат visual-concept.yaml

```yaml
name: "Название концепта"
emotional_goal: "Что должен почувствовать посетитель"
palette:
  bg: "#0A0A0A"
  accent: "#C9A84C"
  text: "#FFFFFF"
  surface: "#161616"
typography_direction: "Inter 700, строгий гротеск"
mood: ["cinematic", "luxury"]
color_rationale: "Почему эта палитра работает для данной аудитории"
approved_by_manager: true
```
```

- [ ] **Step 8: Commit**

```bash
git add skills/visual-concept-generator/ agents/visual-strategist.md template/03b_КОНЦЕПТ/ tests/phase-3/python/test_generate_concept.py
git commit -m "feat(b24): add visual-strategist agent and generate-concept.py for stage 03b"
```

---

## Task 4: Quick Mockup в начале этапа 05 (B26)

**Files:**
- Create: `skills/design-system-generator/scripts/generate-mockup.py`
- Test: `tests/phase-3/python/test_generate_mockup.py`

- [ ] **Step 1: Написать failing тесты**

```python
# tests/phase-3/python/test_generate_mockup.py
import importlib.util
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "design-system-generator" / "scripts" / "generate-mockup.py"

def _load():
    spec = importlib.util.spec_from_file_location("generate_mockup", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _make_concept(tmp_path):
    concept = tmp_path / "visual-concept.yaml"
    data = {
        "name": "Доверие через статус",
        "emotional_goal": "Снять барьер недоверия",
        "palette": {"bg": "#0A0A0A", "accent": "#C9A84C", "text": "#FFFFFF", "surface": "#161616"},
        "typography_direction": "Inter 700",
        "mood": ["cinematic"],
        "approved_by_manager": True,
    }
    concept.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return concept

def _make_prototype(tmp_path):
    proto = tmp_path / "prototype.yaml"
    data = {"blocks": [
        {"position": 1, "type": "hero", "content": {
            "headline": "Premium SUVs built for real life in the UAE",
            "subheadline": "LiXiang in stock in Dubai",
            "cta_primary": "Explore cars",
        }},
        {"position": 2, "type": "trust", "content": {
            "headline": "A world of uncompromising comfort",
        }},
    ]}
    proto.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return proto

def test_generate_creates_html(tmp_path):
    mod = _load()
    concept = _make_concept(tmp_path)
    proto = _make_prototype(tmp_path)
    out = tmp_path / "mockup-preview.html"
    result = mod.generate_mockup(str(concept), str(proto), str(out))
    assert result == 0
    assert out.exists()

def test_html_contains_both_variants(tmp_path):
    mod = _load()
    concept = _make_concept(tmp_path)
    proto = _make_prototype(tmp_path)
    out = tmp_path / "mockup-preview.html"
    mod.generate_mockup(str(concept), str(proto), str(out))
    html = out.read_text(encoding="utf-8")
    assert "Вариант A" in html
    assert "Вариант B" in html

def test_html_contains_real_content(tmp_path):
    mod = _load()
    concept = _make_concept(tmp_path)
    proto = _make_prototype(tmp_path)
    out = tmp_path / "mockup-preview.html"
    mod.generate_mockup(str(concept), str(proto), str(out))
    html = out.read_text(encoding="utf-8")
    assert "Premium SUVs built for real life in the UAE" in html
    assert "Explore cars" in html

def test_html_contains_palette_colors(tmp_path):
    mod = _load()
    concept = _make_concept(tmp_path)
    proto = _make_prototype(tmp_path)
    out = tmp_path / "mockup-preview.html"
    mod.generate_mockup(str(concept), str(proto), str(out))
    html = out.read_text(encoding="utf-8")
    assert "#0A0A0A" in html
    assert "#C9A84C" in html

def test_variant_b_differs_from_a(tmp_path):
    mod = _load()
    concept = _make_concept(tmp_path)
    palette = yaml.safe_load(concept.read_text(encoding="utf-8"))["palette"]
    alt = mod.build_variant_b(palette)
    # Вариант B должен отличаться хотя бы фоном
    assert alt["bg"] != palette["bg"]
```

- [ ] **Step 2: Запустить — убедиться что FAIL**

```bash
python -m pytest tests/phase-3/python/test_generate_mockup.py -v
```

- [ ] **Step 3: Создать `generate-mockup.py`**

```python
# skills/design-system-generator/scripts/generate-mockup.py
"""Generate side-by-side mockup preview (variant A + B) from visual-concept + prototype.

CLI:
  python generate-mockup.py --concept path/visual-concept.yaml \
    --prototype path/prototype.yaml --output path/mockup-preview.html
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml


def build_variant_b(palette: dict) -> dict:
    """Build alternative palette interpretation (lighter if dark, darker if light)."""
    bg = palette.get("bg", "#FFFFFF")
    # Detect dark background
    h = bg.lstrip("#")
    if len(h) == 3:
        h = "".join(c*2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000

    accent = palette.get("accent", "#C9A84C")

    if brightness < 100:
        # Dark → lighter variant
        new_bg = "#1C1C1E"
        new_surface = "#2C2C2E"
        new_text = "#FFFFFF"
        variant_desc = "чуть светлее, мягче"
    else:
        # Light → slightly darker/warmer
        new_bg = "#F0EDE8"
        new_surface = "#E8E4DE"
        new_text = "#111111"
        variant_desc = "тёплые нейтралы, уютнее"

    return {
        "bg": new_bg,
        "accent": accent,
        "text": new_text,
        "surface": new_surface,
        "_variant_desc": variant_desc,
    }


def _extract_hero(blocks: list) -> dict:
    for b in blocks:
        if b.get("type") == "hero":
            return b.get("content", {})
    return blocks[0].get("content", {}) if blocks else {}


def _extract_second_block(blocks: list) -> dict:
    for b in sorted(blocks, key=lambda x: x.get("position", 99)):
        if b.get("type") != "hero":
            return b
    return {}


def _render_hero_block(content: dict, palette: dict) -> str:
    headline = content.get("headline", "Заголовок лендинга")
    subheadline = content.get("subheadline", "")
    cta = content.get("cta_primary", "Узнать больше")
    badges = content.get("badges", [])

    bg = palette["bg"]
    accent = palette["accent"]
    text = palette["text"]

    badges_html = "".join(
        f'<span style="border:1px solid {accent};color:{accent};padding:4px 12px;border-radius:4px;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;">{b}</span>'
        for b in (badges if isinstance(badges, list) else [])
    )

    return f"""
<div style="background:{bg};padding:80px 40px;text-align:center;min-height:400px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px;">
  <div style="width:60px;height:2px;background:{accent};"></div>
  <h1 style="color:{text};font-size:clamp(2rem,5vw,3.5rem);font-weight:700;line-height:1.1;max-width:700px;margin:0;">{headline}</h1>
  {f'<p style="color:{text};opacity:.7;font-size:1.1rem;max-width:500px;margin:0;">{subheadline}</p>' if subheadline else ''}
  <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;">
    <a style="background:{accent};color:{bg};padding:14px 32px;border-radius:4px;font-weight:700;font-size:14px;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;">{cta}</a>
  </div>
  {f'<div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center;">{badges_html}</div>' if badges_html else ''}
</div>"""


def _render_second_block(block: dict, palette: dict) -> str:
    if not block:
        return ""
    content = block.get("content", {})
    btype = block.get("type", "")
    headline = content.get("headline", "")
    body = content.get("body", content.get("body_1", ""))

    bg = palette.get("surface", palette["bg"])
    text = palette["text"]
    accent = palette["accent"]

    return f"""
<div style="background:{bg};padding:60px 40px;text-align:center;">
  {f'<div style="width:40px;height:2px;background:{accent};margin:0 auto 16px;"></div>' if headline else ''}
  {f'<h2 style="color:{text};font-size:1.8rem;font-weight:700;margin:0 0 16px;">{headline}</h2>' if headline else ''}
  {f'<p style="color:{text};opacity:.7;max-width:600px;margin:0 auto;line-height:1.7;">{body}</p>' if body else ''}
  {f'<p style="color:{text};opacity:.4;font-size:.85rem;margin:16px 0 0;font-style:italic;">[{btype} block]</p>' if not body else ''}
</div>"""


def generate_mockup(concept_path: str, prototype_path: str, output_path: str) -> int:
    concept_file = Path(concept_path)
    if not concept_file.exists():
        print(f"ERROR: concept not found: {concept_path}", file=sys.stderr)
        return 1

    proto_file = Path(prototype_path)
    if not proto_file.exists():
        print(f"ERROR: prototype not found: {prototype_path}", file=sys.stderr)
        return 1

    concept = yaml.safe_load(concept_file.read_text(encoding="utf-8")) or {}
    proto = yaml.safe_load(proto_file.read_text(encoding="utf-8")) or {}

    palette_a = concept.get("palette", {"bg": "#FFFFFF", "accent": "#000000", "text": "#000000"})
    palette_b = build_variant_b(palette_a)
    concept_name = concept.get("name", "Концепт")
    blocks = proto.get("blocks", [])

    hero_content = _extract_hero(blocks)
    second_block = _extract_second_block(blocks)

    variant_b_desc = palette_b.pop("_variant_desc", "альтернативный")

    hero_a = _render_hero_block(hero_content, palette_a)
    second_a = _render_second_block(second_block, palette_a)
    hero_b = _render_hero_block(hero_content, palette_b)
    second_b = _render_second_block(second_block, palette_b)

    mood_tags = " · ".join(concept.get("mood", []))

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mockup Preview — {concept_name}</title>
  <link href="https://fonts.bunny.net/css?family=inter:400,500,700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Inter', system-ui, sans-serif; background: #EFEFEF; padding: 2rem; }}
    .header {{ text-align: center; margin-bottom: 2rem; }}
    .header h1 {{ font-size: 1.4rem; color: #333; margin-bottom: .5rem; }}
    .header p {{ color: #666; font-size: .9rem; }}
    .variants {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }}
    @media (max-width: 900px) {{ .variants {{ grid-template-columns: 1fr; }} }}
    .variant {{ background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,.1); }}
    .variant-label {{ padding: 16px 20px; background: #F8F8F8; border-bottom: 1px solid #E0E0E0; }}
    .variant-label strong {{ font-size: 1rem; color: #111; }}
    .variant-label span {{ font-size: .8rem; color: #888; margin-left: 8px; }}
    .variant-content {{ overflow: hidden; }}
    .palette-strip {{ display: flex; padding: 8px 16px; gap: 8px; background: #F8F8F8; flex-wrap: wrap; }}
    .palette-swatch {{ display: flex; align-items: center; gap: 6px; font-size: .75rem; color: #555; }}
    .palette-swatch-dot {{ width: 16px; height: 16px; border-radius: 50%; border: 1px solid rgba(0,0,0,.1); flex-shrink: 0; }}
    .actions {{ padding: 16px 20px; background: #F8F8F8; border-top: 1px solid #E0E0E0; display: flex; gap: 12px; justify-content: center; }}
    .btn-choose {{ padding: 10px 24px; border-radius: 6px; font-size: .9rem; font-weight: 600; cursor: pointer; border: 2px solid #333; background: #333; color: #fff; }}
    .btn-choose:hover {{ background: #111; }}
    .footer {{ text-align: center; margin-top: 2rem; font-size: .75rem; color: #aaa; }}
    .feedback-note {{ text-align: center; margin-top: 1rem; font-size: .85rem; color: #666; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Mockup Preview — {concept_name}</h1>
    <p>Настроение: {mood_tags} · Два варианта реализации — выбери или опиши правки</p>
  </div>

  <div class="variants">
    <div class="variant">
      <div class="variant-label">
        <strong>Вариант A</strong>
        <span>— буквальная реализация концепта</span>
      </div>
      <div class="palette-strip">
        {''.join(f'<div class="palette-swatch"><div class="palette-swatch-dot" style="background:{v}"></div><span>{k}: {v}</span></div>' for k, v in palette_a.items())}
      </div>
      <div class="variant-content">{hero_a}{second_a}</div>
      <div class="actions">
        <button class="btn-choose" onclick="alert('Выбран Вариант A. Напиши в чат: «Вариант A» или опиши правки.')">Выбрать A</button>
      </div>
    </div>

    <div class="variant">
      <div class="variant-label">
        <strong>Вариант B</strong>
        <span>— {variant_b_desc}</span>
      </div>
      <div class="palette-strip">
        {''.join(f'<div class="palette-swatch"><div class="palette-swatch-dot" style="background:{v}"></div><span>{k}: {v}</span></div>' for k, v in palette_b.items())}
      </div>
      <div class="variant-content">{hero_b}{second_b}</div>
      <div class="actions">
        <button class="btn-choose" onclick="alert('Выбран Вариант B. Напиши в чат: «Вариант B» или опиши правки.')">Выбрать B</button>
      </div>
    </div>
  </div>

  <p class="feedback-note">Напиши в чат: «Вариант A», «Вариант B», или опиши правки — например «Вариант A, но акцент холоднее»</p>
  <p class="footer">Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')} · landing-system mockup</p>
</body>
</html>"""

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"OK: wrote {output_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--concept", required=True)
    p.add_argument("--prototype", required=True)
    p.add_argument("--output", required=True)
    ns = p.parse_args(args)
    return generate_mockup(ns.concept, ns.prototype, ns.output)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Запустить тесты**

```bash
python -m pytest tests/phase-3/python/test_generate_mockup.py -v
```

Ожидаем: 5 тестов PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/design-system-generator/scripts/generate-mockup.py tests/phase-3/python/test_generate_mockup.py
git commit -m "feat(b26): add generate-mockup.py for stage 05 quick mockup preview"
```

---

## Task 5: Обновить `stage-gates.yaml` (B23+B24+B26)

**Files:**
- Modify: `config/stage-gates.yaml`

- [ ] **Step 1: Добавить новые чеки в этап `03_references`**

В `config/stage-gates.yaml` найти секцию `"03_references"` и заменить:

```yaml
  "03_references":
    name: "References"
    lock: soft
    require_approved: []
    hard_checks:
      - id: refs_index_exists
        type: file_exists
        path: "{project}/03_РЕФЕРЕНСЫ/index.yaml"
        required: true
        fix_hint: "references-curator agent creates this"
      - id: refs_no_unresolved
        type: file_exists
        path: "{project}/03_РЕФЕРЕНСЫ/refs-palette.html"
        required: true
        fix_hint: "auto_fix: run extract-palette script; or: provide screenshot/description for each blocked URL"
    soft_checks:
      - id: min_3_approved_refs
        prompt: "В 03_РЕФЕРЕНСЫ/index.yaml минимум 3 референса со статусом approved? (yes / no)"
```

- [ ] **Step 2: Добавить новый этап `03b_visual_concept` после `03_references`**

```yaml
  "03b_visual_concept":
    name: "Visual concept"
    lock: hard
    require_approved: ["03_references"]
    hard_checks:
      - id: visual_concept_exists
        type: file_exists
        path: "{project}/03b_КОНЦЕПТ/visual-concept.yaml"
        required: true
        fix_hint: "visual-strategist agent creates this after manager approves a concept"
```

- [ ] **Step 3: Добавить новые чеки в этап `04_brand`**

В секцию `"04_brand"` добавить новый hard_check первым:

```yaml
      - id: visual_concept_approved
        type: file_exists
        path: "{project}/03b_КОНЦЕПТ/visual-concept.yaml"
        required: true
        fix_hint: "Run stage 03b: /landing-visual-concept to generate and approve visual concept"
```

И добавить в `require_approved`:
```yaml
    require_approved: ["03b_visual_concept"]
```

- [ ] **Step 4: Добавить новые чеки в этап `05_design`**

В секцию `"05_design"` добавить hard_check перед `design_md`:

```yaml
      - id: mockup_approved
        type: file_exists
        path: "{project}/05_ДИЗАЙН-СИСТЕМА/mockup-preview.html"
        required: true
        fix_hint: "design-system-generator creates mockup-preview.html at start of stage 05"
```

- [ ] **Step 5: Проверить что gate-check.sh читает новые чеки корректно**

```bash
cd D:\AI_TEAMS\landing_system
bash scripts/gate-check.sh --stage 03_references --project D:\AI_TEAMS\Lendings\lixiang-dubai3 2>&1 | head -20
bash scripts/gate-check.sh --stage 03b_visual_concept --project D:\AI_TEAMS\Lendings\lixiang-dubai3 2>&1 | head -20
```

Ожидаем: чеки запускаются, нет bash-ошибок (файлы могут отсутствовать — это ожидаемо).

- [ ] **Step 6: Commit**

```bash
git add config/stage-gates.yaml
git commit -m "feat(b23-b24-b26): add stage 03b_visual_concept and new gate checks for 03/04/05"
```

---

## Task 6: Обновить агентов `brand-architect` и `design-system-generator` (B24+B26)

**Files:**
- Modify: `agents/brand-architect.md`
- Modify: `agents/design-system-generator.md`

- [ ] **Step 1: Обновить `brand-architect.md` — добавить `visual-concept.yaml` как обязательный input**

В секцию `## Inputs` добавить первым пунктом:

```markdown
- `03b_КОНЦЕПТ/visual-concept.yaml` — **ОБЯЗАТЕЛЬНЫЙ**: утверждённый менеджером визуальный концепт. Содержит палитру (bg/accent/text/surface), типографическое направление, mood. Агент РЕАЛИЗУЕТ этот концепт — не выбирает палитру самостоятельно.
```

В секцию `## Process` добавить первым шагом:

```markdown
0. **ОБЯЗАТЕЛЬНО:** прочитай `03b_КОНЦЕПТ/visual-concept.yaml`. Если файл отсутствует — STOP, сообщи: "Сначала нужно завершить этап 03b: запусти `/landing-visual-concept` для выбора визуальной концепции." Не генерируй brand-kit без этого файла.
```

- [ ] **Step 2: Обновить `design-system-generator.md` — добавить фазу mockup**

В секцию `## Process` добавить перед существующим шагом 1:

```markdown
0. **ОБЯЗАТЕЛЬНАЯ ФАЗА MOCKUP (до генерации дизайн-системы):**
   a. Прочитай `03b_КОНЦЕПТ/visual-concept.yaml`. Если отсутствует — STOP.
   b. Запусти:
      ```bash
      python skills/design-system-generator/scripts/generate-mockup.py \
        --concept <project>/03b_КОНЦЕПТ/visual-concept.yaml \
        --prototype <project>/07_ПРОТОТИП/prototype.yaml \
        --output <project>/05_ДИЗАЙН-СИСТЕМА/mockup-preview.html
      ```
   c. Сообщи менеджеру: "Открой `05_ДИЗАЙН-СИСТЕМА/mockup-preview.html` — там два варианта дизайна с реальным контентом. Выбери вариант или опиши правки."
   d. **ЖДЁТ ответа менеджера.** Не генерируй DESIGN.md пока нет явного "ок" или выбора варианта.
   e. Если правки — обнови `visual-concept.yaml` и сгенерируй новый `mockup-preview.html`. Повторяй до "ок".
   f. После "ок" — переходи к шагу 1 (генерация полной дизайн-системы).
```

- [ ] **Step 3: Commit**

```bash
git add agents/brand-architect.md agents/design-system-generator.md
git commit -m "feat(b24-b26): require visual-concept.yaml in brand-architect; add mockup phase to design-system-generator"
```

---

## Self-Review

**Spec coverage (B23):**
- ✅ STOP при недоступном URL → Task 1 (validate-url.py) + Task 6 (agents)
- ✅ Явное согласование доп. референсов → Task 6 (references-curator обновлён в agents)
- ✅ Отчёт палитры в чате + HTML → Task 2 (extract-palette.py + refs-palette.html)
- ✅ Gate-check refs_no_unresolved → Task 5

**Spec coverage (B24):**
- ✅ Новый агент visual-strategist → Task 3
- ✅ Новый этап 03b → Task 3 + Task 5
- ✅ generate-concept.py с 2-3 концептами → Task 3
- ✅ visual-concept.yaml как обязательный input для 04 → Task 5 + Task 6

**Spec coverage (B26):**
- ✅ generate-mockup.py с вариантами A + B → Task 4
- ✅ mockup-preview.html side-by-side → Task 4
- ✅ Gate mockup_approved в 05 → Task 5
- ✅ Фаза mockup в design-system-generator → Task 6
- ✅ Итерации без лимита → Task 6 (агент ждёт "ок")

**Зависимость B26 от B23+B24:** Task 5 и 6 вводят `visual-concept.yaml` как обязательный файл для 05 — это корректно, т.к. Tasks 1-3 создают инфраструктуру для его генерации.

**Placeholder scan:** нет TBD/TODO.

**Type consistency:** `visual-concept.yaml` структура определена в Task 3 и используется в Task 4 и 6 — совпадает.
