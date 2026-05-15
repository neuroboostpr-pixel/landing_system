# PR-I.a — Photo Pipeline (size + codex + identity)

**Дата:** 2026-05-15
**Источник:** ПЛАН-ДОРАБОТОК.md пункт №3 «Новый порядок работы с фотографиями»
**Статус:** draft на ревью
**Связанный PR:** PR-G (Stage Lock), PR-C (visual-generation — паттерн codex)
**Следом:** PR-I.b — Playwright Visual QA

---

## 1. Зачем (простым языком)

Сейчас агент:
- Может оставить SVG-placeholder вместо реального фото
- Не подгоняет фото под точный размер слота (промахивается с пропорциями)
- Использует сырые фотки без codex-обработки — они не вписываются в дизайн-систему

PR-I.a фиксит каждую из этих проблем через **интерактивный pipeline** где агент:
1. Спрашивает у пользователя что положить в каждый слот
2. Обязательно прогоняет фото через codex с параметрами бренда
3. Подгоняет под точный размер
4. Блокирует закрытие 07c если хоть один слот пустой/placeholder

---

## 2. Главные решения (из брейншторма)

| Решение | Значение |
|---|---|
| Codex интеграция | Переиспользуем паттерн `visual-generation` (PR-C) — обёртка над codex CLI с hash-cache |
| UX подбора фото | Интерактивный чат-диалог «спроси за каждый слот» с подсказками + drag-drop UI остаётся |
| Identity-safe | Уже есть в `skills/photo-curation/IDENTITY_SAFE.md` — переиспользуем |
| HARD GATE | На 07c_composed и 07f_composed_final проверка `verify-photo-pipeline.sh` |
| Региональная адаптация | Через codex prompt: «background should evoke <region>» из market-profile.md |

---

## 3. Pipeline одной фотки

```
[1] INTAKE         — пользователь кладёт фото в 07c_PHOTOS/inbox/
[2] AI-CLASSIFY    — codex определяет тип (уже в PR-B, переиспользуем)
[3] SLOT MATCH     — выбирается слот через интерактивный диалог
[4] VALIDATE RATIO — сравнение фото.ratio vs slot.ratio
                     - совпадение → ОК
                     - <5% расхождение → auto crop_center
                     - >5% → flag для пользователя
[5] CODEX POST     — codex image_gen с промптом:
                     "Process this photo to align with brand:
                      - primary color: {tokens.primary}
                      - mood: {market-profile.mood}
                      - style: {luxury / casual / minimal}
                      - region: {market-profile.geo}
                      PRESERVE original subject (object/face/product)
                      EXACTLY — change only background, lighting,
                      color grading."
[6] IDENTITY CHECK — для слотов portrait/team/car/product:
                     - проверка что объект НЕ изменён значительно
                     - метрика — perceptual hash сравнение before/after
                     - если изменён > threshold → revert + warning
[7] RESIZE         — точный размер слота (desktop) + mobile вариант
                     - desktop: slot.width × slot.height
                     - mobile: соответственно slot.mobile_ratio
[8] CACHE          — 07c_PHOTOS/.cache/<sha256>.jpg
                     ключ кэша: hash(orig_photo + brand_color + niche + region)
[9] SAVE           — 07c_PHOTOS/processed/<slot-name>.jpg
                     07c_PHOTOS/processed/<slot-name>.mobile.jpg
                     07c_PHOTOS/processed/manifest.json (метаданные)
```

---

## 4. Интерактивный slot-fill

### Использование

```bash
/landing-photos --interactive
```

или агент-оркестратор зовёт это при заходе на этап 07c_photos.

### UX-flow (в чате)

```
Photo Pipeline — слот 1 из 8

📍 HERO BACKGROUND (16:9, 1920×1080)
   Контекст: главное фото на первом экране сайта.
   Подсказка: показывает главный продукт/услугу + атмосферу
              региона (Dubai). Например, твой флагманский авто
              на фоне Дубайской архитектуры в золотой час.

Опции:
  [F] Положи фото в 07c_PHOTOS/inbox/ → введи имя файла
  [G] Сгенерировать через codex (опиши что нужно)
  [R] Использовать reference изображение из 03_РЕФЕРЕНСЫ/
  [S] Пропустить (только для non-required слотов)
```

После ответа — pipeline запускается, агент возвращается со скриншотом
результата и переходит к слоту 2/8.

### Drag-drop UI (остаётся из PR-B)

