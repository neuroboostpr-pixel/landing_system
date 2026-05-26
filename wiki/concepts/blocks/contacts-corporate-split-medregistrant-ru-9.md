---
type: block
name: contacts-corporate-split-medregistrant-ru-9
sources: ["block-library/contacts/contacts-corporate-split-medregistrant-ru-9/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["contacts", "corporate", "split", "ru-market", "services", "medical", "b2b-saas"]
---

# Контактная секция на голубом фоне с логотипом, телефоном, иконками и формой заявки

## Что делает

Готовый блок «Контакты» для лендинга: голубой фон, логотип компании, телефон, иконки способов связи и форма заявки — всё в одном визуальном разделе. Разделён на два столбца (split-макет).

## Когда вызывать / в каком этапе

Используется на этапе **07b (Compose)** и **08 (Build)** при сборке страницы лендинга. Подходит для ниш: **медицина**, **B2B-услуги**, **SaaS**. Добавляется в блок-библиотеке при необходимости контактного раздела в корпоративном стиле.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции контактов.
- Логотип компании (из brand-kit).
- Телефон, иконки мессенджеров/способов связи (из brand-kit или content-файлов).
- Конфигурация формы заявки (из mu-plugin `landing-config`, REST endpoint `/wp-json/landing/v1/lead`).

**Выход:**
- HTML-блок секции контактов, готовый к встраиванию в `composed.html`.
- Лазиблок-шаблон (`block.php`) для WordPress-темы после этапа 08.

## Связанные концепты

Явных ссылок на другие концепты в исходнике нет.

## Источник

- `block-library/contacts/contacts-corporate-split-medregistrant-ru-9/meta.yaml`