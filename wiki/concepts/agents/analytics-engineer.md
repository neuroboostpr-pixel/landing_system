---
slug: analytics-engineer
type: agent
name: "Инженер аналитики"
stage: "11"
tags: [analytics, yandex-metrika, utm, stage-11, wordpress]
triggers: []
inputs:
  - .env
  - 08_КОД/wp-theme/functions.php
outputs:
  - 08_КОД/wp-theme/functions.php
  - 11_АНАЛИТИКА/metrika-config.md
  - 11_АНАЛИТИКА/goals-and-events.json
  - 11_АНАЛИТИКА/utm-templates.md
gates: [metrika_config_approved]
pre_reqs: [integrations-engineer]
related:
  - stage-execution-protocol
  - landing-build
  - landing-deploy
sources: ["agents/analytics-engineer.md"]
updated: 2026-05-26
confidence: {triggers: low, gates: low}
---

# Инженер аналитики

## Что делает

Подключает Яндекс.Метрику к WordPress-лендингу и формирует аналитическую документацию. Читает `YM_COUNTER_ID` из `.env`, вставляет PHP-функцию счётчика в `functions.php` через хук `wp_head`, определяет цели по секциям лендинга (клики по CTA, отправка формы). Параллельно создаёт три артефакта в папке `11_АНАЛИТИКА/`: конфиг счётчика, JSON с целями для Метрики и шаблоны UTM-меток для Яндекс.Директа. Завершает работу твёрдым гейтом — показывает `metrika-config.md` и ждёт явного утверждения.

## Когда вызывается

Запускается на этапе 11 (`current_stage == 11_analytics`) после завершения `integrations-engineer`. Перед любым Write/Edit действием агент обязан убедиться, что `.landing-state.yaml` указывает именно этот этап, и пройти `gate-check.sh --stage 11_analytics`. Физически блокируется хуком `enforce_stage_gate.py`, если предшественники не закрыты.

## Вход → выход

**Вход:** `.env` с заполненным `YM_COUNTER_ID` (8-значный ID счётчика); `08_КОД/wp-theme/functions.php` с placeholder-комментарием `// [YM_COUNTER]`; закрытый этап `integrations-engineer`.

**Выход:** `functions.php` дополнен кодом счётчика Метрики; `11_АНАЛИТИКА/metrika-config.md` — описание счётчика и целей; `11_АНАЛИТИКА/goals-and-events.json` — машиночитаемый список событий; `11_АНАЛИТИКА/utm-templates.md` — шаблоны UTM-меток.

## Чем закрывается этап (gates)

- metrika_config_approved — пользователь явно утвердил `metrika-config.md` с ID счётчика и списком целей

## Failure modes

- `YM_COUNTER_ID` отсутствует в `.env` или невалиден — функция вернёт пустоту, счётчик не загрузится, но PHP-ошибки не будет; нужен ручной контроль `.env`
- Placeholder `// [YM_COUNTER]` не найден в `functions.php` — код Метрики вставится в неверное место или дублируется при повторном запуске
- `current_stage` в `.landing-state.yaml` ≠ `11_analytics` — агент обязан остановиться, но при сбое проверки gate-check этап может начаться преждевременно
- Цели определяются автоматически по структуре лендинга; если в composed.html нет явных CTA-атрибутов, список целей окажется пустым или неточным
- Твёрдый гейт пропущен при автоматическом прогоне оркестратора — `metrika-config.md` уйдёт на деплой без ревью маркетолога

## Related

- [[stage-execution-protocol]] — обязательный протокол для всех этапов, включая gate-check и TodoWrite
- [[landing-build]] — этап 08, создаёт `functions.php`, в который analytics-engineer вставляет код счётчика
- [[landing-deploy]] — следующий этап после закрытия 11; деплоит тему с уже подключённой Метрикой