---
slug: premium-07b-checklist
type: rule
name: "PREMIUM 07b — Чек-лист сборки composed.html"
stage: "07b"
tags: [composed, premium, checklist, frontend, css, javascript, accessibility, mobile]
triggers: [landing-compose]
inputs: [00-brif, 04-brend, 05-dizayn-sistema, 07-kontent, 07-prototip]
outputs: [block-composition]
gates:
  - all_inputs_present
  - file_size_60_150kb
  - lighthouse_performance_85
  - lighthouse_accessibility_90
  - composed_mobile_preview_exists
  - composed_explained_md_exists
  - photo_mapping_yaml_exists
pre_reqs: [04-brend, 05-dizayn-sistema, 07-kontent, 07-prototip, landing-wireframe]
related:
  - landing-compose
  - block-composer
  - block-composition
  - ux-composer
  - landing-design
  - landing-wireframe
sources: ["docs/standards/premium-07b-checklist.md"]
updated: 2026-05-26
---

# PREMIUM 07b — Чек-лист сборки composed.html

## Что делает

Задаёт обязательные стандарты качества для этапа **07b_COMPOSED**: архитектуру файла, CSS-переменные, типографику с `clamp()`, набор блоков, правила сетки, 10 интерактивных эффектов (parallax, glassmorphism, count-up, слайдер, lightbox и др.) и финальный набор gate-проверок. Эталон — `dubai-avto-liza/07b_COMPOSED/composed.html` (1757 строк, ~130 KB, 20 premium-фич). Правило жёстко запрещает сборку если хотя бы одного входного артефакта нет.

## Когда вызывается

Агент `block-composer` или скилл `landing-compose` обязан загрузить этот файл **перед началом сборки** 07b. Также передаётся вручную пользователем если нужно переделать или доработать `composed.html` до прохождения HARD GATE (`verify-composed-premium.sh` exit 0).

## Вход → выход

**Вход:** `brief.md`, `brand-kit.md`, `tokens.json`, `final-copy.md`, `selections.yaml` (wireframe), минимум 15 фото клиента в `inbox/`, `photo-mapping.yaml`.

**Выход:** `composed.html` (один файл, inline CSS+JS, 60–150 KB), `composed-mobile-preview.html`, `composed-explained.md`, обновлённый `photo-mapping.yaml`.

## Чем закрывается этап (gates)

- `all_inputs_present` — все 7 входных артефактов существуют, иначе сборка не начинается
- `file_size_60_150kb` — итоговый HTML в пределах 60–150 KB
- `lighthouse_performance_85` — Performance ≥ 85
- `lighthouse_accessibility_90` — Accessibility ≥ 90
- `composed_mobile_preview_exists` — файл `composed-mobile-preview.html` создан
- `composed_explained_md_exists` — файл `composed-explained.md` создан
- `photo_mapping_yaml_exists` — `07c_PHOTOS/photo-mapping.yaml` актуален

## Failure modes

- **Пропуск входных артефактов** — агент начинает сборку без `selections.yaml` или `photo-mapping.yaml`, получается шаблонный HTML без реального контента и фото.
- **Хардкод цветов** — цвета прописываются напрямую (`#fff`, `rgba(...)`) вместо CSS-переменных, при смене бренда рассыпается всё оформление.
- **Отсутствие `clamp()`** — шрифты фиксированные, на мобильном либо слишком крупные, либо слишком мелкие; нет плавного масштабирования.
- **Сторонние библиотеки** — подключается jQuery, Swiper или AOS, файл раздувается, Lighthouse падает ниже порога.
- **Недостаток premium-эффектов** — нет parallax или count-up, визуал «средний AI-лендинг»; HARD GATE (`verify-composed-premium.sh`) возвращает exit 1 и блокирует переход к этапу 08.

## Related

- [[landing-compose]] — скилл, который непосредственно запускает сборку 07b и использует этот чек-лист
- [[block-composer]] — агент-исполнитель сборки composed.html; обязан следовать всем пунктам правила
- [[block-composition]] — выходной артефакт этапа 07b, описание структуры блоков
- [[ux-composer]] — отвечает за логику wireframe и передаёт selections.yaml в 07b
- [[landing-wireframe]] — предшествующий этап: без его outputs нельзя начать 07b
- [[landing-design]] — поставляет tokens.json и brand-kit, на которых строится вся CSS-система