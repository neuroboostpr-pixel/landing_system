---
type: script
name: verify-collage-plan
language: python
sources: ["scripts/verify-collage-plan.py"]
updated: 2026-05-18
---

# verify-collage-plan.py

Гейт «анализ блоков для коллажа» для 07c (reference-driven §3.4).

§3.4 требует: перед вёрсткой агент проходит по КАЖДОМУ блоку и решает —
где пусто/плоско → какой визуальный приём это закрывает. Это обязательный
артефакт collage-plan.md, а не «в голове».

Контракт 07b_COMPOSED/collage-plan.md:
  - строка-вердикт `COLLAGE_PLAN: READY` в конце;
  - содержательная таблица/строки по блокам (>= N блоков покрыто): для каждого
    блока указаны «потребность места» и «приём» (см. каталог §3.4);
  - не заглушка (минимальная длина).

Кол-во разобранных блоков должно совпадать с числом блоков прототипа (±0):
сверяем с prototype.yaml/prototype.md.

Exit 0 — OK; 1 — нет плана/заглушка/неполно; 2 — файлы не найдены.
Usage: verify-collage-plan.py <project-dir>

## Источник

- `scripts/verify-collage-plan.py`
