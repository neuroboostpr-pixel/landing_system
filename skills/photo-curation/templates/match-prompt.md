# match-prompt — photo-to-slot matcher template

## How to use

1. Build context: read `catalog.yaml`, `prototype.yaml` slots, `tokens.json`, market-profile, positioning.
2. Build `[CATALOG_YAML]` (dump catalog photos list) and `[SLOTS_YAML]` (dump active slots with hints).
3. Substitute via render-prompt.py.
4. Pass via codex CLI (text-only, no image input).
5. Validate output as YAML.

## Placeholders

- `[CATALOG_YAML]` — YAML dump of `catalog.yaml:photos`
- `[SLOTS_YAML]` — YAML dump of active photo slots (id, block_id, ratio, mobile_ratio, hint)
- `[BRAND_PRIMARY]`, `[VISUAL_STYLE]`, `[NICHE]`, `[AUDIENCE]` — from `render-prompt.load_context`

## Prompt body

```
ВОЗВРАЩАЙ СТРОГО YAML, БЕЗ КОММЕНТАРИЕВ.

Тебе дан каталог фотографий клиента и список photo-слотов из прототипа лендинга.
Подбери top-3 фото на каждый слот. Если для слота ни одна фотка не подходит — candidates=[] и ai_fallback_needed=true.

Каталог:
[CATALOG_YAML]

Слоты:
[SLOTS_YAML]

Brand context:
- primary: [BRAND_PRIMARY]
- visual_style: [VISUAL_STYLE]
- niche: [NICHE]
- audience: [AUDIENCE]

Правила matching:
- ratio фото (после crop) должно совпадать или близко к slot.ratio
- tag фото должен соответствовать hint слота
- testimonial-* / expert-* / team-* слоты (identity-safe) требуют tag=portrait или group, face_count>=1
- hero-bg требует composition=wide-shot, usable_ratios содержит 16:9
- безопасные слоты (background, process, abstract, interior) — AI-fallback по умолчанию ok
- identity-safe слоты — AI-fallback только если явно нет фотки; required_user_approval=true
- если ai_fallback_needed=true → собери ai_prompt под design-system и slot.hint (1-2 предложения на английском)

Верни YAML:
slots:
  - slot_id: <string>
    candidates:
      - {photo_id: <string>, score: <float 0-1>, reason: <string>}
    ai_fallback_needed: <bool>
    required_user_approval: <bool>
    ai_prompt: <string or null>
```

## Filled example

Small services landing with 1 hero, 2 testimonials, 1 process step photo, catalog with 12 photos. Codex would return:

```
slots:
  - slot_id: hero-bg
    candidates:
      - {photo_id: photo_017, score: 0.91, reason: "wide composition matches 16:9, brand colors present"}
      - {photo_id: photo_023, score: 0.78, reason: "wide but lower brand compat"}
    ai_fallback_needed: false
    required_user_approval: false
    ai_prompt: null
  - slot_id: testimonial-1-avatar
    candidates: []
    ai_fallback_needed: true
    required_user_approval: true
    ai_prompt: "Portrait photo of satisfied client, soft studio lighting, brand color #1e3a8a accent"
```
