---
slug: visual-generation
type: skill
name: "Visual Generation — генерация иконок и инфографики"
stage: "07d"
tags: [visuals, icons, infographics, codex, image-gen, cache, slot-injection]
triggers: [landing-visuals]
inputs: [05-dizayn-sistema, 07b-composed]
outputs: [07d-visuals]
gates: []
pre_reqs: [05-dizayn-sistema, 07b-composed]
related: [visual-curator, landing-visuals, landing-compose, photo-curator, 07c-photos, landing-visuals]
sources: ["skills/visual-generation/SKILL.md"]
updated: 2026-06-19
confidence: {stage: low}
---

# Visual Generation — генерация иконок и инфографики

## Что делает

Скилл генерирует PNG-иконки и инфографику для всех `[SLOT: ...]` placeholders в `composed.html`. Работает на основе `tokens.json` (цвета, бренд) и описания ниши из `market-profile.md`. Каждый слот проходит трёхшаговый конвейер: сканирование → генерация через codex image_gen → инъекция результата обратно в HTML. Хеш-кэш исключает повторные API-вызовы для уже сгенерированных слотов. Стандарт обработки каждого визуального места — `docs/standards/image-pipeline.md`: анализ → цель → спека → референсы → генерация на вырезаемом фоне → rembg → вставка.

## Когда вызывается

Запускается командой `/landing-visuals` после того как этап 05 (design-system) утверждён и файл `07b_COMPOSED/composed.html` существует. Может вызываться с флагами `--type icons`, `--type infographics`, `--slot <name>` или `--force` (обход кэша).

## Вход → выход

**Вход:** утверждённый `05_ДИЗАЙН/design-system.md`, файл `07b_COMPOSED/composed.html` с placeholders `[SLOT: ...]`, `tokens.json` с цветами бренда, описание ниши.

**Выход:** `07d_VISUALS/_slots.yaml` (список слотов), PNG-файлы в `07d_VISUALS/.cache/<hash>.png`, обновлённый `composed.html` с подставленными `<img class="lp-icon">`, `07d_VISUALS/STATE.yaml` (прогресс прогона).

## Failure modes

- **Отсутствует composed.html** — скилл падает на шаге scan; нужно сначала выполнить `/landing-compose`.
- **Кэш устарел после смены бренд-токенов** — используется `--force` для полной перегенерации, иначе старые PNG остаются в HTML.
- **Ошибка codex API** — STATE.yaml фиксирует прерванный слот; повторный запуск продолжит с него, не с начала.
- **Prompt-picker не нашёл совпадений** — waterfall откатывается на generic template; результат может не соответствовать нише.
- **Расхождение stage в pre-flight логе** — в SKILL.md указан `--stage 07e` вместо `07d`; ложное предупреждение в routing-report.

## Related

- [[visual-curator]] — агент-владелец скилла, диспатчит его запуск
- [[landing-visuals]] — slash-команда, являющаяся точкой входа для пользователя
- [[07d-visuals]] — этап пайплайна, который закрывает этот скилл
- [[07b-composed]] — предшествующий этап, чей composed.html является обязательным входом
- [[photo-curator]] — параллельный скилл этапа 07c; выполняются независимо друг от друга