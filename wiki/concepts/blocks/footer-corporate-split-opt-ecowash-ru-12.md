---
type: block
name: footer-corporate-split-opt-ecowash-ru-12
sources: ["block-library/footer/footer-corporate-split-opt-ecowash-ru-12/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer"]
tags: ["footer", "corporate", "split", "ru-market", "dark", "no-animation"]
---

# Футер корпоративный split — тёмный с логотипной зоной (opt.ecowash.ru)

## Что делает
Тёмный нижний блок-футер с тремя зонами: логотип, центральная кнопка связи и строка служебных ссылок. Подходит для строгих корпоративных лендингов без анимации.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Block Compose)** при сборке `composed.html`. Агент [[block-composer]] выбирает блок из библиотеки согласно `selections.yaml`, сформированному на этапе 07a. Агент [[ux-composer]] может предложить этот блок в wireframe при генерации вариантов футера для ниш `services`, `ecommerce`, `b2b-saas`.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — заголовок или слоган в зоне кнопки связи.
- Токены дизайна из `tokens.json` (цвета, типографика) для инъекции на этапе compose.

**Выход:**
- HTML-фрагмент футера, встраиваемый в `composed.html`.
- Тёмный фон, логотипная зона слева, CTA-кнопка по центру, служебные ссылки снизу.

## Характеристики блока

| Параметр | Значение |
|---|---|
| Категория | footer |
| Паттерн раскладки | split |
| Настроение стиля | corporate |
| Анимация | нет |
| Рынок | RU |
| Подходящие ниши | услуги, e-commerce, b2b-saas |
| Источник импорта | opt.ecowash.ru |
| Метод импорта | codex-block-generation |

## Связанные концепты
- [[block-composer]] — агент этапа 07b, инжектирует токены и подставляет тексты в слоты блока
- [[ux-composer]] — агент этапа 07a, предлагает блок при построении wireframe-вариантов
- [[block-composition]] — скилл, описывающий процесс сборки composed.html из блоков библиотеки
- [[block-library-management]] — скилл управления библиотекой блоков, импорт и каталогизация

## Источник
- `block-library/footer/footer-corporate-split-opt-ecowash-ru-12/meta.yaml`