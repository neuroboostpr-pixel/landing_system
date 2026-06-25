---
slug: landing-brand
type: command
name: "Команда /landing-brand — сборка бренд-кита (этап 04)"
stage: "04"
tags: [brand, command, stage-04, brand-kit]
triggers: [landing-brand]
inputs: [04-brend]
outputs: [04-brend]
gates: []
pre_reqs: [03-referensy, landing-moodboard]
related: [brand-architect, brand-kit-build, style-extractor, landing-design, 04-brend, 05-dizayn-sistema]
sources: ["commands/landing-brand.md"]
updated: 2026-06-22
confidence: {gates: low}
---

# /landing-brand — Сборка бренд-кита (этап 04)

## Что делает

Команда запускает агента `brand-architect`, который синтезирует бренд-кит проекта из файлов стилей, ранее извлечённых `style-extractor`-ом. На выходе появляются два файла: канонический `brand-kit.md` с полной провенанс-информацией и HTML-превью `brand-kit.html` с палитрой, образцами шрифтов и иконок. После генерации агент показывает путь к превью и ждёт явного одобрения пользователя, прежде чем система двинется к этапу 05.

## Когда вызывается

Вызывается вручную командой `/landing-brand` внутри папки проекта после того, как `/landing-moodboard` одобрен и `style-extractor` успел сгенерировать файлы `04_БРЕНД/extracted/*.yaml`. Без них pre-flight проверка (`gate-check.sh --stage 04_brand`) завершится ошибкой и команда остановится. Так же остановится при отсутствии флага онбординга `is_complete`.

## Вход → выход

**Вход:** файлы `04_БРЕНД/extracted/*.yaml`, сгенерированные `style-extractor`-ом; пройденный онбординг (`scripts/setup-flag.sh is_complete`); закрытый этап 03 (referensy).

**Выход:**
- `04_БРЕНД/brand-kit.md` — канонический бренд-кит с провенансом (цвета, шрифты, иконки, тональность).
- `04_БРЕНД/brand-kit.html` — визуальный превью: свотчи палитры, образцы шрифтов, миниатюры иконок.

После одобрения пользователем вызывается `gate-check.sh --approve`, этап 04 закрывается.

## Failure modes

- **Нет `extracted/*.yaml`** — `style-extractor` не запускался или упал; команда завершится на pre-flight, нужно сначала пройти `/landing-moodboard`.
- **Онбординг не пройден** — отсутствует флаг `is_complete`; команда выдаёт сообщение и останавливается.
- **Предыдущий этап не закрыт** — gate-check вернёт exit 1, агент сообщит какой этап пропущен.
- **HARD GATE не пройден** — пользователь не одобрил превью; переход на этап 05 заблокирован.
- **Неполные данные в YAML** — `brand-architect` может сгенерировать неполный `brand-kit.md` если в `extracted/*.yaml` отсутствуют ключевые поля (цвета или шрифты); нужна ручная доработка.

## Related

- [[brand-architect]] — агент, синтезирующий бренд-кит из извлечённых стилей
- [[brand-kit-build]] — скилл построения бренд-кита, вызываемый агентом
- [[style-extractor]] — предшествующий агент, производящий входные YAML-файлы
- [[landing-design]] — следующий этап (05) после одобрения бренд-кита
- [[04-brend]] — папка проекта, входящая и исходящая одновременно
- [[landing-moodboard]] — этап 03, обязательный prerequisite