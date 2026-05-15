---
type: stage
name: 07b-composed
sources: ["template/07b_COMPOSED/README.md"]
updated: 2026-05-15
triggers: []
stage: "07b"
uses: ["block-composer", "block-composition", "design-tokens-generation", "photo-curation", "visual-generation", "prototype-import"]
tags: ["compose", "html", "tokens", "premium", "wireframe", "placeholder"]
---

# 07b Composed — цветной макет с токенами и текстами

## Что делает
Собирает финальный HTML-макет лендинга: накладывает дизайн-систему (цвета, шрифты, отступы из `tokens.json`) и реальные тексты/CTA из прототипа на выбранные wireframe-блоки. Места для фотографий, иконок и инфографики остаются явными placeholders — они заполняются позже (PR-B и PR-C).

## Когда вызывать / в каком этапе
Запускается командой `/landing-compose` или агентом `block-composer` после того, как:
- пройден этап `07a` (wireframe с выбором вариантов блоков, файл `selections.yaml` сохранён),
- утверждена дизайн-система (этап `05`),
- импортирован прототип (этап `07`).

HARD GATE этапа 07b не закрывается до прохождения скрипта верификации с exit 0.

## Что на вход / на выход

**Вход:**
- `07a_WIREFRAME/selections.yaml` — выбор блоков пользователем
- `05_ДИЗАЙН/tokens.json` — дизайн-токены (цвета, типографика)
- `07_ПРОТОТИП/prototype.yaml` — структурированные тексты и CTA
- `04_БРЕНД/brand-kit.md` — бренд-стиль

**Выход:**
- `07b_COMPOSED/composed.html` — десктопная сборка (~130 KB, 13 premium-фич)
- `07b_COMPOSED/composed-mobile-preview.html` — iframe-превью для iPhone + iPad
- `07b_COMPOSED/composed-explained.md` — пояснение что и почему собрано
- `07b_COMPOSED/block-injection-log.md` — лог подстановок блоков

## Premium quality bar — обязательные требования
Каждый `composed.html` должен содержать 13 обязательных интерактивных фич: parallax, glassmorphism, slider, lightbox, count-up, reveal-on-scroll, gradient text и другие. Полный чеклист в `docs/standards/premium-07b-checklist.md`.

Верификация перед гейтом:
```bash
bash "$LANDING_SYSTEM_ROOT/scripts/verify-composed-premium.sh" \
     "$PWD/07b_COMPOSED/composed.html"
```

Эталон-референс для сравнения: `~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html`.

## Связанные концепты
- [[block-composer]] — агент, который рендерит `composed.html` из tokens + прототип
- [[block-composition]] — скилл, реализующий логику сборки блоков
- [[design-tokens-generation]] — поставляет `tokens.json` для стилизации
- [[prototype-import]] — поставляет тексты и CTA из прототипа
- [[photo-curation]] — PR-B: заменяет photo-placeholders реальными фото
- [[visual-generation]] — PR-C: заменяет icon/infographic-placeholders PNG-файлами

## Источник
- `template/07b_COMPOSED/README.md`