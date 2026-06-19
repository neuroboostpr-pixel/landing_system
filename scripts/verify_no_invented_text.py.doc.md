---
type: script
name: verify_no_invented_text
language: python
sources: ["scripts/verify_no_invented_text.py"]
updated: 2026-05-18
---

# verify_no_invented_text.py

Гейт «без выдуманного текста» для 07c/07f (reference-driven §2.2).

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

## Источник

- `scripts/verify_no_invented_text.py`
