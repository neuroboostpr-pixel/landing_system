---
type: rule
name: landing-system-design-spec
sources: ["docs/superpowers/specs/2026-05-03-landing-system-design.md"]
updated: 2026-05-03
triggers: []
stage: ""
uses:
  - landing-orchestrator
  - landing-project-init
  - landing-from-context
  - wp-builder
  - wp-deployer
  - brand-architect
  - design-system-generator
  - content-writer
  - references-curator
  - moodboard-composer
  - style-extractor
  - stack-planner
  - integrations-engineer
  - analytics-engineer
  - seo-optimizer
  - qa-auditor
  - lifecycle-keeper
  - scene-director
  - landing-versioning-and-cloning
  - landing-new
  - landing-from-context
  - landing-clone
  - landing-deploy
  - landing-rollback
  - stage-gates
tags: [spec, architecture, overview, workflow, mvp]
---

# Landing System — главный дизайн-документ (Design Spec)

## Что делает

Это master-спецификация всей системы производства WordPress-лендингов. Описывает архитектуру, принципы, 12-этапный workflow, карту из 18 агентов и 10+ скиллов, механизм деплоя на Бегет, DNS-автоматизацию, A/B-клонирование и хранение секретов. Служит единым источником истины при доработке системы.

## Когда вызывать / в каком этапе

Это не команда и не агент — это нормативный документ. Читать перед:
- проектированием нового агента или скилла;
- принятием архитектурного решения (хостинг, стек, деплой);
- написанием нового spec/plan (он должен быть согласован с этим документом);
- онбордингом нового участника системы.

Автоматически не вызывается — используется как справочник.

## Что на вход / на выход

**Вход:** результат брейншторма, требования к системе.

**Выход:** зафиксированные решения по:
- платформе (WordPress + GeneratePress + GenerateBlocks + ACF + Fluent Forms);
- структуре папки проекта (00–12 + `.env`, `CLAUDE.md`, `.gitignore`);
- 12 этапам pipeline с hard gate на каждом;
- карте 18 агентов с ролями и привязкой к этапам;
- frontend-стеку (базовый и cinematic-режим с GSAP/ScrollTrigger/Lenis);
- механизму деплоя (SSH + rsync + WP-CLI на Бегет);
- версионированию и A/B-копиям через `lifecycle-keeper`;
- всем API-ключам, местам хранения секретов и шагам установки.

## Связанные концепты

- [[landing-orchestrator]] — главный агент, реализует 12-этапный workflow из этого спека
- [[stage-gates]] — правила hard gate между этапами, вытекают из спека
- [[landing-project-init]] — скилл создания структуры папки 00–12
- [[landing-from-context]] — скилл старта из родительского проекта агентства
- [[wp-cli-deployer]] — скилл деплоя по SSH+WP-CLI, описан в разделе 11
- [[landing-versioning-and-cloning]] — скилл снепшотов и A/B-клонов, раздел 13
- [[scene-director]] — агент cinematic-режима, раздел 9
- [[lifecycle-keeper]] — агент A/B-сравнения конверсий, раздел 13
- [[landing-new]] — главная точка входа, описана в разделе 10
- [[landing-clone]] — команда A/B-клонирования, раздел 13

## Источник

- `docs/superpowers/specs/2026-05-03-landing-system-design.md`