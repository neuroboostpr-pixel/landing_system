---
type: command
name: landing-compose
sources: ["commands/landing-compose.md"]
updated: 2026-05-20
triggers: ["собрать composed.html", "запустить этап 07b", "вставить токены дизайна в вайрфрейм", "склеить блоки с контентом"]
stage: "07b"
uses: ["block-composer", "landing-go", "landing-wireframe", "landing-prototype", "design-tokens-generation"]
tags: ["compose", "07b", "composed-html", "design-tokens", "prototype"]
---

# /landing-compose — сборка composed.html

## Что делает

Запускает этап **07b_COMPOSED**: берёт выбранные блоки вайрфрейма, вставляет в них дизайн-токены (цвета, шрифты, отступы) и тексты из прототипа, и рендерит финальный HTML-макет `composed.html`. Визуальные заглушки для фото и иконок остаются — они заполняются позднее на этапах 07c/07d.

## Когда вызывать / в каком этапе

Вызывается **после** того, как:
- завершён импорт прототипа (`/landing-prototype`) и существует `07_ПРОТОТИП/prototype.yaml`,
- пользователь выбрал варианты блоков в wireframe.html и положил `07a_WIREFRAME/selections.yaml`,
- сгенерирована дизайн-система (`/landing-design`) и существует `05_ДИЗАЙН-СИСТЕМА/tokens.json`.

Рекомендуется запускать автоматически через `/landing-go` — оркестратор сам проверяет готовность всех предусловий. Ручной вызов `/landing-compose` допустим для повторного прогона или отладки.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/prototype.yaml` — машинная версия прототипа с текстами блоков
- `07a_WIREFRAME/selections.yaml` — выбор пользователя: какой вариант каждого блока использовать
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены проекта (цвета, типографика, spacing)

**Выход:**
- `07b_COMPOSED/composed.html` — десктопная сборка с инъекцией токенов и реального текста
- `07b_COMPOSED/composed-mobile.html` — мобильная версия
- `07b_COMPOSED/block-injection-log.md` — лог: какой блок из какого источника и с каким контентом попал в сборку

## Связанные концепты

- [[block-composer]] — агент, который выполняет непосредственную сборку composed.html
- [[landing-go]] — рекомендуемый способ запуска: оркестратор автоматически диспатчит этот этап
- [[landing-wireframe]] — предшествующий этап: пользователь выбирает варианты блоков
- [[landing-prototype]] — поставляет `prototype.yaml` с текстовым контентом
- [[design-tokens-generation]] — скилл, создающий `tokens.json`, которые инъектируются в HTML
- [[landing-photos]] — этап 07c: после compose заполняет фото-слоты в composed.html
- [[landing-visuals]] — этап 07d: после compose заполняет иконки/инфографику в composed.html

## Источник

- `commands/landing-compose.md`