`07c_PHOTOS/photo-board.html` — альтернатива интерактивному диалогу. Пользователь сам расставляет фото в слоты drag-drop, скачивает `selections.yaml`, кладёт в проект. Pipeline дальше тот же.

---

## 5. Структура файлов

### Создаются

**Скрипты:**
- `skills/photo-curation/scripts/codex-process-photo.sh` — обёртка над codex CLI для обработки одного фото (аналог `codex-generate-icon.sh` из visual-generation)
- `skills/photo-curation/scripts/photo-pipeline.py` — главный pipeline (шаги 4-9 из раздела 3)
- `skills/photo-curation/scripts/interactive-slot-fill.py` — интерактивный диалог
- `skills/photo-curation/scripts/identity-check.py` — perceptual hash сравнение before/after
- `scripts/verify-photo-pipeline.sh` — bash wrapper для hard_check
- `scripts/verify_photo_pipeline.py` — python helper (парсинг composed.html, проверка manifest)

**Шаблоны промптов:**
- `skills/photo-curation/templates/codex-photo-prompt.md` — шаблон codex запроса

**Тесты:**
- `tests/pr-i-a/test_photo_ratio_validates.bats`
- `tests/pr-i-a/test_codex_caches.bats`
- `tests/pr-i-a/test_no_placeholders.bats`
- `tests/pr-i-a/test_interactive_slot_fill.bats`
- `tests/pr-i-a/helpers.bash`

### Модифицируются

- `config/stage-gates.yaml` — новый hard_check `photo_pipeline_valid` для 07c_composed и 07f_composed_final
- `skills/photo-curation/SKILL.md` — обновить workflow секцию (добавить codex шаг + интерактив)
- `commands/landing-photos.md` — добавить `--interactive` флаг
- `agents/photo-curator.md` — усилить промпт: «обязан использовать codex для каждой фотки»

---

## 6. Интеграция в stage-gates.yaml

Для **07c_composed** и **07f_composed_final** добавляется новый hard_check:

```yaml
- id: photo_pipeline_valid
  type: script
  script: "scripts/verify-photo-pipeline.sh"
  args: ["{project}"]
  required: true
  fix_hint: "Photo pipeline не пройден. Проверь: (a) все <img src> указывают на 07c_PHOTOS/processed/*.jpg, (b) SVG placeholder'ов нет, (c) размеры соответствуют slot.ratio из block-library."
```

---

## 7. Verify-скрипт (логика)

`verify-photo-pipeline.sh` → `verify_photo_pipeline.py`:

```python
def verify(project_dir):
    composed = project_dir / "07b_COMPOSED" / "composed.html"
    processed = project_dir / "07c_PHOTOS" / "processed"
    manifest = processed / "manifest.json"
    soup = BeautifulSoup(composed.read_text(), "html.parser")
    
    issues = []
    
    # 1. Все <img src> ведут на processed/
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or src.startswith(("http", "data:")):
            continue
        if "placeholder" in src.lower() or src.endswith(".svg"):
            issues.append(f"placeholder остался: {src}")
        if "07c_PHOTOS/processed" not in src and "processed/" not in src:
            issues.append(f"img НЕ из processed/: {src}")
    
    # 2. Manifest существует и содержит метаданные для каждого processed файла
    if not manifest.exists():
        issues.append("manifest.json отсутствует")
    else:
        data = json.loads(manifest.read_text())
        for processed_file in processed.glob("*.jpg"):
            if processed_file.name not in data:
                issues.append(f"нет метаданных для {processed_file.name}")
    
    # 3. Размеры соответствуют слотам
    # Подгружаем block-library/<category>/<block-id>/meta.yaml
    # Сравниваем actual_width/height vs slot.ratio
    # (детали в коде)
    
    if issues:
        print("❌ Photo pipeline issues:", file=sys.stderr)
        for i in issues[:10]:
            print(f"   - {i}", file=sys.stderr)
        return 1
    print(f"✅ Photo pipeline OK ({len(list(processed.glob('*.jpg')))} processed)")
    return 0
```

---

## 8. Identity-safe механика

### Какие слоты identity-критичны
Из meta.yaml блоков: слоты с `type: photo` и `identity_safe: true` (мы добавим это поле):
- portraits / team members
- car / vehicle hero
- product hero shots
- testimonial avatars

### Проверка через perceptual hash

```python
from PIL import Image
import imagehash  # pip install imagehash

def identity_changed(orig_path, processed_path, threshold=10):
    """Возвращает True если объект изменился сильнее порога."""
    h1 = imagehash.phash(Image.open(orig_path))
    h2 = imagehash.phash(Image.open(processed_path))
    return (h1 - h2) > threshold  # Hamming distance
```

