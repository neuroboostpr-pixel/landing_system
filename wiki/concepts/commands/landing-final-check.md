---
slug: landing-final-check
type: command
name: "Финальная проверка перед деплоем"
stage: "09"
tags: [qa, verify, pre-deploy, bundle]
triggers: [landing-final-check]
inputs: []
outputs: [10-qa]
gates: []
pre_reqs: [07b-composed, 07c-photos, 07d-visuals]
related: [landing-deploy, landing-qa, premium-07b-checklist, visual-qa, stage-execution-protocol]
sources: ["commands/landing-final-check.md"]
updated: 2026-06-22
confidence: {stage: low, pre_reqs: low}
---

# Финальная проверка перед деплоем

## Что делает

Запускает единый bundle всех обязательных verify-скриптов системы непосредственно перед деплоем лендинга. Команда последовательно прогоняет проверки: синхронность wiki, premium-чеклист composed.html (13 фич), сохранность текста из прототипа, корректность photo pipeline (фото в processed/, отсутствие placeholders, hero без обрезки), целостность identity (manifest без violations) и опциональный visual QA. Формирует детальный отчёт и возвращает единый exit-код: 0 если всё обязательное прошло, 1 если хотя бы одна проверка провалилась.

## Когда вызывается

Вызывается вручную командой `/landing-final-check <project>` после того как все этапы производства (composed, photos, visuals) завершены и одобрены, но до запуска `/landing-deploy`. Это финальный контрольный рубеж перед отправкой на Бегет.

## Вход → выход

**Вход:** слаг проекта; наличие `07b_COMPOSED/composed.html`, артефактов photo pipeline, визуального контента и prototype.yaml в папке проекта.

**Выход:** краткая сводка в stdout + файл `<project>/10_QA/final-check-report.md` с детальными результатами по каждой проверке. Exit 0 = всё готово к деплою, exit 1 = есть блокирующие проблемы.

## Failure modes

- **Composed не проходит premium-чеклист** — отсутствуют обязательные фичи (токены, clamp, motion, head документа); нужно вернуться в `/landing-compose`.
- **Текст прототипа не сохранён** — `verify-content-preserved.sh` находит выдуманный или усечённый контент; источник — неточный парсинг в `/landing-prototype`.
- **Photo pipeline неполный** — есть незаменённые placeholders или фото не попали в `processed/`; нужно перезапустить `/landing-photos`.
- **Identity violations** — manifest фиксирует несогласованные изменения клиентских материалов (лого, фото команды); требует ручной проверки.
- **Wiki out of sync** — хук не установлен или упал; исправляется через `bash scripts/install-git-hooks.sh` и пересборкой wiki.

## Related

- [[landing-deploy]] — следующий шаг после успешного прохождения финальной проверки
- [[landing-qa]] — отдельный QA-этап; финальная проверка — его авто-часть
- [[premium-07b-checklist]] — перечень 13 фич, проверяемых в composed
- [[visual-qa]] — опциональная составляющая bundle
- [[stage-execution-protocol]] — обязательный протокол перед любым этапом