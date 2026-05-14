# Retro Windows Style Mood

**Inspiration:** `zhangzara-retro-windows` (OpenDesign) — Windows 95, CRT monitors, 8-bit nostalgia

## Когда применять

- Геймификация, игровые продукты
- Nostalgia marketing (90s-ориентированная аудитория)
- Инди-разработчики, hackers, tech hobbyists
- Когда клиент говорит: "Мы хотим что-то неожиданное и мемное"

## НЕ применять

- Серьёзные B2B продукты (воспримут несерьёзно)
- Медицина, финансы (доверие важнее)
- Luxury/premium (конфликт с нишей)

## Что подключать

**Patterns:** `scroll-reveal` (без spring easing)
**НЕ подключать:** `ambient-mesh-bg`, `cursor-aura`, `gradient-mesh-animated`, `magnetic-button` (всё слишком modern)

## Правила дизайна

1. **Window chrome:** Titlebar с `linear-gradient(90deg, #000080, #0000a0)`, close/min/max buttons
2. **3D bevel:** `inset 1px 1px 0 #fff, inset -1px -1px 0 #000` на всех элементах
3. **CRT overlay:** `repeating-linear-gradient(0deg, rgba(0,0,0,0.03) 0px, ... transparent 3px)` поверх всего
4. **VT323 font:** для заголовков и display текста
5. **Цвета:** Только Win95 system palette — никакого cobalt или coral
6. **Border-radius:** НОЛЬ — все углы прямые
7. **Cursor:** Рассмотри custom cursor (pointer.cur style) для иммерсивности

## Window chrome CSS

```css
.win-window {
  background: #d4d0c8;
  border: 2px solid #fff;
  border-right-color: #000;
  border-bottom-color: #000;
  box-shadow: inset 1px 1px 0 #fff, inset -1px -1px 0 #404040;
}

.win-titlebar {
  background: linear-gradient(90deg, #000080, #0000a0);
  color: #fff;
  padding: 4px 8px;
  font-weight: bold;
}
```

## Google Fonts

```html
<link href="https://fonts.googleapis.com/css2?family=VT323&family=Press+Start+2P&display=swap" rel="stylesheet">
```
