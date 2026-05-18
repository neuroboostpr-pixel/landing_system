---
type: block
name: ru-features-05-method-steps
sources: ["block-library/features/ru-features-05-method-steps/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "ru-market", "steps", "method", "services", "b2c", "local", "opendesign"]
---

# Метод — 4 шага с линией-соединителем

## Что делает

Показывает процесс работы в виде четырёх пронумерованных шагов (01–04), визуально связанных горизонтальной линией. Слева — вводный заголовок и лид, справа — сами шаги. Создаёт у пользователя ощущение чёткой, надёжной последовательности.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при сборке wireframe.html через [[ux-composer]] или [[wireframe-rendering]]. Подходит для лендингов услуг, где нужно объяснить сложный процесс: диагностика → анализ → решение → результат. Рекомендован для сегментов b2c, местных сервисов и услуговых бизнесов. Хорошо работает в стилях **Editorial & Magazine** и **Minimalism & Swiss Style**.

## Что на вход / на выход

**Слоты (вход):**

| Слот | Обязательный | Лимит |
|---|---|---|
| `kicker` | нет | 50 символов |
| `headline` | **да** | 70 символов |
| `subhead` | нет | 200 символов |
| `step-1-title` … `step-4-title` | **да** | 40 символов каждый |
| `step-1-desc` … `step-4-desc` | **да** | 160 символов каждый |

Минимальный набор: headline + 4 пары title/desc (итого 9 полей).

**Выход:** HTML-блок с двухколоночным layout — заголовочная часть слева, шаги справа. На мобильных устройствах блок перестраивается в вертикальный стек с разделителями между шагами.

## Ключевые детали реализации

- Горизонтальная линия-соединитель над четырьмя шагами визуально передаёт прогресс и упорядоченность.
- Акцентные числа 01–04 выделены типографически и фиксируют внимание пользователя.
- Источник: open-design-landing (Apache-2.0) — `github.com/nexu-io/open-design`.
- Только для **ru-market** (`ru_market: true`).

## Связанные концепты

- [[ux-composer]] — собирает wireframe.html, выбирает блок из библиотеки
- [[block-composer]] — на этапе 07b инжектирует design-tokens и подставляет тексты из prototype.yaml
- [[wireframe-rendering]] — скилл, управляющий рендером wireframe с вариантами блоков
- [[block-composition]] — скилл этапа 07b, финальная сборка composed.html
- [[block-library-management]] — управление каталогом блоков, куда входит этот блок

## Источник

- `block-library/features/ru-features-05-method-steps/meta.yaml`