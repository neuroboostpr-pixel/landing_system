---
type: block
name: cta-minimal-centered-opt-ecowash-ru-3
sources: ["block-library/cta/cta-minimal-centered-opt-ecowash-ru-3/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer"]
tags: ["cta", "minimal", "centered", "ru-market", "ecommerce", "services"]
---

# CTA Minimal Centered — белый раздел-переход с крупным вопросом

## Что делает

Белый переходный раздел с крупно отцентрированным вопросом-заголовком и декоративной продуктовой графикой. Создаёт паузу между смысловыми блоками лендинга и фокусирует внимание посетителя перед целевым действием.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Block Compose)** — когда `block-composer` собирает `composed.html` из библиотеки блоков. Подходит для вставки между информационными секциями (например, после описания услуги и перед формой заявки). Актуален для **российского рынка** (`ru_market: true`).

Подходящие ниши: **ecommerce** и **services**.

## Что на вход / на выход

**Слоты (входные данные):**
| Слот | Тип | Обязательный | Описание |
|------|-----|-------------|----------|
| `heading` | text | ✅ да | Крупный вопрос или тезис, выводимый в центре блока |

**Визуальные placeholders:**
Декоративная продуктовая графика остаётся как labeled placeholder — заполняется на этапах PR-B (фото) или PR-C (генерация визуала).

**На выход:** готовый HTML-фрагмент блока с подставленным `heading` и токенами дизайн-системы (`tokens.json`).

**Параметры стиля:**
- `style_mood`: minimal
- `layout_pattern`: centered
- `has_animation`: false (анимации нет — блок статичный)

## Связанные концепты

- [[block-composer]] — рендерит блок в `composed.html` на этапе 07b, подставляет design-tokens и тексты из prototype.yaml
- [[ux-composer]] — выбирает этот блок из библиотеки при сборке wireframe на этапе 07a
- [[block-composition]] — скилл, управляющий сборкой блоков и инъекцией токенов
- [[block-library-management]] — скилл, отвечающий за ведение и пополнение библиотеки блоков
- [[07b-composed]] — этап pipeline, в котором блок используется

## Источник

- `block-library/cta/cta-minimal-centered-opt-ecowash-ru-3/meta.yaml`
- Импортирован с [opt.ecowash.ru](https://opt.ecowash.ru/) методом `codex-block-generation` (2026-05-16)