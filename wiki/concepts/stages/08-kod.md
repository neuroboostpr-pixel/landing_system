---
type: stage
name: 08-kod
sources: ["template/08_КОД/README.md"]
updated: 2026-05-26
triggers: []
stage: "08"
uses: ["landing-build", "wp-builder", "landing-orchestrator"]
tags: ["wordpress", "theme", "gutenberg", "build", "php", "css", "js"]
---

# 08_КОД — Сборка WordPress-темы и блоков

## Что делает
Хранит и генерирует весь код WordPress-лендинга: PHP-тему, Gutenberg-блоки (Lazy Blocks) и конфиг полей. Это финальный технический артефакт, готовый к деплою на сервер.

## Когда вызывать / в каком этапе
Этап **08_build** запускается автоматически оркестратором после того, как пользователь утвердил этап 07b (composed.html). Вручную инициируется командой `/landing-build`.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — утверждённый composed с токенами и контентом
- `05_ДИЗАЙН/` — design-система (токены, шрифты, цвета)
- `04_БРЕНД/` — brand-kit (логотипы, цвета, реквизиты)

**Выход:**
- `08_КОД/wp-theme/` — полноценная WordPress-тема (PHP-темплейты, CSS, JS)
- `08_КОД/gutenberg-blocks/` — конфиги Lazy Blocks (JSON + block.php)
- `08_КОД/acf-fields.json` — конфиг полей Advanced Custom Fields (если используется)

## Связанные концепты
- [[landing-build]] — slash-команда, запускающая генерацию кода этапа 08
- [[wp-builder]] — агент, непосредственно создающий файлы темы и блоков
- [[landing-orchestrator]] — управляет порядком этапов и запускает 08_build после approve 07b
- [[landing-deploy]] — следующий этап (09), берёт код отсюда и деплоит на Бегет
- [[landing-style]] — этап 08b, дополнительно прописывает per-block CSS и block.php поверх сгенерированного кода

## Источник
- `template/08_КОД/README.md`