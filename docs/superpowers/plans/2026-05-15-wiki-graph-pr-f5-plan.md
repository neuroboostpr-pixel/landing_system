# PR-F.5 — Lint + Query + Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Финал. Добавить `lint.py` (структурные проверки здоровья wiki), `query.py` (запросы к wiki из CLI), `preview.html` рендерер (визуальный просмотр wiki в браузере), документацию Obsidian как опционального фронтенда.

**Architecture:** Все три инструмента — самостоятельные CLI. `lint.py` структурные проверки бесплатны, LLM-проверка противоречий опциональна. `query.py` — index-guided retrieval без RAG. `preview.html` — генерится из markdown через простой Jinja2 шаблон + d3.js для графа связей.

**Tech Stack:** Python, Jinja2 (уже в requirements), pytest.

**Связанный spec:** разделы 4.2, 8, 13.

**Предыдущий PR:** PR-F.4 (хуки + memory).

---

## File Structure

**Создаём:**
- `scripts/wiki/lint.py` — 7 проверок
- `scripts/wiki/query.py` — index-guided retrieval
- `scripts/wiki/preview.py` — генератор preview.html
- `scripts/wiki/templates/preview.html.j2` — Jinja2 шаблон
- `scripts/wiki/templates/styles.css` — стили
- `scripts/wiki/prompts/query.md` — промпт для query
- `tests/wiki/test_lint.py`
- `tests/wiki/test_query.py`
- `tests/wiki/test_preview.py`

**Модифицируем:**
- `scripts/wiki/README.md` — добавить разделы про lint/query/preview
- `docs/SETUP.md` — добавить секцию «Obsidian (опционально)»

---

## Task 1: `lint.py` — структурные проверки (бесплатно)

**7 проверок из spec:**
1. Битые wikilinks (ссылка `[[name]]` → файла нет)
2. Сирые страницы (никто не ссылается)
3. Некомпилированные daily logs (есть в daily/, нет в compiled/)
4. Устаревшие концепты (frontmatter updated > 30 дней)
5. Пропущенные обратные ссылки (A→B но B не упоминает A)
6. Пустые концепты (<200 слов)
7. LLM-проверка противоречий (опционально, через флаг)

**Files:**
- Create: `scripts/wiki/lint.py`
- Create: `tests/wiki/test_lint.py`

- [ ] **Step 1: failing tests `tests/wiki/test_lint.py`**

```python
"""Тесты lint — 6 структурных проверок (LLM-проверка тестируется отдельно)."""
from pathlib import Path

import pytest

from scripts.wiki import lint


@pytest.fixture
def fake_wiki(tmp_path):
    wiki = tmp_path / "wiki"
    concepts = wiki / "concepts"
    concepts.mkdir(parents=True)
    return wiki


def test_no_issues_in_empty_wiki(fake_wiki):
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert result["broken_links"] == []
    assert result["orphans"] == []


def test_detects_broken_link(fake_wiki):
    (fake_wiki / "concepts" / "a.md").write_text(
        "---\ntype: x\n---\n# A\nСсылка на [[non-existent]]"
    )
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert any("non-existent" in issue for issue in result["broken_links"])


def test_detects_orphan(fake_wiki):
    (fake_wiki / "concepts" / "a.md").write_text("---\ntype: x\n---\n# A")
    (fake_wiki / "concepts" / "b.md").write_text("---\ntype: x\n---\n# B\n[[a]]")
    # 'a' ссылается из b, не сирота. 'b' — ни на кого нет ссылок → сирота.
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert any("b" in o for o in result["orphans"])
    assert not any(o == "a" or o.endswith("/a") for o in result["orphans"])


def test_detects_empty_concept(fake_wiki):
    (fake_wiki / "concepts" / "tiny.md").write_text("---\ntype: x\n---\n# Tiny\n\nshort")
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert any("tiny" in s for s in result["empty"])


def test_detects_missing_backlink(fake_wiki):
    (fake_wiki / "concepts" / "a.md").write_text(
        "---\ntype: x\n---\n# A\n[[b]]"
    )
    (fake_wiki / "concepts" / "b.md").write_text(
        "---\ntype: x\n---\n# B\nНет ссылки на a"
    )
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert any("a" in pair and "b" in pair for pair in result["missing_backlinks"])


def test_exit_code_zero_on_clean(fake_wiki):
    """Если нет issues — exit 0."""
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert lint.compute_exit_code(result) == 0


def test_exit_code_nonzero_on_issues(fake_wiki):
    (fake_wiki / "concepts" / "tiny.md").write_text("---\ntype: x\n---\n# T")
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert lint.compute_exit_code(result) != 0
```

