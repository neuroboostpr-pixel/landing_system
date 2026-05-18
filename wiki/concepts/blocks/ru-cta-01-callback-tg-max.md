---
type: block
name: ru-cta-01-callback-tg-max
sources: ["block-library/cta/ru-cta-01-callback-tg-max/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["cta", "ru_market", "telegram", "b2c", "services", "local"]
---

# 📞 CTA: Telegram / Max / Перезвоните

## Что делает

CTA-блок для российского рынка: предлагает посетителю три способа выйти на связь — Telegram, Max и обратный звонок. WhatsApp намеренно исключён как запрещённый в РФ мессенджер.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при выборе CTA-блока для услуговых, B2C или локальных лендингов. Подключается через `ux-composer` при сборке wireframe.html и через `block-composer` на этапе 07b Compose. Рекомендован когда целевая аудитория — российский пользователь, для которого Max является основной альтернативой WhatsApp.

## Что на вход / на выход

**Слоты (входные данные):**

| Слот | Тип | Обязателен | Лимит |
|---|---|---|---|
| `headline` | текст | да | 80 символов |
| `subhead` | текст | нет | 140 символов |
| `tg-cta` | кнопка-ссылка | да | текст по умолчанию: «Написать в Telegram» |
| `max-cta` | кнопка-ссылка | да | текст по умолчанию: «Написать в Max» |
| `callback-cta` | кнопка-ссылка | да | текст по умолчанию: «Перезвоните мне» |

**На выход:** HTML-секция с заголовком, подзаголовком и тремя CTA-кнопками, адаптированная под стили Flat Design 2.0 или Minimalism & Swiss Style.

**Конверсионная логика:** три параллельных канала связи снижают трение — пользователь выбирает удобный мессенджер. Наличие Max критично для аудитории, перешедшей с запрещённых платформ.

**Рекомендуемые стили:**
- Flat Design 2.0
- Minimalism & Swiss Style

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe
- [[block-composer]] — инжектирует токены и тексты прототипа в слоты блока
- [[wireframe-rendering]] — рендерит интерактивный вариант блока в wireframe.html
- [[block-composition]] — этап 07b, финальная сборка composed.html
- [[block-library-management]] — управление каталогом блоков, куда входит этот блок

## Источник

- `block-library/cta/ru-cta-01-callback-tg-max/meta.yaml`