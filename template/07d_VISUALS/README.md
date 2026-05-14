# 07d_VISUALS — иконки и инфографика

Это папка для AI-сгенерённых визуальных элементов лендинга: иконки и инфографика.

## Что произойдёт когда запустишь /landing-visuals

1. Система просканирует `07b_COMPOSED/composed.html`, найдёт все слоты с `data-slot-type="icon"` и `data-slot-type="infographic"`.
2. Для каждого слота — codex (gpt-image-2) сгенерит PNG под брендинг проекта (цвета, стиль, ниша из tokens.json + market-profile).
3. PNG сохранится в `icons/<slot-name>.png` или `infographics/<slot-name>.png`.
4. `composed.html` перерендерится — placeholders `[SLOT: ...]` заменятся на `<img>`.

## Кэш

`07d_VISUALS/.cache/<hash>.png` — кэшированные генерации по hash(hint + style + brand_color + niche).
- Перезапуск `/landing-visuals` НЕ зовёт codex второй раз для одних и тех же слотов — берёт из кэша.
- Чтобы перегенерить — `/landing-visuals --force`.
- Один слот — `/landing-visuals --slot feature-1-icon`.

## Артефакты

- `_slots.yaml` — найденные слоты в composed.html (auto)
- `icons/` — сгенерённые PNG иконки
- `infographics/` — сгенерённые PNG инфографики
- `.cache/` — кэш по hash (НЕ удаляй — экономит codex API)
- `prompts.yaml` — какой промпт → какой PNG (для аудита и attribution)
- `STATE.yaml` — статусы этапов
- `.logs/` — codex prompts + responses

## Что НЕ делать

- Не редактируй PNG в `icons/` или `infographics/` вручную — `--force` их перезапишет. Лучше отредактируй промпт-шаблон в `skills/visual-generation/templates/`.
- Не коммить `.cache/` в git — это локальный кеш.

## Перезапуск

```
/landing-visuals --force                 # перегенерить всё с нуля
/landing-visuals --type icons            # только иконки
/landing-visuals --slot feature-3-icon   # один конкретный слот
```

См. полную документацию: [`/landing-visuals`](../../commands/landing-visuals.md).
