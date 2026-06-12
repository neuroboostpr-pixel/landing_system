---
slug: qa-auditor
type: agent
name: "QA-аудитор"
stage: "10"
tags: [qa, audit, https, analytics, forms, mobile, deploy]
triggers: [landing-deploy]
inputs: [00_БРИФ/brief.md]
outputs: [10_QA/qa-report.md]
gates: [qa_report_approved]
pre_reqs: []
related: [landing-orchestrator, lifecycle-keeper, integrations-engineer]
sources: ["agents/qa-auditor.md"]
updated: 2026-05-26
confidence: {triggers: low, gates: low}
---

# QA-аудитор

## Что делает

Проверяет живой сайт по 7 критериям качества после деплоя: доступность (HTTP 200), корректный HTTPS-редирект, наличие мета-тегов (title, description, og:title), подключение Яндекс.Метрики, Google Tag Manager, рендер формы Fluent Forms и наличие viewport-тега для мобильных устройств. По результатам формирует структурированный отчёт в виде таблицы и ожидает явного утверждения — без него этап не закрывается.

## Когда вызывается

Запускается на этапе `10_qa` после успешного деплоя (`/landing-deploy`). Обязательное условие — `current_stage == 10_qa` в `.landing-state.yaml`. Если предшественник (stage 09) не закрыт, хук `enforce_stage_gate.py` блокирует любые Write/Edit-операции.

## Вход → выход

**Вход:** URL задеплоенного сайта из `00_БРИФ/brief.md`; доступ к интернету для `curl`-запросов; пройденный gate-check `--stage 10_qa`.

**Выход:** `10_QA/qa-report.md` — markdown-таблица с результатами по каждому из 7 критериев (✅ / ❌). После утверждения пользователем этап помечается `approved` через `gate-state.sh`.

## Чем закрывается этап (gates)

- `qa_report_approved` — пользователь явно подтвердил отчёт; все 7 критериев в статусе ✅ либо расхождения объяснены и приняты.

## Failure modes

- **Сайт недоступен (не 200)** — curl возвращает ошибку; аудит прерывается на первом шаге, дальнейшие проверки не имеют смысла.
- **HTTPS не настроен или редирект отсутствует** — HTTP 200 вместо 301 → https, браузер не показывает замок.
- **Метрика / GTM отсутствуют в HTML** — analytics-фрагменты не вставлены в тему или удалены при регенерации `functions.php`.
- **Fluent Forms shortcode не рендерится** — плагин не активирован или форма не опубликована на странице.
- **Предшественник не закрыт** — `enforce_stage_gate.py` блокирует запись в `10_QA/`; агент должен остановиться и сообщить пользователю.

## Related

- [[landing-orchestrator]] — вызывает агента в рамках pipeline; управляет переходом к этапу 10
- [[lifecycle-keeper]] — фиксирует статус этапа и вызов gate-state approve
- [[integrations-engineer]] — отвечает за встройку GTM/Метрики в тему, которую здесь проверяют