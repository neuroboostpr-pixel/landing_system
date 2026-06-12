# Трекер Доработки Wiki

> **Для agentic workers:** этот файл является **единым источником правды** по доработке wiki. Если по задаче в этом файле уже есть свежие `Evidence`, **не нужно заново прогонять полный аудит**.

**Дата:** `2026-05-26`  
**Назначение:** разложить wiki-задачи на максимально мелкие шаги для **параллельной работы в git**, при этом сохранить **исходную терминологию и смысл code review от 2026-05-23**, чтобы задача не превратилась в новую из-за пересказа.

**Какие findings покрывает этот трекер:**
- `SUMMARY.md` finding `#4` / `phase-5-correctness.md` `#1`
  Цитата из summary: **"Wiki-скрипты hard-coded на `~/Lendings/` — на Windows у пользователя `d:/AI_TEAMS/Lendings/`, не работает"**
- `SUMMARY.md` finding `#12` / `phase-2-token-hotspots.md` `#3`
  Цитата из summary: **"wiki/ (480 файлов) построена как навигационный граф, но никто не инструктирован по нему ходить"**

**Что НЕ входит в этот трекер:**
- CRM adapter dispatch
- REST/XSS/security-задачи вне wiki
- общий bash-hardening, кроме случаев, когда это напрямую нужно для wiki-flow

---

## Правила Ведения Статусов

Использовать только эти статусы:

| Статус | Что значит |
|---|---|
| `todo` | Не начато |
| `in_progress` | Кто-то уже взял и делает |
| `blocked` | Нельзя продолжать без решения или другого merge |
| `done` | Сделано и проверено |
| `wontfix` | Осознанно не делаем |

Если задача переведена в `done`, в ней **обязательно** должны быть заполнены все поля:

| Поле | Что писать |
|---|---|
| `Owner` | кто делал |
| `Date` | дата `YYYY-MM-DD` |
| `Branch/PR` | ветка или PR |
| `Evidence` | точная команда, grep, тест, diff или ссылка на файл |
| `Findings closed` | какие finding ID этим закрыты |
| `Notes` | кратко: что изменилось и что не нужно перепроверять следующему человеку |

Если работа сделана частично, **не ставить `done`**. Оставлять `in_progress` и явно писать, что осталось.

---

## Зафиксированная Стартовая Картина

Это согласованное состояние **на 2026-05-26**, чтобы не делать повторный мини-аудит с нуля.

| Пункт | Состояние | Основание |
|---|---|---|
| Единый path-layer через `LANDINGS_ROOT` в Python wiki runtime | `done` | уже есть в `scripts/lib/paths.py`, `scripts/wiki/compile.py`, `scripts/wiki/flush.py`, `scripts/wiki/hooks/session_start.py` |
| Bash-helper для `LANDINGS_ROOT` | `done` | уже есть в `scripts/lib/paths.sh` |
| Формулировка review "Wiki-скрипты hard-coded на `~/Lendings/`" | `stale` | audit старше текущего состояния кода |
| Человеческие docs всё ещё учат старой модели `~/Lendings/<slug>/` | `open` | много живых файлов всё ещё используют старую формулировку |
| Сгенерированные wiki-артефакты всё ещё содержат старый путь | `open` | `wiki/preview.html` и часть `wiki/concepts/*` пока отстают |
| Явная инструкция агенту "начни с `wiki/index.md`" | `open` | в `landing-orchestrator` такой явной инструкции пока нет |
| Отдельные focused tests для `scripts/lib/paths.py` | `open` | отдельного test-файла на path-resolution не найдено |

---

## Принцип Параллельной Работы

Работа разбита на независимые потоки так, чтобы вы могли делать её параллельно с другим сотрудником и не мешать друг другу в git.

| Поток | Owner | Что входит | С чем можно делать параллельно |
|---|---|---|---|
| Поток A | unassigned | runtime + tests для path-resolution и hooks | Поток B |
| Поток B | unassigned | правка source docs, commands, agents с `~/Lendings` на `LANDINGS_ROOT`-модель | Поток A |
| Поток C | unassigned | подключение wiki в агентский flow / orchestrator entry | после стабилизации A, частично параллельно с B |
| Поток D | unassigned | регенерация derived wiki-артефактов и синхронизация статусов аудита | после merge B и C |

Рекомендуемые имена веток:

