---
type: rule
name: api-validators-tests
sources: ["tests/api_validators/README.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["system-setup", "wp-deployer", "analytics-engineer", "integrations-engineer", "seo-optimizer"]
tags: ["tests", "pytest", "api", "validation", "credentials"]
---

# API Validators — тест-группа

## Что делает
Проверяет, что все внешние API-ключи и сервисные подключения в системе настроены корректно. Каждый тест имитирует реальный вызов сервиса через моки и проверяет три сценария: отсутствие ключа, валидный ключ, невалидный ответ.

## Когда вызывать / в каком этапе
Запускается вручную или в CI перед любым деплоем. Особенно важен после изменений в `.env` или конфигурации системы. Связан со стадией `system-setup` — именно там пользователь вводит ключи, которые эти тесты валидируют.

## Что на вход / на выход

**Вход:**
- Переменные окружения (API-ключи) из `.env` / shell-окружения
- `conftest.py` с фикстурой `clean_env` — автоматически очищает все 20 переменных перед каждым тестом

**Выход:**
- `ValidationResult(is_valid, message, service)` — dataclass с булевым результатом и описанием
- `run_all(only=[...])` — агрегатный прогон всех 15 сервисов одновременно, возвращает список `ValidationResult`

**Покрываемые сервисы (15):**

| Категория | Сервисы |
|---|---|
| Медиа / фото | firecrawl, pexels, unsplash, pixabay, huggingface, whatthefont |
| Аналитика | yandex_metrika, yandex_wordstat |
| Интеграции | telegram, amocrm, bitrix24 |
| Хостинг / DNS | beget_ssh, beget_api, cloudflare, regru |

**Запуск:**
```bash
pytest tests/api_validators/
# или только конкретный файл:
pytest tests/api_validators/test_beget_ssh.py
```

## Связанные концепты
- [[system-setup]] — онбординг вводит ключи, которые проверяют эти тесты
- [[wp-deployer]] — использует `beget_ssh` и `beget_api` для деплоя
- [[analytics-engineer]] — использует `yandex_metrika`
- [[integrations-engineer]] — использует `telegram`, `amocrm`, `bitrix24`
- [[seo-optimizer]] — использует `yandex_wordstat`

## Источник
- `tests/api_validators/README.md`