---
type: block
name: ru-cta-06-editorial-paper
sources: ["block-library/cta/ru-cta-06-editorial-paper/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["cta", "editorial", "ru_market", "b2c", "services", "local", "opendesign"]
---

# Редакционный CTA — бежевый, курсив, пульс, нумерация

## Что делает
Финальный призыв к действию в редакционном стиле: бежевый фон, курсивный заголовок, пульсирующая точка рядом с нижней сноской и нумерация раздела римскими цифрами. Подходит для сервисного и B2C-лендинга на российский рынок.

## Когда вызывать / в каком этапе
Используется на этапе **07a Wireframe** и **07b Compose**. Агент [[ux-composer]] подбирает блок из библиотеки при построении wireframe.html; агент [[block-composer]] инжектирует токены и тексты при рендере composed.html. Рекомендован для стилей «Editorial & Magazine» и «Minimalism & Swiss Style».

## Что на вход / на выход

**Вход:**
- Тексты слотов из `prototype.yaml`: заголовок (обязательно, до 80 символов), подзаголовок (до 220 символов), текст кнопок, нижняя сноска, нумерация раздела.
- Изображение в слоте `cta-image` (соотношение 1:1) — необязательно; на мобайле скрывается автоматически.
- Токены дизайна из `tokens.json` (цвета, шрифты).

**Выход:**
- HTML-блок в составе `wireframe.html` (этап 07a) или `composed.html` (этап 07b).
- Двухколоночный layout: текст слева, изображение справа. На мобайле — вертикальный стек без изображения.

## Слоты

| Имя слота | Тип | Обязательный | Лимит |
|---|---|---|---|
| `section-num` | text | нет | 10 символов |
| `section-label` | text | нет | 40 символов |
| `section-index` | text | нет | 6 символов |
| `kicker` | text | нет | 50 символов |
| `headline` | text | **да** | 80 символов |
| `subhead` | text | нет | 220 символов |
| `primary-cta` | cta | **да** | — |
| `secondary-cta` | cta | нет | — |
| `footer-note` | text | нет | 60 символов |
| `cta-image` | photo (1:1) | нет | скрыт на mobile |

## Конверсионные заметки
Пульсирующая точка у `footer-note` создаёт ощущение активности («сейчас онлайн»). Нумерация разделов строит финальность — пользователь понимает, что это последний блок. **Не использовать** кнопки WhatsApp/Telegram.

## Атрибуция
Основан на стиле `cta-section` из репозитория `nexu-io/open-design` (Apache-2.0).

## Связанные концепты
- [[ux-composer]] — выбирает блок при построении wireframe на этапе 07a
- [[block-composer]] — инжектирует токены и тексты прототипа в этапе 07b
- [[wireframe-rendering]] — скилл рендера wireframe.html с кандидатами блоков
- [[block-composition]] — скилл compose-этапа, финальная сборка composed.html
- [[block-library-management]] — скилл управления библиотекой блоков

## Источник
- `block-library/cta/ru-cta-06-editorial-paper/meta.yaml`