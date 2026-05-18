---
type: block
name: trust-luxury-centered-romanmelnikov-tilda-5
sources: ["block-library/trust/trust-luxury-centered-romanmelnikov-tilda-5/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composition", "ux-composer", "block-composer"]
tags: ["trust", "luxury", "centered", "dark", "ru-market"]
---

# Имиджевый trust-блок — Luxury Centered (Роман Мельников / Tilda)

## Что делает
Отображает имиджевый блок доверия с крупным словом-заголовком, декоративной подписью и спокойной тёмной композицией — создаёт ощущение премиальности и надёжности без лишних деталей.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** при сборке `composed.html`. Агент [[ux-composer]] выбирает блок из библиотеки на этапе 07a (wireframe), если нише подходит luxury/services/education и нужен тёмный имиджевый акцент. [[block-composer]] инжектирует токены дизайна и подставляет текст прототипа в слот `heading`.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (type: text) — главное слово или короткая фраза (из `prototype.yaml`)
- `tokens.json` (цвета, шрифты из этапа 05) — инжектируются автоматически

**Выход:**
- HTML-фрагмент блока, встроенный в `07b_COMPOSED/composed.html`
- Визуальных слотов (фото/иконки) нет — блок полностью типографический

## Особенности
- **Стиль:** luxury, тёмная цветовая композиция, центрированный макет
- **Анимации:** отсутствуют (`has_animation: false`)
- **Рынок:** адаптирован под русскоязычную аудиторию (`ru_market: true`)
- **Ниши:** luxury, services, education
- **Источник:** импортирован с [romanmelnikov.tilda.ws](https://romanmelnikov.tilda.ws/) методом `codex-block-generation` (2026-05-16)

## Связанные концепты
- [[block-composition]] — скилл этапа 07b, управляет сборкой блоков с токенами
- [[ux-composer]] — агент 07a, выбирает этот блок из библиотеки при рендере wireframe
- [[block-composer]] — агент 07b, финально собирает composed.html
- [[block-library-management]] — скилл управления библиотекой блоков, куда входит этот блок

## Источник
- `block-library/trust/trust-luxury-centered-romanmelnikov-tilda-5/meta.yaml`