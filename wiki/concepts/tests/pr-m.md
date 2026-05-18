Теперь у меня достаточно данных. Формирую wiki-страницу:

---
type: unknown
name: pr-m-tests
sources: ["tests/pr-m/README.md", "tests/pr-m/test_index_has_4_buttons.bats", "tests/pr-m/test_previews_generated.bats", "tests/pr-m/test_previews_have_iframes.bats", "tests/pr-m/helpers.bash"]
updated: 2026-05-18
triggers: []
stage: "07b"
uses: ["block-composer", "landing-compose", "landing-previews"]
tags: ["tests", "bats", "previews", "composed", "pr-m"]
---

# Тест-группа PR-M — превью composed.html

## Что делает

Проверяет работу скрипта `generate-previews.sh`, который генерирует HTML-обёртки для предпросмотра `composed.html` в разных разрешениях экрана (desktop, mobile, responsive-index). Убеждается, что все выходные файлы создаются корректно и содержат правильную разметку.

## Когда вызывать / в каком этапе

Запускается после этапа **07b (Compose)**, когда `07b_COMPOSED/composed.html` уже существует. Тесты являются частью CI-проверки PR-M и должны проходить до мержа любых изменений в `scripts/generate-previews.sh` или связанных командах.

```bash
bats tests/pr-m/
```

## Что на вход / на выход

**Вход:**
- Временный проект с минимальным `07b_COMPOSED/composed.html` (создаётся хелпером `make_project_with_composed`)
- `scripts/generate-previews.sh` — тестируемый скрипт

**Выход (проверяемые артефакты):**
- `07b_COMPOSED/composed-desktop-preview.html` — iframe 1280×800
- `07b_COMPOSED/composed-mobile-preview.html` — iframe 375×812
- `07b_COMPOSED/composed-previews-index.html` — responsive-переключатель с 4 кнопками (375 / 768 / 1280 / 1920) и JS-логикой переключения

**Проверяемые сценарии:**
| Файл теста | Что проверяет |
|---|---|
| `test_previews_generated.bats` | Все 3 файла созданы; exit 2 если `composed.html` отсутствует |
| `test_previews_have_iframes.bats` | Каждый preview-файл содержит `<iframe src="composed.html">` с правильными размерами |
| `test_index_has_4_buttons.bats` | Index содержит `data-w` кнопки на 375/768/1280/1920 и JS `addEventListener` |

## Связанные концепты

- [[block-composer]] — агент этапа 07b, создаёт `composed.html` который тесты берут как входной файл
- [[landing-compose]] — команда, запускающая этап 07b и генерацию composed.html
- [[landing-previews]] — команда, вызывающая `generate-previews.sh` в продакшн-сценарии

## Источник

- `tests/pr-m/README.md`
- `tests/pr-m/test_index_has_4_buttons.bats`
- `tests/pr-m/test_previews_generated.bats`
- `tests/pr-m/test_previews_have_iframes.bats`
- `tests/pr-m/helpers.bash`