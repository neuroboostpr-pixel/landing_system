---
type: rule
name: tests-deploy
sources: ["tests/deploy/README.md"]
updated: 2026-05-18
triggers: []
stage: "09"
uses: ["wp-deployer", "wp-builder", "wp-cli-deployer"]
tags: ["tests", "bats", "deploy", "lazy-blocks"]
---

# Тесты деплоя (tests/deploy)

## Что делает
Группа автотестов, которая проверяет корректность деплоя WordPress-темы на Бегет: Lazy Blocks зарегистрированы, файлы скопированы, wp-cli отработал без ошибок.

## Когда вызывать / в каком этапе
Этап **09 — Deploy**. Запускаются после того, как `wp-deployer` завершил деплой на хостинг. Также рекомендуется запускать локально перед `git push`, чтобы убедиться, что Lazy Blocks корректно собраны `wp-builder`-ом.

## Что на вход / на выход

**Вход:**
- Готовая WordPress-тема в `08_КОД/` (Lazy Blocks, `functions.php`, page-content.html)
- Настроенное SSH-подключение к Бегету (конфиг в `.env`)

**Выход:**
- Результаты bats-прогона (pass / fail по каждому `@test`)
- При наличии `test_*.py` — результаты pytest

**Файлы тестов:**
- `tests/deploy/test_deploy_lazy_blocks.bats` — проверка что Lazy Blocks деплоятся правильно

## Запуск

```bash
# Bats-тесты
bats tests/deploy/

# Pytest (если есть test_*.py)
pytest tests/deploy/
```

## Связанные концепты
- [[wp-deployer]] — агент, который выполняет сам деплой; тесты верифицируют его результат
- [[wp-builder]] — собирает Lazy Blocks до деплоя; тесты проверяют корректность сборки
- [[wp-cli-deployer]] — скилл низкого уровня, используемый при деплое через wp-cli

## Источник
- `tests/deploy/README.md`