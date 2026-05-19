---
description: Создать новый сегмент целевой аудитории — поддомен + WordPress subsite + skeleton директории. Если проект ещё single-site, автоматически мигрирует в multisite.
allowed-tools: Bash, Read
---

# /landing-segment

Создаёт новый сегмент целевой аудитории (subsite в multisite-сети WordPress) для текущего
landing-проекта.

## Использование

```
/landing-segment <slug>
```

Пример: `/landing-segment russian`

`<slug>` — имя сегмента, регекс `^[a-z][a-z0-9-]*$` (только нижний регистр,
цифры, дефисы; начинается с буквы).

## Что делаю

1. Проверяю что есть `.landing-state.yaml` + `.env` в текущей папке проекта.
2. Если `state.multisite=false` — запускаю `migrate-to-multisite.sh` (одноразово).
3. Создаю Beget subdomain `<slug>.<корневой-домен>` через API.
4. Создаю WordPress subsite (`wp site create --slug=<slug>`).
5. Копирую `13_СЕГМЕНТЫ_ЦА/_skeleton/` → `13_СЕГМЕНТЫ_ЦА/<slug>/`.
6. Записываю сегмент в `.landing-state.yaml::audience_segments[]`.
7. Сообщаю URL нового сегмента + следующий шаг для маркетолога.

## После выполнения

1. Открой `13_СЕГМЕНТЫ_ЦА/<slug>/subbrief.yaml` — заполни описание целевой аудитории.
2. (Будущая фаза CD2) запусти pipeline генерации контента под сегмент.
3. (Будущая фаза CD2) задеплой контент в новый subsite.

## Скрипт

`skills/wp-multisite/scripts/landing-segment.sh <project-dir> <slug>`
