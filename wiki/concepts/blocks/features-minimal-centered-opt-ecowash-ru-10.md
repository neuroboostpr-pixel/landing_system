---
type: block
name: features-minimal-centered-opt-ecowash-ru-10
sources: ["block-library/features/features-minimal-centered-opt-ecowash-ru-10/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "minimal", "centered", "segmentation", "ru-market", "ecommerce", "services", "education"]
---

# Блок сегментации с цветными тегами (features-minimal-centered-opt-ecowash-ru-10)

## Что делает
Белый минималистичный блок для сегментации аудитории: задаёт вопрос посетителю и предлагает набор цветных тегов, соответствующих разным типам клиентов. Помогает пользователю быстро найти «свой» сценарий и перейти к релевантному предложению.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при сборке интерактивного прототипа. Агент [[ux-composer]] выбирает блок из библиотеки, когда в `prototype.yaml` нужен раздел «Для кого» или «Выберите ваш тип». Затем на этапе **07b (Compose)** агент [[block-composer]] заполняет слот `heading` реальным текстом из прототипа через скилл [[block-composition]].

Подходящие ниши: **ecommerce, services, education**.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — секция с заголовком сегментации и перечнем типов клиентов
- `tokens.json` — цвета бренда (теги окрашиваются по токенам)

**Выход:**
- HTML-секция внутри `wireframe.html` (этап 07a) — каркас с вариантами оформления
- HTML-секция внутри `composed.html` (этап 07b) — финальная разметка с подставленным текстом и цветовыми токенами

**Обязательный слот:**
| Слот | Тип | Описание |
|------|-----|----------|
| `heading` | text | Вопрос к посетителю («Кто вы?», «Что вы ищете?» и т.п.) |

**Анимации:** отсутствуют (`has_animation: false`) — блок статичный, быстро загружается.

## Связанные концепты
- [[ux-composer]] — подбирает блок при формировании wireframe на этапе 07a
- [[wireframe-rendering]] — рендерит HTML-каркас блока с CSS-переключателями вариантов
- [[block-composer]] — наполняет блок текстом и токенами на этапе 07b
- [[block-composition]] — скилл, управляющий подстановкой токенов и текста прототипа
- [[block-library-management]] — скилл учёта и обновления библиотеки блоков

## Источник
- `block-library/features/features-minimal-centered-opt-ecowash-ru-10/meta.yaml`
- Импортирован с `https://opt.ecowash.ru/` методом `codex-block-generation` (2026-05-16)