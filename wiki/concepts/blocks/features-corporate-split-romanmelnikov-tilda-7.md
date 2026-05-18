---
type: block
name: features-corporate-split-romanmelnikov-tilda-7
sources: ["block-library/features/features-corporate-split-romanmelnikov-tilda-7/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "corporate", "split", "b2b", "expert", "services", "education"]
---

# Деловой блок с числовым акцентом и портретом эксперта

## Что делает
Отображает блок преимуществ или характеристик в деловом стиле: числовой акцент (крупные цифры или статистика), текстовые колонки с пояснениями и портрет эксперта в контурной карточке. Создаёт ощущение экспертности и доверия — подходит для B2B и профессиональных услуг.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при сборке интерактивного wireframe.html. `ux-composer` выбирает блок из библиотеки когда прототип содержит секцию «Преимущества», «Экспертиза», «Почему мы» или «Цифры» в корпоративном / деловом стиле. На этапе **07b (Compose)** `block-composer` инжектирует в блок токены дизайн-системы и тексты из prototype.yaml.

Подходящие ниши: профессиональные услуги (`services`), образование (`education`), B2B SaaS (`b2b-saas`).

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — тексты для слота `heading` (обязательный) и дополнительных текстовых колонок
- `tokens.json` — цвета, шрифты, отступы из дизайн-системы
- Фото эксперта из `07c_PHOTOS/` (слот портрета, опционально)

**Выход:**
- HTML-фрагмент блока внутри `wireframe.html` (этап 07a) или `composed.html` (этап 07b)
- Числовые акценты и текстовые колонки с применёнными токенами
- Контурная карточка с портретом (placeholder если фото нет)

## Особенности
- **Стиль:** corporate, раскладка split (контент слева / эксперт справа или колонки)
- **Анимации:** отсутствуют (`has_animation: false`)
- **Рынок:** адаптирован под ru_market
- **Источник:** импортирован с `romanmelnikov.tilda.ws` методом codex-block-generation

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[block-composer]] — инжектирует токены и тексты на этапе 07b
- [[wireframe-rendering]] — скилл рендеринга wireframe.html, использует этот блок
- [[block-composition]] — скилл сборки composed.html
- [[block-library-management]] — управление всей библиотекой блоков

## Источник
- `block-library/features/features-corporate-split-romanmelnikov-tilda-7/meta.yaml`