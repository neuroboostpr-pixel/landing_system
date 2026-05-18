---
type: block
name: ru-features-08-kpi-metrics
sources: ["block-library/features/ru-features-08-kpi-metrics/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["infographic-builder", "ux-composer", "block-composer", "visual-curator"]
tags: ["features", "kpi", "metrics", "infographic", "ru-market", "b2c", "services"]
---

# 📊 4 KPI-метрики (87% / 12 лет / 1000+ клиентов)

## Что делает

Отображает четыре ключевых показателя компании (процент успешных проектов, лет на рынке, количество клиентов, завершённых проектов) в виде крупных чисел с инфографикой. Усиливает доверие посетителя конкретными цифрами.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** — `ux-composer` выбирает блок из библиотеки, если прототип содержит секцию с KPI или числовыми достижениями. Подходит для услуговых сайтов и B2C-лендингов. Рекомендованные стили: Minimalism & Swiss Style, Flat Design 2.0.

## Что на вход / на выход

**Вход:**
- Реальные числа от клиента (% успеха, лет на рынке, кол-во клиентов, кол-во проектов)
- `tokens.json` с цветами бренда (используется `infographic-builder` при генерации PNG)
- Слот `kpi-4` — опциональный, остальные три обязательны

**Выход:**
- Wireframe-блок в `wireframe.html` с четырьмя ячейками в ряд (desktop) / сеткой 2×2 (mobile)
- Четыре infographic-слота типа `number` (`kpi-1` … `kpi-4`) — заполняются агентом [[infographic-builder]] на этапе 07d
- После этапа 07d — готовые PNG-инфографики, встроенные в `composed.html` агентом [[visual-curator]]

## Структура слотов

| Слот | Значение по умолчанию | Обязателен |
|---|---|---|
| kpi-1 | 87% успешных проектов | да |
| kpi-2 | 12 лет на рынке | да |
| kpi-3 | 1000+ клиентов | да |
| kpi-4 | 500+ завершённых проектов | нет |

> **Важно:** числа должны быть честными — `conversion_notes` в meta.yaml прямо предупреждает: уточни цифры у клиента перед публикацией.

## Связанные концепты

- [[infographic-builder]] — генерирует PNG-инфографику для каждого kpi-слота через codex image_gen
- [[visual-curator]] — оркестратор этапа 07d, запускает [[infographic-builder]] и вшивает результаты в composed.html
- [[ux-composer]] — выбирает этот блок из библиотеки при составлении wireframe
- [[block-composer]] — на этапе 07b подставляет реальные числа из prototype.yaml вместо плейсхолдеров

## Источник

- `block-library/features/ru-features-08-kpi-metrics/meta.yaml`