| Поток | Ветка |
|---|---|
| Поток A | `fix/wiki-path-tests` |
| Поток B | `docs/wiki-landings-root-sync` |
| Поток C | `feat/wiki-orchestrator-entry` |
| Поток D | `chore/wiki-regenerate-sync` |

---

## Порядок Merge

1. Поток A
2. Поток B
3. Поток C
4. Поток D

Почему так:
- Поток A закрепляет базу: path-layer и test coverage.
- Поток B обновляет source truth в docs.
- Поток C меняет реальное поведение agent flow.
- Поток D должен идти после этого, чтобы регенерировать wiki уже из актуальных источников.

---

## Поток A — Runtime И Tests

### Задача A1 — Добавить focused tests для `scripts/lib/paths.py`

**Статус:** `todo`  
**Owner:**  
**Файлы:**  
создать `tests/wiki/test_paths.py` или `tests/helpers/test_paths.py`  
использовать `scripts/lib/paths.py`

- [ ] Добавить тест на `LANDINGS_ROOT` через env override.
- [ ] Добавить тест на fallback `REPO_ROOT.parent / "Lendings"`.
- [ ] Добавить тест на fallback `Path.home() / "Lendings"`.
- [ ] Добавить тест на `project_dir("slug")`.
- [ ] Добавить тест на понятное сообщение `require_landings_root()`.
- [ ] Сделать так, чтобы тесты не зависели от реальной машины.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача A2 — Расширить hook tests под кастомный `LANDINGS_ROOT`

**Статус:** `todo`  
**Owner:**  
**Файлы:**  
`tests/wiki/test_hooks.py`

- [ ] Добавить сценарий, где `cwd` находится внутри fake `LANDINGS_ROOT/<slug>/`.
- [ ] Проверить, что появляется `project_wiki_index`.
- [ ] Проверить, что появляется recent memory block при наличии `memory/daily/*.md`.
- [ ] Сначала прогнать только hook-тесты, потом общий wiki test subset.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача A3 — Добавить smoke coverage для `compile.py --source-mode=project-graph`

**Статус:** `todo`  
**Owner:**  
**Файлы:**  
существующие тесты в `tests/wiki/`

- [ ] Добавить или обновить тест, подтверждающий, что `project-graph` mode резолвится через shared path helper, а не через `Path.home()`.
- [ ] Добавить или обновить тест для `conversations` mode по тому же принципу.
- [ ] Не раздувать задачу: здесь нужна только проверка path-resolution, а не качества всего wiki output.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

---

## Поток B — Source Docs Cleanup

### Задача B1 — Обновить `CLAUDE.md`, где он всё ещё учит модели `~/Lendings/<slug>/`

**Статус:** `todo`  
**Owner:**  
**Файлы:**  
`CLAUDE.md`

- [ ] Найти живые инструкции, где `~/Lendings/<slug>/` подаётся как единственный канонический путь.
- [ ] Переписать на модель `LANDINGS_ROOT/<slug>/`.
- [ ] Если нужен пример, можно упоминать `~/Lendings` только как legacy/default fallback, а не как единственную правду.
- [ ] Не переписывать в этой задаче unrelated product claims.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача B2 — Обновить command docs с устаревшим путём

**Статус:** `todo`  
**Owner:**  
**Файлы:**  
`commands/landing-new.md`  
`commands/landing-start.md`

- [ ] Заменить формулировки вида "default to `~/Lendings/<slug>/`" на `LANDINGS_ROOT/<slug>/`.
- [ ] Сохранить пояснение про absolute/relative path там, где оно уже есть.
- [ ] Коротко добавить path resolution order:
  `LANDINGS_ROOT env` -> sibling `../Lendings` -> `~/Lendings`.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача B3 — Обновить agent docs с устаревшим путём

**Статус:** `todo`  
**Owner:**  
**Файлы:**  
`agents/landing-onboarding-wizard.md`  
другие agent-файлы, которые покажет grep

- [ ] Заменить user-facing формулировки с `~/Lendings/<slug>/` на `LANDINGS_ROOT/<slug>/`.
- [ ] Не менять здесь agent logic, только синхронизировать wording.
- [ ] Если в тексте есть пример "создаю папку: ~/Lendings/..." — переписать без потери исходного смысла.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача B4 — Обновить setup/docs-страницы, которые всё ещё описывают старую каноническую модель

