---
name: wp-multisite
description: Manage WordPress Multisite networks on Beget shared hosting — migration from single-site, segment creation, subsite cloning. Use when a project needs more than one landing under one client domain.
---

# wp-multisite

Скилл управляет WordPress Multisite-сетями на Beget shared hosting:
миграция single-site → multisite, создание сегментов ЦА (поддоменов),
клонирование контента между сегментами.

Все скрипты валидированы POC на ailexi.ru — см. [tests/poc/RESULTS.md](../../tests/poc/RESULTS.md).

## Скрипты

### migrate-to-multisite.sh
```bash
bash skills/wp-multisite/scripts/migrate-to-multisite.sh <project-dir>
```
Превращает single-site WordPress проект в multisite (subdomain mode).
Идемпотентен. Read `.landing-state.yaml::multisite` — если уже `true`, no-op.

### landing-segment.sh
```bash
bash skills/wp-multisite/scripts/landing-segment.sh <project-dir> <segment-slug>
```
Создаёт новый сегмент ЦА: Beget subdomain + WP subsite + skeleton директории
`<project>/13_СЕГМЕНТЫ_ЦА/<slug>/`. Если проект ещё single-site —
автоматически запускает миграцию.

### clone-subsite.sh
```bash
bash skills/wp-multisite/scripts/clone-subsite.sh <project-dir> <source-slug> <dest-slug>
```
Копирует все страницы из source-сегмента в новый dest-сегмент.
Byte-by-byte: текст, фото-ссылки, опции (siteurl/home переписываются).

## Lib

- `lib/beget-api.sh` — обёртка Beget API
- `lib/ssh-helpers.sh` — SSH + wp-cli обёртки
- `lib/state.sh` — read/write `.landing-state.yaml`
