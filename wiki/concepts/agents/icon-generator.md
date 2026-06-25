---
slug: icon-generator
type: agent
name: "Генератор иконок"
stage: "07e"
tags: [visual-generation, icons, codex, cache, helper-agent]
triggers: []
inputs: [07d-visuals]
outputs: [07d-visuals]
gates: []
pre_reqs: [05-dizayn-sistema, 07b-composed]
related: [visual-curator, visual-generation, visual-qa, 07d-visuals, infographic-builder]
sources: ["agents/icon-generator.md"]
updated: 2026-06-19
confidence: {triggers: low, stage: low}
---

# Генератор иконок

## Что делает

Вспомогательный агент, генерирующий один PNG-файл иконки для одного визуального слота через codex image_gen. Используется родительским агентом `visual-curator` в рамках этапа 07d/07e. Перед генерацией проверяет хеш-кэш — если иконка с такими параметрами уже создавалась, просто копирует её, не обращаясь к codex. При успешной генерации сохраняет результат в кэш для будущих прогонов. Строго следует стандарту image-pipeline: анализ места → спецификация → генерация на вырезаемом фоне → rembg → вставка с цветовым оверлеем.

## Когда вызывается

Агент не вызывается напрямую пользователем — его диспатчит `visual-curator` при обработке каждого иконочного слота (`[SLOT: feature-N-icon]`) в `composed.html`. Требует одобрённого этапа 05 (дизайн-система) и существующего `composed.html` (этап 07b).

## Вход → выход

**Вход:** абсолютный путь к папке проекта, имя слота (например, `feature-1-icon`), опциональный hint (например, `shield`); брендовый акцент и ниша берутся из `tokens.json` и `market-profile.md`.

**Выход:** `<project>/07d_VISUALS/icons/<slot_name>.png` — готовый PNG-файл иконки; побочно — запись в хеш-кэш `.cache/<hash>.png`.

## Чем закрывается этап (gates)

Агент не владеет этапом и не закрывает gates самостоятельно — это задача родительского `visual-curator`.

## Failure modes

- **codex недоступен или упал после retry** — откат к SVG-плейсхолдеру через `svg-placeholder.py` (из PR-B).
- **Chroma-key бахрома по краям** — повтор с `--edge-contract 1` или альтернативным chroma `#ff00ff`.
- **Кэш повреждён или файл < 1 KB** — кэш-промах, запускается повторная генерация.
- **hint не передан** — используется generic-промпт из `icons.csv` waterfall, качество иконки может быть ниже ожидаемого.
- **Прямой вызов агента** — агент не знает контекст этапа и не имеет собственного stage-gate; результат непредсказуем без parent `visual-curator`.

## Related

- [[visual-curator]] — родительский агент, диспатчит icon-generator для каждого слота
- [[visual-generation]] — скилл с bash-скриптами кодогенерации (codex-generate-icon.sh, visual-cache.py)
- [[infographic-builder]] — аналогичный helper для инфографики
- [[07d-visuals]] — этап, в рамках которого работает агент
- [[visual-qa]] — следующий шаг после генерации: проверка качества визуала