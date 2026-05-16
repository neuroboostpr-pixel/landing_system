# PR-J — Static Prompts (через engine) + Identity Hardening

**Дата:** 2026-05-16
**Источник:** ПЛАН-ДОРАБОТОК.md пункт №4 + правило user'а о стационарных промптах
**Статус:** draft на ревью
**Связанные PR:** PR-I.a (Photo Pipeline), PR-I.b (Visual QA), gpt5-prompting-engine

---

## 1. Зачем

**Две связанные проблемы:**

### A. Стационарные промпты
В системе три codex-промпта. Один (review-prompt.md) уже сделан через engine на 10/10. Два других (atlas-prompt, codex-photo-prompt) написаны без engine — могут быть слабее. Правило системы: **все codex-промпты должны быть стационарными файлами, валидированными через `gpt5-prompting-engine`**.

### B. Identity Hardening (пункт 4 плана)
Сейчас `identity-check.py` использует один threshold для всех типов фоток. Но для лица допустимо меньше изменений чем для машины. Плюс при violation сейчас просто exit 1 — нужна **revert логика** (использовать оригинал) + **HARD GATE** в финальной композиции.

---

## 2. Главные решения (из брейншторма)

| Решение | Значение |
|---|---|
| Стационарные промпты | Перепрогнать `atlas-prompt.md` и `codex-photo-prompt.md` через engine, validation ≥8/10 |
| Per-type thresholds | Словарь `THRESHOLDS` в `identity-check.py` (portrait=5, vehicle=10, product=8, …) |
| Поведение при violation | Revert на оригинал (с resize, без codex), warning в manifest |
| HARD GATE | На 07f_composed_final — нет identity_violations в manifest. На 07c — soft warning. |

---

## 3. Часть A — Стационарные промпты через engine

### A.1 atlas-prompt.md (параллакс-герой)

Существующий файл `skills/paralaximus-codex/templates/atlas-prompt.md` — написан до engine, ~180 строк. Содержит template + filled example.

**Что делаем:**
- Прогон через engine: classify=migrate, target=Codex CLI image_gen
- Engine применит migration checks (GPT-5 rules), validation rubric
- Сохранить **новую версию** в том же файле
- Оригинал → `templates/atlas-prompt.legacy.md` для отката (1 commit)
- Score должен быть ≥8/10

### A.2 codex-photo-prompt.md (обработка фотки)

Существующий `skills/photo-curation/templates/codex-photo-prompt.md` написан мной без engine.

**Что делаем:**
- Через engine: classify=create, target=Codex CLI vision/image_gen
- Бриф для engine:
  ```
  Промпт для обработки клиентской фотки через codex CLI image_gen с -i flag.
  
  Параметры (плейсхолдеры в шаблоне):
  - {RATIO} — целевое соотношение слота
  - {BRAND_COLOR} — primary цвет бренда (hex)
  - {NICHE} — ниша (premium-auto, real-estate, etc.)
  - {REGION} — гео-локация (Dubai, Moscow, etc.)
  - {SLOT_TYPE} — тип слота (portrait, vehicle, product, hero-bg)
  
  Цели:
  - Адаптировать фон под region atmosphere
  - Цветокор под brand color (subtle)
  - Сохранить identity объекта DOSLOVNO
  
  Identity-strict правила:
  - PRESERVE original subject EXACTLY (no AI repaint of car/face/product)
  - Modify ONLY: background, lighting, color grading
  - If cannot preserve identity → output original unchanged
  
  Output: одна PNG обработанная картинка.
  ```
- Validation ≥8/10
- Сохранить в том же файле
- Оригинал → `codex-photo-prompt.legacy.md`

### A.3 (Опционально) Общий promot-quality check

В существующем `scripts/check-wiki-sync.sh` уже есть паттерн проверки целостности. Можно по аналогии создать `scripts/check-prompts-quality.sh` — проверяет что **каждый файл в `*/templates/*-prompt.md`** имеет заголовок `# <name> Prompt` + раздел `## Validation` со score.

