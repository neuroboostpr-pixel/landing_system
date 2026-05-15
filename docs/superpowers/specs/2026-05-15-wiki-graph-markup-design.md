# Wiki/граф разметка системы и проектов (по методу Карпати)

**Дата:** 2026-05-15
**Источник:** ПЛАН-ДОРАБОТОК.md пункт №0 + видео «Как сделать Claude Code в 10 раз умнее»
**Статус:** draft на ревью
**Связанный PR:** PR-F (Wiki Graph)

---

## 1. Зачем это нужно (простым языком)

Сейчас агент при старте каждой новой сессии не помнит, что было до неё. Он лезет сканировать папки, перечитывает агентов, скиллы, артефакты проекта. Это 5-10 минут и куча токенов на то, что он уже знал вчера.

Решение по Карпати: **папка с markdown-файлами становится «компилированной памятью»**. Агент читает её один индексный файл за 1 секунду и сразу знает всё — архитектуру системы и состояние конкретного проекта.

Этот пункт — **фундамент** для остальных доработок из плана. Без него:
- Пункт #1 (агент идёт строго по шагам) — не работает, потому что агент не помнит, где остановился.
- Пункт #2 (текст прототипа не меняется) — не работает, потому что агент не помнит правило.
- Все остальные правила (identity-safe, premium-07b) — забываются между сессиями.

---

## 2. Три слоя wiki (главное решение)

| Слой | Где живёт | Источник данных | Когда обновляется |
|---|---|---|---|
| **A. Системный wiki** | `landing-system/wiki/` | Сами файлы системы: `agents/`, `skills/`, `commands/`, `template/`, `docs/standards/` | При изменении кода системы — вручную `npm run wiki:compile` или git pre-push hook |
| **B1. Память проекта (разговоры)** | `~/Lendings/<slug>/memory/` | Транскрипты сессий Claude Code по этому лендингу | Автоматически — хуки `session-end` и `pre-compact` |
| **B2. Граф проекта (структура)** | `~/Lendings/<slug>/wiki/` | Артефакты проекта: `composed.html`, `selections.yaml`, `tokens.json`, `prototype.md`, `.landing-state.yaml` | Автоматически — при завершении каждого этапа pipeline (07a→07b→07c…) |

**Принцип:** три слоя независимы, но используют **одни и те же скрипты** (`compile.py`, `query.py`, `lint.py`) с разным `--source-mode`. Запрос идёт во все три и синтезирует ответ.

---

## 3. Структура папок

### 3.1 Слой A — системный wiki (`landing-system/wiki/`)

```
landing-system/wiki/
├── index.md                          # МАСТЕР-ИНДЕКС. Агент читает первым делом.
├── log.md                            # Хронология обновлений системы
├── concepts/
│   ├── agents/
│   │   ├── landing-orchestrator.md   # Что делает оркестратор, какие этапы ведёт
│   │   ├── block-composer.md
│   │   ├── photo-curator.md
│   │   └── ... (35 файлов, по одному на агента)
│   ├── skills/
│   │   ├── photo-curation.md
│   │   ├── block-composition.md
│   │   └── ... (25 файлов)
│   ├── commands/
│   │   ├── landing-start.md
│   │   ├── landing-go.md
│   │   ├── landing-photos.md
│   │   └── ... (27 файлов)
│   ├── stages/
│   │   ├── 00-brief.md               # Этап: что делается, какой агент, какие артефакты
│   │   ├── 01a-niche-analysis.md
│   │   ├── 07a-wireframe.md
│   │   ├── 07b-composed.md           # Включает premium-07b checklist
│   │   ├── 07c-photos.md
│   │   ├── ... (все 18 этапов template)
│   │   └── 12-seo.md
│   └── rules/
│       ├── identity-safe-photos.md   # Правило: фото клиента не репеинтятся
│       ├── content-preserve.md       # Правило: текст прототипа не меняется
│       ├── hard-gate-between-stages.md
│       ├── premium-07b-checklist.md
│       └── ...
├── connections/                      # Перекрёстные связи (граф)
│   ├── stage-07c-photo-pipeline.md   # Как связаны команда → агент → скилл → артефакты
│   ├── orchestrator-flow.md          # Полный flow PR-D
│   ├── photos-vs-visuals.md          # Чем отличается 07c от 07d
│   └── ...
└── preview.html                      # HTML-просмотрщик wiki (свой, не Obsidian)
```

### 3.2 Слой B1 + B2 — внутри каждого лендинга

