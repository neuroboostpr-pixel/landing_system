# B37 — Точность парсинга прототипов (no-loss, no-hallucination)

**Дата:** 2026-06-02
**Статус:** PLAN (ожидает утверждения)
**Триггер:** на neurokreator парсер docx→prototype.yaml потерял ~52% текста
клиента и выдумал структуру (меню `[Home,About,Services,Contact]`, тарифы
`standard/premium/vip` вместо реальных цен 100 990 ₽).

## Проблема (диагноз)

Парсинг docx → prototype.yaml делает **LLM-агент `prototype-importer` в
свободной форме** — без детерминированного скрипта извлечения. Когда структура
неясна, LLM **выдумывает** типовое (шапка с меню, абстрактные тарифы) вместо
того, чтобы взять только то, что есть, или спросить.

| Слой | Что не так | Файл |
|---|---|---|
| Парсер docx | нет скрипта; LLM читает «как понял», выдумывает | `agents/prototype-importer.md` (step 4) |
| Валидатор yaml | только синтаксис/типы, не полнота | `skills/prototype-import/scripts/validate-prototype.py` |
| Gate 07a | только «файл существует» | `config/stage-gates.yaml` (07a_prototype) |
| Gate 07_content | ловит только Lorem ipsum, не частичную потерю | `validate-content-extraction.py` |
| content-writer | читает неполный yaml → усугубляет | `agents/content-writer.md` |

Итог: потеря и галлюцинации **проходят все гейты незамеченными**.

## Принципы (что чиним)

1. **Извлечение — детерминированное.** docx читается скриптом (python-docx),
   который вытаскивает ВЕСЬ текст (параграфы, заголовки, списки, таблицы) с
   сохранением порядка. Не LLM «как понял».
2. **Нулевая выдумка.** Структуру (типы блоков, секции) определяет LLM ТОЛЬКО
   из реально извлечённого текста. Чего нет в источнике — того нет в yaml.
   Неуверен — спрашивает пользователя, не пишет типовое.
3. **Проверяемая полнота.** Гейт сравнивает текст источника с текстом yaml и
   падает, если потеряно > порога. Плюс anti-hallucination check на типовые
   паттерны (Home/About/Services/Contact, standard/premium/vip).

## Фазы

### Фаза 0 — Детерминированный экстрактор docx
**Файл:** `skills/prototype-import/scripts/extract-docx-text.py` (новый).
- python-docx → плоский список параграфов + таблиц (ячейки), в порядке
  документа, с пометкой стиля (Heading 1/2, List, Table).
- Выход: `source-extracted.txt` (весь текст) + `source-extracted.json`
  (структурные единицы с типом). Это ЭТАЛОН полноты.
- Fallback: если не docx — существующий `extract-pdf-text.py` / .md as-is.
- Тест: на фикстуре .docx извлекается 100% текста, таблицы не теряются.

### Фаза 1 — Anti-hallucination промпт + явный вход
**Файл:** `agents/prototype-importer.md` + (новый) промпт
`skills/prototype-import/prompts/structure-from-extracted.md`.
- Агент НЕ читает docx сам — получает `source-extracted.json` (Фаза 0).
- Промпт жёстко: «Используй ТОЛЬКО строки из extracted. НЕ добавляй меню,
  тарифы, CTA, которых нет в тексте. Если секция/тип неясен — ставь
  `type: unknown` + `needs_review: true`, НЕ выдумывай. Каждый blocks[].text
  обязан быть подстрокой источника.»
- Запрещённые дефолты перечислены явно (Home/About/Services/Contact,
  standard/premium/vip, «Get Started», Lorem).

### Фаза 2 — Валидатор полноты + anti-hallucination
**Файлы:** `skills/prototype-import/scripts/verify-prototype-fidelity.py`
(новый) + расширение `validate-prototype.py`.
- **Completeness:** доля текста источника (`source-extracted.txt`),
  присутствующая в prototype.yaml (по нормализованным фразам). FAIL если
  покрытие < порога (старт: 70% строк / 60% знаков, настраивается).
- **Hallucination:** каждый `blocks[].text`/`items[]` обязан встречаться в
  источнике (substring/fuzzy). Строки не из источника → список «выдумано».
- **Pattern blocklist:** Home|About|Services|Contact как полный menu,
  standard/premium/vip как price → FAIL.
- Отчёт: `fidelity-report.md` (потеряно/выдумано построчно).
- Тест: на neurokreator (текущий yaml) скрипт обязан показать потерю + меню
  как выдуманное (красный), на исправленном — зелёный.

### Фаза 3 — Hard gate 07a
**Файл:** `config/stage-gates.yaml`.
- Добавить в `07a_prototype` hard-check `prototype_fidelity` →
  `verify-prototype-fidelity.py`. Гейт 07a не закрывается при потере/выдумке.
- fix_hint: «Парсер потерял/выдумал контент — см. fidelity-report.md,
  перепарсь или поправь prototype.yaml вручную».

### Фаза 4 — Перепарсить neurokreator
- Прогнать новый пайплайн на `source/prototype.docx`.
- Убедиться: меню убрано (его нет в источнике), тарифы с реальными ценами,
  блок экспертов, outcome-абзацы программы, рассрочка, галерея — на месте.
- fidelity-report зелёный.

### Фаза 5 — Доки
- `docs/standards/prototype-fidelity.md` — правило «no loss, no hallucination»,
  пороги, как читать fidelity-report.
- Обновить CLAUDE.md (секция PR-A) + `skills/prototype-import/SKILL.md`.

## Решения (подтверждены 2026-06-02)
1. Порог гейта: **≥90% покрытия** текста источника (FAIL если потеряно >10%).
2. Порядок: **neurokreator first** — сначала экстрактор (Фаза 0) + перепарс
   neurokreator (Фаза 4), затем валидатор/гейт/промпт как закрепление.
3. docx-ридер: **python-docx** (установлен, 1.2.0). Добавить в зависимости.