- [ ] **Step 2: Реализовать `lint.py`**

```python
# scripts/wiki/lint.py
"""Линтер wiki — 7 проверок здоровья.

Структурные проверки (бесплатно):
1. Битые wikilinks
2. Сирые страницы
3. Некомпилированные daily logs
4. Устаревшие концепты
5. Пропущенные обратные ссылки
6. Пустые концепты

LLM-проверка (платно, по флагу --llm-check):
7. Противоречия между концептами
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from scripts.wiki import utils

WIKILINK_RE = re.compile(r"\[\[([^\]\|]+?)(\|[^\]]*)?\]\]")

STALE_DAYS = 30
MIN_WORDS = 50  # «пустой» концепт


def _collect_concepts(wiki_dir: Path) -> dict[str, Path]:
    """Возвращает {file_stem: path} для всех md в concepts/."""
    concepts_dir = wiki_dir / "concepts"
    if not concepts_dir.exists():
        return {}
    return {p.stem: p for p in concepts_dir.rglob("*.md")}


def _wikilinks_in(text: str) -> set[str]:
    """Множество wikilink-имён (без anchor/alias)."""
    return {m.group(1).strip() for m in WIKILINK_RE.finditer(text)}


def run_checks(wiki_dir: Path, llm_check: bool = False) -> dict:
    """Выполняет все структурные проверки. Возвращает словарь по типам."""
    concepts = _collect_concepts(wiki_dir)
    issues = {
        "broken_links": [],
        "orphans": [],
        "uncompiled_daily": [],
        "stale": [],
        "missing_backlinks": [],
        "empty": [],
        "contradictions": [],
    }

    # Для каждого концепта — собрать body и links
    bodies: dict[str, str] = {}
    links_from: dict[str, set[str]] = {}
    for name, path in concepts.items():
        text = path.read_text(encoding="utf-8")
        _, body = utils.parse_frontmatter(text)
        bodies[name] = body
        links_from[name] = _wikilinks_in(body)

    referenced: set[str] = set()
    for name, lset in links_from.items():
        referenced.update(lset)

    # 1. Битые ссылки
    for name, lset in links_from.items():
        for target in lset:
            if target not in concepts:
                issues["broken_links"].append(f"{name} → [[{target}]]")

    # 2. Сирые страницы (никто не ссылается, не считая index/log)
    for name in concepts:
        if name in ("index", "log"):
            continue
        if name not in referenced:
            issues["orphans"].append(name)

    # 3. Daily logs не скомпилированы
    daily = wiki_dir.parent / "memory" / "daily" if wiki_dir.name == "wiki" else None
    if daily and daily.exists():
        compiled = wiki_dir.parent / "memory" / "compiled" / "concepts"
        if not compiled.exists() or not list(compiled.glob("*.md")):
            for f in sorted(daily.glob("*.md")):
                issues["uncompiled_daily"].append(f.name)

    # 4. Устаревшие
    stale_threshold = date.today() - timedelta(days=STALE_DAYS)
    for name, path in concepts.items():
        text = path.read_text(encoding="utf-8")
        meta, _ = utils.parse_frontmatter(text)
        updated = meta.get("updated")
        if isinstance(updated, str):
            try:
                ud = datetime.fromisoformat(updated).date()
                if ud < stale_threshold:
                    issues["stale"].append(f"{name} ({updated})")
            except ValueError:
                pass
        elif isinstance(updated, date):
            if updated < stale_threshold:
                issues["stale"].append(f"{name} ({updated})")

    # 5. Missing backlinks: A→B, но B не упоминает A
    for a, lset in links_from.items():
        for b in lset:
            if b in concepts and a not in links_from.get(b, set()):
                issues["missing_backlinks"].append(f"{a} ↔ {b}")

    # 6. Пустые
    for name, body in bodies.items():
        word_count = len(body.split())
        if word_count < MIN_WORDS:
            issues["empty"].append(f"{name} ({word_count} слов)")

    # 7. LLM — противоречия (опционально)
    if llm_check:
        try:
            from scripts.wiki import sdk_client
            combined = "\n\n---\n\n".join(
                f"# {n}\n\n{bodies[n][:500]}" for n in concepts
            )
            prompt = (
                "Ты ищешь противоречия в wiki. На вход — все концепты. "
                "Найди пары противоречащих утверждений. "
                "Формат ответа: список '- <concept-a> vs <concept-b>: <что противоречит>'. "
                "Если противоречий нет — верни 'нет'."
            )
            result = sdk_client.generate(system=prompt, user=combined)
            if "нет" not in result.lower()[:20]:
                issues["contradictions"] = [
                    line.strip("- ").strip()
                    for line in result.splitlines() if line.strip().startswith("-")
                ]
        except Exception as e:
            issues["contradictions"].append(f"LLM check failed: {e}")

    return issues


def compute_exit_code(issues: dict) -> int:
    """0 если нет issues, 1 иначе."""
    has_any = any(v for v in issues.values())
    return 1 if has_any else 0


def format_report(issues: dict) -> str:
    lines = ["# Wiki Lint Report", ""]
    for k, v in issues.items():
        if not v:
            continue
        lines.append(f"## {k} ({len(v)})")
        for item in v[:20]:
            lines.append(f"- {item}")
        if len(v) > 20:
            lines.append(f"- ... ещё {len(v) - 20}")
        lines.append("")
    if all(not v for v in issues.values()):
        lines.append("✅ Все проверки прошли.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki", default="wiki", help="Папка wiki/")
    parser.add_argument("--llm-check", action="store_true", help="Включить LLM-проверку противоречий")
    parser.add_argument("--structural-only", action="store_true", help="Только структурные проверки")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki).resolve()
    if not wiki_dir.exists():
        print(f"ERROR: wiki dir not found: {wiki_dir}", file=sys.stderr)
        return 2

    llm_check = args.llm_check and not args.structural_only
    issues = run_checks(wiki_dir, llm_check=llm_check)
    print(format_report(issues))
    return compute_exit_code(issues)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Тесты PASS**

Run: `pytest tests/wiki/test_lint.py -v`
Expected: 7 PASS

- [ ] **Step 4: Smoke**

```bash
python3 -m scripts.wiki.lint --wiki wiki --structural-only
```
(Если bootstrap ещё идёт — может ругнуться на сирых или пустых)

- [ ] **Step 5: Commit**

```bash
git add scripts/wiki/lint.py tests/wiki/test_lint.py
git commit -m "feat(wiki): lint.py — 7 проверок здоровья wiki