```
~/Lendings/<slug>/
├── 00_БРИФ/
├── 01a_АНАЛИЗ_НИШИ/
├── ... (существующие папки template)
├── memory/                           # Слой B1: разговоры (автоматом)
│   ├── daily/
│   │   ├── 2026-05-15.md             # Сырые логи сессий за день
│   │   └── 2026-05-16.md
│   └── compiled/
│       ├── index.md
│       ├── concepts/
│       │   ├── решение-цены-у-конкурентов.md
│       │   └── правка-hero-копии-2026-05-14.md
│       ├── connections/
│       └── qa/                       # Ответы из query.py --file-back
└── wiki/                             # Слой B2: граф структуры (авто после каждого этапа)
    ├── index.md                      # Текущее состояние проекта: этап, что собрано
    ├── log.md                        # Какие этапы когда закрылись
    ├── concepts/
    │   ├── stage-current.md          # current_stage, last_verified
    │   ├── blocks/
    │   │   ├── hero.md               # Какой блок выбран, копия откуда, фото откуда
    │   │   ├── features.md
    │   │   └── ...
    │   ├── photos.md                 # Mapping slot → файл
    │   ├── brand.md                  # Цвета, шрифты, токены
    │   ├── prototype.md              # Что было в исходнике клиента
    │   └── decisions.md              # Ключевые решения по этому проекту
    └── connections/
        └── ...
```

---

## 4. Скрипты и хуки

### 4.1 Источник

Форкаем [coleam00/claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler) → кладём в `landing-system/scripts/wiki/`. Адаптируем для трёх source-mode (см. ниже).

### 4.2 Скрипты в `landing-system/scripts/wiki/`

| Файл | Что делает | Стоимость |
|---|---|---|
| `compile.py --source-mode=system` | Компилит `agents/`, `skills/`, `commands/`, `template/`, `docs/standards/` в `landing-system/wiki/` | ~$0.45-0.65 за прогон, запускается редко (при изменении системы) |
| `compile.py --source-mode=project-graph --project=<slug>` | Компилит артефакты `~/Lendings/<slug>/` в `~/Lendings/<slug>/wiki/` | ~$0.10-0.20 за прогон, запускается после каждого этапа |
| `compile.py --source-mode=conversations --project=<slug>` | Стандартный coleam00 mode: daily logs → `memory/compiled/` | ~$0.45-0.65 за день |
| `query.py "вопрос"` | Запрос ко всем трём слоям, синтез ответа | ~$0.05-0.10 за запрос |
| `lint.py` | 7 проверок здоровья wiki | structural — бесплатно, contradictions — ~$0.15-0.25 |
| `flush.py` | Извлекает уроки из транскрипта в daily/ | вызывается хуком, ~$0.05 за сессию |
| `utils.py`, `config.py` | Общие хелперы | — |

### 4.3 Хуки (`.claude/settings.json`)

Три хука, ставятся **на двух уровнях**:

**А) В `landing-system/.claude/settings.json`** — для сессий когда работаем над самой системой:
- `SessionStart` → инжектит `landing-system/wiki/index.md` + последний `wiki/log.md`
- `SessionEnd` → `flush.py --target=landing-system` сохраняет уроки о работе с системой
- `PreCompact` → страховка, сохраняет до сжатия

**Б) В `template/.claude/settings.json`** (копируется в каждый новый проект) — для сессий по конкретному лендингу:
- `SessionStart` → инжектит `<project>/wiki/index.md` + `<project>/memory/compiled/index.md` + последний `memory/daily/`
- `SessionEnd` → `flush.py --project=<slug>` пишет в `<project>/memory/daily/`
- `PreCompact` → страховка для долгих сессий по проекту

### 4.4 Дополнительный вызов после закрытия этапа (не хук Claude Code)

`landing-orchestrator` после успешного `gate-check.sh` вызывает компайлер сам:
```bash
python scripts/wiki/compile.py --source-mode=project-graph --project=<slug> --stage=<07c>
```

Это обновляет `<project>/wiki/` сразу после того, как этап закрылся, и следующая сессия видит актуальное состояние. Это не «хук Claude Code», а правило в промпте оркестратора + одна строка в `gate-check.sh` (вызов компайлера после exit 0).

---

## 5. Source-mode компилятора (что новое относительно coleam00)

Coleam00 умеет только `conversations`. Дописываем два режима:

### 5.1 `--source-mode=system`

**Входные источники:** определены в `landing-system/scripts/wiki/config.py`:
```python
SYSTEM_SOURCES = [
    {"path": "agents/*.md", "concept_dir": "agents/"},
    {"path": "skills/*/SKILL.md", "concept_dir": "skills/"},
    {"path": "commands/*.md", "concept_dir": "commands/"},
    {"path": "template/*/README.md", "concept_dir": "stages/"},
    {"path": "docs/standards/*.md", "concept_dir": "rules/"},
]
```

