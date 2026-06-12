---
slug: landing-stack
type: command
name: "Планирование стека WordPress (этап 06)"
stage: "06"
tags: [stack, wordpress, plugins, stage-06, design-stack]
triggers: [landing-stack]
inputs: [05_ДИЗАЙН-СИСТЕМА/DESIGN.md]
outputs: [06_СТЕК/design-stack.yaml, 06_СТЕК/component-library-plan.md, 06_СТЕК/effects-plan.md, 06_СТЕК/font-and-color-plan.md]
gates: [design-stack-approved]
pre_reqs: [landing-design, design-system-generator]
related: [stack-planner, landing-build, landing-content, landing-design, wp-builder]
sources: ["commands/landing-stack.md"]
updated: 2026-05-26
---

# Планирование стека WordPress (этап 06)

## Что делает

Команда запускает агента `stack-planner`, который анализирует утверждённую дизайн-систему и формирует технический стек проекта. В результате появляется файл `design-stack.yaml` со списком WordPress-плагинов, JS-библиотек, иконочного набора и CDN-шрифтов. Дополнительно создаются три плана: по компонентной библиотеке, визуальным эффектам и схеме шрифтов/цветов. Перед переходом к следующему этапу обязателен явный approve пользователя.

## Когда вызывается

Запускается вручную командой `/landing-stack` внутри папки проекта. Условие — этап 05 (дизайн-система) завершён и файл `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` утверждён. Перед началом работы команда проверяет прохождение onboarding (`setup-flag.sh`) и гейт предыдущего этапа (`gate-check.sh --stage 06_stack`).

## Вход → выход

**Вход:** `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — утверждённая дизайн-система, сгенерированная `design-system-generator`.

**Выход:**
- `06_СТЕК/design-stack.yaml` — реестр плагинов и библиотек
- `06_СТЕК/component-library-plan.md` — план компонентной библиотеки
- `06_СТЕК/effects-plan.md` — план визуальных эффектов
- `06_СТЕК/font-and-color-plan.md` — план шрифтов и цветов

## Чем закрывается этап (gates)

- design-stack-approved — пользователь явно подтверждает `design-stack.yaml` перед переходом к этапу 07; гейт проставляется через `gate-check.sh --stage 06_stack --project <project> --approve`

## Failure modes

- Onboarding не пройден — `setup-flag.sh` возвращает exit 1, команда останавливается с подсказкой запустить `/landing-onboarding`.
- Этап 05 не закрыт — `gate-check.sh` возвращает ошибку о незавершённом предыдущем этапе, выполнение прекращается.
- `DESIGN.md` отсутствует или не утверждён — `stack-planner` не находит входных данных и не может сформировать стек.
- Пользователь не даёт approve — HARD GATE не позволяет перейти к этапу 07, проект «зависает» на 06.
- `design-stack.yaml` содержит несовместимые плагины — конфликты версий или Pro-зависимости проявляются уже на этапе 08 при сборке темы.

## Related

- [[stack-planner]] — агент, непосредственно формирующий стек
- [[landing-design]] — предыдущая команда, должна быть выполнена и утверждена
- [[design-system-generator]] — генерирует DESIGN.md, являющийся входом для этапа 06
- [[landing-build]] — следующий этап, потребляет `design-stack.yaml` при сборке темы
- [[landing-content]] — параллельный этап 07, также идёт после утверждения стека
- [[wp-builder]] — использует результаты стека при генерации WordPress-кода