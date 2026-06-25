---
slug: style-extractor
type: agent
name: "Style Extractor — Извлечение стиля из референсов"
stage: "04"
tags: [brand, style, palette, fonts, extraction, stage-04]
triggers: [landing-brand]
inputs: [03_РЕФЕРЕНСЫ/index.yaml, 03-referensy]
outputs: [04_БРЕНД/extracted/palette.yaml, 04_БРЕНД/extracted/fonts.yaml, 04_БРЕНД/extracted/icons.yaml, 04_БРЕНД/extracted/grid.md, 04_БРЕНД/extracted/motion.md]
gates: []
pre_reqs: [03-referensy, landing-moodboard]
related: [brand-architect, style-decomposition, 04-brend, landing-brand, references-collection, visual-curator]
sources: ["agents/style-extractor.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Style Extractor — Извлечение стиля из референсов

## Что делает

Агент обрабатывает утверждённые визуальные референсы (изображения и URL) и извлекает из них конкретную, готовую к использованию в коде стилевую систему. Запускает цепочку Python-скриптов: извлечение палитры цветов, идентификацию шрифтов, подбор иконочного набора, агрегацию через orchestrate.py. Результатом являются ровно 5 структурированных файлов в папке `04_БРЕНД/extracted/`, на которые опирается `brand-architect` при сборке brand-kit.

## Когда вызывается

Вызывается в рамках этапа `04_brand` после того, как мудборд утверждён пользователем. Агент не запускается, если предшественники (этапы 03 и ниже) не закрыты — hook `enforce_stage_gate.py` физически блокирует запись файлов при незакрытых шлюзах.

## Вход → выход

**Вход:** `03_РЕФЕРЕНСЫ/index.yaml` с записями `status: approved`; изображения референсов; URL сайтов-ориентиров; `.landing-state.yaml` с `current_stage == 04_brand`.

**Выход:** пять файлов в `04_БРЕНД/extracted/`:
- `palette.yaml` — извлечённая цветовая палитра;
- `fonts.yaml` — кандидаты шрифтов;
- `icons.yaml` — выбранный иконочный набор;
- `grid.md` — сеточная система (placeholder при недоступных референсах);
- `motion.md` — правила анимации (placeholder при недоступных референсах).

## Failure modes

- **Заблокированные источники** (Behance / Dribbble / Instagram): скрипты не могут считать цвета — агент создаёт пустые placeholder-файлы и берёт палитру из `03b_КОНЦЕПТ/visual-concept.yaml`; при отсутствии этого файла — тихий некорректный результат.
- **Неутверждённые референсы**: если ни один ref не имеет `status: approved` в index.yaml, pipeline получает пустые данные и brand-kit строится без реальных цветов.
- **Отсутствие хотя бы одного из 5 файлов**: hard gate не закрывается; `gate-check.sh` вернёт exit != 0 и следующий этап не запустится.
- **Ошибка orchestrate.py**: при падении агрегирующего скрипта частично созданные файлы остаются, но могут содержать невалидный YAML — brand-architect упадёт при чтении.
- **Запуск не из stage 04**: если `.landing-state.yaml` показывает другой `current_stage`, агент обязан остановиться, но при ручном вызове это условие может быть пропущено.

## Related

- [[brand-architect]] — следующий агент в цепочке; читает все 5 файлов для сборки brand-kit
- [[style-decomposition]] — skill, содержащий Python-скрипты extract-palette / identify-fonts / match-icons / orchestrate
- [[03-referensy]] — этап-источник: утверждённые референсы, без которых нечего извлекать
- [[04-brend]] — этап, которому принадлежит агент; закрывается после approve всех 5 файлов
- [[landing-brand]] — skill-команда, диспатчащая этот агент
- [[references-collection]] — skill сбора и каталогизации референсов (pre-req)
- [[visual-curator]] — смежный агент ручной оценки визуала перед запуском extractor'а