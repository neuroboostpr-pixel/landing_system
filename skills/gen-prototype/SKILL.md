---
name: gen-prototype
description: Извлечение данных из прототипа клиента (графического PNG/PDF — читая ГЛАЗАМИ, или текстового DOCX/MD — раскладывая весь текст) в типизированный prototype-NN.yaml с разметкой role/group по словарю ролей. Комментарии клиента хранятся отдельно (client_notes); комментарии-инструкции (карусель/бегущая строка/слайдер/аккордеон) помечают блок для генерации по инструкции. Ставит meta.active:true (ровно один активный), ведёт prototypes-index.md. Этап 07a. Источник истины структуры/текстов для всего флоу.
---

# gen-prototype

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill gen-prototype --stage 07a
```

Извлекает СТРУКТУРУ + ТЕКСТЫ из прототипа клиента в один типизированный yaml.
Прототип = **что где стоит и какие тексты** (НЕ вид — вид из референса, см. `gen-design-system`).

## Вход

- **Графический прототип** (`07_ПРОТОТИП/source/*.png|*.pdf`) — вайрфрейм/эскиз.
- **ИЛИ текстовый прототип** (`*.docx|*.md|*.txt`) — текстовое ТЗ от клиента.
- Комментарии клиента (в файле или отдельно) — пожелания/инструкции к блокам.

## Инструменты (в этом скиле: `scripts/`)

| Скрипт | Когда | Что делает |
|---|---|---|
| `scripts/extract-docx-text.py --source <docx> --out <prefix>` | флоу B (.docx) | детерминированный экстрактор: весь текст + таблицы (цены не терять) → `<prefix>.txt`+`.json`. Писать `--out` во ВРЕМЕННУЮ папку, не в проект. |
| `scripts/render-pdf-slices.py --source <pdf> [--slices 12] [--zoom 3.0]` | флоу A (графический PDF) | режет страницу на N полос при зуме → PNG во временной папке; пути в stdout. Агент читает их Read-ом ГЛАЗАМИ. |
| `scripts/verify-prototype-fidelity.py --source-text <txt> --prototype <yaml> [--folder <dir>]` | **обязательно** после записи yaml | гейт точности: покрытие ≥90%, 0 галлюцинаций, `meta.blocks==len(blocks)`, ровно один `active` в `--folder`. Отчёт → temp (не в проект). exit 0/1. |

## Выход (yaml проекта)

- `07_ПРОТОТИП/prototype-NN.yaml` — типизированный, с `role`/`group`, `meta.active`, `client_notes`, `block_instructions`.
- `07_ПРОТОТИП/prototypes-index.md` — реестр (какой активный, словарь ролей).

## Флоу

### A. Графический прототип (PNG/PDF)
1. Нарезать исходник на полосы (`scripts/render-pdf-slices.py` для PDF) и читать **ГЛАЗАМИ**
   (зум ×2–3) — НЕ доверять авто-OCR. Текстовый слой PDF годится только для сверки гейтом, НЕ как источник.
2. Извлечь по блокам типизированными ключами (см. ниже структуру).
3. Тексты — ДОСЛОВНО и ПОЛНЫЕ (не усекать «Пошаговый финплан» → «финплан»; сохранять опечатки источника).

### B. Текстовый прототип (DOCX/MD/текст)
1. Разложить ВЕСЬ текст по блокам и ключам — ничего не терять.
2. Для .docx — детерминированный экстрактор `scripts/extract-docx-text.py` (текст + таблицы, цены не терять).
3. Сопоставить абзацы/списки с типами блоков и ролями.

### C. Общее (оба случая)
4. **Разметить каждый элемент** `role:` + опц. `group:` по словарю ролей (`prototypes-index.md`).
   Связанные (cta-кнопка+подпись, имя+роль+реплика) — ОДИН `group`.
5. **Комментарии клиента → `client_notes`** (отдельно от контента). **Хранить ДОСЛОВНО**
   (не переформулировать) — иначе гейт сочтёт их «потерянными» из источника.
   Если комментарий = ИНСТРУКЦИЯ к блоку (карусель / бегущая строка / слайдер / аккордеон / автопрокрутка /
   видео-фон и т.п.) → записать в `block_instructions` с привязкой к блоку. gen-spec/gen-html сгенерят блок ПО инструкции.
6. Проставить `meta.blocks` = фактическому числу блоков (гейт это проверяет).
7. Поставить `meta.active: true` (ровно ОДИН активный yaml в папке; у старых снять).
8. Обновить `prototypes-index.md` (строка в таблицу, флаг active).
9. **ОБЯЗАТЕЛЬНО прогнать гейт** `scripts/verify-prototype-fidelity.py --source-text <извлечённый.txt>
   --prototype <yaml> --folder <папка>`. При FAIL (покрытие <90% / галлюцинации / неверный счётчик /
   ≠1 active) — дорабатывать yaml, НЕ закрывать этап. Отчёт пишется в temp, в проект его НЕ класть.

## Структура yaml (типизированные ключи + роли)

```yaml
meta: {project, niche, source, active: true, blocks: N}
client_notes:                      # пожелания клиента, отдельно от контента
  - "хочу строгий минимализм"
block_instructions:                # комментарии-ИНСТРУКЦИИ → влияют на генерацию блока
  - {block: testimonials, instruction: "карусель с автопрокруткой"}
  - {block: partners, instruction: "бегущая строка логотипов"}
seo_phrases:                       # SEO-фразы клиента (если даны отдельным блоком), опц.
  label: "SEO-фразы для индексации"
  items: ["как закрыть долги", "финплан за 5 дней"]
blocks:
  - position: 1
    type: header
    logo: {text, sub, role: logo}
    nav: {items: [...], role: nav}
    cta: {text, role: head-cta}
  - position: 2
    type: hero
    eyebrow:  {text, role: eyebrow}
    headline: {text, role: h1, accent_word}
    subhead:  {text, role: subhead}
    features: {role: feature, group: features, items: [...]}   # ПОЛНЫЕ тексты
    cta:
      button: {text, role: cta-button, group: cta}
      note:   {text, role: cta-note,   group: cta}             # подпись = ОДИН объект с кнопкой
    trust_strip: {role: trust-item, group: trust, items: [...]}
    expert_quote: {group: expert-quote, author:{...}, author_role:{...}, text:{...}}  # ЦИТАТА, не заголовки
  # stats / problem-solution(pains/gains) / process(formats/benefits) / case-study / trust / testimonials ...
```

## ПРАВИЛА (⛔ нарушение = дефект)

- ⛔ **Тексты ДОСЛОВНО и ПОЛНЫЕ.** Не переписывать, не усекать, смысл не переворачивать, опечатки источника сохранять (`no_invented_text`).
- ⛔ **Активный — по флагу `meta.active: true`, НЕ по имени/номеру файла.** Ровно один активный (гейт проверяет, см. шаг 9).
- ⛔ **`meta.blocks` = фактическому числу блоков.** Расхождение = дефект (гейт проверяет).
- ⛔ **Связанное → один `group`** (cta+note, имя+роль+реплика). Не раскидывать.
- ⛔ **Комментарии ≠ контент.** Пожелания → `client_notes` (ДОСЛОВНО); инструкции к блокам → `block_instructions`.
- ⛔ **Не плодить промежуточные файлы** (parse .md, логи, fidelity-report) В ПРОЕКТЕ. Источник один — типизированный `.yaml`; временное — в temp.
- Размечать элементы ролями (словарь — `prototypes-index.md`): eyebrow/h1/h2/h3/subhead/feature/cta-button/
  cta-note/trust-item/quote-text/quote-author/quote-author-role/stat-num/stat-label/pain/gain/process-step/case-card.

## Стандарт

- Точность парсинга: [`docs/standards/prototype-fidelity.md`](../../docs/standards/prototype-fidelity.md) (hard-gate `prototype_fidelity` — потеря >10% текста / выдуманная структура = FAIL).
- Гейт-скрипт: `scripts/verify-prototype-fidelity.py` (этот скил). Проверяет покрытие + галлюцинации + `meta.blocks` + ровно один `active`.
- Словарь ролей + правило active: `07_ПРОТОТИП/prototypes-index.md` (в проекте).

## Следующий шаг

→ `gen-design-system` (референс→муды) → `gen-spec` (ТЗ-mapping) → `gen-html`.
