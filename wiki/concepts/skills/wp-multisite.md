---
slug: wp-multisite
type: skill
name: "WP Multisite — управление Multisite-сетью на Beget"
tags: [multisite, beget, wordpress, segments, cloning]
triggers: [landing-segment, landing-clone]
inputs: ["<project-dir>/.landing-state.yaml", "<project-dir>/13_СЕГМЕНТЫ_ЦА/"]
outputs: ["<project-dir>/13_СЕГМЕНТЫ_ЦА/<slug>/", ".landing-state.yaml::multisite", ".landing-state.yaml::audience_segments[]"]
pre_reqs: [wp-deployer, wp-builder]
related: [landing-orchestrator, wp-builder, wp-deployer, lifecycle-keeper]
sources: ["skills/wp-multisite/SKILL.md"]
updated: 2026-05-26
confidence: {triggers: low, pre_reqs: low}
---

# WP Multisite — управление Multisite-сетью на Beget

## Что делает

Скилл превращает одиночный WordPress-лендинг на Beget в полноценную Multisite-сеть и управляет её сегментами. Позволяет под одним клиентским доменом (например `liauto.dubai`) держать несколько отдельных поддоменов (`russian.liauto.dubai`, `family.liauto.dubai`) — каждый как самостоятельный WP-сабсайт. Обеспечивает три операции: миграцию single-site → multisite (идемпотентно), создание нового сегмента ЦА с Beget-поддоменом и скелетом директорий, а также byte-by-byte клонирование контента между сегментами.

## Когда вызывается

Вызывается командами `/landing-segment <slug>` (создать сегмент ЦА) и `/landing-clone <source> <dest>` (скопировать сегмент). Если проект ещё не в режиме multisite — `landing-segment.sh` сам запускает миграцию перед созданием сабсайта. `migrate-to-multisite.sh` может вызываться напрямую для ручной миграции.

## Вход → выход

**Вход:** директория проекта с валидным `.landing-state.yaml`, задеплоенным WordPress-сайтом на Beget, переменными окружения `BEGET_*` (включая `BEGET_SITE_ID` — обязателен для multisite), SSH-доступом и wp-cli.

**Выход:** флаг `multisite: true` и массив `audience_segments[]` в `.landing-state.yaml`; Beget-поддомен; WP-сабсайт с blog_id; скелет `13_СЕГМЕНТЫ_ЦА/<slug>/` с `subbrief.yaml` и `.subsite-meta.yaml`; при клонировании — полная копия страниц, медиа-ссылок и WP-опций (siteurl/home переписываются под новый поддомен).

## Чем не является

Скилл не управляет контентом сегментов — только инфраструктурой (сеть, поддомены, сабсайты). Заполнение `subbrief.yaml` — задача маркетолога.

## Failure modes

- **`BEGET_SITE_ID` не задан** — скрипт не может зарегистрировать поддомен через Beget API; миграция падает на первом шаге.
- **WP-сайт ещё не задеплоен** — `migrate-to-multisite.sh` находит пустой public_html, прерывается.
- **wp-cli недоступен по SSH** — все три скрипта зависят от wp-cli; нет wp-cli → нет операции.
- **Сабсайт с тем же slug уже существует** — `landing-segment.sh` не идемпотентен по созданию WP-сабсайта (только `migrate-to-multisite.sh` идемпотентен); возможен дубль записи в `audience_segments[]`.
- **DNS-пропагация поддомена** — Beget регистрирует поддомен через API, но реальная доступность может занять минуты; последующие wp-cli команды в том же прогоне могут завершиться ошибкой timeout.

## Related

- [[landing-orchestrator]] — диспатчит мультисайт-этапы через `.landing-state.yaml`
- [[wp-builder]] — собирает тему до того, как multisite-сегмент начинает использоваться
- [[wp-deployer]] — деплоит исходный single-site, который затем мигрирует
- [[lifecycle-keeper]] — ведёт актуальность `.landing-state.yaml` между этапами