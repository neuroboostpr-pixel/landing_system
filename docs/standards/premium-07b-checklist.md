# PREMIUM 07b — Чек-лист сборки composed.html

Универсальные требования к этапу **07b_COMPOSED**, чтобы лендинг получался уровня dubai-avto-liza, а не «средний AI-лендинг».

Передавай этот файл агенту перед запуском сборки 07b. Каждый пункт — обязательный.

---

## 0. Что должно быть на входе (иначе НЕ собираем)

- [ ] `00_БРИФ/brief.md` — ниша, ЦА, KPI, тон голоса
- [ ] `04_БРЕНД/brand-kit.md` — палитра (мин. 2 акцента) + типографика
- [ ] `05_ДИЗАЙН-СИСТЕМА/tokens.json` — все CSS-переменные
- [ ] `07_КОНТЕНТ/final-copy.md` — реальные тексты для каждого блока
- [ ] `07a_WIREFRAME/selections.yaml` — список блоков с ID из библиотеки
- [ ] `02_МАТЕРИАЛЫ_КЛИЕНТА/inbox/` — минимум 15 реальных фото клиента
- [ ] `07c_PHOTOS/photo-mapping.yaml` — какие фото в какие слоты

**Если чего-то нет — НЕ собираем 07b. Возвращаемся на предыдущий этап.**

---

## 1. Архитектура файла

- [ ] Один файл `composed.html` — HTML + CSS + JS inline
- [ ] Никаких фреймворков (React/Vue/jQuery)
- [ ] Никаких CSS-фреймворков (Bootstrap/Tailwind CDN)
- [ ] Только Google Fonts через `<link preconnect>`
- [ ] Фото из `assets/photos/` относительными путями
- [ ] Размер итогового файла 60–150 KB (CSS не водянистый)

---

## 2. CSS-переменные (`:root`) — обязательный набор

```css
:root {
  /* Цвета — берём из tokens.json */
  --color-primary: ...;
  --color-primary-hover: ...;
  --color-accent: ...;
  --color-accent-light: ...;
  --color-bg: ...;
  --color-bg-alt: ...;
  --color-bg-card: ...;
  --color-text: ...;
  --color-text-secondary: ...;
  --color-text-inverse: ...;

  /* Типографика */
  --font: 'Inter', -apple-system, sans-serif;

  /* Радиусы */
  --radius-sm: 8px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-full: 9999px;

  /* Тени */
  --shadow-card: 0 8px 32px rgba(0,0,0,0.4);
  --shadow-hover: 0 20px 60px rgba(0,0,0,0.6);

  /* Анимации */
  --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

Все цвета и тени **только через переменные** — никаких хардкод `#fff` в коде блоков.

---

## 3. Типографика — `clamp()` для всех заголовков

- [ ] H1 hero: `font-size: clamp(40px, 6vw, 80px)`
- [ ] H2 section: `font-size: clamp(28px, 4vw, 48px)`
- [ ] Body: `font-size: clamp(15px, 1.4vw, 17px)`
- [ ] Letter-spacing `-0.02em` или `-0.03em` на крупных заголовках
- [ ] Letter-spacing `+0.15em` + `uppercase` на eyebrow/kicker
- [ ] Inter подгружен с весами 300, 400, 500, 600, 700, 800, 900

---

## 4. Структура страницы — обязательный минимум блоков

1. **Sticky nav** — с glassmorphism (см. §6)
2. **Hero** — full-screen 100vh + parallax фон + бейдж + savings + 2 CTA
3. **Social proof** — 3 stat-карточки с count-up анимацией
4. **Models/Products** — карточки 1fr/1fr с reverse-чередованием + per-card slider
5. **Features** — 4–6 карточек, `auto-fit minmax(280px, 1fr)`
6. **Why us** — фото + нумерованный список (2-кол grid)
7. **Process** — 4 шага с номерами
8. **Testimonials** — 3 отзыва с автарами-инициалами и звёздами
9. **FAQ** — native `<details>/<summary>`, без JS
10. **CTA + Lead form** — большая форма с pulse-dot бейджем
11. **Footer** — 4 колонки grid: бренд + 3 списка ссылок

Каждая секция обёрнута в `.container { max-width: 1200px; margin: 0 auto; padding: 0 40px }`.

---

## 5. Сетка — Grid + Flexbox правила

| Блок | Раскладка | Почему |
|---|---|---|
| Hero | `position: absolute` слои + flex center | фон full-bleed под текстом |
| Model card | `grid-template-columns: 1fr 1fr` + класс `.reverse` для чередования | визуальный ритм |
| Features | `grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))` | сам адаптируется без media |
| Why | `grid-template-columns: 1.1fr 1fr` | премиум-пропорции |
| Footer | `grid-template-columns: 2fr 1fr 1fr 1fr` | бренд-колонка шире |
| Testimonials | `grid-template-columns: repeat(3, 1fr)` → 1fr на mobile | равные карточки |