В этом PR — оставим как nice-to-have, делать после.

---

## 4. Часть B — Identity Hardening

### B.1 Per-type thresholds в `identity-check.py`

```python
# Default Hamming distance thresholds by slot type.
# Lower = stricter (small change = violation).
THRESHOLDS = {
    "portrait": 5,
    "team": 5,
    "testimonial": 5,
    "expert": 5,
    "vehicle": 10,
    "car": 10,
    "product": 8,
    "hero-bg": 12,
    "interior": 15,
    "lifestyle": 15,
    "background": 18,
    "default": 10,
}
```

CLI:
```bash
identity-check.py <orig> <processed> --slot-type portrait
# или
identity-check.py <orig> <processed> --threshold 7  # ручной override
```

Если `--slot-type` указан — берём из dict. Если нет — `--threshold` (или default 10).

### B.2 Revert логика в `photo-pipeline.py`

В функции `process_one_slot()` блок identity check уже есть:

```python
# Сейчас:
if codex_ok:
    try:
        check = subprocess.run([...identity-check.py...])
        if check.returncode != 0:
            codex_ok = False  # revert на оригинал
    except ...:
        pass
```

**Дополняем:**
- Передаём `--slot-type` в identity-check.py (из slot_meta)
- При violation — добавляем `identity_violation: true` + `distance` + `threshold` в manifest entry для этого слота
- Используем оригинал для дальнейшего pipeline (crop + resize, но без codex)

```python
# После:
manifest[f"{slot_name}.jpg"] = {
    "slot": slot_name,
    "status": "raw-resized" if not codex_ok else "processed",
    "identity_violation": not codex_ok and identity_check_was_run,
    "distance": measured_distance,
    "threshold": threshold_used,
    "size": f"{target_w}x{target_h}",
}
```

### B.3 Verify-скрипт `verify-identity-preserved.sh`

```bash
#!/bin/bash
set -uo pipefail
PROJECT="${1:?ERROR: project required}"
MANIFEST="$PROJECT/07c_PHOTOS/processed/manifest.json"
[ -f "$MANIFEST" ] || { echo "✅ identity OK (нет processed manifest)"; exit 0; }

python3 -c "
import json, sys
data = json.load(open('$MANIFEST'))
violations = [(k, v) for k, v in data.items() if v.get('identity_violation')]
if not violations:
    print('✅ Identity сохранён для всех слотов')
    sys.exit(0)
print(f'❌ Identity violations ({len(violations)}):')
for k, v in violations:
    d, t = v.get('distance'), v.get('threshold')
    print(f'  - {k}: distance={d} > threshold={t}')
sys.exit(1)
"
```

### B.4 stage-gates integration

В `config/stage-gates.yaml`:

```yaml
"07c_composed":
  soft_checks:
    - id: identity_preserved
      prompt: "Identity check для фоток прошёл? Опционально, не блокирует 07c."

"07f_composed_final":
  hard_checks:
    - id: identity_preserved
      type: script
      script: "scripts/verify-identity-preserved.sh"
      args: ["{project}"]
      required: true
      fix_hint: "Identity нарушен для одной или нескольких фоток. Пересмотреть промпт или вернуть оригинал. Подробности в 07c_PHOTOS/processed/manifest.json."
```

(На 07c soft потому что photo pipeline только начинается; на 07f hard т.к. это финальная композиция перед деплоем.)

### B.5 Усиление промпта (закрытый цикл с Частью A.2)

В новом `codex-photo-prompt.md` (через engine, Часть A.2) явно прописано identity-strict. Так что:
1. Engine пишет хороший промпт с identity rules
2. photo-pipeline вызывает codex с этим промптом
3. identity-check (per-type threshold) проверяет результат
4. Revert если не прошло

---

## 5. Структура файлов

**Создаются:**
- `skills/paralaximus-codex/templates/atlas-prompt.legacy.md` (бекап старого)
- `skills/photo-curation/templates/codex-photo-prompt.legacy.md` (бекап старого)
- `scripts/verify-identity-preserved.sh`
- `tests/pr-j/helpers.bash`
- `tests/pr-j/test_threshold_per_type.bats`
- `tests/pr-j/test_revert_on_violation.bats`
- `tests/pr-j/test_verify_identity.bats`

