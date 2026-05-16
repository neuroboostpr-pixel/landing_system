# classify-prompt-type — one-word photo type classifier (PR-K)

Назначение: быстро определить **тип** фото для жадного matching фото ↔ слот.
В отличие от `classify-prompt.md` (полный YAML-tagger), здесь нужен **один
ответ из закрытого списка**: hero/portrait/team/car/vehicle/product/interior/lifestyle/background.

## How to use

1. Вызывается из `classify-photos.py` — по одному фото за раз.
2. Codex принимает промпт через stdin и фото через `-i <path>` (паттерн как в
   `codex-process-photo.sh`).
3. Результат — ОДНО слово. Парсер берёт первое валидное слово из ответа;
   если ничего не подходит — fallback `lifestyle`.

## Placeholders

(нет — промпт self-contained, чтобы classify работал даже без проектного контекста)

## Prompt body

```
Look at this photo and answer with ONE word from this exact list:

hero, portrait, team, car, vehicle, product, interior, lifestyle, background

Rules:
- Output only the word, no explanation.
- "hero" = wide cinematic shot suitable for top of landing page
- "portrait" = single person face/upper body
- "team" = multiple people
- "car"/"vehicle" = automobile
- "product" = single product/item shot
- "interior" = inside a building/room
- "lifestyle" = people doing activities in a setting
- "background" = generic textured backdrop

If unclear, default to "lifestyle".
```

## Filled example

Промпт self-contained, плейсхолдеров нет. Ответ codex (пример):

```
team
```

Парсер делает `.strip().lower().split()[0]`, валидирует против списка типов.