**Что делает компилятор:**
1. Читает каждый исходник.
2. Через Claude Agent SDK генерирует **краткую** статью (200-400 слов) с frontmatter:
   ```yaml
   ---
   type: agent | skill | command | stage | rule
   name: landing-orchestrator
   sources: ["agents/landing-orchestrator.md"]
   updated: 2026-05-15
   triggers: [...]   # для команд: когда вызывать
   stage: 07c        # для этапов
   uses: [skill1, skill2]  # обратные ссылки
   ---
   ```
3. Обновляет `wiki/index.md` (категоризированный список со ссылками).
4. Генерирует `connections/` — синтез связей (какой агент вызывает какой скилл, какой этап зависит от какого).
5. Логирует в `wiki/log.md`.

### 5.2 `--source-mode=project-graph`

**Входные источники:**
```python
PROJECT_SOURCES = [
    {"path": ".landing-state.yaml", "concept": "stage-current.md"},
    {"path": "07_ПРОТОТИП/prototype.md", "concept": "prototype.md"},
    {"path": "07a_WIREFRAME/selections.yaml", "concept": "blocks/"},
    {"path": "07b_COMPOSED/composed.html", "concept": "blocks/"},
    {"path": "07c_PHOTOS/selections.yaml", "concept": "photos.md"},
    {"path": "04_БРЕНД/tokens.json", "concept": "brand.md"},
    {"path": "04_БРЕНД/brand-kit.md", "concept": "brand.md"},
]
```

**Что делает:** парсит структурированные артефакты и пишет markdown-резюме каждого. Для блоков — отдельную страницу с пометкой «копия из строки X прототипа, фото `07c/processed/hero-bg.jpg`, цвет primary из tokens». На большинство файлов LLM **не нужен** — это простой парсинг YAML/JSON в markdown. LLM зовём только для синтеза `decisions.md` (что важного решили) и `connections/`.

---

## 6. Интеграция в template (новые проекты)

В `landing-system/template/` добавляем:

1. `template/.claude/settings.json` — хуки B1/B2 (см. 4.3.Б).
2. `template/wiki/.gitkeep` + `template/wiki/README.md` (короткое объяснение «здесь живёт граф структуры этого проекта, обновляется автоматом»).
3. `template/memory/.gitkeep` + `template/memory/README.md`.

При создании нового проекта через `/landing-start` или `/landing-new`:
- Папки `wiki/` и `memory/` создаются пустыми.
- При первом запуске `/landing-go` орchestrator вызывает `compile.py --source-mode=project-graph` → создаются `wiki/index.md` с пометкой «этап 00_БРИФ, ничего ещё не собрано».
- Дальше — обновляется после каждого этапа.

`PR-E` (onboarding wizard) меняется минимально: добавить упоминание в welcome-параграф «у проекта будет своя wiki-память, она ведётся автоматически».

---

## 7. Миграция существующих проектов

### 7.1 Для `dubai-avto-liza` и других ранее созданных:

Скрипт `landing-system/scripts/migrate-add-wiki.sh <project>`:
1. Создаёт `<project>/wiki/` и `<project>/memory/`.
2. Копирует `template/.claude/settings.json` в `<project>/.claude/settings.json` (мерджит если есть).
3. Запускает `compile.py --source-mode=project-graph --project=<slug>` → начальная разметка существующего состояния.
4. Готово.

### 7.2 Для landing-system самой:

Одноразовая команда `npm run wiki:bootstrap` (или просто `bash scripts/wiki/bootstrap-system.sh`):
1. Создаёт `landing-system/wiki/`.
2. Запускает `compile.py --source-mode=system`.
3. Получаем первую версию системного wiki.
4. Коммит в git.

---

## 8. Obsidian как опциональный фронтенд

Карпати использует Obsidian как vault — отлично для визуализации графа связей. Но **не требуем** его установки.

**Что делаем:**
- Папки `wiki/` и `memory/` совместимы с Obsidian: используем `[[wikilinks]]` для перекрёстных ссылок, frontmatter YAML, относительные пути к картинкам.
- Кирилл может открыть `~/Lendings/dubai-avto-liza/` как Obsidian vault и увидеть граф.
- В `docs/SETUP.md` добавляем секцию «Obsidian (опционально)» с инструкцией установки + Web Clipper + плагин Local Images Plus (как в видео).
- Для тех кто без Obsidian — рендерим **свой `wiki/preview.html`** (как у других этапов: MD + HTML preview, по правилу пользователя). HTML генерируется тем же `compile.py`, показывает список статей + поиск + граф связей (через простой d3.js).

