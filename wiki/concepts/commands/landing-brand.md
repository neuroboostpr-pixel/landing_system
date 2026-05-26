---
slug: landing-brand
type: command
name: "/landing-brand — Построить бренд-кит"
stage: "04"
tags: [brand, command, stage-04, brand-kit]
triggers: [landing-brand]
inputs: [04_БРЕНД/extracted/*.yaml]
outputs: [04_БРЕНД/brand-kit.md, 04_БРЕНД/brand-kit.html]
gates: []
pre_reqs: [moodboard-creation, style-decomposition]
related: [brand-architect, brand-kit-build, style-extractor, moodboard-composer, design-system-generator]
sources: ["commands/landing-brand.md"]
updated: 2026-05-26
confidence: {gates: low}
---

# /landing-brand — Построить бренд-кит

## Что делает

Команда запускает агента `brand-architect`, который синтезирует все извлечённые стилевые данные в единый бренд-кит проекта. По итогу формируются два артефакта: полноценный `brand-kit.md` с указанием источника каждого решения и визуальный HTML-превью с образцами палитры, шрифтами и иконками. До получения явного подтверждения пользователя переход к этапу 05 заблокирован.

## Когда вызывается

Пользователь вручную вводит `/landing-brand` внутри папки проекта после того, как `style-extractor` уже сформировал файлы `04_БРЕНД/extracted/*.yaml` (т.е. этап мудборда одобрен). Команда также может быть вызвана оркестратором в рамках `landing-go`.

## Вход → выход

**Вход:** YAML-файлы с извлечёнными стилями в `04_БРЕНД/extracted/`; флаг онбординга `~/.landing-system/setup_complete`; пройденный гейт этапа 03 (референсы).

**Выход:** `04_БРЕНД/brand-kit.md` — канонический бренд-кит с провенанс-комментариями; `04_БРЕНД/brand-kit.html` — визуальный превью для утверждения пользователем. После явного approve выставляется статус этапа 04 в `.landing-state.yaml`.

## Failure modes

- Онбординг не пройден (`setup_complete` отсутствует) — команда останавливается с подсказкой запустить `/landing-onboarding`.
- Гейт этапа 04 не пройден (нет одобрённого мудборда или извлечённых YAML) — выводится ошибка с указанием, какой предыдущий этап не закрыт.
- `04_БРЕНД/extracted/` пуст или содержит битые YAML — `brand-architect` не может синтезировать бренд-кит и завершится с ошибкой парсинга.
- Пользователь не даёт явного approve — hard gate не снимается, этап 05 не начнётся.
- `brand-kit.html` не рендерится корректно (отсутствуют шрифты/иконки) — превью может быть неполным, но `brand-kit.md` остаётся каноничным источником истины.

## Related

- [[brand-architect]] — агент, выполняющий синтез бренд-кита из стилевых данных
- [[brand-kit-build]] — скилл, содержащий логику построения бренд-кита
- [[style-extractor]] — поставляет входные YAML перед запуском этой команды
- [[moodboard-composer]] — предшествующий этап, результаты которого питают style-extractor
- [[design-system-generator]] — следующий этап (05), который потребляет brand-kit.md