**Статус:** `todo`  
**Owner:**  
**Файлы:**  
`docs/SETUP.md`  
`scripts/wiki/README.md`

- [ ] Обновить примеры для `project-graph` и `conversations`.
- [ ] Добавить короткое объяснение path resolution order:
  `LANDINGS_ROOT env` -> sibling `../Lendings` -> `~/Lendings`.
- [ ] Сделать wording дружелюбным для Windows-сценария.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача B5 — Отдельно решить, что делать с историческими specs/plans, где старый путь уже зашит

**Статус:** `todo`  
**Owner:**  
**Файлы:**  
`docs/superpowers/specs/*`  
`docs/superpowers/plans/*`

- [ ] Зафиксировать решение в `Notes`:
  `оставляем как historical`, `аннотируем`, или `массово правим`.
- [ ] Не переписывать исторические design/plan docs без необходимости.
- [ ] Если решение — оставить как historical, явно написать это, чтобы следующий человек не считал это незакрытым runtime-багом.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача B6 — После source-doc cleanup зафиксировать остаточный grep-хвост

**Статус:** `todo`  
**Owner:**  
**Зависит от:** B1, B2, B3, B4, B5

- [ ] Прогнать focused grep по **живым source docs**.
- [ ] Оставшиеся вхождения `~/Lendings` классифицировать как:
  `historical`, `generated`, `needs fix`.
- [ ] Список остатка вставить в `Notes`, чтобы второй человек не повторял этот grep заново.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

---

## Поток C — Подключение Wiki В Agent Flow

### Задача C1 — Зафиксировать минимальный runtime contract для wiki

**Статус:** `todo`  
**Owner:**  
**Файлы:**  
этот трекер  
`agents/landing-orchestrator.md`

- [ ] Зафиксировать, какой именно минимум считаем закрытием finding `#12`.
- [ ] Рекомендуемая формулировка без пересказа смысла review:
  оркестратор должен **"начинать с `wiki/index.md`"**, а не только писать wiki.
- [ ] Если команда хочет другой контракт, записать его здесь дословно, до начала правок.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача C2 — Добавить явную wiki-first инструкцию в `landing-orchestrator`

**Статус:** `todo`  
**Owner:**  
**Зависит от:** C1  
**Файлы:**  
`agents/landing-orchestrator.md`

- [ ] Добавить короткую и явную инструкцию, что orchestrator **сначала читает `<project>/wiki/index.md`**, если он есть.
- [ ] Оставить явный fallback на raw sources, если wiki отсутствует или неактуальна.
- [ ] Не превращать эту задачу в большой rewrite orchestrator prompt.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача C3 — Синхронизировать entry/help wording с новой ролью wiki

**Статус:** `todo`  
**Owner:**  
**Файлы:**  
подходящие entry/help docs, найденные grep

- [ ] Добавить там, где уместно, фразу, что wiki auto-generated и используется как навигационный/context layer.
- [ ] Не обещать поведение, которого ещё нет.
- [ ] Wording должен совпадать с тем, что реально добавлено в C2.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача C4 — Добавить минимальную verification для wiki-first поведения

**Статус:** `todo`  
**Owner:**  
**Зависит от:** C2

- [ ] Если уже есть doc/prompt-level tests — расширить их минимально.
- [ ] Если нет, не придумывать большой harness: достаточно manual verification + exact evidence.
- [ ] В `Evidence` должно быть видно, что finding из review закрывается именно по исходной формулировке:
  **"ни один агент не инструктирован по нему ходить"**.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача C5 — Обновить статус finding `#12` в этом трекере

**Статус:** `todo`  
**Owner:**  
**Зависит от:** C1, C2, C3, C4

- [ ] Обновить `Матрица Статусов Аудита`.
- [ ] Поставить finding `#12` как `open`, `partially_closed` или `closed`.
- [ ] Если не `closed`, прямо написать, что ещё отсутствует.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

---

## Поток D — Generated Artifacts И Синхронизация С Аудитом

### Задача D1 — Перегенерировать wiki-derived артефакты после merge source truth

**Статус:** `todo`  
**Owner:**  
**Зависит от:** merge Потока B  
**Файлы:**  
артефакты в `wiki/`

