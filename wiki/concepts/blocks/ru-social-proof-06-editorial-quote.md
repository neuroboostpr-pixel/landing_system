---
type: block
name: ru-social-proof-06-editorial-quote
sources: ["block-library/social-proof/ru-social-proof-06-editorial-quote/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-library-management"]
tags: ["social-proof", "testimonial", "editorial", "serif", "partners", "b2c", "ru-market"]
---

# Редакционная цитата — засечный шрифт + партнёры

## Что делает
Отображает отзыв клиента в виде редакционной цитаты: крупный курсивный засечный шрифт создаёт журнальную атмосферу доверия, а блок логотипов/имён партнёров добавляет B2B-авторитетность рядом с фото автора.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** при сборке `composed.html`. Подходит для лендингов услуг, B2C и локального бизнеса, где важно передать редакционный или экспертный тон — особенно в стилях **Editorial & Magazine** и **Minimalism & Swiss Style**.

## Что на вход / на выход

**Вход:**
- Текстовые слоты: цитата (обязательно, до 280 символов), имя и роль автора (обязательно), инициал-аватар, кикер, метка раздела с roman-нумерацией, до 3 партнёров с подписями
- Фото: `testimonial-image` (пропорция 4:5, на мобайле пропускается)
- Данные дизайн-токенов из `tokens.json` (цвета, типографика)

**Выход:**
- HTML-блок, вставленный в `07b_COMPOSED/composed.html`
- Двухколоночный layout: слева — цитата + автор + список партнёров, справа — портретное фото
- На мобайле — вертикальный стек

## Детали слотов

| Слот | Тип | Макс. символов | Обязателен |
|---|---|---|---|
| quote | text | 280 | да |
| author-name | text | 60 | да |
| author-role | text | 80 | да |
| author-initial | text | 3 | нет |
| section-num / section-label | text | 10 / 40 | нет |
| partner-1…3 + roles | text | 40 / 30 | нет |
| testimonial-image | photo 4:5 | — | нет |

## Рекомендации по контенту
Использовать реальные цитаты с конкретными результатами — это ключевой фактор конверсии. Список партнёров работает как социальное доказательство для B2B-аудитории внутри B2C-страницы.

## Связанные концепты
- [[block-composer]] — рендерит блок в composed.html на этапе 07b
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe (07a)
- [[block-library-management]] — управление каталогом блоков, регистрация новых блоков
- [[block-composition]] — скилл, описывающий логику подстановки токенов и текстов в блоки

## Атрибуция
Блок основан на шаблоне OpenDesign (`open-design-landing`, лицензия **Apache-2.0**).
Оригинал: `github.com/nexu-io/open-design`

## Источник
- `block-library/social-proof/ru-social-proof-06-editorial-quote/meta.yaml`