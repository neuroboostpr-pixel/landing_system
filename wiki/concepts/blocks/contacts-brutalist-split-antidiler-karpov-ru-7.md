---
type: block
name: contacts-brutalist-split-antidiler-karpov-ru-7
sources: ["block-library/contacts/contacts-brutalist-split-antidiler-karpov-ru-7/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["contacts", "brutalist", "split", "premium-auto", "luxury", "services", "ru-market"]
---

# Контактная полоса с крупным номером (brutalist-split)

## Что делает
Отображает контактный блок в брутальном стиле: крупный телефонный номер занимает половину полосы, рядом — подпись и небольшая оранжевая ссылка. Привлекает внимание без анимаций, за счёт жирной типографики и контрастного разделения пространства.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при подборе блоков секции «Контакты». Подходит для ниш премиум-авто, услуг и люксового сегмента, ориентированных на российский рынок. `ux-composer` выбирает блок из библиотеки при наличии `contacts`-слота в `prototype.yaml`. На этапе **07b (Compose)** `block-composer` заполняет текстовый слот `heading` из прототипа.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — секция с контактами, из которой берётся текст `heading`
- `tokens.json` — дизайн-токены (цвет ссылки, типографика)
- `selections.yaml` — выбор именно этого варианта блока пользователем

**Выход:**
- HTML-фрагмент блока, встраиваемый в `wireframe.html` (этап 07a)
- Заполненный блок в `composed.html` (этап 07b) с реальным текстом из прототипа

**Слоты:**
| Имя | Тип | Обязателен |
|-----|-----|-----------|
| `heading` | text | да |

**Параметры блока:**
- Стиль: `brutalist`
- Раскладка: `split`
- Анимация: нет
- Импортирован с: `antidiler-karpov.ru` (2026-05-16, метод: codex-block-generation)

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[block-composer]] — наполняет слот `heading` текстом из прототипа на этапе 07b
- [[wireframe-rendering]] — рендерит вариант блока в интерактивный wireframe.html
- [[block-composition]] — скилл сборки composed.html, куда встраивается этот блок
- [[block-library-management]] — управляет реестром всех блоков, включая этот

## Источник
- `block-library/contacts/contacts-brutalist-split-antidiler-karpov-ru-7/meta.yaml`