#!/usr/bin/env bash
# Migrate a legacy 01a_АНАЛИЗ_НИШИ project to niche-analysis v2.
#
# Idempotent:
#   - Adds **Mode:** legacy_v1 header to positioning.md if missing
#   - Creates market-profile.md stub if missing (does not overwrite)
#   - Creates landing-structure.md stub if missing (does not overwrite)
#
# Usage: migrate-niche-to-v2.sh <project-dir>
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: migrate-niche-to-v2.sh <project-dir>" >&2
  exit 2
fi

PROJECT="$1"
NICHE_DIR="$PROJECT/01a_АНАЛИЗ_НИШИ"

if [[ ! -d "$NICHE_DIR" ]]; then
  echo "ERROR: $NICHE_DIR does not exist" >&2
  exit 1
fi

POS="$NICHE_DIR/positioning.md"
MP="$NICHE_DIR/market-profile.md"
LS="$NICHE_DIR/landing-structure.md"

# 1. Add Mode: legacy_v1 to positioning.md if missing
if [[ -f "$POS" ]]; then
  if ! grep -qE '^\*\*Mode:\*\*' "$POS"; then
    tmp="$(mktemp)"
    {
      head -n 1 "$POS"
      echo ""
      echo "**Mode:** legacy_v1"
      tail -n +2 "$POS"
    } > "$tmp"
    mv "$tmp" "$POS"
    echo "✓ Added **Mode:** legacy_v1 to $POS"
  else
    echo "= positioning.md already has Mode header — skip"
  fi
else
  echo "! positioning.md not found — skip Mode injection"
fi

# 2. market-profile.md stub
if [[ ! -f "$MP" ]]; then
  cat > "$MP" <<'EOF'
# Рыночный профиль (LEGACY STUB)

> Этот файл сгенерирован `migrate-niche-to-v2.sh` для совместимости.
> Заполните вручную или перезапустите `niche-analyst` для полного v2-анализа.

## 1. Accessibility tier
**Tier:** mid_premium
- [ДОПУЩЕНИЕ] legacy migration — tier не рассчитан

## 2. Consideration cycle
**Cycle:** medium
- [ДОПУЩЕНИЕ] legacy migration

## 3. Decision unit
**Unit:** single
- [ДОПУЩЕНИЕ] legacy migration

## 4. Regulated category
**Regulated:** no
- [ДОПУЩЕНИЕ] legacy migration

## 5. Emotional load
**Load:** medium
- [ДОПУЩЕНИЕ] legacy migration

## 6. Cultural context
[ДОПУЩЕНИЕ] legacy migration — заполнить вручную.

## 7. Сводная рекомендация режима
**Predicted mode:** legacy_v1
- Старый проект — режим не классифицировался.

## 8. Источники и допущения
- [ДОПУЩЕНИЕ] весь файл — стаб для миграции, требует ручной проверки.
EOF
  echo "✓ Created stub $MP"
else
  echo "= market-profile.md exists — skip"
fi

# 3. landing-structure.md stub
if [[ ! -f "$LS" ]]; then
  cat > "$LS" <<'EOF'
# Структура лендинга (LEGACY STUB)

> Тип бренда: 2
> Режим: legacy_v1
> Дата: legacy migration

> Этот файл сгенерирован `migrate-niche-to-v2.sh`. Карта блоков выведена из обобщённого шаблона. Перезапустите `niche-analyst` для актуального landing-structure.

## Блоки лендинга

| # | Блок | Обязательный? | Цель | Содержание (откуда) |
|---|---|---|---|---|
| 1 | Hero | yes | Главная задача | positioning.md core promise |
| 2 | About | optional | Знакомство | brief.md |
| 3 | Catalog | yes | Продукты/услуги | client materials |
| 4 | Trust | yes | Доверие | testimonials |
| 5 | CTA | yes | Целевое действие | brief.md |
| 6 | FAQ | optional | Снятие возражений | brief.md |
| 7 | Footer | yes | Контакты | brief.md |

## Обоснование выбора структуры

Legacy-миграция: структура взята как универсальный fallback для проектов, созданных до niche-analysis v2. Перегенерируйте через `niche-analyst`, если важна точность для текущего Mode × типа бренда.

## Что НЕ включаем (и почему)

- Lifestyle/Experience: legacy режим не определён, добавить вручную если нужно.

## Контракт с wp-builder

Список template-parts (минимальный универсальный набор):
- block-hero.php
- block-about.php
- block-catalog.php
- block-trust.php
- block-cta.php
- block-faq.php
- block-footer.php
EOF
  echo "✓ Created stub $LS"
else
  echo "= landing-structure.md exists — skip"
fi

echo ""
echo "Migration complete for $PROJECT"
