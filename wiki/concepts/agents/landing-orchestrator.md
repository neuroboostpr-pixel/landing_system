---
slug: landing-orchestrator
type: agent
name: "Главный дирижёр (Landing Orchestrator)"
tags: [orchestrator, workflow, pipeline, stages, hard-gate]
triggers: [landing-go, landing-new, landing-build, landing-deploy]
inputs: [.landing-state.yaml, 07_ПРОТОТИП/source/prototype.pdf, config/stage-gates.yaml]
outputs: [wiki/pipeline-map.md, 00_БРИФ/brief.md, артефакты каждого этапа]
pre_reqs: [landing-onboarding-wizard]
related:
  - niche-analyst
  - brand-architect
  - content-writer
  - design-system-generator
  - moodboard-composer
  - client-assets-collector
  - photo-curator
  - block-composer
  - integrations-engineer
  - analytics-engineer
  - lifecycle-keeper
sources: ["agents/landing-orchestrator.md"]
<<<<<<< HEAD
updated: 2026-05-19
triggers: []
stage: "00–12"
uses:
  - niche-analyst
  - client-assets-collector
  - photo-stylist
  - references-curator
  - moodboard-composer
  - style-extractor
  - brand-architect
  - design-system-generator
  - scene-director
  - stack-planner
  - content-writer
  - wp-builder
  - integrations-engineer
  - analytics-engineer
  - seo-optimizer
  - wp-deployer
  - qa-auditor
  - lifecycle-keeper
  - prototype-importer
  - photo-curator
  - visual-curator
  - block-composer
  - landing-go
  - landing-build
  - landing-deploy
  - landing-qa
  - landing-rollback
  - landing-clone
  - stage-execution-protocol
  - gate-check
tags: [orchestrator, workflow, pipeline, core]
=======
updated: 2026-05-26
confidence:
  triggers: low
>>>>>>> block-library-cleanup
---

# Главный дирижёр (Landing Orchestrator)

## Что делает

<<<<<<< HEAD
Ведёт проект-лендинг через все 12 этапов производственного конвейера — от брифа до SEO. На каждом шаге диспатчит нужного специализированного агента, проверяет качество результата и не даёт перепрыгнуть этап без явного одобрения маркетолога.
=======
Ведёт проект-лендинг через 12 этапов — от брифа до SEO — и обеспечивает соблюдение качества на каждом из них. Перед любым действием читает `.landing-state.yaml`, рисует Mermaid-карту pipeline, формирует TodoWrite со всеми оставшимися этапами и запускает `gate-check.sh`. На каждом этапе диспатчит специализированного агента, ждёт HTML-превью, затем требует явного утверждения пользователя (HARD GATE) перед переходом к следующему шагу. В prototype-first режиме (PR-D) запускается через `/landing-go` и самостоятельно распределяет параллельные этапы 07d (фото) и 07e (визуалы).
>>>>>>> block-library-cleanup

## Когда вызывается

<<<<<<< HEAD
Активируется после инициализации проекта (`landing-project-init` или `landing-from-context`). Основная точка входа — команда `/landing-go`, которая читает `.landing-state.yaml` и продолжает с того этапа, где остановились. Отдельные этапы также запускаются через `/landing-build`, `/landing-deploy`, `/landing-qa`, `/landing-rollback`, `/landing-clone`.
=======
Запускается командой `/landing-go` после инициализации проекта (онбординг завершён, папка проекта создана). Также задействуется внутри команд `/landing-new`, `/landing-build`, `/landing-deploy` — всякий раз, когда нужен контроль workflow. Не запускается в обход — пользователь не может попросить «перейти сразу к деплою».

## Вход → выход
>>>>>>> block-library-cleanup

**Вход:** инициализированный проект с `.landing-state.yaml`, файл `config/stage-gates.yaml` со списком зависимостей между этапами; в prototype-first режиме — `prototype.pdf` в `07_ПРОТОТИП/source/`.

<<<<<<< HEAD
**Вход:**
- Инициализированная папка проекта (`~/Lendings/<slug>/`) со структурой template/
- `.landing-state.yaml` с текущим статусом этапов
- `config/stage-gates.yaml` — правила переходов между этапами

**Выход:**
- Последовательно заполненные папки `00_БРИФ/` → `12_SEO/`
- HTML-превью на каждом ключевом этапе (moodboard.html, brand-kit.html, design-preview.html, composed.html, build-preview.html)
- Полностью задеплоенный WordPress-сайт на Бегете