**Модифицируются:**
- `skills/paralaximus-codex/templates/atlas-prompt.md` — через engine (migrate)
- `skills/photo-curation/templates/codex-photo-prompt.md` — через engine (create)
- `skills/photo-curation/scripts/identity-check.py` — per-type thresholds + `--slot-type`
- `skills/photo-curation/scripts/photo-pipeline.py` — revert логика + manifest violation flag
- `config/stage-gates.yaml` — soft check 07c + hard check 07f

---

## 6. Тесты (3 bats)

### Test 1: `test_threshold_per_type.bats`
- Setup: identical-content тест-фото
- Action: `identity-check.py <a> <b> --slot-type portrait`
- Expected: distance=0, exit 0
- Cross-check: `--slot-type vehicle` тоже exit 0 (distance=0 < 10)

### Test 2: `test_revert_on_violation.bats`
- Setup: фикстура photo-pipeline в моке (codex генерит чем-то очень далёким)
- Mock: `identity-check.py` возвращает exit 1
- Action: `photo-pipeline.py --slot=hero-bg`
- Expected: `processed/hero-bg.jpg` существует, но это оригинал (по hash сравнению), manifest[hero-bg.jpg].identity_violation == true

### Test 3: `test_verify_identity.bats`
- Setup: project с manifest где один слот имеет `identity_violation: true`
- Action: `verify-identity-preserved.sh <project>`
- Expected: exit 1, stderr содержит violation details
- Cross-check: manifest без violations → exit 0

---

## 7. Объём

| Этап | Время | SDK/codex |
|---|---|---|
| A.1 atlas-prompt через engine | 30 мин | 0 |
| A.2 codex-photo-prompt через engine | 30 мин | 0 |
| B.1 per-type thresholds | 20 мин | 0 |
| B.2 revert логика | 40 мин | 0 |
| B.3 verify-identity скрипт | 20 мин | 0 |
| B.4 stage-gates integration | 10 мин | 0 |
| C: 3 bats теста | 40 мин | 0 |
| Smoke + push | 20 мин | 0 |

**Итого ~3.5 часа, 0 SDK calls.**

---

## 8. Открытые вопросы

1. **Threshold для slot-type'ов** — выбраны эмпирически (portrait=5, vehicle=10). Возможно потребуют тюнинга после реальных прогонов.
2. **Backward compat** — старые проекты (dubai-avto-liza) с уже processed фотами без manifest entries для identity — verify пройдёт (manifest пустой → identity OK). Это OK.
3. **Legacy промпт-файлы** — оставляем для отката. Если engine выдаст хуже — можно вернуться. После пары прогонов на реальных задачах — удалить legacy.

---

## 9. Что меняется для пользователя

**До PR-J:**
- Codex мог переделать машину под другую модель — identity-check ловил, но один threshold для всех = false positives для интерьеров и false negatives для лиц
- Промпты для codex написаны ad-hoc, без engine валидации
- При identity-violation — pipeline просто отказывался, но revert логики не было

**После PR-J:**
- Per-type thresholds — лицо охраняется в 2 раза строже чем машина, интерьер в 1.5 раза свободнее
- Revert на оригинал — если codex сорвался, мы не теряем слот, просто используем сырое фото с resize
- HARD GATE на 07f — нельзя задеплоить лендинг с identity violations
- Все 3 codex-промпта системы валидированы через engine ≥8/10

---

## 10. Связь с другими PR

- **PR-I.a** (Photo Pipeline) — основа, PR-J усиливает identity часть
- **PR-I.b** (Visual QA) — параллельная защита (визуально ловит то что hash не уловил)
- **gpt5-prompting-engine** — инструмент для Части A
- **PR-H** (Content Preserve) — параллельный принцип «не ломать» (текст) — PR-J делает то же для фото