Если изменился — pipeline возвращает оригинал (без codex обработки) + warning в manifest. Пользователь решает вручную.

---

## 9. Кэш

Аналогично `visual-generation`:

```python
cache_key = hashlib.sha256((
    open(orig_photo, "rb").read() +
    brand_primary.encode() +
    niche.encode() +
    region.encode() +
    slot_ratio.encode()
).hexdigest())[:16]

cache_path = Path("07c_PHOTOS/.cache") / f"{cache_key}.jpg"

if cache_path.exists() and not force:
    shutil.copy(cache_path, processed_path)  # cache hit
else:
    # codex call → write to cache + processed
```

---

## 10. Тесты

### Test 1: `test_photo_ratio_validates.bats`
- Setup: фикстура фото 16:9, slot.ratio = "9:16" (mismatch)
- Action: `photo-pipeline.py --slot=hero-mobile --photo=fixture.jpg`
- Expected: warning о crop, фото обрезается по центру до 9:16

### Test 2: `test_codex_caches.bats`
- Setup: запустить pipeline на одно фото дважды
- Mock: `codex-process-photo.sh` пишет в stderr "CALLED" каждый раз
- Expected: первый прогон — 1 codex call, второй — 0 calls (cache hit)

### Test 3: `test_no_placeholders.bats`
- Setup: composed.html содержит `<img src="placeholder-1920x1080.svg">`
- Action: `verify-photo-pipeline.sh <project>`
- Expected: exit 1, stderr содержит «placeholder остался»

### Test 4: `test_interactive_slot_fill.bats`
- Setup: composed.html с 3 photo-слотами
- Action: `interactive-slot-fill.py <project> --dry-run`
- Expected: stdout содержит описания всех 3 слотов с подсказками

---

## 11. Объём

| Задача | Время | SDK/Codex |
|---|---|---|
| `codex-process-photo.sh` | 40 мин | 0 |
| `photo-pipeline.py` | 1 ч | 0 |
| `interactive-slot-fill.py` | 40 мин | 0 |
| `identity-check.py` (perceptual hash) | 30 мин | 0 |
| `verify-photo-pipeline.sh` + helper | 30 мин | 0 |
| Stage-gates integration | 10 мин | 0 |
| Промпты (photo-curator, landing-photos.md, SKILL.md) | 20 мин | 0 |
| 4 bats-теста с моками | 50 мин | 0 |
| Smoke на dubai-avto-liza (с реальными фото) | 30 мин | ~$0.30-0.50 codex |

**Итого: ~5 часов, ~$0.50 на real smoke (~10 фоток × $0.04 codex call).**
На моках — почти бесплатно.

---

## 12. Открытые вопросы (на ревью)

1. **identity-safe threshold** (раздел 8): сейчас Hamming distance > 10. Возможно надо точнее настраивать на реальных фото.
2. **Region detection**: сейчас из `market-profile.md`. Если поле отсутствует — что делать? Сейчас skip (без region в codex prompt). OK?
3. **Reference photos из 03_РЕФЕРЕНСЫ/**: опция [R] в интерактиве — нужна на v1 или можно без неё?

Эти 3 нюанса можно подкрутить итеративно после первого реального прогона.

---

## 13. Что меняется для пользователя

**До PR-I.a:**
- Агент мог оставить `<img src="placeholder-9-16.svg">` в финальной композиции
- Размер фото не подгонялся — выглядело криво
- Сырые фотки без обработки — не соответствуют brand mood

**После PR-I.a:**
- При закрытии 07c — verify проверит что все слоты заполнены реальными jpg
- Каждое фото прогоняется через codex с параметрами бренда
- Точные размеры (desktop + mobile варианты)
- Identity объекта (машина/лицо/товар) сохраняется
- Hash-cache экономит codex calls между прогонами
- Интерактивный «опрос за каждый слот» — пользователь видит что куда идёт

---

## 14. Связь с PR-I.b (Playwright Visual QA)

PR-I.a фиксит источник правды (фото на диске → composed.html ссылки).

PR-I.b добавляет визуальный финальный контроль: открывает composed.html в headless browser, делает скриншоты, агент глазами проверяет на видимые косяки (обрезание, перекрытие, плохой контраст), фиксит. Это **отдельная подсистема** — независима от PR-I.a, может пускаться поверх любого composed.html.

PR-I.b следующим шагом после PR-I.a.
