---
slug: landing-design
type: command
name: "Генерация дизайн-системы (этап 05)"
stage: "05"
tags: [design, tokens, stage-05, design-system]
triggers: [/landing-design]
inputs: [04_БРЕНД/brand-kit.md]
outputs:
  - 05_ДИЗАЙН-СИСТЕМА/DESIGN.md
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - 05_ДИЗАЙН-СИСТЕМА/design-preview.html
  - 05_ДИЗАЙН-СИСТЕМА/scenes.md
gates: [05_design]
pre_reqs: [brand-kit-build, landing-onboarding]
related:
  - design-system-generator
  - design-tokens-generation
  - scene-director
  - brand-architect
  - landing-orchestrator
sources: ["commands/landing-design.md"]
updated: 2026-05-26
confidence: {gates: low}
---

# Генерация дизайн-системы (этап 05)

## Что делает

Команда запускает генерацию полной дизайн-системы проекта на основе утверждённого `brand-kit.md`. Вызывает агента `design-system-generator`, затем скрипты `build-tokens.py` и `render-preview.py`, которые производят DESIGN.md с YAML-фронтматтером, машиночитаемый `tokens.json` и живой HTML-превью компонентов. При флаге `--cinematic` дополнительно вызывается агент `scene-director`, создающий грамматику кинематографических сцен (`scenes.md`).

## Когда вызывается

Вызывается пользователем вручную командой `/landing-design` после того, как `brand-architect` завершил этап 04 и `brand-kit.md` утверждён. До запуска автоматически проверяет завершённость онбординга и прохождение гейта этапа 05.

## Вход → выход

**Вход:** `04_БРЕНД/brand-kit.md` — утверждённый бренд-кит, сформированный агентом `brand-architect` на этапе 04.

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — токен-источник правды с YAML-фронтматтером
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые дизайн-токены
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — живой превью компонентов
- `05_ДИЗАЙН-СИСТЕМА/scenes.md` — кинограмматика сцен (только с флагом `--cinematic`)

## Чем закрывается этап (gates)

- `05_design` — явное одобрение превью пользователем; скрипт `gate-check.sh --stage 05_design --approve` фиксирует переход; без этого оркестратор не идёт на этап 06.

## Failure modes

- Онбординг не пройден (`setup-flag.sh` возвращает exit 1) — команда останавливается с инструкцией запустить `/landing-onboarding`.
- Этап 04 не закрыт (`gate-check.sh` возвращает exit 1) — команда сообщает, какой предыдущий этап не завершён, и не продолжает.
- `brand-kit.md` отсутствует или повреждён — `build-tokens.py` упадёт с ошибкой парсинга; нужно перепроверить выход `brand-architect`.
- `render-preview.py` генерирует пустой или битый HTML — обычно из-за невалидных цветовых токенов в `brand-kit.md` (неправильный HEX).
- Пользователь не даёт явного подтверждения — HARD GATE не закрывается, этап 06 не стартует; `gate-check.sh --approve` не вызывается.

## Related

- [[design-system-generator]] — агент, который выполняет основную логику генерации системы
- [[design-tokens-generation]] — скилл со скриптами `build-tokens.py` и `render-preview.py`
- [[scene-director]] — агент кинограмматики, вызывается при `--cinematic`
- [[brand-architect]] — агент этапа 04, чей выход является входом для этой команды
- [[landing-orchestrator]] — диспатчит эту команду в контексте полного пайплайна