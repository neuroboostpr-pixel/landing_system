---
type: block
name: cta-minimal-split-portfolio-kdm1-ru-8
sources: ["block-library/cta/cta-minimal-split-portfolio-kdm1-ru-8/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: "07b"
uses: ["landing-compose", "landing-wireframe", "landing-build"]
tags: ["cta", "minimal", "split", "ru-market", "ecommerce", "services", "education"]
---

# Контактная форма в светлой карточке (CTA Minimal Split)

## Что делает
Блок призыва к действию: контактная форма в светлой карточке расположена рядом с lifestyle-фотографией. Заметная кнопка отправки побуждает пользователя оставить заявку прямо с экрана.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** при сборке `composed.html`. Подходит для финального CTA-блока лендинга — там, где нужно совместить визуальный lifestyle-образ с формой захвата. Выбирается в `wireframe.html` как один из вариантов CTA-секции; после подтверждения `selections.yaml` автоматически встраивается в composed-версию.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок над формой
- Lifestyle-фотография в слоте изображения (подставляется из `07c_PHOTOS/` после фото-пайплайна)
- Данные формы и CRM-интеграции из mu-plugin `landing-config`

**Выход:**
- HTML-секция CTA с двухколоночным split-лейаутом: левая часть — светлая карточка с формой, правая — lifestyle-фото
- Готовый блок в `composed.html` / финальном WordPress-шаблоне
- Lazy Block PHP-шаблон на этапе 08 Build

## Связанные концепты
- [[landing-compose]] — этап сборки composed.html, куда вставляется блок
- [[landing-wireframe]] — на этом этапе пользователь выбирает блок из 2–3 вариантов
- [[landing-build]] — генерирует Lazy Blocks PHP-шаблон для WordPress
- [[landing-photos]] — поставляет lifestyle-фото для слота изображения (этап 07c)

## Источник
- `block-library/cta/cta-minimal-split-portfolio-kdm1-ru-8/meta.yaml`