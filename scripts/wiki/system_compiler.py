"""Компилит landing-system в landing-system/wiki/.

Алгоритм:
1. Обходим SYSTEM_SOURCES (glob-паттерны).
2. Для каждого файла — проверяем sha256 против .cache.json.
3. Изменённые → SDK → wiki/concepts/<concept_dir>/<slug>.md.
4. После всех — генерируем wiki/index.md через SDK.
5. Аппендим запись в wiki/log.md.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from scripts.wiki import hash_cache, sdk_client, utils

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


GENERIC_STEMS = {"SKILL", "README", "readme", "meta", "META", "index"}


def _slug_for_source(path: Path) -> str:
    """Slug файла без расширения.

    Если stem общий (SKILL/README/meta/index) — используем имя родительской папки.
    Это нужно для `skills/foo/SKILL.md` → slug `foo`, не `skill`.
    """
    if path.stem in GENERIC_STEMS:
        return utils.slugify(path.parent.name)
    return utils.slugify(path.stem)


def _compile_concept(
    source_path: Path, repo_root: Path
) -> str:
    """Зовёт SDK для одного исходника, возвращает markdown концепта."""
    system_prompt = _load_prompt("system_concept.md")
    rel = source_path.relative_to(repo_root).as_posix()
    user_msg = f"Источник: `{rel}`\n\n---\n\n{source_path.read_text(encoding='utf-8')}"
    return sdk_client.generate(system=system_prompt, user=user_msg)


GROUP_TITLES_INDEX = [
    ("stage", "## 📋 Этапы pipeline"),
    ("agent", "## 🤖 Агенты"),
    ("skill", "## 🛠 Скиллы"),
    ("command", "## ⚡ Команды"),
    ("rule", "## 📐 Правила (стандарты качества)"),
    ("block", "## 🧱 Блоки"),
    # PR-S
    ("pattern", "## ✨ Премиум-паттерны"),
    ("style", "## 🎨 Style moods"),
    ("config", "## ⚙️ Конфигурация"),
    ("doc", "## 📖 Документация"),
    # PR-T: полное покрытие системы
    ("script", "## 🛠 Скрипты"),
    ("test-group", "## 🧪 Тесты"),
    ("spec", "## 📜 Спецификации (specs)"),
    ("plan", "## 📋 Планы реализации"),
    ("preset", "## 🎁 Пресеты"),
    ("unknown", "## ❓ Прочее"),
]


def _build_index(concepts: list[dict[str, Any]]) -> str:
    """Детерминированно строит index.md БЕЗ SDK.

    SDK для index выдавал мусор (мета-комментарии вместо markdown).
    Stub надёжнее, бесплатно и предсказуемо.
    """
    groups: dict[str, list[dict[str, Any]]] = {}
    for c in concepts:
        type_ = c.get("type", "unknown")
        groups.setdefault(type_, []).append(c)

    lines = [
        "# Landing-System Wiki — главный индекс",
        "",
        "> Авто-сгенерированный индекс. Обновляется при `python -m scripts.wiki.compile --source-mode=system`.",
        "",
        f"**Концептов всего:** {sum(len(v) for v in groups.values())}",
        f"**Категории:** {', '.join(sorted(groups.keys()))}",
        "",
        "**Известные ограничения:**",
        "- Блоки из `block-library/` ещё не в wiki — отдельная задача.",
        "- Часть `[[wikilinks]]` ссылается на скрипты/конфиги вне wiki — это норма.",
        "",
    ]

    for type_, title in GROUP_TITLES_INDEX:
        if type_ not in groups:
            continue
        lines.append(title)
        lines.append("")
        for c in sorted(groups[type_], key=lambda x: x.get("file_stem", "")):
            stem = c.get("file_stem", "?")
            name = c.get("name") or stem
            lines.append(f"- [[{stem}]] — {name}")
        lines.append("")

    return "\n".join(lines)


def _append_log(log_path: Path, entries: list[str]) -> None:
    """Аппендит запись в wiki/log.md."""
    today = date.today().isoformat()
    header = f"\n## [{today}] compile --source-mode=system\n"
    body = "\n".join(f"- {e}" for e in entries) if entries else "- no changes\n"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(header)
        f.write(body)
        f.write("\n")


def compile_system(
    repo_root: Path,
    wiki_dir: Path,
    sources: list[dict[str, str]],
    dry_run: bool = False,
) -> dict[str, Any]:
    """Главная функция системного компайлера.

    Returns:
        {"compiled": [...], "skipped": [...], "errors": [...]}.
    """
    cache_path = wiki_dir / ".cache.json"
    cache = hash_cache.load_cache(cache_path)

    # Pre-populate cache from existing concepts: если концепт уже есть на диске
    # а source в кэше нет — добавляем текущий sha source в кэш. Это позволяет
    # возобновить bootstrap после падения без перекомпиляции.
    if not dry_run:
        for source_def in sources:
            for source_path in sorted(repo_root.glob(source_def["path"])):
                rel_key = source_path.relative_to(repo_root).as_posix()
                slug = _slug_for_source(source_path)
                concept_path = wiki_dir / "concepts" / source_def["concept_dir"] / f"{slug}.md"
                if concept_path.exists() and rel_key not in cache:
                    cache[rel_key] = hash_cache.compute_hash(source_path)
        hash_cache.save_cache(cache_path, cache)

    concepts_summary: list[dict[str, Any]] = []
    compiled: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []

    # Count total upfront so progress lines can show [N/total].
    all_sources = [
        (sd, sp)
        for sd in sources
        for sp in sorted(repo_root.glob(sd["path"]))
    ]
    total_sources = len(all_sources)
    idx = 0

    for source_def in sources:
        pattern = source_def["path"]
        concept_dir = source_def["concept_dir"]
        for source_path in sorted(repo_root.glob(pattern)):
            idx += 1
            rel_key = source_path.relative_to(repo_root).as_posix()
            slug = _slug_for_source(source_path)
            concept_path = wiki_dir / "concepts" / concept_dir / f"{slug}.md"

            if not hash_cache.is_changed(source_path, rel_key, cache):
                skipped.append(rel_key)
                # всё равно собираем для index
                if concept_path.exists():
                    meta, _ = utils.parse_frontmatter(
                        concept_path.read_text(encoding="utf-8")
                    )
                    concepts_summary.append(
                        {
                            "file_stem": slug,
                            "type": meta.get("type", "unknown"),
                            "name": meta.get("name", slug),
                            "source": rel_key,
                        }
                    )
                continue

            print(
                f"[{idx}/{total_sources}] compiling {rel_key} ...",
                flush=True,
            )
            try:
                content = _compile_concept(source_path, repo_root)
            except sdk_client.SDKError as e:
                print(f"  ! SDK error: {e}", flush=True)
                errors.append(f"{rel_key}: {e}")
                # Кэшируем hash даже при ошибке — иначе post-commit будет
                # звать SDK на этот файл КАЖДЫЙ раз. Пользователь увидит
                # ошибку в errors[], кэш починится при следующем коммите
                # с обновлённым source-файлом.
                cache[rel_key] = hash_cache.compute_hash(source_path)
                continue

            meta, _ = utils.parse_frontmatter(content)
            concepts_summary.append(
                {
                    "file_stem": slug,
                    "type": meta.get("type", "unknown"),
                    "name": meta.get("name", slug),
                    "source": rel_key,
                }
            )
            if not dry_run:
                utils.atomic_write(concept_path, content)
                cache[rel_key] = hash_cache.compute_hash(source_path)
            compiled.append(rel_key)

    # Финальный save кэша — один раз за прогон, не в цикле (O(N²) → O(N)).
    # Сохраняем и при ошибках: hash «сломанных» источников остаётся в кэше,
    # чтобы post-commit не звал SDK на них каждый раз.
    if not dry_run and (compiled or errors):
        hash_cache.save_cache(cache_path, cache)

    # Индекс
    if concepts_summary:
        try:
            index_content = _build_index(concepts_summary)
            if not dry_run:
                utils.atomic_write(wiki_dir / "index.md", index_content)
        except sdk_client.SDKError as e:
            errors.append(f"index: {e}")

    # Лог
    if not dry_run:
        _append_log(
            wiki_dir / "log.md",
            entries=[f"compiled {p}" for p in compiled]
            + [f"skipped {p}" for p in skipped]
            + [f"error {e}" for e in errors],
        )

    return {"compiled": compiled, "skipped": skipped, "errors": errors}
