"""
Общий помощник для путей и кодировки.

Назначение:
  - Найти корневую папку с лендингами (LANDINGS_ROOT) кросс-платформенно.
  - Принудительно включить UTF-8 для stdout/stderr на любой ОС.

Использование в Python-скриптах:
    from scripts.lib.paths import LANDINGS_ROOT, REPO_ROOT, project_dir
    state = LANDINGS_ROOT / "my-landing" / ".landing-state.yaml"
    # или:
    state = project_dir("my-landing") / ".landing-state.yaml"

Импорт этого модуля сам по себе включает UTF-8 для вывода — никакой
дополнительной настройки в скриптах делать не нужно.
"""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path


# ──────────────────────────────────────────────────────────────────
# 1. UTF-8 для вывода (важно для Windows + русского текста)
# ──────────────────────────────────────────────────────────────────

def _ensure_utf8_streams() -> None:
    """Перенаправить stdout/stderr на UTF-8 если ОС/консоль выставила другое.

    На Windows консоль cp1251 по умолчанию: print('русский') ломается при
    выводе в pipe. На Linux/Mac обычно уже UTF-8, тогда no-op.
    """
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is None:
            continue
        enc = getattr(stream, "encoding", None) or ""
        if enc.lower().replace("-", "") == "utf8":
            continue
        try:
            buffer = stream.buffer
        except AttributeError:
            # Поток уже обёрнут (например в тестах) — пропускаем.
            continue
        setattr(
            sys,
            name,
            io.TextIOWrapper(buffer, encoding="utf-8", line_buffering=True),
        )


_ensure_utf8_streams()


# ──────────────────────────────────────────────────────────────────
# 2. Поиск корня репозитория landing_system
# ──────────────────────────────────────────────────────────────────

def _find_repo_root() -> Path:
    """Подняться от текущего файла до корня landing_system.

    Корень определяем по наличию CLAUDE.md + папки agents/ — этого
    достаточно чтобы не спутать с другим репозиторием.
    """
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "CLAUDE.md").exists() and (parent / "agents").is_dir():
            return parent
    # Fallback — два уровня вверх от scripts/lib/.
    return here.parent.parent.parent


REPO_ROOT: Path = _find_repo_root()


# ──────────────────────────────────────────────────────────────────
# 3. Поиск корня папки с лендингами
# ──────────────────────────────────────────────────────────────────

def _find_landings_root() -> Path:
    """Найти папку с проектами-лендингами по трём правилам:

    1. Переменная окружения LANDINGS_ROOT (явное переопределение).
    2. Папка Lendings рядом с landing_system (типичная установка).
    3. ~/Lendings (домашняя папка пользователя, старый дефолт).

    Если ни один путь не существует — возвращаем выбранный вариант
    с обозначением «не найден»; скрипт-потребитель решает что делать.
    """
    # Правило 1: явная переменная окружения.
    env_value = os.environ.get("LANDINGS_ROOT", "").strip()
    if env_value:
        return Path(env_value).expanduser().resolve()

    # Правило 2: рядом с landing_system.
    sibling = REPO_ROOT.parent / "Lendings"
    if sibling.is_dir():
        return sibling.resolve()

    # Правило 3: домашняя папка.
    home_path = Path.home() / "Lendings"
    if home_path.is_dir():
        return home_path.resolve()

    # Ничего не нашли — возвращаем sibling-вариант как наиболее вероятный.
    # Скрипт-потребитель увидит что папка не существует и выдаст
    # понятное сообщение через require_landings_root().
    return sibling.resolve()


LANDINGS_ROOT: Path = _find_landings_root()


def require_landings_root() -> Path:
    """Вернуть LANDINGS_ROOT, выкинуть SystemExit если папка не найдена.

    Использовать в скриптах, которым обязательно нужна папка с
    проектами. Выводит понятное сообщение, как настроить.
    """
    if LANDINGS_ROOT.is_dir():
        return LANDINGS_ROOT
    sys.exit(
        "[paths] Не найдена папка с лендингами.\n"
        f"  Пробовали: {LANDINGS_ROOT}\n"
        "  Реши одним из способов:\n"
        f"    1. Создай папку: mkdir -p {LANDINGS_ROOT}\n"
        f"    2. Задай переменную: export LANDINGS_ROOT=/path/to/your/Lendings\n"
        "    3. Дoбавь LANDINGS_ROOT в .env (см. .env.example)"
    )


def project_dir(slug: str) -> Path:
    """Получить путь до конкретного проекта-лендинга.

    Не проверяет существование — это задача скрипта-потребителя.
    """
    return LANDINGS_ROOT / slug
