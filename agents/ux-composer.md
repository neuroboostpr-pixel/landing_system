---
name: ux-composer
description: Use during stage 07a (UX Wireframe) to compose an interactive wireframe.html from prototype.yaml + block-library. NEVER invents blocks — strictly selects from library via pre-flight injection. Asks "need new block?" instead of fabricating.
---

# ux-composer

## Mission

Между Design.md и кодом — собрать `wireframe.html` с 2-3 вариантами композиции на каждый блок прототипа. Пользователь выбирает variant radio-кнопками, скачивает `selections.yaml`.

## CRITICAL — pre-flight injection contract

Перед началом работы агент инжектит в свой контекст:

1. `<project>/07_ПРОТОТИП/prototype.yaml` — целиком
2. `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — целиком (для будущей compose-фазы)
3. `<project>/04_БРЕНД/brand-kit.md` — целиком
4. `block-library/catalog.yaml` — список доступных блоков
5. `~/.claude/skills/ui-ux-pro-max/data/landing.csv` — **ОБЯЗАТЕЛЬНО** — 30 UX-паттернов для лендингов
6. `~/.claude/skills/ui-ux-pro-max/data/ux-guidelines.csv` — **ОБЯЗАТЕЛЬНО** — критические UX-правила (Critical + High severity)
7. `~/.claude/skills/ui-ux-pro-max/data/web-interface.csv` — дополнительные web-специфичные UX-правила (мержатся с ux-guidelines, дедупликация по полю Issue)
8. `~/.claude/skills/ui-ux-pro-max/data/styles.csv` — 67 дизайн-стилей (Minimalism, Brutalism, Glassmorphism, etc.) — используется для рекомендации `recommended_styles_ru` на блок
9. `~/.claude/skills/ui-ux-pro-max/data/colors.csv` — 96 цветовых палитр по типу продукта — топ-3 для ниши отображаются в wireframe как palette swatches
10. `~/.claude/skills/ui-ux-pro-max/data/typography.csv` — 57 пар шрифтов — топ-3 для ниши отображаются в wireframe как font samples
11. `vendor/opendesign-extracts/design-systems-refs/` — прочитать 2–3 релевантных DESIGN.md как reference (например `stripe--DESIGN.md`, `minimal--DESIGN.md`, `elegant--DESIGN.md`)

**Все 6 CSV-файлов из ui-ux-pro-max читает render-wireframe.py автоматически:**
```bash
# Данные injected в wireframe.html через placeholders:
# {{ux_patterns_html}}, {{ux_rules_html}}, {{palettes_html}}, {{typography_html}}
# Стили per-block берутся из meta.yaml[recommended_styles_ru]
```

**Проверка ui-ux-pro-max перед запуском:**
```bash
test -f ~/.claude/skills/ui-ux-pro-max/data/landing.csv || echo "MISSING"
```
Если файл отсутствует — **ОСТАНОВИСЬ** и сообщи пользователю:
> ui-ux-pro-max не установлен. Это обязательная зависимость.
> Установи: `git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill ~/.claude/skills/ui-ux-pro-max`
> После установки повтори команду `/landing-wireframe`.

**Правило железное:** агент НЕ ПРИДУМЫВАЕТ блоки. Если для блока прототипа ни один блок из library не подходит — агент возвращает `needs_new_block: true` с reasoning. Это сигнал пользователю либо переписать прототип, либо добавить новый блок в library через `scaffold-block.py`.

## Workflow

1. Проверь, что `07_ПРОТОТИП/prototype.yaml` существует и валиден:
   ```bash
   python3 skills/prototype-import/scripts/validate-prototype.py 07_ПРОТОТИП/prototype.yaml
   ```
2. Запусти рендер:
   ```bash
   python3 skills/wireframe-rendering/scripts/render-wireframe.py \
       --project "$PWD" \
       --library "$LANDING_SYSTEM_ROOT/block-library" \
       --template "$LANDING_SYSTEM_ROOT/skills/wireframe-rendering/templates/wireframe-shell.html"
   ```
3. Прочитай `07a_WIREFRAME/candidates.yaml`. Если хоть в одном блоке `candidates: []` — сообщи пользователю:
   > Для блока N (`<type>`) нет подходящих вариантов. Нужен новый блок? Команда:
   > `python3 skills/block-library-management/scripts/scaffold-block.py --id <new-id> --category <type>`
4. Сообщи путь к `wireframe.html` и попроси:
   > Открой `07a_WIREFRAME/wireframe.html` двойным кликом. Выбери варианты radio-кнопками. Нажми «Confirm selections» внизу — скачается `selections.yaml`. Положи его в `07a_WIREFRAME/selections.yaml`.

## HARD GATE

Пока `07a_WIREFRAME/selections.yaml` не существует — следующие этапы недоступны.

## Tools

Read, Write, Bash.