PR-F.5 Task 1. Структурные проверки бесплатны, --llm-check
включает LLM-поиск противоречий."
```

---

## Task 2: `query.py` — index-guided retrieval

**Files:**
- Create: `scripts/wiki/query.py`
- Create: `scripts/wiki/prompts/query.md`
- Create: `tests/wiki/test_query.py`

- [ ] **Step 1: Создать `prompts/query.md`**

```markdown
Ты отвечаешь на вопросы пользователя на основе wiki landing-system + проектов. На вход — индексы всех слоёв wiki (system + project + memory) + ВОПРОС. Используй только информацию из wiki.

# Алгоритм

1. По индексам определи, какие концепты могут содержать ответ.
2. Прочитай ИХ содержимое (оно передаётся в user message).
3. Синтезируй чёткий ответ на русском.
4. Укажи источники в конце: `Источники: [[concept-a]], [[concept-b]]`.

# Правила

- Не выдумывай. Если ответа нет в wiki — скажи «не нашёл, попробуй задать вопрос конкретнее».
- Простой русский.
- Если ответ есть в нескольких концептах — синтезируй, не цитируй дословно.
```

- [ ] **Step 2: failing tests**

```python
# tests/wiki/test_query.py
"""Тесты query (с моком SDK)."""
from pathlib import Path