- [ ] Пересобрать wiki нормальным project/system compiler flow.
- [ ] Зафиксировать точную команду в `Evidence`.
- [ ] Проверить, что regenerated artifacts уже не учат старой активной модели пути там, где source docs были исправлены.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача D2 — Проверить хвосты `~/Lendings` в `wiki/preview.html` и generated concepts

**Статус:** `todo`  
**Owner:**  
**Зависит от:** D1

- [ ] Прогнать grep по `wiki/preview.html`.
- [ ] Если остались только historical fragments — явно так и записать.
- [ ] Если остались живые generated pages, которые всё ещё реплицируют stale source truth, не прятать это: зафиксировать как незакрытый хвост.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача D3 — Обновить локальную матрицу статусов аудита без повторного полного review

**Статус:** `todo`  
**Owner:**  
**Зависит от:** A1, A2, A3, C5, D1, D2

- [ ] Обновить статусы finding `#4` и `#12` в `Матрица Статусов Аудита`.
- [ ] Добавить короткое пояснение, почему **full re-audit не требуется**.
- [ ] Исторический `docs/code-review/SUMMARY.md` не переписывать, если команда специально этого не хочет.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

### Задача D4 — Финальный residue-scan и handoff

**Статус:** `todo`  
**Owner:**  
**Зависит от:** все релевантные задачи выше

- [ ] Прогнать финальный focused grep по активным путям:
  `scripts`, `agents`, `commands`, `docs/SETUP.md`, `CLAUDE.md`, `scripts/wiki/README.md`.
- [ ] Остатки классифицировать как:
  `acceptable historical`, `generated`, `must-fix later`.
- [ ] Добавить handoff note для следующего человека, чтобы он не тратил время на повторную разведку.

**Запись после завершения:**  
Owner:  
Date:  
Branch/PR:  
Evidence:  
Findings closed:  
Notes:  

---

## Матрица Статусов Аудита

Эта таблица нужна, чтобы **не гонять повторно весь code review**.

| Finding | Как было в review | Текущее состояние по этому трекеру | На чём основано | Owner |
|---|---|---|---|---|
| `#4` — **"Wiki-скрипты hard-coded на `~/Lendings/`"** | `open` в отчёте от `2026-05-23` | `partially_closed` | на `2026-05-26` вручную подтвержден shared `LANDINGS_ROOT` runtime; docs/tests/generated artefacts ещё не доведены | |
| `#12` — **"wiki/ построена как навигационный граф, но никто не инструктирован по нему ходить"** | `open` | `open` | явной инструкции orchestrator "начни с `wiki/index.md`" пока нет | |

Правила обновления этой таблицы:
- `partially_closed` = часть работы уже реально сделана, но docs/tests/runtime contract ещё не дотянуты.
- `closed` = есть правка + проверка + evidence в соответствующей задаче.
- Нельзя менять статус в таблице, не заполнив `Done record` у связанной задачи.

---

## Команды Для Evidence

Использовать как быстрые команды-подтверждения и вставлять **точный вывод/суть вывода** в `Evidence`.

```powershell
rg -n -F "~/Lendings" CLAUDE.md commands agents docs/SETUP.md scripts/wiki/README.md
rg -n -F "LANDINGS_ROOT" scripts scripts/wiki tests docs CLAUDE.md
pytest tests/wiki -q
pytest tests/wiki/test_hooks.py -q
```

Если использована другая команда, записать именно её, а не пересказ.

---

## Шаблон Записи О Завершении

Копировать в задачу после завершения:

```md
Owner: <имя>
Date: 2026-05-26
Branch/PR: <ветка или PR>
Evidence: <точная команда / grep / test / file link>
Findings closed: <например, #4 partial>
Notes: <что изменено, что осталось, что следующему человеку не нужно проверять повторно>
```

---

## Критерии Завершения Этого Трекера

Считать трекер закрытым, когда одновременно выполнено всё:

- finding `#4` закрыт хотя бы до уровня `closed` для активного runtime и source docs;
- finding `#12` закрыт хотя бы до уровня `partially_closed` с явной orchestrator/wiki инструкцией;
- живые docs больше не подают `~/Lendings` как единственную каноническую модель;
- wiki-derived артефакты перегенерированы после правок source truth;
- по заполненным `Evidence` следующий человек действительно может **не запускать повторный аудит**, а продолжить работу от текущей точки.