---

## 6. Обязательные интерактивные эффекты

### 6.1 Sticky nav с glassmorphism
```css
.nav.scrolled {
  background: rgba(10, 22, 40, 0.92);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
}
```
```js
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 60);
}, { passive: true });
```

### 6.2 Parallax hero-фон
```css
.hero-bg { position: absolute; inset: -20%; will-change: transform; }
```
```js
if (heroBg) heroBg.style.transform = 'translateY(' + (window.scrollY * 0.3) + 'px)';
```

### 6.3 Reveal-on-scroll через IntersectionObserver
```css
.reveal { opacity: 0; transform: translateY(32px); transition: 0.7s cubic-bezier(0.4,0,0.2,1); }
.reveal.visible { opacity: 1; transform: translateY(0); }
.reveal-delay-1 { transition-delay: 0.1s; }
.reveal-delay-2 { transition-delay: 0.2s; }
.reveal-delay-3 { transition-delay: 0.3s; }
.reveal-delay-4 { transition-delay: 0.4s; }
```
```js
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('visible'); revealObs.unobserve(e.target); }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));
```
**Используй каскад** `.reveal-delay-1/2/3/4` на соседних карточках — они появляются по очереди.

### 6.4 Count-up для статистики
```html
<div class="stat-number count-up" data-target="1500">0</div>
```
```js
function animateCount(el) {
  const target = parseInt(el.dataset.target, 10);
  const dur = 1800;
  const t0 = performance.now();
  function step(now) {
    const p = Math.min((now - t0) / dur, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(ease * target).toLocaleString();
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}
const countObs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) { animateCount(e.target); countObs.unobserve(e.target); }
  });
}, { threshold: 0.5 });
document.querySelectorAll('.count-up').forEach(el => countObs.observe(el));
```

### 6.5 Per-product slider (vanilla JS)
```html
<div class="model-slider" data-index="0">
  <div class="slider-track">
    <img src="..."> <img src="..."> <img src="..."> <img src="..."> <img src="...">
  </div>
  <button class="slider-btn prev" onclick="slideModel(this, -1)">←</button>
  <button class="slider-btn next" onclick="slideModel(this, 1)">→</button>
  <div class="slider-dots">
    <span class="dot active"></span><span class="dot"></span>...
  </div>
</div>
```
```js
function slideModel(btn, dir) {
  const wrap = btn.closest('.model-slider');
  const track = wrap.querySelector('.slider-track');
  const dots = wrap.querySelectorAll('.dot');
  const total = track.children.length;
  let idx = parseInt(wrap.dataset.index || 0);
  idx = (idx + dir + total) % total;
  wrap.dataset.index = idx;
  track.style.transform = 'translateX(-' + (idx * 100) + '%)';
  dots.forEach((d, i) => d.classList.toggle('active', i === idx));
}
```

### 6.6 Lightbox с клавиатурой
```html
<div class="lightbox" id="lightbox" onclick="closeLightboxOnBg(event)">
  <button class="lightbox-close" onclick="closeLightbox()">✕</button>
  <button class="lightbox-nav lightbox-prev" onclick="lightboxNav(-1)">←</button>
  <img id="lightboxImg" src="">
  <button class="lightbox-nav lightbox-next" onclick="lightboxNav(1)">→</button>
</div>
```
```js
document.addEventListener('keydown', e => {
  const lb = document.getElementById('lightbox');
  if (!lb.classList.contains('active')) return;
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowLeft') lightboxNav(-1);
  if (e.key === 'ArrowRight') lightboxNav(1);
});
```

### 6.7 Hover lift на всех карточках
```css
.card { transition: transform var(--transition), box-shadow var(--transition); }
.card:hover { transform: translateY(-4px); box-shadow: var(--shadow-hover); }
```

### 6.8 Scroll-to-top кнопка
```js
scrollTopBtn.classList.toggle('visible', window.scrollY > 400);
```

### 6.9 Smooth scroll по якорям
```js
function scrollTo(id) {
  const el = document.getElementById(id);
  const offset = 72; // высота nav
  window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - offset, behavior: 'smooth' });
}
```

### 6.10 Pulse-dot бейдж (signal of life)
```css
.hero-badge::before {
  content: ''; width: 6px; height: 6px;
  background: var(--gold); border-radius: 50%;
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}
```

---

## 7. Премиум-приёмы в типографике

- [ ] **Gradient text** на 1–2 ключевых словах:
```css
.accent {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```
- [ ] **Eyebrow** над H2: 11px, uppercase, letter-spacing 0.15em, цвет accent
- [ ] **Line-height 1.05** на huge headlines, **1.65** на body
- [ ] **Font-weight 900** на hero-заголовке (Inter Black), не 700

---

## 8. Hero — обязательные элементы

