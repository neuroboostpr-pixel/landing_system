---
slug: landing-import-blocks
type: command
name: "Импорт блоков из URL в block-library"
stage: "block-library"
tags: [block-library, codex, vision, import, scraping]
triggers: ["/landing-import-blocks"]
inputs: ["block-library/catalog.yaml"]
outputs: ["block-library/<type>/<id>/index.html", "block-library/<type>/<id>/styles.css", "block-library/<type>/<id>/meta.yaml", "block-library/<type>/<id>/reference.png", "block-library/catalog.yaml"]
gates: []
pre_reqs: []
related: [block-library-management, block-composition, block-composer, gpt5-prompting-engine, visual-curator]
sources: ["commands/landing-import-blocks.md"]
updated: 2026-05-26
confidence: {stage: low}
---

# Импорт блоков из URL в block-library

## Что делает

Команда принимает URL (сайт или PDF-файл) и автоматически расширяет библиотеку блоков проекта. Через Playwright снимает полностраничный скриншот, затем codex CLI vision анализирует визуальную структуру и выделяет отдельные блоки с их типом, раскладкой и style-mood. Для каждого найденного блока codex в текстовом режиме генерирует чистый HTML+CSS в системном стиле — с CSS-переменными и `{{slot:*}}`-плейсхолдерами вместо чужого контента. Результат укладывается в `block-library/` и регистрируется в `catalog.yaml`.

## Когда вызывается

Вызывается вручную, когда нужно пополнить `block-library/` новым структурным паттерном: нашёл интересный сайт или получил PDF с референсом и хочешь добавить структуру (не чужой контент) в свою библиотеку. Подходит как для разовых импортов, так и для систематического расширения коллекции блоков перед этапами wireframe/compose.

## Вход → выход

**Вход:** URL страницы или путь к PDF; опционально — тег ниши (`premium-auto` и т.п.); актуальный `block-library/catalog.yaml`.

**Выход:** Один или несколько новых каталогов `block-library/<type>/<unique-id>/` с файлами `index.html`, `styles.css`, `meta.yaml`, `reference.png`; обновлённый `block-library/catalog.yaml`.

## Failure modes

- **Playwright не может открыть URL** — приватные сайты, требующие авторизации или блокирующие headless-браузеры; скриншот не будет сделан.
- **Codex не распознаёт структуру** — низкокачественный PDF или перегруженный анимацией сайт; vision-анализ вернёт неполный или пустой JSON.
- **Дублирование блоков** — одинаковые паттерны могут импортироваться повторно, засоряя `catalog.yaml`.
- **Чужой стиль просачивается в шаблон** — если промпты block-generation-prompt.md не достаточно строги, codex может воспроизвести чужие цвета или типографику вместо системных CSS-vars.
- **Перерасход бюджета codex** — страницы с большим количеством блоков (>10) дают несколько text-generation вызовов подряд; итоговая цена может превысить ожидаемые $0.40.

## Related

- [[block-library-management]] — управление каталогом, в который записывается результат импорта
- [[block-composition]] — использует импортированные блоки при сборке wireframe/composed.html
- [[block-composer]] — агент, работающий с block-library на этапах 07a–07b
- [[gpt5-prompting-engine]] — промпты команды прошли оценку через этот инструмент
- [[visual-curator]] — смежная задача работы с внешними визуальными референсами