---
type: block
name: social-proof-corporate-grid-3-zilant-group-5
sources: ["block-library/social-proof/social-proof-corporate-grid-3-zilant-group-5/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "block-composition", "ux-composer"]
tags: ["social-proof", "corporate", "grid-3", "statistics", "ru-market", "services", "b2b-saas", "premium-auto", "tech"]
---

# Статистический блок с крупными числами и видеопревью (Zilant Group)

## Что делает

Отображает ключевые бизнес-показатели в виде крупных цветных (красных) цифр с краткими подписями, расположенных в сетке из трёх колонок. Ниже — широкое видеопревью, усиливающее доверие. Подходит для B2B-компаний, которым важно показать масштаб и результаты в цифрах.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Block Compose)** — когда `block-composer` собирает `composed.html` из выбранных блоков. `ux-composer` выбирает этот блок на этапе 07a (wireframe) при наличии в прототипе раздела с цифровыми достижениями или социальными доказательствами.

Блок особенно уместен для ниш: **услуги, b2b-saas, premium-auto, tech** — там, где важна демонстрация масштаба через конкретные метрики.

Анимация при скролле **отсутствует** (`has_animation: false`) — блок статичен, что ускоряет загрузку и не требует JS-зависимостей.

## Что на вход / на выход

**Входные слоты:**

| Слот | Тип | Обязательность |
|------|-----|---------------|
| `heading` | text | обязательный |

Дополнительные слоты (цифры, подписи, видеоURL) заполняются контент-райтером из `prototype.yaml` на этапе 07b при подстановке токенов.

**На выход:** HTML-фрагмент блока, встроенный в `composed.html` с дизайн-токенами из `tokens.json` (цвета, типографика).

## Связанные концепты

- [[block-composer]] — оркестрирует сборку `composed.html`, вставляет этот блок
- [[block-composition]] — скилл, определяющий правила подстановки токенов и текстов в блоки
- [[ux-composer]] — выбирает этот блок из библиотеки при рендере wireframe.html
- [[block-library-management]] — хранит и версионирует блок в общей библиотеке
- [[07b-composed]] — этап, на котором блок становится частью итогового composed.html

## Источник

- `block-library/social-proof/social-proof-corporate-grid-3-zilant-group-5/meta.yaml`
- Импортирован с [zilant.group](https://zilant.group/) методом `codex-block-generation` (2026-05-16)