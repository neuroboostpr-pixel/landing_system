#!/usr/bin/env python3
"""Гейт «без выдуманного текста» для 07c/07f (reference-driven §2.2).

Зеркало verify_content_preserved.py: тот проверяет, что текст прототипа ЕСТЬ
в composed (prototype → composed). Этот — ОБРАТНОЕ: что в composed.html нет
НОВЫХ смысловых слов, которых нет в прототипе (composed → prototype).

ВАЖНО — что РАЗРЕШЕНО (не считается выдумкой):
  - оформление существующего текста (иконки, шрифты, CSS, span, разбивка);
  - служебные/связующие слова из allowlist (CTA-глаголы, «соцсети», копирайт,
    единицы, предлоги) — их можно добавлять для вёрстки;
  - числа и символы валют (цифры-якоря из реального контента);
  - технические токены/slot-имена в sr-only блоке (latin, дефисы).

Что ЗАПРЕЩЕНО (фейл): новые СОДЕРЖАТЕЛЬНЫЕ слова (кириллица, len>=4), которых
нет ни в прототипе, ни в allowlist — это выдуманный смысл (как egg-описания,
фейк-преимущества, новые буллеты).

Exit: 0 — чисто; 1 — найдены выдуманные слова; 2 — файлы не найдены.

Usage: verify_no_invented_text.py <project-dir> [--max-invented N] [--min-word-len L]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: нужен beautifulsoup4", file=sys.stderr)
    sys.exit(2)

# Связующие/служебные слова, которые ОК добавлять для вёрстки (не выдумка смысла).
ALLOWED = {
    # предлоги/союзы/местоимения
    "и", "в", "во", "на", "по", "за", "к", "ко", "с", "со", "из", "от", "до",
    "для", "о", "об", "у", "же", "ли", "бы", "не", "ни", "или", "а", "но",
    "что", "как", "так", "это", "этот", "эта", "эти", "вы", "ты", "мы", "вас",
    "вам", "ваш", "ваша", "ваше", "ваши", "себя", "под", "над", "при", "про",
    # частые UI / связки
    "получить", "получи", "узнать", "узнайте", "записаться", "записатьcя",
    "начать", "начните", "сделать", "сделайте", "хочу", "посмотреть", "задать",
    "соцсети", "контакты", "подробнее", "далее", "ещё", "еще", "сейчас",
    "бесплатно", "эксперт", "эксперта", "финансам", "финансовый", "личным",
    # единицы / общие
    "руб", "рублей", "год", "года", "лет", "день", "дня", "дней", "месяц",
    "месяца", "недели", "неделя", "шаг", "шага", "шагов",
}


def _norm_word(w: str) -> str:
    return w.lower().strip("«»\"'`(),.:;!?—–-…")


def _words(text: str) -> list[str]:
    raw = re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", text)
    return [_norm_word(w) for w in raw if _norm_word(w)]


def _share_root(a: str, b: str, stem: int) -> bool:
    """Слова считаются однокоренными, если их общий префикс >= stem букв
    (терпимо к рус. словоизменению: падежи/число/род)."""
    n = 0
    for ca, cb in zip(a, b):
        if ca != cb:
            break
        n += 1
    return n >= stem and n >= min(len(a), len(b)) - 3


def _is_content_word(w: str, min_len: int) -> bool:
    """Содержательное слово: кириллица, длиной >= min_len, не число."""
    if w.isdigit():
        return False
    if not re.search(r"[А-Яа-яЁё]", w):  # latin (slot-имена, токены) — пропускаем
        return False
    return len(w) >= min_len


def _proto_words(project_dir: Path) -> set[str]:
    """Слова АКТИВНОГО прототипа.

    Источник истины — `meta.active: true` (новый формат gen-prototype:
    prototype-NN.yaml). Если активного нет — legacy-имена prototype.yaml/.md.
    Раньше читались только legacy-имена → новый prototype-01.yaml не находился
    и ВЕСЬ текст считался «выдуманным» (ложный FAIL).
    """
    proto_dir = project_dir / "07_ПРОТОТИП"
    words: set[str] = set()

    # 1) активный prototype-*.yaml по флагу meta.active:true
    active_found = False
    try:
        import yaml
        for p in sorted(proto_dir.glob("prototype-*.yaml")):
            try:
                d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            except Exception:
                continue
            if (d.get("meta") or {}).get("active") is True:
                words |= set(_words(p.read_text(encoding="utf-8")))
                active_found = True
    except ImportError:
        pass

    # 2) fallback — legacy-имена (старые проекты)
    if not active_found:
        for name in ("prototype.yaml", "prototype.md"):
            p = proto_dir / name
            if p.exists():
                words |= set(_words(p.read_text(encoding="utf-8")))
    return words


def main(project_dir: Path, max_invented: int, min_word_len: int) -> int:
    composed = project_dir / "07b_COMPOSED" / "composed.html"
    if not composed.exists():
        print(f"ERROR: {composed} не найден", file=sys.stderr)
        return 2
    if not (project_dir / "07_ПРОТОТИП").exists():
        print("ERROR: нет 07_ПРОТОТИП", file=sys.stderr)
        return 2

    soup = BeautifulSoup(composed.read_text(encoding="utf-8"), "html.parser")
    # sr-only / aria-hidden блоки со slot-именами — не контент, исключаем из текста
    for el in soup.select('[aria-hidden="true"]'):
        el.decompose()
    visible = soup.get_text(separator=" ")

    proto = _proto_words(project_dir)
    allowed = ALLOWED

    invented: list[str] = []
    seen: set[str] = set()
    for w in _words(visible):
        if not _is_content_word(w, min_word_len):
            continue
        if w in proto or w in allowed or w in seen:
            continue
        # терпим словоформы (рус. словоизменение): общий префикс-корень >=4 букв
        # с любым словом прототипа. Ловит реальные выдумки («эксклюзивная»),
        # но пропускает падежи/числа («ольга»→«ольги», «долги»→«долгов»).
        STEM = 4
        if any(_share_root(w, pw, STEM) for pw in proto):
            continue
        seen.add(w)
        invented.append(w)

    if len(invented) > max_invented:
        print(f"❌ Найдено {len(invented)} выдуманных слов (порог {max_invented}) — "
              f"текст, которого нет в прототипе:", file=sys.stderr)
        for w in invented[:30]:
            print(f"   - {w}", file=sys.stderr)
        print("Разрешено ОФОРМЛЯТЬ текст прототипа (иконки/шрифты/css), "
              "но НЕ добавлять новые смыслы (reference-driven §2.2).", file=sys.stderr)
        return 1

    print(f"✅ Без выдуманного текста (выдуманных слов: {len(invented)}, "
          f"порог {max_invented}).")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--max-invented", type=int, default=0)
    ap.add_argument("--min-word-len", type=int, default=4)
    args = ap.parse_args()
    sys.exit(main(Path(args.project), args.max_invented, args.min_word_len))
