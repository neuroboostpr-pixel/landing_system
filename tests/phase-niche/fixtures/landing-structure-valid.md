# Структура лендинга: Test

> Тип бренда: 2
> Режим: emotional_aspiration
> Дата: 2026-05-06

## Блоки лендинга (в порядке отображения)

| # | Блок | Обязательный? | Цель | Содержание (откуда) |
|---|---|---|---|---|
| 1 | Hero | yes | hook | positioning §3 |
| 2 | Brand short story | yes | trust | brand-kit §1 |
| 3 | Featured Models | yes | catalog | models data |
| 4 | Trust signals | yes | warranty | brief |
| 5 | CTA | yes | conversion | positioning §5 |
| 6 | FAQ | optional | objections | content |
| 7 | Footer | yes | legal | brief |

## Обоснование выбора структуры
Тип 2 + emotional_aspiration: brand story нужна (региональный бренд),
catalog — основной контент, lifestyle опционален.

## Что НЕ включаем (и почему)
- About-Founder: бренд не personality-driven

## Контракт с wp-builder
Список template-parts:
- block-hero.php
- block-brand-story.php
- block-models.php
- block-trust.php
- block-cta.php
- block-faq.php
- block-footer.php
