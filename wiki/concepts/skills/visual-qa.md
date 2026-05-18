---
type: skill
name: visual-qa
sources: ["skills/visual-qa/SKILL.md"]
updated: 2026-05-16
triggers: ["/landing-qa", "визуальный QA", "проверка лендинга после сборки", "auto-fix цикл"]
stage: "07c, 07f, 08, 09"
uses: ["qa-auditor", "block-composer", "photo-curator", "visual-curator", "gpt5-prompting-engine"]
tags: ["qa", "screenshot", "playwright", "codex", "auto-fix", "visual"]
---

# Visual QA — автоматический визуальный контроль качества

## Что делает

Делает скриншоты лендинга через Playwright (desktop + mobile), отправляет их в codex vision, получает список визуальных проблем в формате JSON и — при необходимости — автоматически исправляет CSS-ошибки за до трёх итераций. Итог: читаемый отчёт о качестве в папке проекта.

## Когда вызывать / в каком этапе

Используется на этапах **07c, 07f, 08, 09** — после того, как `composed.html` готов или тема собрана. Вызывается командой `/landing-qa`:

```bash
/landing-qa <project>            # скриншоты + анализ + отчёт
/landing-qa <project> --strict   # падает с exit 1 при critical issues
/landing-qa <project> --iterate  # авто-цикл исправлений (макс 3 раза)
```

## Что на вход / на выход

**Вход:**
- `composed.html` или задеплоенный сайт проекта
- `templates/review-prompt.md` — промпт для codex (генерируется через `gpt5-prompting-engine`, не пишется вручную)

**Выход:**
- `<project>/10_QA/visual-qa-report.md` — финальный отчёт со списком issues по уровням: `critical` / `warning` / `info`
- JSON-список проблем: тип, CSS-селектор, подсказка по исправлению

**Внутренний pipeline:**
1. `take-screenshots.py` → Playwright: desktop 1280×800 + mobile 375×812
2. `codex-review-screenshot.sh` → codex vision анализирует каждый скриншот
3. `visual-qa-loop.py` → парсит JSON, при `--iterate` запускает `apply-fix.py`

**Ограничения auto-fix:**
- ✅ Разрешено: `css_tweak` (inline style по selector)
- ❌ Запрещено: `text_*` (контент под защитой PR-H), `block_*` (структура блоков)
- 🟡 Остальное — в отчёт без автофикса

## Связанные концепты

- [[qa-auditor]] — агент этапа 10, проверяет live-сайт (доступность, HTTPS, формы, аналитика)
- [[block-composer]] — создаёт `composed.html`, который этот скилл затем проверяет
- [[gpt5-prompting-engine]] — генерирует промпт `review-prompt.md` для codex vision
- [[visual-curator]] — этап 07d, предшествует QA; добавляет иконки и инфографику в composed.html
- [[photo-curator]] — этап 07c, добавляет реальные фото перед QA

## Источник

- `skills/visual-qa/SKILL.md`