---
type: rule
name: validate-palettes
sources: ["scripts/validate-palettes.py", "scripts/validate-palettes.py.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["design-tokens-generation", "brand-kit-build"]
tags: ["python", "validation", "palette", "yaml", "ci"]
---

# validate-palettes — валидатор библиотеки палитр

## Что делает

Проверяет YAML-файл с палитрами на соответствие зафиксированной схеме: наличие обязательных полей, правильный формат `id` в kebab-case, отсутствие дублей и наличие всех 20 обязательных цветовых токенов в каждой палитре.

## Когда вызывать / в каком этапе

Вызывается вручную или через CI перед коммитом/мержем любых изменений в файле `palettes.yaml` (библиотека палитр дизайн-системы). Особенно актуален на этапе **05 (design-system)**, когда формируются токены бренда.

```bash
python3 scripts/validate-palettes.py path/to/palettes.yaml
```

При успехе печатает `OK: N palette(s) valid`, при ошибке завершается с `exit 1` и описанием проблемы в stderr.

## Что на вход / на выход

**Вход:**
- YAML-файл с ключом `palettes` — список объектов палитры.

Каждый объект обязан содержать поля: `id`, `name`, `description`, `created_at`, `created_in_project`, `tokens`.

Поле `tokens` — словарь с 20 обязательными ключами:
`bg_base`, `bg_section`, `bg_elevated`, `border_subtle`, `border_strong`,
`text_primary`, `text_soft`, `text_dim`, `accent_mint`, `accent_teal`,
`accent_coral`, `accent_coral_hover`, `accent_coral_text`,
`accent_rgb_mint`, `accent_rgb_coral`, `card_bg`, `card_border`,
`card_border_hover`, `accent_cta_glow_opacity`.

**Выход:**
- `stdout`: строка `OK: N palette(s) valid in <path>` при успехе.
- `stderr` + `exit 1`: сообщение об ошибке (невалидный YAML, отсутствующее поле, неправильный `id`, дубль, нехватающий токен).

## Связанные концепты

- [[design-tokens-generation]] — скилл генерации токенов; палитры — его исходный материал
- [[brand-kit-build]] — скилл сборки бренд-кита; опирается на валидные палитры

## Источник

- `scripts/validate-palettes.py`
- `scripts/validate-palettes.py.doc.md`