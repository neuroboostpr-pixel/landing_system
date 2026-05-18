---
type: block
name: footer-minimal-split-romanmelnikov-tilda-14
sources: ["block-library/footer/footer-minimal-split-romanmelnikov-tilda-14/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-library-management"]
tags: ["footer", "minimal", "split", "ru-market", "no-animation", "services", "education", "b2b-saas"]
---

# Футер минимальный сплит (footer-minimal-split)

## Что делает

Блок нижней части страницы с приглушённой контактной информацией и мелкими юридическими ссылками. Визуально спокойный, не перегружает финал лендинга — всё лишнее убрано, остаётся только необходимое.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Compose)** — когда `block-composer` собирает `composed.html` из блоков, выбранных пользователем в `selections.yaml`. Подходит для проектов в нишах: **услуги**, **образование**, **b2b-saas**. Ориентирован на **российский рынок** (`ru_market: true`). Анимации нет, поэтому не требует GSAP или дополнительных JS-зависимостей.

Выбирается через интерактивный wireframe на этапе 07a: пользователь видит 2–3 варианта футера и останавливается на минималистичном сплит-варианте, если нужен сдержанный финал без акцента.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — заголовок или название компании в футере.
- Токены дизайна из `tokens.json` (цвета, типографика).
- Контент из `prototype.yaml` (юридические ссылки, контактные данные).

**Выход:**
- HTML-секция футера в `composed.html` с подставленными текстами и токенами.
- Стиль: `minimal`, паттерн: `split` (левая и правая колонки).

## Связанные концепты

- [[block-composer]] — агент, который вставляет этот блок в `composed.html` на этапе 07b
- [[ux-composer]] — агент, показывающий блок в `wireframe.html` как один из вариантов футера на этапе 07a
- [[block-library-management]] — скилл управления библиотекой блоков, регистрирует и обновляет мета-данные блока
- [[block-composition]] — скилл этапа 07b, управляет логикой выбора и подстановки блоков
- [[07b-composed]] — этап, на котором блок используется

## Источник

- `block-library/footer/footer-minimal-split-romanmelnikov-tilda-14/meta.yaml`
- Импортирован с `https://romanmelnikov.tilda.ws/` методом `codex-block-generation` (2026-05-16)