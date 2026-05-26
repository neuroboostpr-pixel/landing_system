---
slug: landing-visuals
type: command
name: "/landing-visuals — Генерация визуальных ассетов"
stage: "07d"
tags: [visuals, icons, infographics, codex, image-gen, pr-c]
triggers: [landing-visuals]
inputs:
  - 07b_COMPOSED/composed.html
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - .landing-state.yaml
outputs:
  - 07d_VISUALS/_slots.yaml
  - 07d_VISUALS/icons/
  - 07d_VISUALS/infographics/
  - 07d_VISUALS/.cache/
  - 07d_VISUALS/prompts.yaml
  - 07d_VISUALS/STATE.yaml
  - 07b_COMPOSED/composed.html
gates: []
pre_reqs:
  - landing-compose
  - landing-design
related:
  - visual-curator
  - icon-generator
  - infographic-builder
  - landing-compose
  - landing-go
  - landing-photos
  - visual-generation
sources: ["commands/landing-visuals.md"]
updated: 2026-05-26
---

# /landing-visuals — Генерация визуальных ассетов

## Что делает

Команда запускает генерацию PNG-иконок и инфографики для всех `data-slot` плейсхолдеров в `composed.html`. Ассеты стилизованы под брендинг проекта: цвета берутся из `tokens.json`, контекст — из `market-profile.md` (ниша). Используется кэш по хешу входных параметров, что позволяет экономить вызовы к codex API при повторных прогонах. После генерации `composed.html` перерендерится — плейсхолдеры `[SLOT: …]` и `[INFOGRAPHIC: …]` заменятся на реальные теги `<img>`.

## Когда вызывается

Вызывается вручную командой `/landing-visuals` или автоматически через `/landing-go` на этапе 07d. Необходимые условия: этап 05 (design-system) должен быть в статусе `approved`, а файл `07b_COMPOSED/composed.html` — существовать.

## Вход → выход

**Вход:** `composed.html` со слотами типа `icon` и `infographic`; `tokens.json` с дизайн-токенами; `market-profile.md` с описанием ниши; `.landing-state.yaml` для проверки статуса этапов.

**Выход:** PNG-файлы в `07d_VISUALS/icons/` и `07d_VISUALS/infographics/`; обновлённый `07b_COMPOSED/composed.html` с подставленными `<img>`; лог промптов `prompts.yaml`; кэш `.cache/`.

## Failure modes

- **Этап 05 не утверждён** — команда падает с требованием сначала закрыть `05_ДИЗАЙН-СИСТЕМА/DESIGN.md`; без `tokens.json` нет стилизации.
- **`composed.html` не существует** — блокировка с подсказкой запустить `/landing-compose`.
- **Cache miss + API недоступен** — codex не отвечает, слоты остаются незаполненными; повтор через `--force` не помогает до восстановления API.
- **Слот не найден по `--slot <name>`** — тихий пропуск или ошибка, если `_slots.yaml` устарел и не содержит нужного имени.
- **Инфографика не вписывается в макет** — `compose-blocks.py` подставляет PNG без проверки размеров; визуальные артефакты заметны только в браузере.

## Related

- [[visual-curator]] — агент, оркестрирующий весь процесс генерации
- [[icon-generator]] — субагент для иконок
- [[infographic-builder]] — субагент для инфографики
- [[landing-compose]] — предыдущий этап (07b), создаёт `composed.html`
- [[landing-go]] — рекомендуемый способ запуска через оркестратор
- [[visual-generation]] — концепт всего процесса генерации визуалов