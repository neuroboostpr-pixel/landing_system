---
name: gen-html
description: Генерация composed.html по ТЗ (build-spec.md) + дизайн-системе + активному прототипу. Агент РИСУЕТ макет (reference-driven, не склейка блоков). Поддерживает ВСЕ моды (1..∞) — авто-скан 05_ДИЗАЙН-СИСТЕМА/moods/*, каждый мод = своя раскладка под html[data-mood], панель-переключатель строится по найденным модам. Размеры/цвета — только через var() из metrics/palette; контент первого экрана видим сразу (on-load), reveal по скроллу только ниже сгиба; параллакс + float декора. Блоки с инструкцией (карусель/бегущая строка) генерятся по инструкции. Движок эффектов/мудов — scripts/html-engine.js (дублируется в макет). Этап 07c.
---

# gen-html

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill gen-html --stage 07c
```

Агент **рисует** `composed.html` сам по цепочке: ТЗ(mapping) → ДС(вид-токены) → прототип(контент) → composition(расположение).
Без подбора готовых блоков. Все моды держатся в одном файле, переключаются `[data-mood]`.

## Вход (yaml проекта)

1. **ТЗ** `07b_COMPOSED/build-spec.md` — ГЛАВНЫЙ. Mapping контент↔роль, требования к блокам, инструкции (карусель и т.п.).
2. **Активный прототип** `07_ПРОТОТИП/prototype-*.yaml` (`meta.active: true`) — контент дословно + `role`/`group` + `block_instructions`.
3. **Все муды** `05_ДИЗАЙН-СИСТЕМА/moods/*/` — `objects.yaml`(вид-токены) · `metrics/palette/typography/motion.css` · `compositions/*.yaml`(расположение).

## Выход

- `07b_COMPOSED/composed.html` (+ `composed-mobile.html`) — все моды под `[data-mood]`, панель-переключатель.

## Флоу (ПРОТОКОЛ — соблюдать порядок)

1. **Прочитать ТЗ** → выписать mapping (какой C-элемент какой ролью, какие `group`-склейки).
2. **Просканировать `moods/*`** — список мудов (1..∞). На каждый мод — своя раскладка/секция под `html[data-mood="{m}"]`.
3. **ДВИЖОК: сгенерить вид объектов из ДС, НЕ выдумывать.** Прогнать
   `scripts/roles-to-css.py <…/moods>` → на каждый мод появится `objects.css` с классом `.lp-{role}` для КАЖДОЙ
   роли (вид из `visual`/`size`/`type_props` через токены: контур/заливка/круг/вырез/тень — детерминированно).
   В HTML на элемент роли вешать `.lp-{role}` (вид из движка) + свой класс ТОЛЬКО для расположения. Подключить
   `objects.css` каждого мода в `<head>`. ⛔ НЕ переопределять вид роли (bg/border/radius/object-fit) в своём
   CSS — иначе объект разойдётся с ДС (контур станет заливкой, вырез — боксом). Свой CSS = только позиция/наезд/grid.
4. Расположение — из `composition/*.yaml` (ref + зона/наезд). Раскладки РАЗНЫЕ по модам (не только цвета).
5. **Эффекты:**
   - первый экран (above the fold) → класс `.on-load` (видим СРАЗУ, не по скроллу);
   - секции ниже сгиба → `.reveal` (IntersectionObserver, stagger);
   - параллакс — `data-px="--parallax-bg|decor|figure"`; idle-float декора — CSS `@keyframes` + `--float-dur`;
   - `@prefers-reduced-motion` → всё off.
6. **Блоки с инструкцией** (`block_instructions`: карусель/бегущая строка/слайдер/аккордеон) — генерить ПО инструкции.
6a. **ИЗОБРАЖЕНИЯ — вызвать `gen-images` ДО финала (не «потом»).** Для КАЖДОГО визуального слота:
   - есть фото клиента в `07c_PHOTOS/` → вырез+feather (`gen-images` пайплайн B) и вставить `<img>`/`<picture>`;
   - нужна иконка (фиша/cta-note/контакт) → SVG по смыслу (`gen-images` пайплайн A), вставить inline `<svg>`.
   ⛔ Голый placeholder («фото эксперта», пустой `.ph`, пустой кружок-иконка) на финале = НЕЗАКРЫТЫЙ этап.
   Если источника визуала реально нет (фото не загружено) — стилизованный плейсхолдер (силуэт/градиент), НЕ серая пустая плашка с текстом.
7. Подключить в `<head>` ВСЕ css каждого мода: `palette+typography+motion+metrics`; шрифты через `<link>`.
8. **Вставить движок** `scripts/html-engine.js` (reveal+on-load+parallax+float+mood-switch) — скопировать в `<script>` макета.
9. Панель мудов (`#moodBar`, `data-preview=on/off`) — переключатель по найденным модам (превью до прода).
10. Сверка гейтами (ниже).

## ПРАВИЛА (⛔ нарушение = дефект)

- ⛔ **Активный прототип — по `meta.active: true`**, не по имени/номеру файла.
- ⛔ **0 голых размеров и хексов** — всё `var()` из metrics/palette. Различие по модам = токен, не значение.
- ⛔ **Контент первого экрана видим СРАЗУ** (`.on-load`), reveal-по-скроллу только НИЖЕ сгиба (стандарт §7 п.8).
- ⛔ **Состав строго прототип**; связанное (`group`) не разбивать (cta+note вместе); иконка по СМЫСЛУ текста.
- ⛔ **Все моды = разная РАСКЛАДКА** под `[data-mood]`, не только перекрашивание.
- ⛔ **ФОНЫ секций, ПЕРЕХОДЫ между блоками, ПОДЛОЖКИ под фигурой — из ДС, не «плоский body».** Если в
  objects.yaml есть роли `section-bg`/`page-canvas`/`block-transition`/подложка фигуры (`figure-cutout.decor`)
  — реализовать их в HTML (холст-карта, серая плашка под вырезом + наезд, соединитель-разделитель на стыках).
  Глобальный фон на `body` без этих ролей = «фон протёк». Гейт `verify-block-transitions.py` сверяет переходы.
- ⛔ **ТЗ обязателен** если есть (генерация мимо ТЗ = «ТЗ протекает мимо флоу»).
- ⛔ **Эффекты обязательны** (reveal/on-load/parallax/float) + `prefers-reduced-motion` off.
- ⛔ **НЕТ пустых placeholder на финале.** Серая плашка «фото эксперта», пустой `.ph`, пустой кружок вместо иконки
  = дефект (читается как «дёшево/плоско»). Фото/иконки вставлены через `gen-images` ДО закрытия этапа.
- ⛔ **КАЖДЫЙ объект СТРОГО по `visual` своей роли из objects.yaml** (не только кнопки — все: карточки, плашки,
  иконки, фигуры, декор). Контур≠заливка, круг=radius50%, тень/glow/подложка — как в роли. Не «упрощать» вид.
  Каждый мод — свой `visual` из своего objects.yaml. Гейт `verify_html_vs_ds.py` сверяет объект↔роль.
- ⛔ **Текст кнопки ВИДИМ** (контраст ≥4.5): цвет текста `--lp-on-accent` задан ЯВНО, не сливается с заливкой.
- ⛔ **CTA-круг не режет/не перекрывает текст** соседних элементов (subhead/подпись) — координаты absolute проверить визуально.

## Движки

- [`scripts/roles-to-css.py`](scripts/roles-to-css.py) — **objects.yaml → objects.css** (класс `.lp-{role}` на роль,
  вид из ДС через токены). Гарантирует соответствие объект↔ДС и переносимость (тот же objects.yaml на другой нише →
  тот же CSS). Прогнать ПЕРЕД версткой; на элемент роли вешать `.lp-{role}`. Свой CSS — только расположение.
- [`scripts/html-engine.js`](scripts/html-engine.js) — готовый JS: reveal (stagger) + on-load + parallax (scroll) +
  float (CSS-driven) + mood-switch (data-mood, localStorage, перезапуск анимаций при смене мода). Копировать в `<script>` composed.html.
- [`scripts/base.css`](scripts/base.css) — базовые классы `.reveal/.on-load/.sr-only` + keyframes (копировать в `<style>`).
- [`scripts/base.css`](scripts/base.css) — базовые классы `.reveal/.on-load/.sr-only` + keyframes (копировать в `<style>`).

## Гейты (07c, hard)

- `scripts/verify_tokens.py` — 0 хексов вне palette.
- `scripts/verify_html_vs_ds.py` — размеры через токены metrics; роли composition реализованы; ровно один active-прототип.
- `scripts/verify-composed-premium.sh` — движение (IO/@keyframes), prefers-reduced-motion, коллаж/глубина.
- `scripts/verify_no_invented_text.py` + `verify-content-preserved.sh` — тексты из прототипа, не выдумано.

## Стандарт

[`docs/standards/reference-driven-rules.md`](../../docs/standards/reference-driven-rules.md) §1 (три источника), §6 (архитектура), §7-8 (требования, эффекты above-the-fold).

## Следующий шаг

← `gen-spec`, `gen-design-system`, `gen-prototype` · → `gen-images` (иконки/фото в макет) → build/deploy.
