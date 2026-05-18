---
type: command
name: landing-design
sources: ["commands/landing-design.md"]
updated: 2026-05-15
triggers: ["сгенерировать дизайн-систему", "создать токены дизайна", "запустить этап 05", "дизайн после бренда"]
stage: "05"
uses: ["design-system-generator", "design-tokens-generation", "scene-director", "brand-architect", "landing-brand", "landing-stack"]
tags: ["design", "tokens", "stage-05", "command"]
---

# /landing-design — Генерация дизайн-системы (этап 05)

## Что делает
Команда запускает генерацию дизайн-системы проекта: читает утверждённый бренд-кит и превращает его в машиночитаемые токены (`tokens.json`), исчерпывающий документ дизайна (`DESIGN.md`) и живой HTML-превью компонентов. Результат — единый источник правды для всех последующих этапов верстки.

## Когда вызывать / в каком этапе
Этап 05. Вызывается вручную после того, как `brand-architect` создал `04_БРЕНД/brand-kit.md` и пользователь подтвердил результат команды `/landing-brand`. Перед запуском система автоматически проверяет: пройден ли онбординг и закрыт ли gate предыдущего этапа. Если нет — выдаёт понятную ошибку и останавливается.

Опциональный флаг `--cinematic` подключает дополнительный агент `scene-director`, который создаёт кинематографическую грамматику из 8 сцен и план GSAP-анимаций (`scenes.md`).

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — утверждённый бренд-кит от `brand-architect`
- Флаг `--cinematic` (опционально) — для кинематографического режима

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — главный документ токенов (YAML frontmatter + структура блоков)
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены для сборки
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — живой превью компонентов в браузере
- `05_ДИЗАЙН-СИСТЕМА/scenes.md` — кинематографическая грамматика сцен (только при `--cinematic`)

**HARD GATE:** после генерации система показывает путь к превью и ждёт явного подтверждения пользователя, прежде чем разрешить переход к этапу 06 (stack-planner).

## Как работает внутри
1. Запускает агента `design-system-generator`
2. Выполняет `skills/design-tokens-generation/scripts/build-tokens.py` → `DESIGN.md` + `tokens.json`
3. Выполняет `skills/design-tokens-generation/scripts/render-preview.py` → `design-preview.html`
4. При флаге `--cinematic` — запускает агента `scene-director` → `scenes.md`
5. После approve пользователя — закрывает gate командой `scripts/gate-check.sh --approve`

## Связанные концепты
- [[brand-architect]] — создаёт `brand-kit.md`, который является входом для этой команды
- [[landing-brand]] — предшествующая команда, без её approve gate не откроется
- [[design-system-generator]] — агент, исполняющий основную логику генерации
- [[design-tokens-generation]] — скилл со скриптами build-tokens и render-preview
- [[scene-director]] — агент кинематографических сцен (опционально)
- [[landing-stack]] — следующий этап после approve дизайн-системы
- [[stack-planner]] — агент этапа 06, читает `DESIGN.md` как входной документ

## Источник
- `commands/landing-design.md`