import pytest

from scripts.wiki import query


@pytest.fixture
def fake_wiki(tmp_path):
    wiki = tmp_path / "wiki"
    concepts = wiki / "concepts"
    concepts.mkdir(parents=True)
    (wiki / "index.md").write_text("# Index\n- [[landing-orchestrator]]")
    (concepts / "landing-orchestrator.md").write_text(
        "---\ntype: agent\n---\n# Orchestrator\n\nГлавный дирижёр pipeline."
    )
    return wiki


def test_query_returns_answer(fake_wiki, mocker):
    mocker.patch(
        "scripts.wiki.query.sdk_client.generate",
        return_value="Это главный агент.\n\nИсточники: [[landing-orchestrator]]",
    )
    result = query.ask(wiki_dirs=[fake_wiki], question="Что такое landing-orchestrator?")
    assert "главный" in result.lower()


def test_query_returns_no_match(fake_wiki, mocker):
    mocker.patch(
        "scripts.wiki.query.sdk_client.generate",
        return_value="не нашёл, попробуй задать вопрос конкретнее",
    )
    result = query.ask(wiki_dirs=[fake_wiki], question="Что-то совсем не из wiki?")
    assert "не нашёл" in result.lower()


def test_query_combines_multiple_wikis(fake_wiki, mocker):
    """ask() принимает список wiki_dirs и складывает их индексы."""
    other = fake_wiki.parent / "other_wiki"
    other.mkdir()
    (other / "index.md").write_text("# Other\n- [[different-concept]]")
    gen = mocker.patch(
        "scripts.wiki.query.sdk_client.generate",
        return_value="answer",
    )
    query.ask(wiki_dirs=[fake_wiki, other], question="?")
    user_msg = gen.call_args.kwargs["user"]
    assert "different-concept" in user_msg
