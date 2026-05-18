---
type: block
name: ru-features-07-2col-split
sources: ["block-library/features/ru-features-07-2col-split/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "about", "split", "2col", "ru-market", "b2c", "local", "services", "opendesign"]
---

# О нас — двухколоночный split с манифестом

## Что делает
Создаёт раздел «О нас» или блок-манифест компании: слева — история или ценности с заголовком и кнопкой, справа — имиджевое фото. Выглядит как журнальный разворот, вызывает доверие, а не давит на продажу.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** и **07b (Compose)** — агентами [[ux-composer]] и [[block-composer]]. Подходит для лендингов услуг, B2C и локального бизнеса, где важно рассказать о компании или донести фирменный манифест. Рекомендован при стилях Editorial & Magazine и Minimalism & Swiss Style.

## Что на вход / на выход

**Слоты (входные данные):**
| Слот | Тип | Лимит | Обязателен |
|---|---|---|---|
| `kicker` | text | 50 симв. | нет |
| `headline` | text | 80 симв. | **да** |
| `subhead` | text | 300 симв. | **да** |
| `art-image` | photo | 1:1 (mobile 4:3) | нет |
| `cta` | cta | — (default: «Узнать больше о нас») | нет |
| `footnote` | text | 80 симв. | нет |

**На выход:**
- HTML-блок с сеткой `1.05fr / 1fr` (десктоп)
- Мобильная версия: фото сверху, текст снизу
- Ghost-кнопка как вспомогательный CTA (не главный призыв к действию)

## Заметки по конверсии
Блок не продаёт напрямую — он строит доверие. Тон текста должен быть честным и человечным. Кнопка `ghost` играет вспомогательную роль: не перетягивает внимание от основного CTA на странице. Засечный курсив в заголовке усиливает редакционный характер.

## Атрибуция
Блок основан на шаблоне из **OpenDesign** (`nexu-io/open-design`, лицензия Apache-2.0). Источник: `github.com/nexu-io/open-design: design-templates/open-design-landing`.

## Связанные концепты
- [[ux-composer]] — выбирает блок при построении wireframe на этапе 07a
- [[block-composer]] — рендерит блок с токенами и прототипными текстами на этапе 07b
- [[wireframe-rendering]] — скилл, в рамках которого блок попадает в wireframe.html
- [[block-composition]] — скилл финальной сборки composed.html
- [[block-library-management]] — управление библиотекой, где хранится этот блок

## Источник
- `block-library/features/ru-features-07-2col-split/meta.yaml`