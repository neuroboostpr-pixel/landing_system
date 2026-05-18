---
type: rule
name: check-block-registration
sources: ["scripts/lib/check-block-registration.sh"]
updated: 2026-05-18
triggers: []
stage: "08"
uses: ["wp-builder", "wp-gutenberg-block-builder", "stage-gates"]
tags: ["bash", "hard-check", "lazy-blocks", "functions.php", "gate"]
---

# check-block-registration — Проверка регистрации Lazy Blocks

## Что делает

Скрипт-гейт проверяет, что все блоки Lazy Blocks правильно зарегистрированы в `functions.php` через хук `lzb/init`. Это обязательное условие перед переходом дальше по этапу 08 (код → деплой).

## Когда вызывать / в каком этапе

Запускается на этапе **08** как часть `gate-check.sh` перед финальной сборкой и деплоем. Вызывается автоматически `landing-orchestrator` после того, как `wp-builder` или `wp-gutenberg-block-builder` сгенерировали тему. При отсутствии регистрации гейт падает и дальнейший прогресс блокируется.

Можно обойти через `legacy: true` в `.landing-state.yaml` — это разрешено для старых проектов, где блоки зарегистрированы иначе.

## Что на вход / на выход

**Вход:**
- `functions.php` текущей темы WordPress (должен содержать вызов `lazyblocks()->add_block()` внутри хука `lzb/init`)
- `.landing-state.yaml` — читается флаг `legacy: true` для обхода проверки

**Выход:**
- `exit 0` — регистрация найдена (или `legacy: true`), гейт пройден
- `exit 1` + сообщение об ошибке — регистрация отсутствует, этап заблокирован

## Технические детали

Ожидаемый паттерн регистрации в `functions.php`:

```php
add_action( 'lzb/init', function() {
    lazyblocks()->add_block( ... );
} );
```

Стандартный WordPress `register_block_type()` не принимается — скрипт явно проверяет именно `lazyblocks()->add_block(`.

## Связанные концепты

- [[wp-builder]] — генерирует `functions.php` с регистрацией блоков через `lzb/init`
- [[wp-gutenberg-block-builder]] — скилл сборки Gutenberg-блоков, обязан соблюдать паттерн
- [[stage-gates]] — общая система жёстких гейтов между этапами pipeline

## Источник

- `scripts/lib/check-block-registration.sh`