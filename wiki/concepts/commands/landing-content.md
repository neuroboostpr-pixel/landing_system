---
slug: landing-content
type: command
name: "Адаптация прототипа в контент блоков (stage 07)"
stage: "07"
tags: [content, gutenberg, prototype, seo, copywriting]
triggers: [landing-content]
inputs: [07-prototip, 06-stek]
outputs: [07-kontent]
gates: []
pre_reqs: [06-stek, 07-prototip]
related: [content-writer, landing-prototype, landing-stack, landing-compose, landing-orchestrator]
sources: ["commands/landing-content.md"]
updated: 2026-06-22
---

# Адаптация прототипа в контент блоков (stage 07)

## Что делает

Команда `/landing-content` запускает агента `content-writer`, который читает `prototype.md` и структуру блоков из `DESIGN.md`, затем собирает финальные тексты лендинга, распределяя их по блокам Gutenberg в соответствии со стеком проекта. Параллельно формируется SEO-копирайтинг. Выход этапа — два файла в `07_КОНТЕНТ/`, которые служат основой для сборки `composed.html` на этапе 07b.

## Когда вызывается

Запускается вручную командой `/landing-content` после того, как утверждён стек проекта (`06_СТЕК/design-stack.yaml`). Gate-check проверяет, что этап 06 закрыт; при незакрытом этапе команда останавливается с объяснением, какой предыдущий шаг пропущен.

## Вход → выход

**Вход:**
- `07_ПРОТОТИП/prototype.md` — исходный прототип с реальными текстами клиента.
- `06_СТЕК/design-stack.yaml` — определения блоков стека.
- `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/` — реальные отзывы (при наличии).

**Выход:**
- `07_КОНТЕНТ/final-copy.md` — финальный копирайтинг, распределённый по блокам Gutenberg.
- `07_КОНТЕНТ/seo-copy.md` — SEO-заголовки, описания, варианты h1.

## Чем закрывается этап (gates)

Этап имеет **HARD GATE**: агент показывает `final-copy.md` и ждёт явного подтверждения пользователя перед переходом к этапу 08. Без approve дальнейшая работа оркестратора блокируется. После утверждения запускается `gate-check.sh --approve`.

## Failure modes

- **Отсутствует `prototype.md`** — агент не может извлечь тексты; команда остановится или сгенерирует пустые блоки.
- **Onboarding не пройден** — pre-flight возвращает exit 1 до запуска агента.
- **Стек не утверждён (этап 06 не закрыт)** — gate-check блокирует выполнение с сообщением об ошибке.
- **Lorem ipsum в output** — нарушение правила «реальные тексты из прототипа»; проверяется ревью `final-copy.md` перед approve.
- **Пользователь не даёт approve** — пайплайн встаёт на HARD GATE и не переходит к composed/08.

## Related

- [[content-writer]] — агент, который непосредственно пишет `final-copy.md` и `seo-copy.md`
- [[landing-prototype]] — предыдущий этап: импорт и нормализация прототипа в `prototype.md`
- [[landing-stack]] — предыдущий этап: утверждение стека блоков (`design-stack.yaml`)
- [[landing-compose]] — следующий этап: сборка `composed.html` с токенами и текстами из этого этапа
- [[landing-orchestrator]] — оркестратор, диспатчит этот этап в рамках общего пайплайна