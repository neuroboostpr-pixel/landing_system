---
type: block
name: cta-cinematic-split-portfolio-kdm1-ru-3
sources: ["block-library/cta/cta-cinematic-split-portfolio-kdm1-ru-3/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition"]
tags: ["cta", "cinematic", "split", "ru-market", "services", "education", "b2b-saas"]
---

# CTA — Контрастный переход с иллюстрацией команды

## Что делает

Блок призыва к действию в кинематографичном стиле: левая и правая части контрастируют между собой, на одной — иллюстрация команды, на другой — крупный тезис и кнопка внизу. Создаёт ощущение весомого финального шага перед отправкой заявки.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Block Compose)** — когда `block-composer` собирает `composed.html` из утверждённого `wireframe.html`. Подходит как завершающий CTA-блок для лендингов в нишах услуг, образования и B2B-SaaS. Оптимален для российского рынка (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — крупный тезис, основной аргумент перед кнопкой.
- Токены дизайна из `tokens.json` (цвета, шрифты) — инжектятся агентом `block-composer`.

**Выход:**
- HTML-фрагмент блока, встраиваемый в `07b_COMPOSED/composed.html`.
- Слот для иллюстрации команды остаётся лейблированным placeholder'ом (`[SLOT: team-illustration]`) — заполняется на этапах PR-B (фото) или PR-C (инфографика).

**Особенности:**
- `has_animation: false` — без JS-анимаций, статичная вёрстка.
- Макет `split` — двухколоночный горизонтальный разрез.
- Стиль `cinematic` — тёмный/контрастный mood, соответствует кинематографичной теме проекта.

## Связанные концепты

- [[block-composer]] — агент, который рендерит `composed.html` и инжектирует этот блок с токенами.
- [[block-composition]] — скилл, описывающий механику сборки блоков на этапе 07b.
- [[ux-composer]] — агент этапа 07a, который подбирает этот блок при формировании wireframe.
- [[07b-composed]] — этап, в котором блок используется.
- [[visual-curator]] — агент PR-C, который заполняет иллюстративный слот блока.

## Источник

- `block-library/cta/cta-cinematic-split-portfolio-kdm1-ru-3/meta.yaml`