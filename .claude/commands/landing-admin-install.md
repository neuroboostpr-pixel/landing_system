---
description: Установить mu-plugin landing-config на текущий проект (через rsync на Beget). Авто-активируется (mu-plugins always-active), создаёт таблицы wp_<bid>_landing_leads, регистрирует REST /wp-json/landing/v1/lead.
allowed-tools: Bash, Read
---

# /landing-admin-install

Копирует `skills/wp-landing-config/mu-plugin/landing-config/` на Beget,
триггерит миграцию БД, проверяет что REST endpoint отвечает.

## Использование

```
/landing-admin-install
```

(вызывается из корня landing-проекта где есть `.env`)

## Что делаю

1. Запускаю `bash skills/wp-landing-config/scripts/install-mu-plugin.sh .`
2. После rsync — выполняю `bash skills/wp-landing-config/scripts/test-smoke-rest.sh .`
   чтобы проверить:
   - таблица `wp_<bid>_landing_leads` создалась на всех subsite
   - REST endpoint `/wp-json/landing/v1/lead` отвечает 200 на валидный POST
3. Сообщаю URL admin pages для каждого subsite.

## После выполнения

Зайди в `<subsite-url>/wp-admin/` → меню «Лендинг» → 4 подстраницы
(Заявки/CTA/Head/Интеграции).

В A1 (текущая фаза) реализованы только: каркас, БД, REST endpoint, email-fallback.
Полная функциональность подстраниц — в фазах A2-A5.
