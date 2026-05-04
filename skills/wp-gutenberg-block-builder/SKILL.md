---
name: wp-gutenberg-block-builder
description: Generate WordPress theme scaffold, Gutenberg blocks, and ACF fields JSON from DESIGN.md + final-copy.md. Used by wp-builder agent during stage 08.
---

# wp-gutenberg-block-builder

Скилл для генерации кода WordPress-темы из токенов и контента.

## Scripts

### generate-theme.py

Читает `05_ДИЗАЙН-СИСТЕМА/tokens.json` + `06_СТЕК/design-stack.yaml`.
Создаёт `08_КОД/wp-theme/` с:
- `style.css` — Theme header + CSS-переменные из всех токенов
- `functions.php` — enqueue стилей/скриптов (шрифты с Bunny CDN, GSAP если cinematic)
- `index.php`, `front-page.php` — базовые PHP-шаблоны
- `template-parts/section-{hero,about,services,proof,form,faq}.php` — заглушки для агента
- `assets/css/main.css`, `assets/js/main.js` — заглушки
- `08_КОД/gutenberg-blocks/` — директория для блоков

```bash
python3 skills/wp-gutenberg-block-builder/scripts/generate-theme.py <project-dir>
```

### generate-acf.py

Парсит `07_КОНТЕНТ/final-copy.md` (H2-секции → ACF-группы).
Создаёт `08_КОД/acf-fields.json` с правильными field types по типу секции.
Поддерживает русские названия секций (ОТЗЫВЫ→proof, ФОРМА→form, УСЛУГИ→services).

```bash
python3 skills/wp-gutenberg-block-builder/scripts/generate-acf.py <project-dir>
```

## Usage in wp-builder agent

```
1. Run generate-theme.py → получаем scaffold
2. Run generate-acf.py → получаем ACF конфиг
3. Заполнить template-parts/*.php реальным кодом блоков
4. Написать assets/css/main.css и assets/js/main.js
```
