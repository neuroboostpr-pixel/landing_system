Готово. Вот wiki-страница для группы тестов `preflight`:

---
type: rule
name: preflight-tests
sources: ["tests/preflight/README.md", "tests/preflight/test_preflight_lazy_blocks.bats"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["wp-cli-deployer", "wp-builder"]
tags: ["testing", "bats", "preflight", "lazy-blocks", "validate"]
---

# Тесты preflight

## Что делает
Группа bats-тестов, которая проверяет цепочку preflight-проверок системы: что скрипт `preflight.sh` делегирует работу в `validate-all.sh`, а тот в свою очередь убеждается, что в деплой-скрипте присутствует установка плагина `lazy-blocks`.

## Когда вызывать / в каком этапе
Запускается вручную перед деплоем или в CI, чтобы убедиться, что механизм preflight-проверок работает исправно. Не привязан к конкретному этапу pipeline — это мета-тест самой системы валидации.

```bash
# Bats-тесты
bats tests/preflight/
```

## Что на вход / на выход

**Вход:**
- `scripts/preflight.sh` — главный preflight-скрипт системы
- `scripts/validate-all.sh` — агрегирующий валидатор
- `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` — деплой-скрипт, который должен содержать установку `lazy-blocks`

**Выход:**
- exit 0 — все проверки прошли (цепочка preflight → validate-all → lazy-blocks intact)
- exit ≠ 0 + сообщение «lazy-blocks» — деплой-скрипт не содержит установку плагина; pipeline небезопасен

## Тест-кейсы

| Тест | Что проверяет |
|---|---|
| `preflight delegates to validate-all.sh` | В `preflight.sh` есть вызов `validate-all.sh` |
| `validate-all.sh checks deploy script for lazy-blocks install` | `validate-all.sh` проверяет наличие строки `lazy-blocks` в деплой-скрипте |
| `validate-all.sh fails fast when deploy script lacks lazy-blocks install` | При подменённом (сломанном) деплой-скрипте — выход с ошибкой и упоминание `lazy-blocks` в выводе |

## Связанные концепты
- [[wp-cli-deployer]] — содержит `deploy-wordpress.sh`, который тесты проверяют на наличие установки `lazy-blocks`
- [[wp-builder]] — этап 08, генерирует Lazy Blocks; их корректная установка — причина существования этих тестов

## Источник
- `tests/preflight/README.md`
- `tests/preflight/test_preflight_lazy_blocks.bats`