## Как работает (протокол)

Перед каждым действием оркестратор обязан:
1. Прочитать `.landing-state.yaml`, показать Mermaid-карту pipeline через `render-pipeline-map.sh`.
2. Создать TodoWrite-список всех оставшихся этапов.
3. Запустить `gate-check.sh` для текущего этапа; при провале — предложить авто-fix.
4. После verify и явного одобрения пользователя — закрыть этап через `gate-check.sh --approve` и перейти к следующему.

В prototype-first режиме (PR-D) этапы 00–02 помечаются `n/a`, старт — с `07a_prototype`. Этапы `07d_photos` и `07e_visuals` диспатчатся **параллельно** через `superpowers:dispatching-parallel-agents`.

HARD GATE — нельзя пропустить этап даже по просьбе пользователя. Пропуск «сойдёт» — недопустим.
=======
**Выход:** обновлённый `.landing-state.yaml` с отметками `approved` для каждого пройденного этапа; `wiki/pipeline-map.md` с актуальной Mermaid-картой; все промежуточные артефакты этапов (brief.md, brand-kit.html, composed.html, build-preview.html и т.д.).

## Failure modes

- Пользователь просит пропустить этап — оркестратор отказывает жёстко, ссылаясь на `require_approved` из `stage-gates.yaml`.
- Hard-check на гейте падает, но `fix_hint` не прописан в `stage-gates.yaml` — авто-фикс невозможен, оркестратор сообщает об ошибке и зависает.
- Verify-скрипт (например `verify-composed-premium.sh`) возвращает ненулевой exit-код — оркестратор НЕ объявляет этап завершённым и гоняет `block-composer` в цикле.
- Параллельные субагенты 07d/07e вернули ошибку в одном из потоков — оркестратор не переходит к 07f до тех пор, пока оба гейта не закрыты.
- `.landing-state.yaml` отсутствует или повреждён — весь pipeline недоступен; нужен `migrate-state-for-prd.sh`.

## Ключевые команды (Stage Execution Protocol)

Перед каждым действием — обязательно 4 шага:

```bash
# Шаг 1 — состояние + Mermaid-карта
bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki

# Шаг 3 — gate-check текущего этапа
bash scripts/gate-check.sh --stage <id> --project <project>

# Шаг 4 — approve после verify
bash scripts/gate-check.sh --stage <id> --project <project> --approve
>>>>>>> block-library-cleanup

# Wiki-запрос перед диспатчем агента
python -m scripts.wiki.query --stage=<N> --type=agent
python -m scripts.wiki.query --slug=<concept-slug>
```

<<<<<<< HEAD
- [[niche-analyst]] — этап 01a, анализ ниши
- [[brand-architect]] — этап 04, бренд-кит
- [[design-system-generator]] — этап 05, токены и DESIGN.md
- [[wp-builder]] — этап 08, генерация WordPress-темы
- [[photo-curator]] — этап 07d, обработка клиентских фото
- [[visual-curator]] — этап 07e, генерация иконок и инфографики
- [[block-composer]] — этап 07b, сборка composed.html
- [[qa-auditor]] — этап 10, аудит live-сайта
- [[stage-execution-protocol]] — обязательный протокол 4 шагов перед каждым действием
- [[gate-check]] — скрипт проверки и утверждения этапов
- [[landing-go]] — команда-триггер для prototype-first режима
=======
Полный протокол: `docs/standards/stage-execution-protocol.md`
>>>>>>> block-library-cleanup

## Related

- [[niche-analyst]] — диспатчится на этапе 01a
- [[brand-architect]] — диспатчится на этапе 04
- [[design-system-generator]] — диспатчится на этапе 05
- [[moodboard-composer]] — диспатчится на этапе 03
- [[content-writer]] — диспатчится на этапе 07
- [[block-composer]] — переделывает composed.html если 07b-гейт упал
- [[photo-curator]] — параллельный субагент этапа 07d
- [[integrations-engineer]] — диспатчится на этапе 08
- [[analytics-engineer]] — диспатчится на этапах 08 и 11
- [[lifecycle-keeper]] — диспатчится на rollback и clone
- [[landing-onboarding-wizard]] — должен завершиться до первого запуска оркестратора