---

## 9. Связь с пунктом №1 плана (строго по шагам)

Wiki **частично** решает проблему перепрыгивания этапов:
- ✅ Лечит «агент забыл где остановились» — SessionStart хук инжектит current_stage.
- ✅ Лечит «правила разбросаны» — все правила в `wiki/concepts/rules/` с индексом.
- ❌ НЕ лечит «агент игнорирует существующие гейты» — это уже дисциплина оркестратора.

**Отдельный PR (не входит в этот spec) — PR-G «Stage Lock»:**
- Усилить промпт `landing-orchestrator`: первая строка «прочитай `<project>/wiki/index.md`, любое действие вне `current_stage` → отказ».
- В `scripts/gate-check.sh` добавить hard-fail при попытке войти в этап N+1 без verified N.
- SessionStart хук дополнительно печатает в консоль: `🔒 STAGE LOCK: вы на 07c, доступны действия только этапа 07c`.

PR-G делаем сразу после PR-F.

---

## 10. Стоимость и производительность

| Операция | Стоимость | Частота |
|---|---|---|
| `compile.py system` | $0.45-0.65 | ~раз в неделю (когда систему меняем) |
| `compile.py project-graph` | $0.10-0.20 | После каждого этапа (~15 раз на проект) |
| `compile.py conversations` (flush + auto-compile) | $0.45-0.65/день | Только в дни активной работы |
| `query.py` | $0.05-0.10 | По мере необходимости |
| `lint.py` structural | $0 | Раз в неделю на cron |
| `lint.py` LLM contradictions | $0.15-0.25 | По кнопке, не на cron |

**Ожидаемая экономия:** 5-10 минут на старте каждой сессии × сейчас примерно 10 сессий в неделю = **1+ час в неделю**, плюс ~95% экономия токенов на «вспоминание контекста» (по словам видео).

**Всё работает на подписке Claude Max** (использует Claude Agent SDK через ту же подписку, отдельный API-ключ не нужен).

---

## 11. Что НЕ входит в этот spec (out of scope)

- Векторные базы / RAG / эмбеддинги — Карпати показал, что для нашего масштаба (десятки агентов, ~20-50 лендингов) индекс по markdown достаточно.
- Шаринг wiki между разными машинами — пока локально. Если понадобится — git push в приватный репо (отдельный PR).
- Автоматическое исправление противоречий, найденных линтером — линтер только сообщает, фиксит человек.
- Интеграция с MCP-сервером для wiki (как у Ar9av/obsidian-wiki) — рассматриваем после PR-F если выяснится, что нужно.

---

## 12. Открытые вопросы для финального ревью

1. **Источники для системного wiki — полный список:** утвердить ли список в 5.1, или добавить ещё (например, `block-library/*/meta.yaml`, `presets/*`)?
2. **Триггер для `compile.py project-graph` после этапа:** хук в `landing-orchestrator` или вызывать вручную через флаг `--auto-wiki` в `/landing-go`?
3. **Где живёт глобальный `landing-system/wiki/` относительно git:** коммитим в репо (тогда команда вместе видит карту, но конфликты при merge) или в `.gitignore` (каждый собирает локально)?
4. **`memory/` в git:** коммитим? Это разговоры из сессий — могут содержать клиентские детали. Скорее `.gitignore` по умолчанию + явное правило.

---

## 13. Артефакты по правилу пользователя (MD + HTML)

Согласно [auto-memory: всегда MD + HTML на русском для каждого артефакта](memory/feedback_always_md_and_html_review.md), на каждом этапе wiki создаёт:
- `wiki/index.md` (агент читает)
- `wiki/preview.html` (Кирилл смотрит глазами — список + поиск + граф связей)

`preview.html` генерируется `compile.py` в конце своего прогона.

---

## 14. Этапы реализации (high-level)

1. **PR-F.1** — портировать coleam00 в `landing-system/scripts/wiki/`, проверить что хуки работают на самой системе (Слой A работает).
2. **PR-F.2** — реализовать `--source-mode=system`, скомпилировать первый системный wiki, проверить что SessionStart хук инжектит индекс.
3. **PR-F.3** — реализовать `--source-mode=project-graph`, добавить в template, прогнать миграцию на `dubai-avto-liza`.
4. **PR-F.4** — `preview.html` рендерер + Obsidian-инструкция в SETUP.md.
5. **PR-F.5** — `lint.py` адаптирован под три слоя.
6. (отдельно) **PR-G** — Stage Lock усиление (см. раздел 9).

Детальный план — отдельный документ через skill `writing-plans`.
