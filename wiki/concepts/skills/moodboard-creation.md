---
type: skill
name: moodboard-creation
sources: ["skills/moodboard-creation/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: "03"
uses: ["moodboard-composer", "landing-references"]
tags: ["moodboard", "визуал", "референсы", "html-preview"]
---

# Moodboard Creation — рендер мудборда из референсов

## Что делает
Превращает список утверждённых визуальных референсов в готовый HTML-мудборд. Берёт `index.yaml` из папки референсов, фильтрует одобренные позиции и генерирует интерактивный HTML-превью.

## Когда вызывать / в каком этапе
Вызывается на **этапе 03 (Референсы)** агентом `moodboard-composer` после того, как пользователь утвердил список визуальных референсов через `/landing-references`. Скилл активируется, когда в `03_РЕФЕРЕНСЫ/index.yaml` есть хотя бы один одобренный (`approved`) референс.

## Что на вход / на выход

**Вход:**
- `03_РЕФЕРЕНСЫ/index.yaml` — список референсов с метками `approved` / `rejected`
- `moodboard.md` (опционально) — текстовый нарратив к мудборду
- `moodboard.html.j2` — Jinja2-шаблон для рендера

**Выход:**
- `moodboard.html` — готовый HTML-файл с визуальной подборкой одобренных референсов; при наличии `moodboard.md` — с встроенным нарративом

## Связанные концепты
- [[moodboard-composer]] — агент-владелец скилла, вызывает его в рамках этапа 03
- [[landing-references]] — команда, которая собирает и размечает референсы до запуска скилла

## Источник
- `skills/moodboard-creation/SKILL.md`