- [ ] `min-height: 100vh`
- [ ] Фоновое фото с overlay (gradient 0.7–0.9 opacity)
- [ ] Бейдж с pulse-dot ("Authorized Dealer", "Since 2018" и т.п.)
- [ ] H1 с gradient-словом
- [ ] Подзаголовок 16–20px, цвет text-secondary, max-width 560px
- [ ] **Savings/value** строка зелёная: "from AED 35,000 vs ..."
- [ ] 2 кнопки: primary (gold pill) + secondary (ghost outline)
- [ ] 3 stat-числа внизу с count-up
- [ ] Scroll hint анимация внизу (плавающая стрелка)

---

## 9. Кнопки

```css
.btn-primary {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-light));
  color: var(--color-primary);
  padding: 14px 32px;
  border-radius: var(--radius-sm);
  font-weight: 700;
  transition: var(--transition);
}
.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(accent-rgb, 0.45);
}
```

- [ ] Primary — gold gradient + lift + glow on hover
- [ ] Secondary — transparent + ghost border, hover меняет border на gold
- [ ] Кнопки **с translateY на hover** — всегда

---

## 10. Mobile responsive

- [ ] Breakpoint 768px — обязательный
- [ ] Breakpoint 1024px — для tablets
- [ ] Nav-links скрываются на mobile (`display: none`), бургер опционально
- [ ] Все grid → 1 column на mobile
- [ ] Padding контейнеров `40px` → `20px` на mobile
- [ ] Section padding `100px 0` → `64px 0` на mobile
- [ ] `composed-mobile-preview.html` — отдельный файл с iframe iPhone+iPad

---

## 11. Семантика и accessibility

- [ ] `<nav>`, `<section>`, `<article>`, `<footer>` — не везде `<div>`
- [ ] `aria-label` на nav
- [ ] `alt=""` на всех `<img>`
- [ ] `<label>` или `placeholder` на каждом input
- [ ] FAQ — native `<details>/<summary>`
- [ ] Контраст текста к фону — минимум 4.5:1

---

## 12. Что НЕЛЬЗЯ делать

- ❌ Эмодзи как «иконки» в production-блоках (только как временный placeholder с пометкой)
- ❌ Inline-стили `style="..."` для повторяющихся свойств
- ❌ Хардкод цветов в коде блоков (только через `var(--...)`)
- ❌ `font-size: 48px` без `clamp()`
- ❌ Слайдер на 4 картинки в ряд вместо настоящего слайдера
- ❌ `<a target="_blank">` вместо lightbox для фото
- ❌ Подключать jQuery / Swiper / AOS — пиши vanilla
- ❌ Скрывать блоки на mobile через `display: none` — стекируй

---

## 13. Финальная проверка перед HARD GATE

- [ ] Открыть `composed.html` из `file://` — работает без сервера
- [ ] Прокрутить полностью — fade-in каскадно, parallax работает
- [ ] Кликнуть фото в слайдере — lightbox открывается
- [ ] Нажать ESC / стрелки — lightbox реагирует
- [ ] Открыть на mobile (DevTools 393×852) — всё стекируется
- [ ] Resize окно плавно — `clamp()` плавно меняет шрифты, без ступенек
- [ ] Lighthouse Performance > 85, Accessibility > 90
- [ ] Создан `composed-explained.md` с описанием изменений
- [ ] Создан `composed-mobile-preview.html`
- [ ] Создан / обновлён `07c_PHOTOS/photo-mapping.yaml`

---

## Эталон-референс

`/Users/kirillbezikov/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html` —
1757 строк, ~130 KB, все 15 premium-фич, реальные фото.

Когда сомневаешься «достаточно ли премиум» — открой эталон и сравни.

---

## Дополнительные премиум-фичи (PR-P, 2026-05-16)

После анализа топовых русских лендингов 2026 — добавлены требования:

### 14. Scroll-driven анимации (intersection observer или scroll-timeline)
Элементы появляются при попадании в viewport (fade-in / slide-in / scale-in).
**Минимум 3 блока** должны иметь scroll-reveal.

### 15. Hover-эффекты на интерактивах
Все `<button>`, `<a class="...cta...">`, `.card` имеют `transition` и hover-state (cursor: pointer + visual feedback за 200-300ms).

### 16. Backdrop-filter где есть overlay (glassmorphism)
Если есть `<header sticky>`, modal или overlay panel — backdrop-filter: blur() для премиум-эффекта.

### 17. Complex gradient mesh background
Один из больших блоков (hero, cta) имеет animated multi-stop gradient или mesh-gradient для премиум-визуала.

### 18. Mix-blend-mode для текста-поверх-фото
Если текст лежит поверх фото — `mix-blend-mode: difference|overlay` для гарантированного контраста.

### 19. @media prefers-reduced-motion
Все анимации обёрнуты в `@media (prefers-reduced-motion: no-preference)` для accessibility.

### 20. clip-path или mask-image для нестандартных форм
Хотя бы один блок имеет нестандартную форму через clip-path (geometric mask, angled bottom) — премиум-маркер 2026.

