"""Управление run_id для wiki routing корреляции.

run_id — идентификатор одного рабочего запуска (один /landing-go или ручной старт).
Хранится в .wiki-run-id в корне репо. Новый запуск = reset().
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from scripts.wiki import config

RUN_ID_PATH = config.REPO_ROOT / ".wiki-run-id"


def _generate() -> str:
    return "landing-" + datetime.now().strftime("%Y%m%d-%H%M")


def get() -> str | None:
    """Читает run_id из файла. None если файла нет."""
    try:
        return RUN_ID_PATH.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def get_or_create() -> str:
    """Читает run_id если файл есть, иначе генерирует новый и записывает."""
    existing = get()
    if existing:
        return existing
    return reset()


def reset() -> str:
    """Генерирует новый run_id, перезаписывает файл. Возвращает новый id."""
    new_id = _generate()
    RUN_ID_PATH.write_text(new_id, encoding="utf-8")
    return new_id
