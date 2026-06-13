---
slug: wiki-audit-checklist
type: rule
name: "Wiki Audit Checklist"
tags: [wiki, audit, quality, knowledge-management, code-review]
triggers: []
related: [landing-orchestrator, landing-go, seo-tech-audit]
sources: ["docs/standards/wiki-audit-checklist.md"]
updated: 2026-05-26
---

# Wiki Audit Checklist

## Что делает
Стандарт для проведения read-only аудита knowledge-layer папок (`wiki/`, `kb/`, `docs/wiki/`) в агентных системах. Описывает 10-шаговый чеклист, severity-модель (Critical / Major / Minor), шаблоны findings и структуру итогового отчёта. Цель — убедиться, что wiki реально снижает token-cost, не расходится с исходниками и явно инструктирует агентов читать себя как первичный источник знаний.

## Когда вызывается
Применяется вручную — аудитором (человеком или агентом) по запросу или перед мажорными изменениями исходников системы. Не запускается автоматически: это декларативный стандарт, а не исполняемый скрипт. Формально точкой входа служит прямое обращение к файлу стандарта.

## Вход → выход
**Вход:** исходные папки `wiki/`, `agents/`, `skills/`, `commands/`, `.claude/`, `docs/standards/`, compile-скрипт системы (`scripts/wiki/`), hooks-инфраструктура (`.githooks/`).  
**Выход:** файл отчёта `docs/code-review/<project>-wiki-audit-YYYY-MM-DD.md` со структурированными findings: Summary, Critical issues, Major issues, Minor issues, Positive feedback, Questions for author, Verdict (`Approve` / `Comment` / `Request Changes`).

## Failure modes
- Аудитор редактирует файлы вместо фиксации наблюдений — прямое нарушение read-only режима.
- Intent wiki не формализован заранее → severity findings определяется произвольно.
- Проверяется только структура папок, но пропускается ключевой пункт 5 (reader-инструкции для агентов) — самый критичный пункт упущен.
- Находки описываются без `file:line` evidence → отчёт не верифицируем и теряет ценность.
- Verdict выносится без проверки freshness и compression benefit → ложный Approve при устаревшей wiki.

## Related
- [[landing-orchestrator]] — wiki auto-sync хук интегрирован через `post-commit` в pipeline оркестратора
- [[landing-go]] — главная точка входа, для которой wiki служит навигационным контекстом
- [[seo-tech-audit]] — пример стандарта-чеклиста того же класса (audit-style rule с severity-моделью)