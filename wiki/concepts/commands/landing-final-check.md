---
slug: landing-final-check
type: command
name: "Финальная проверка лендинга"
stage: "10"
tags: [qa, verify, bundle, pre-deploy, final-check]
triggers: [landing-final-check]
inputs: []
outputs: ["<project>/10_QA/final-check-report.md"]
gates: []
pre_reqs: [block-composer, photo-curator, visual-generation, wp-cli-deployer]
related: [qa-auditor, visual-qa, seo-tech-audit, wp-cli-deployer, photo-curator]
sources: ["commands/landing-final-check.md"]
updated: 2026-05-26
confidence: {stage: low, pre_reqs: low}
---

# Финальная проверка лендинга

## Что делает

`/landing-final-check` — единый пакет авто-проверок, который запускается перед деплоем и агрегирует результаты всех verify-скриптов системы. Проверяет, что composed.html содержит все 13 premium-фич, текст прототипа сохранён, фото прошли обработку без placeholders, hero-блок не обрезает изображения, а в identity-манифесте нет нарушений. Опционально проверяет синхронность wiki и прогоняет visual QA. На выходе — единый отчёт с агрегированным статусом pass/fail.

## Когда вызывается

Вызывается вручную командой `/landing-final-check <project>` после того, как завершены этапы сборки (08), фото-пайплайна (07c), генерации визуалов (07d) и compose (07b) — непосредственно перед деплоем (09). Является финальным гейтом качества: деплой не рекомендуется, пока хотя бы одна обязательная проверка возвращает fail.

## Вход → выход

**Вход:** slug или путь к проекту с завершёнными этапами 07b–08; наличие `composed.html`, `processed/`-фото, `identity-manifest`, опционально собранная wiki и visual QA артефакты.

**Выход:** краткая сводка в stdout по каждой проверке; детальный файл `<project>/10_QA/final-check-report.md`; exit-код 0 если все обязательные проверки прошли, exit-код 1 если хотя бы одна упала.

## Failure modes

- **Composed premium fail** — одна или несколько из 13 обязательных premium-фич отсутствуют в `composed.html`; команда не закроется с exit 0, пока `block-composer` не доработает файл.
- **Photo placeholders остались** — фото не прошли через `processed/` или слоты не были заполнены; photo-pipeline нужно перепрогнать.
- **Hero crop violation** — hero-изображение выставлено с обрезкой; нарушает требование no-crop для главного блока.
- **Identity violations в манифесте** — AI-лица или перекрашенные клиентские фото попали в `identity-manifest` как violations; требует ручного удаления или замены ассетов.
- **Wiki out-of-sync** — опциональная проверка сигнализирует, что исходники изменились без пересборки wiki; не блокирует деплой, но фиксируется в отчёте.

## Related

- [[qa-auditor]] — агент, который исполняет отдельные проверки качества
- [[visual-qa]] — опциональная проверка визуальных артефактов, вызывается внутри бандла
- [[seo-tech-audit]] — SEO-аудит задеплоенного сайта, следующий этап после деплоя
- [[wp-cli-deployer]] — деплой-скилл, для которого финальная проверка является pre-condition
- [[photo-curator]] — отвечает за photo-pipeline; его артефакты проверяются внутри бандла