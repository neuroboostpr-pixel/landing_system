# classify-prompt — photo tagging template

## How to use

1. Pass via codex CLI with `--image <photo_path>` flag (mechanism confirmed in Task 0 research).
2. Substitute `[NICHE]`, `[AUDIENCE]`, `[VISUAL_STYLE]`, `[BRAND_PRIMARY]` via `render-prompt.py`.
3. Expect strict YAML output. Validate with `yaml.safe_load`.

## Placeholders

- `[NICHE]` — niche label from `01a_АНАЛИЗ_НИШИ/market-profile.md`
- `[AUDIENCE]` — audience description from `01a_АНАЛИЗ_НИШИ/positioning.md`
- `[VISUAL_STYLE]` — `tokens.json:design.visual_style`
- `[BRAND_PRIMARY]` — `tokens.json:colors.primary`

## Prompt body

```
ВОЗВРАЩАЙ СТРОГО YAML, БЕЗ КОММЕНТАРИЕВ ДО И ПОСЛЕ. НЕ ИСПОЛЬЗУЙ MARKDOWN CODE FENCES.

Ты анализируешь фотографию для лендинга в нише [NICHE], целевая аудитория [AUDIENCE].
Brand style: [VISUAL_STYLE], primary color [BRAND_PRIMARY].

Верни строго YAML со следующими ключами:
tags: список из набора [portrait, group, object, process, interior, exterior, before-after, document, team, abstract]
caption: одна строка на русском, до 100 символов, описывающая что на фото
face_count: число лиц на фото
composition: одно из [tight-portrait, medium-shot, wide-shot, object-only]
usable_ratios: список из [1:1, 4:3, 3:4, 16:9, 9:16] — где фото обрежется без потери сюжета
brand_compatible: одно из [yes, no, maybe] — насколько цвета/настроение фото подходят к brand style
notes: технические дефекты (размытие, шум, плохой свет) или пустая строка

Пример валидного ответа:
tags: [portrait, team]
caption: "Женщина 35 лет, улыбается, светлый офис на фоне"
face_count: 1
composition: medium-shot
usable_ratios: ["1:1", "3:4"]
brand_compatible: yes
notes: ""
```

## Filled example

When [NICHE]=услуги, [AUDIENCE]=владельцы малого бизнеса 35-50, [VISUAL_STYLE]=Minimalism & Swiss Style, [BRAND_PRIMARY]=#1e3a8a:

```
ВОЗВРАЩАЙ СТРОГО YAML, БЕЗ КОММЕНТАРИЕВ ДО И ПОСЛЕ. НЕ ИСПОЛЬЗУЙ MARKDOWN CODE FENCES.

Ты анализируешь фотографию для лендинга в нише услуги, целевая аудитория владельцы малого бизнеса 35-50.
Brand style: Minimalism & Swiss Style, primary color #1e3a8a.

Верни строго YAML со следующими ключами:
tags: список из набора [portrait, group, object, process, interior, exterior, before-after, document, team, abstract]
caption: одна строка на русском, до 100 символов, описывающая что на фото
face_count: число лиц на фото
composition: одно из [tight-portrait, medium-shot, wide-shot, object-only]
usable_ratios: список из [1:1, 4:3, 3:4, 16:9, 9:16] — где фото обрежется без потери сюжета
brand_compatible: одно из [yes, no, maybe] — насколько цвета/настроение фото подходят к brand style
notes: технические дефекты (размытие, шум, плохой свет) или пустая строка
```