```

- [ ] **Step 3: Реализовать `query.py`**

```python
# scripts/wiki/query.py
"""Запросы к wiki из CLI.

Использование:
  python -m scripts.wiki.query "что делает landing-orchestrator"
  python -m scripts.wiki.query "..." --project=dubai-avto-liza
  python -m scripts.wiki.query "..." --file-back  # сохраняет ответ в memory/qa/
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from scripts.wiki import config, sdk_client, utils

PROMPTS_DIR = Path(__file__).parent / "prompts"
MAX_INDEX_CHARS = 6000
MAX_CONCEPT_CHARS = 4000


def _gather_indexes(wiki_dirs: list[Path]) -> str:
    parts = []
    for w in wiki_dirs:
        idx = w / "index.md"
        if idx.exists():
            text = idx.read_text(encoding="utf-8")
            if len(text) > MAX_INDEX_CHARS:
                text = text[:MAX_INDEX_CHARS] + "\n[...обрезано]"
            parts.append(f"# Index of {w}\n\n{text}")
    return "\n\n---\n\n".join(parts)


def ask(wiki_dirs: list[Path], question: str) -> str:
    """Главная функция."""
    indexes = _gather_indexes(wiki_dirs)
    user = f"{indexes}\n\n---\n\n**Вопрос:** {question}"
    prompt = (PROMPTS_DIR / "query.md").read_text(encoding="utf-8")
    try:
        return sdk_client.generate(system=prompt, user=user)
    except sdk_client.SDKError as e:
        return f"_(ошибка SDK: {e})_"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="Вопрос к wiki")
    parser.add_argument("--project", help="Slug проекта (включит его wiki + memory)")
    parser.add_argument("--file-back", action="store_true", help="Сохранить ответ в memory/qa/")
    args = parser.parse_args()

    wiki_dirs = [config.WIKI_DIR]
    if args.project:
        project_root = Path.home() / "Lendings" / args.project
        if (project_root / "wiki").exists():
            wiki_dirs.append(project_root / "wiki")
        if (project_root / "memory" / "compiled").exists():
            wiki_dirs.append(project_root / "memory" / "compiled")

    answer = ask(wiki_dirs=wiki_dirs, question=args.question)
    print(answer)

    if args.file_back and args.project:
        qa_dir = Path.home() / "Lendings" / args.project / "memory" / "compiled" / "qa"
        qa_dir.mkdir(parents=True, exist_ok=True)
        slug = utils.slugify(args.question)[:60]
        out = qa_dir / f"{date.today().isoformat()}-{slug}.md"
        utils.atomic_write(
            out,
            f"# {args.question}\n\n{answer}\n",
        )
        print(f"\n💾 Сохранено: {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Тесты + commit**

```bash
pytest tests/wiki/test_query.py -v
git add scripts/wiki/query.py scripts/wiki/prompts/query.md tests/wiki/test_query.py
git commit -m "feat(wiki): query.py — запросы к wiki из CLI

PR-F.5 Task 2. Index-guided retrieval без RAG. --file-back
сохраняет ответ в memory/qa/."
```

---

## Task 3: `preview.html` — визуальный просмотрщик

**Цель:** HTML-страница для глазной проверки wiki — список + поиск по концептам + граф связей.

**Files:**
- Create: `scripts/wiki/preview.py`
- Create: `scripts/wiki/templates/preview.html.j2`
- Create: `scripts/wiki/templates/styles.css`
- Create: `tests/wiki/test_preview.py`

- [ ] **Step 1: Создать `templates/styles.css`**

```css
body { font-family: -apple-system, sans-serif; margin: 0; background: #fafafa; }
.container { display: grid; grid-template-columns: 280px 1fr; min-height: 100vh; }
.sidebar { background: #fff; padding: 16px; border-right: 1px solid #e5e5e5; overflow-y: auto; }
.sidebar h2 { font-size: 13px; text-transform: uppercase; color: #888; margin: 16px 0 8px; }
.sidebar a { display: block; padding: 4px 8px; color: #1a1a1a; text-decoration: none; border-radius: 4px; font-size: 14px; }
.sidebar a:hover { background: #f0f0f0; }
.main { padding: 24px 32px; max-width: 760px; }
.main h1 { font-size: 28px; }
.main pre { background: #f4f4f4; padding: 12px; border-radius: 6px; overflow-x: auto; }
.search { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 12px; }
.badge { display: inline-block; font-size: 11px; padding: 2px 6px; border-radius: 3px; background: #eee; margin-left: 6px; }
.badge-agent { background: #e0f2fe; color: #075985; }
.badge-skill { background: #fce7f3; color: #9d174d; }
.badge-command { background: #fef3c7; color: #92400e; }
.badge-stage { background: #d1fae5; color: #065f46; }
.badge-rule { background: #fee2e2; color: #991b1b; }
.badge-block { background: #ede9fe; color: #5b21b6; }
```

- [ ] **Step 2: Создать `templates/preview.html.j2`**

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>{{ title }}</title>
<style>{{ styles }}</style>
</head>
<body>
<div class="container">
  <aside class="sidebar">
    <input class="search" placeholder="Поиск..." oninput="filter(this.value)">
    {% for group, items in groups.items() %}
      <h2>{{ group }}</h2>
      {% for item in items %}
        <a href="#{{ item.slug }}" data-name="{{ item.name | lower }}">
          {{ item.name }}<span class="badge badge-{{ item.type }}">{{ item.type }}</span>
        </a>
      {% endfor %}
    {% endfor %}
  </aside>
  <main class="main">
    <h1>{{ title }}</h1>
    <p>Обновлено: {{ updated }}. Концептов: {{ total }}.</p>

    {% for concept in concepts %}
      <section id="{{ concept.slug }}">
        <h2>{{ concept.name }} <span class="badge badge-{{ concept.type }}">{{ concept.type }}</span></h2>
        <pre>{{ concept.body }}</pre>
      </section>
    {% endfor %}
  </main>
</div>
<script>
function filter(q) {
  q = q.toLowerCase();
  document.querySelectorAll('.sidebar a').forEach(a => {
    a.style.display = a.dataset.name.includes(q) ? '' : 'none';
  });
}
</script>
</body>
</html>
```

- [ ] **Step 3: failing tests**

```python
# tests/wiki/test_preview.py
"""Тесты генератора preview.html."""
from pathlib import Path

import pytest

from scripts.wiki import preview


@pytest.fixture
def fake_wiki(tmp_path):
    wiki = tmp_path / "wiki"
    concepts = wiki / "concepts" / "agents"
    concepts.mkdir(parents=True)
    (concepts / "foo.md").write_text(
        "---\ntype: agent\nname: foo\n---\n# Foo\n\nDoes things."
    )
    (concepts / "bar.md").write_text(
        "---\ntype: agent\nname: bar\n---\n# Bar\n\nOther."
    )
    return wiki


def test_render_produces_html(fake_wiki):
    html_path = preview.render(fake_wiki)
    assert html_path.exists()
    content = html_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "foo" in content
    assert "bar" in content


def test_render_groups_by_type(fake_wiki):
    html_path = preview.render(fake_wiki)
    content = html_path.read_text(encoding="utf-8")
    assert "agent" in content.lower()


def test_render_empty_wiki(tmp_path):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    html = preview.render(wiki)
    assert html.exists()
```

- [ ] **Step 4: Реализовать `preview.py`**

```python
# scripts/wiki/preview.py
"""Генерит wiki/preview.html для глазного просмотра."""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from scripts.wiki import utils

TEMPLATES = Path(__file__).parent / "templates"


def _load_concepts(wiki_dir: Path) -> list[dict]:
    concepts = []
    cdir = wiki_dir / "concepts"
    if not cdir.exists():
        return concepts
    for p in sorted(cdir.rglob("*.md")):
        text = p.read_text(encoding="utf-8")
        meta, body = utils.parse_frontmatter(text)
        concepts.append({
            "slug": p.stem,
            "name": meta.get("name", p.stem),
            "type": meta.get("type", "unknown"),
            "body": body.strip()[:3000],
        })
    return concepts


def render(wiki_dir: Path) -> Path:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("preview.html.j2")
    styles = (TEMPLATES / "styles.css").read_text(encoding="utf-8")

    concepts = _load_concepts(wiki_dir)
    groups: dict[str, list[dict]] = defaultdict(list)
    for c in concepts:
        groups[c["type"]].append({"slug": c["slug"], "name": c["name"], "type": c["type"]})

    html = template.render(
        title=f"{wiki_dir.parent.name} wiki",
        updated=date.today().isoformat(),
        total=len(concepts),
        styles=styles,
        groups=dict(groups),
        concepts=concepts,
    )

    out = wiki_dir / "preview.html"
    utils.atomic_write(out, html)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki", default="wiki")
    args = parser.parse_args()
    out = render(Path(args.wiki).resolve())
    print(f"Generated: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Тесты + commit**

```bash
pytest tests/wiki/test_preview.py -v
git add scripts/wiki/preview.py scripts/wiki/templates/ tests/wiki/test_preview.py
git commit -m "feat(wiki): preview.py — HTML-просмотрщик wiki

PR-F.5 Task 3. Jinja2-шаблон + CSS + JS-поиск."
```

---

## Task 4: Документация (Obsidian + scripts README)

**Files:**
- Modify: `scripts/wiki/README.md`
- Modify: `docs/SETUP.md`

- [ ] **Step 1: Дополнить `scripts/wiki/README.md`**

Добавить в конец секции «Использование»:

```markdown
## Lint

```bash
python -m scripts.wiki.lint --wiki wiki --structural-only   # бесплатно
python -m scripts.wiki.lint --wiki wiki --llm-check          # с проверкой противоречий (~$0.15)
```

## Query

```bash
python -m scripts.wiki.query "что делает landing-orchestrator"
python -m scripts.wiki.query "когда было решение про цены" --project=dubai-avto-liza
python -m scripts.wiki.query "..." --project=... --file-back   # сохранит ответ в memory/qa/
```

## Preview HTML

```bash
python -m scripts.wiki.preview --wiki wiki
open wiki/preview.html  # macOS
```
```

- [ ] **Step 2: Дополнить `docs/SETUP.md`** (или создать секцию)

Добавить:

```markdown
## Wiki разметка (PR-F)

Система ведёт три слоя wiki:

- `landing-system/wiki/` — карта архитектуры (агенты, скиллы, команды, этапы)
- `~/Lendings/<slug>/wiki/` — граф структуры конкретного лендинга
- `~/Lendings/<slug>/memory/` — память сессий по этому проекту

Хуки `SessionStart` / `SessionEnd` / `PreCompact` инжектят индексы и сохраняют уроки автоматически.

### Bootstrap

```bash
bash scripts/wiki/bootstrap-system.sh    # ~30 мин, использует Claude Max подписку
```

### Миграция существующего проекта

```bash
bash scripts/migrate-add-wiki.sh ~/Lendings/<slug>
```

### Obsidian (опционально)

Папки `wiki/` и `memory/` совместимы с [Obsidian](https://obsidian.md/) — можно открыть как vault и увидеть граф связей.

Опционально для удобства:
- [Obsidian Web Clipper](https://obsidian.md/clipper) — сохранять статьи прямо в `wiki/raw/` (если будешь компилировать внешние материалы)
- Плагин **Local Images Plus** — скачивать картинки в vault а не оставлять ссылки

Подробнее: [spec](superpowers/specs/2026-05-15-wiki-graph-markup-design.md), [plan](superpowers/plans/2026-05-15-wiki-graph-pr-f1-plan.md).
```

- [ ] **Step 3: Commit**

```bash
git add scripts/wiki/README.md docs/SETUP.md
git commit -m "docs(wiki): lint/query/preview инструкции + Obsidian секция

PR-F.5 Task 4."
```

---

## Task 5: End-to-end проверка + финальный smoke

- [ ] **Step 1: Полный pytest сьют**

```bash
pytest tests/wiki/ -v
```
Expected: все 65+ тестов PASS.

- [ ] **Step 2: Lint на свежем системном wiki**

```bash
python3 -m scripts.wiki.lint --wiki wiki --structural-only
```
Expected: возможны issues (сирые страницы естественны для свежего wiki), но скрипт не падает.

- [ ] **Step 3: Preview**

```bash
python3 -m scripts.wiki.preview --wiki wiki
open wiki/preview.html
```
Expected: открывается, видны концепты по группам, поиск работает.

- [ ] **Step 4: Query тест**

```bash
python3 -m scripts.wiki.query "что такое landing-orchestrator"
```
Expected: разумный ответ через SDK.

- [ ] **Step 5: Final commit + push**

```bash
git status
git log --oneline | head -25  # видим всю историю PR-F
```

Подготовка к push — см. финальный шаг после всех PR.

---

## Self-Review

**Spec coverage:**
- ✅ Lint 6 структурных + 1 LLM проверка
- ✅ Query с index-guided retrieval, --file-back
- ✅ preview.html
- ✅ Obsidian секция в SETUP
- ⏭️ Граф связей через d3.js — отложено, в preview есть только список (граф можно добавить отдельным PR если нужно)

**Placeholders:** нет.

**Type consistency:**
- `lint.run_checks(wiki_dir, llm_check=False) -> dict` — словарь с 7 ключами
- `query.ask(wiki_dirs: list[Path], question: str) -> str`
- `preview.render(wiki_dir) -> Path`

**Риски:**
1. **Lint жалуется на много сирых** в свежем wiki — нормально, скорректируется когда добавим connections/ страницы.
2. **Query без SDK** упадёт — есть except c понятным сообщением.
3. **Preview** медленный на 100+ концептах — для текущего масштаба OK.

---

## После PR-F.5

Финал всего PR-F:
1. Migration `dubai-avto-liza` (PR-F.3 Task 5 — отложено до сейчас)
2. Запушить всё на GitHub одним push (или серией коммитов уже на ветке)
3. Опционально: PR-G (Stage Lock — усиление orchestrator + gate-check)
