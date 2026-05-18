---
type: block
name: trust-editorial-grid-2-romanmelnikov-tilda-11
sources: ["block-library/trust/trust-editorial-grid-2-romanmelnikov-tilda-11/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer"]
tags: ["trust", "editorial", "grid-2", "ru-market", "no-animation", "services", "education", "b2b-saas"]
---

# Длинный блок критериев с двумя плотными колонками (Editorial Grid-2)

## Что делает
Отображает критерии доверия или аргументы выбора в двух плотных текстовых колонках на фоне большого «воздушного» пространства. Создаёт ощущение солидности и экспертности без перегруза визуалом.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** при сборке `composed.html`. Агент `block-composer` подставляет блок, когда в `prototype.yaml` есть секция с перечнем критериев, преимуществ или условий сотрудничества. Хорошо подходит для ниш **услуги**, **образование** и **B2B-SaaS**, где важно логически обосновать выбор без яркого визуального акцента.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — заголовок блока критериев.
- Текстовый контент двух колонок из `prototype.yaml` (критерии, пункты, аргументы).

**Выход:**
- HTML-фрагмент блока с редакционной сеткой `grid-2`.
- Встраивается в `07b_COMPOSED/composed.html` как самостоятельная секция категории `trust`.

## Особенности блока
- **Стиль:** editorial — минималистичная типографика, акцент на тексте, много белого пространства.
- **Анимации:** отсутствуют (`has_animation: false`) — блок статичен, не требует GSAP.
- **Адаптация под ru-рынок:** да (`ru_market: true`).
- **Источник вдохновения:** [romanmelnikov.tilda.ws](https://romanmelnikov.tilda.ws/), импортирован через `codex-block-generation`.

## Связанные концепты
- [[block-composer]] — рендерит этот блок в `composed.html` на этапе 07b
- [[ux-composer]] — выбирает блок при построении `wireframe.html` на этапе 07a
- [[block-composition]] — скилл, управляющий сборкой блоков из библиотеки
- [[block-library-management]] — скилл для управления и импорта блоков в библиотеку
- [[07b-composed]] — этап, на котором блок активируется

## Источник
- `block-library/trust/trust-editorial-grid-2-romanmelnikov-tilda-11/meta.yaml`