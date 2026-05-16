---
type: block
name: cta-cinematic-split-portfolio-kdm1-ru-9
sources: ["block-library/cta/cta-cinematic-split-portfolio-kdm1-ru-9/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a, 07b"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["cta", "cinematic", "split", "ru-market", "education", "services", "b2b-saas", "dark", "emotional"]
---

# CTA Cinematic Split — тёмный эмоциональный блок с иллюстрацией

## Что делает
Блок призыва к действию (CTA) в тёмной эмоциональной стилистике: крупная иллюстрация действия занимает одну половину экрана, сильный текстовый акцент — другую. Раскладка split создаёт визуальное напряжение и удерживает внимание. Подходит для ниш, где нужно произвести впечатление, а не просто информировать.

## Когда вызывать / в каком этапе
Блок используется на этапах **07a (Wireframe)** и **07b (Compose)**. Агент [[ux-composer]] выбирает его из библиотеки при формировании интерактивного wireframe.html — если прототип содержит CTA-секцию с визуально насыщенным акцентом в cinematic-стиле. На этапе 07b агент [[block-composer]] инжектирует design-tokens и подставляет текст из prototype.yaml.

Подходит для проектов с `style_mood: cinematic` (тёмная палитра, кино-эстетика). Особенно эффективен в нишах **education**, **services**, **b2b-saas** на российском рынке (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- Слот `heading` (тип `text`, обязательный) — главный заголовок или призыв к действию.
- Design-tokens из `tokens.json` (цвета, шрифты, радиусы) — инжектируются автоматически на этапе 07b.

**Выход:**
- HTML-фрагмент блока в составе `07a_WIREFRAME/wireframe.html` (вариант для выбора пользователем).
- Финальный HTML-блок в `07b_COMPOSED/composed.html` с подставленными текстами и токенами; слот иллюстрации остаётся плейсхолдером до этапа 07c (фото) или 07d (визуал).

## Связанные концепты
- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe по prototype.yaml
- [[block-composer]] — рендерит composed.html с инжекцией токенов и текстов прототипа
- [[wireframe-rendering]] — скилл, который управляет рендером интерактивного wireframe.html
- [[block-composition]] — скилл этапа 07b, отвечает за финальную сборку блоков
- [[block-library-management]] — скилл управления библиотекой; этот блок импортирован через `codex-block-generation` из портфолио kdm1.ru

## Источник
- `block-library/cta/cta-cinematic-split-portfolio-kdm1-ru-9/meta.yaml`