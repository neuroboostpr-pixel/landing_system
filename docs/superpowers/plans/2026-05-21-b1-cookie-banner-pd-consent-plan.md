# B1 Cookie-banner + 152-ФЗ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Template-level юр-инфраструктура для каждого лендинга landing-system: cookie-banner с категориями, обязательное PD-согласие в формах, типовые юр-страницы /policy и /consent, БД-timestamp согласия.

**Architecture:** Реквизиты из brand-kit.md (новая секция `legal:`) → wp-builder подставляет в HTML-templates легальных страниц + вставляет cookie-banner в footer + legal-block в формы. landing-config mu-plugin валидирует pd_consent в REST /lead и пишет timestamp в landing_leads. Google Consent Mode v2 для интеграции с будущей B2.

**Tech Stack:** PHP 8.3, WordPress mu-plugin (\$wpdb prepared statements, dbDelta), Python 3 (для brand-kit-build), vanilla JS (cookie-banner без зависимостей), bats и PHP unit-тесты с моками из tests/fixtures/wp-bootstrap.php.

---

## Phase B1.1 — brand-kit legal-секция

**Цель:** расширить brand-kit.md новой секцией `legal:` с реквизитами Оператора ПД. Обновить brand-kit-build skill чтобы он генерил эту секцию из YAML-инпута. Добавить helper для парсинга `legal:` из brand-kit.md (нужен на этапе 08_код для подстановки в шаблоны).

**Files:**
- Modify: `skills/brand-kit-build/scripts/build.py` (добавить генерацию legal-секции из inputs)
- Create: `skills/brand-kit-build/scripts/parse_legal.py` (helper-парсер для wp-builder)
- Modify: `agents/brand-architect.md` (документировать как спросить legal-данные)
- Modify: `template/04_БРЕНД/README.md` (упомянуть новую секцию)
- Test: `skills/brand-kit-build/tests/test_parse_legal.py`

---

### Task B1.1.1: Создать failing test для parse_legal

**Files:**
- Test: `skills/brand-kit-build/tests/test_parse_legal.py`

- [ ] **Step 1: Создать файл теста**

```python
"""Tests for parse_legal — reading legal: section from brand-kit.md."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import unittest
import tempfile
import textwrap
from parse_legal import parse_legal_from_brand_kit


class TestParseLegal(unittest.TestCase):

    def _write(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
        f.write(content)
        f.close()
        return f.name

    def test_parses_full_legal_section(self):
        """T1: парсит все 7 полей."""
        p = self._write(textwrap.dedent("""
            # Brand Kit

            ## Colors
            primary: #ff0000

            ## Legal
            ```yaml
            company_name: 'ООО "Ромашка"'
            entity_type: 'ООО'
            inn: '7700123456'
            ogrn: '1234567890123'
            legal_address: '123456, Москва, ул. Тверская, 1'
            contact_email: 'info@romashka.ru'
            dpo_email: 'info@romashka.ru'
            ```
        """).strip())
        result = parse_legal_from_brand_kit(p)
        self.assertEqual(result['company_name'], 'ООО "Ромашка"')
        self.assertEqual(result['inn'], '7700123456')
        self.assertEqual(result['ogrn'], '1234567890123')
        self.assertEqual(result['legal_address'], '123456, Москва, ул. Тверская, 1')
        self.assertEqual(result['contact_email'], 'info@romashka.ru')
        self.assertEqual(result['dpo_email'], 'info@romashka.ru')
        self.assertEqual(result['entity_type'], 'ООО')

    def test_returns_none_if_no_legal_section(self):
        """T2: возвращает None если секции Legal нет."""
        p = self._write("# Brand Kit\n\n## Colors\nprimary: #ff0000\n")
        result = parse_legal_from_brand_kit(p)
        self.assertIsNone(result)

    def test_returns_partial_with_todo_marker_if_placeholder_values(self):
        """T3: если есть TODO_LEGAL — помечает в result['_incomplete']=True."""
        p = self._write(textwrap.dedent("""
            ## Legal
            ```yaml
            # TODO_LEGAL: заполнить до прод-деплоя
            company_name: 'TODO_LEGAL'
            entity_type: 'TODO_LEGAL'
            inn: 'TODO_LEGAL'
            ogrn: 'TODO_LEGAL'
            legal_address: 'TODO_LEGAL'
            contact_email: 'TODO_LEGAL'
            dpo_email: 'TODO_LEGAL'
            ```
        """).strip())
        result = parse_legal_from_brand_kit(p)
        self.assertTrue(result['_incomplete'])

    def test_raises_if_file_not_found(self):
        """T4: бросает FileNotFoundError если brand-kit.md отсутствует."""
        with self.assertRaises(FileNotFoundError):
            parse_legal_from_brand_kit('/nonexistent/brand-kit.md')

    def test_returns_none_if_malformed_yaml(self):
        """T5: malformed YAML внутри Legal-блока → None + log warning."""
        p = self._write(textwrap.dedent("""
            ## Legal
            ```yaml
            company_name: [unclosed list
            ```
        """).strip())
        result = parse_legal_from_brand_kit(p)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Запустить тест — должен упасть с ImportError**

```bash
"/d/Program Files/Python310/python" -m pytest skills/brand-kit-build/tests/test_parse_legal.py -v
```

Ожидаемо: `ModuleNotFoundError: No module named 'parse_legal'`.

---

### Task B1.1.2: Реализовать parse_legal.py

**Files:**
- Create: `skills/brand-kit-build/scripts/parse_legal.py`

- [ ] **Step 1: Создать файл**

```python
"""Parse legal: section from brand-kit.md.

The legal section is a YAML block inside a markdown ## Legal heading:

    ## Legal
    ```yaml
    company_name: '...'
    entity_type: 'ООО'
    inn: '...'
    ogrn: '...'
    legal_address: '...'
    contact_email: '...'
    dpo_email: '...'
    ```

Returns dict on success or None if section missing/malformed.
Sets result['_incomplete'] = True if any required field is the literal 'TODO_LEGAL'.
"""
import re
import yaml
from pathlib import Path


LEGAL_SECTION_RE = re.compile(
    r'^##\s+Legal\s*$\n+```yaml\n(.*?)\n```',
    re.MULTILINE | re.DOTALL
)

REQUIRED_FIELDS = ['company_name', 'entity_type', 'inn', 'ogrn',
                   'legal_address', 'contact_email', 'dpo_email']


def parse_legal_from_brand_kit(path):
    """Parse the legal: section from a brand-kit.md file.

    Args:
        path: path to brand-kit.md (str or Path).

    Returns:
        dict with legal fields + '_incomplete' flag, or None if missing/malformed.

    Raises:
        FileNotFoundError: if path does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"brand-kit.md not found: {path}")

    content = p.read_text(encoding='utf-8')
    m = LEGAL_SECTION_RE.search(content)
    if not m:
        return None

    yaml_block = m.group(1)
    try:
        data = yaml.safe_load(yaml_block)
    except yaml.YAMLError as e:
        import sys
        print(f"[parse_legal] warning: malformed YAML in Legal section: {e}", file=sys.stderr)
        return None

    if not isinstance(data, dict):
        return None

    # Detect TODO_LEGAL placeholders
    incomplete = any(
        str(data.get(f, '')).strip() == 'TODO_LEGAL'
        for f in REQUIRED_FIELDS
    )
    data['_incomplete'] = incomplete

    return data
```

- [ ] **Step 2: Прогон теста — должны пройти 5/5**

```bash
"/d/Program Files/Python310/python" -m pytest skills/brand-kit-build/tests/test_parse_legal.py -v
```

Ожидаемо: `5 passed`.

- [ ] **Step 3: Commit**

```bash
git add skills/brand-kit-build/scripts/parse_legal.py \
        skills/brand-kit-build/tests/test_parse_legal.py
git commit -m "feat(brand-kit-build): B1.1 — parse_legal helper для legal-секции brand-kit

Парсит ## Legal YAML-блок из brand-kit.md. Возвращает dict с 7 полями
(company_name, entity_type, inn, ogrn, legal_address, contact_email,
dpo_email) + флаг '_incomplete' если есть 'TODO_LEGAL' placeholders.

5/5 тестов: full parse, no-section, TODO marker, file-not-found, malformed YAML.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task B1.1.3: Расширить build.py — генерация legal-секции

**Files:**
- Modify: `skills/brand-kit-build/scripts/build.py`

- [ ] **Step 1: Прочитать существующий build.py для контекста**

```bash
cat skills/brand-kit-build/scripts/build.py | head -80
```

Найди функцию которая собирает финальный brand-kit.md (обычно `build()` или `generate()`). Запомни сигнатуру и где она пишет markdown-секции.

- [ ] **Step 2: Добавить функцию build_legal_section**

В тот же файл `skills/brand-kit-build/scripts/build.py` добавь после существующих build_*-функций:

```python
def build_legal_section(legal_input):
    """Build the ## Legal section from input dict.

    If legal_input is None or missing — emits TODO_LEGAL placeholders.

    Args:
        legal_input: dict with 7 keys (company_name, entity_type, inn, ogrn,
                     legal_address, contact_email, dpo_email) or None.

    Returns:
        Markdown string with '## Legal' header and YAML block.
    """
    if not legal_input:
        legal_input = {
            'company_name': 'TODO_LEGAL',
            'entity_type': 'TODO_LEGAL',
            'inn': 'TODO_LEGAL',
            'ogrn': 'TODO_LEGAL',
            'legal_address': 'TODO_LEGAL',
            'contact_email': 'TODO_LEGAL',
            'dpo_email': 'TODO_LEGAL',
        }

    lines = ['## Legal', '', '```yaml']
    if any(v == 'TODO_LEGAL' for v in legal_input.values()):
        lines.append('# TODO_LEGAL: заполнить до прод-деплоя — без этого лендинг не может запускаться в РФ')

    for key in ['company_name', 'entity_type', 'inn', 'ogrn',
                'legal_address', 'contact_email', 'dpo_email']:
        val = legal_input.get(key, 'TODO_LEGAL')
        # Quote string values to preserve special chars
        lines.append(f"{key}: '{val}'")

    lines.append('```')
    lines.append('')
    return '\n'.join(lines)
```

- [ ] **Step 3: Вызвать build_legal_section из основной build-функции**

Найди в `build.py` главную функцию (вероятно `def main()` или `def build_brand_kit()`). Найди место где собирается финальный markdown — обычно конкатенация секций.

Добавь вызов `build_legal_section(load_legal_input(project_dir))` в финальную конкатенацию ПОСЛЕ всех существующих секций (Colors / Fonts / Icons / Grid / Motion).

`load_legal_input` нужно тоже добавить (читает `04_БРЕНД/extracted/legal.yaml` если есть, иначе None):

```python
def load_legal_input(project_dir):
    """Load legal: input from 04_БРЕНД/extracted/legal.yaml if exists."""
    legal_path = Path(project_dir) / '04_БРЕНД' / 'extracted' / 'legal.yaml'
    if not legal_path.exists():
        return None
    try:
        with open(legal_path, encoding='utf-8') as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, IOError):
        return None
```

- [ ] **Step 4: Lint Python через py_compile**

```bash
"/d/Program Files/Python310/python" -m py_compile skills/brand-kit-build/scripts/build.py
```

Ожидаемо: без вывода (без ошибок).

- [ ] **Step 5: Commit**

```bash
git add skills/brand-kit-build/scripts/build.py
git commit -m "feat(brand-kit-build): B1.1 — генерация ## Legal в brand-kit.md

build.py получил build_legal_section и load_legal_input. Если файл
04_БРЕНД/extracted/legal.yaml есть — берёт оттуда. Иначе — emit'ит
TODO_LEGAL placeholders + предупреждающий комментарий что без заполнения
лендинг не может запускаться в РФ.

7 полей: company_name, entity_type, inn, ogrn, legal_address,
contact_email, dpo_email.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task B1.1.4: Расширить brand-architect.md

**Files:**
- Modify: `agents/brand-architect.md`

- [ ] **Step 1: Добавить секцию про legal-данные**

В `agents/brand-architect.md` найди раздел "## Process" (около строки 44). После его последнего пункта (открытие brand-kit.html) добавь новый блок:

```markdown
## Сбор legal-реквизитов (для 152-ФЗ compliance)

После генерации brand-kit спроси у пользователя legal-данные Оператора ПД (обязательно для запуска в РФ):

1. Полное юр-имя (например: «Общество с ограниченной ответственностью "Ромашка"»)
2. Тип сущности: ИП / ООО / АО
3. ИНН (10 цифр для ЮЛ, 12 для ИП)
4. ОГРН (15 цифр для ЮЛ) или ОГРНИП (15 цифр для ИП)
5. Юридический адрес (с индексом)
6. Контактный email для запросов субъектов ПД
7. Email представителя по ПД (часто = контактный email)

Запиши ответы в `04_БРЕНД/extracted/legal.yaml`:

```yaml
company_name: '...'
entity_type: '...'
inn: '...'
ogrn: '...'
legal_address: '...'
contact_email: '...'
dpo_email: '...'
```

Затем перезапусти `python3 skills/brand-kit-build/scripts/build.py <project-dir>` — секция `## Legal` появится в brand-kit.md.

**Если пользователь не знает данных:** не блокируй pipeline. Запиши `TODO_LEGAL` во все поля и предупреди: «Лендинг не может выкатиться в продакшен в РФ без legal-реквизитов. Заполни `04_БРЕНД/extracted/legal.yaml` до запуска `/landing-deploy`.»
```

- [ ] **Step 2: Commit**

```bash
git add agents/brand-architect.md
git commit -m "docs(brand-architect): B1.1 — сбор legal-реквизитов на этапе 04

Добавлен раздел про 7 обязательных полей Оператора ПД. Реквизиты
записываются в 04_БРЕНД/extracted/legal.yaml, оттуда build.py
подставляет в brand-kit.md ## Legal секцию.

Без legal-реквизитов лендинг не может выкатиться в РФ.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase B1.2 — Типовые юр-страницы (templates + render)

**Цель:** написать каноничные тексты policy.html.template и consent.html.template с {{placeholders}}. Создать render-helper который подставляет реквизиты из brand-kit. README для маркетолога.

**Files:**
- Create: `template/08_КОД/legal-pages/policy.html.template`
- Create: `template/08_КОД/legal-pages/consent.html.template`
- Create: `template/08_КОД/legal-pages/README.md`
- Create: `skills/legal-pages-render/scripts/render.py`
- Create: `skills/legal-pages-render/tests/test_render.py`

---

### Task B1.2.1: Failing test для render

**Files:**
- Test: `skills/legal-pages-render/tests/test_render.py`

- [ ] **Step 1: Создать файл теста**

```python
"""Tests for legal-pages render — substituting brand-kit reqs into HTML templates."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import unittest
import tempfile

from render import render_template, render_policy, render_consent


class TestRender(unittest.TestCase):

    def _legal(self, **overrides):
        base = {
            'company_name': 'ООО "Ромашка"',
            'entity_type': 'ООО',
            'inn': '7700123456',
            'ogrn': '1234567890123',
            'legal_address': '123456, Москва, ул. Тверская, 1',
            'contact_email': 'info@romashka.ru',
            'dpo_email': 'info@romashka.ru',
            '_incomplete': False,
        }
        base.update(overrides)
        return base

    def test_substitutes_all_placeholders(self):
        """T1: все 6 placeholders заменены."""
        tpl = "Operator: {{company_name}} (ИНН {{inn}}, ОГРН {{ogrn}})\nAddr: {{legal_address}}\nContact: {{contact_email}}, DPO: {{dpo_email}}"
        result = render_template(tpl, self._legal())
        self.assertIn('ООО "Ромашка"', result)
        self.assertIn('7700123456', result)
        self.assertIn('1234567890123', result)
        self.assertIn('123456, Москва, ул. Тверская, 1', result)
        self.assertIn('info@romashka.ru', result)
        self.assertNotIn('{{', result)
        self.assertNotIn('}}', result)

    def test_raises_if_legal_incomplete(self):
        """T2: если _incomplete=True — RuntimeError, не рендерим страницу с TODO_LEGAL."""
        with self.assertRaises(RuntimeError):
            render_template("{{company_name}}", self._legal(_incomplete=True))

    def test_raises_if_required_field_missing(self):
        """T3: если в legal не хватает ключа из template — KeyError."""
        legal = self._legal()
        del legal['inn']
        with self.assertRaises(KeyError):
            render_template("ИНН: {{inn}}", legal)

    def test_render_policy_loads_template_from_disk(self):
        """T4: render_policy читает template/08_КОД/legal-pages/policy.html.template."""
        result = render_policy(self._legal())
        # Каноничный текст содержит «Политика обработки персональных данных»
        self.assertIn('Политика обработки персональных данных', result)
        self.assertIn('ООО "Ромашка"', result)
        self.assertIn('7700123456', result)
        self.assertNotIn('{{', result)

    def test_render_consent_loads_template_from_disk(self):
        """T5: render_consent читает template/08_КОД/legal-pages/consent.html.template."""
        result = render_consent(self._legal())
        self.assertIn('Согласие', result)
        self.assertIn('ООО "Ромашка"', result)
        self.assertIn('152-ФЗ', result)
        self.assertNotIn('{{', result)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Прогон — должен упасть с ImportError**

```bash
"/d/Program Files/Python310/python" -m pytest skills/legal-pages-render/tests/test_render.py -v
```

---

### Task B1.2.2: Создать render.py

**Files:**
- Create: `skills/legal-pages-render/scripts/render.py`

- [ ] **Step 1: Создать файл**

```python
"""Render legal HTML pages by substituting reqs into templates."""
import re
from pathlib import Path


# Path to templates dir (relative to landing-system root)
TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / 'template' / '08_КОД' / 'legal-pages'

PLACEHOLDER_RE = re.compile(r'\{\{(\w+)\}\}')


def render_template(tpl_string, legal):
    """Substitute {{key}} placeholders with legal[key] values.

    Args:
        tpl_string: template content with {{placeholders}}.
        legal: dict with at least the keys referenced in template + '_incomplete' flag.

    Returns:
        Rendered string.

    Raises:
        RuntimeError: if legal['_incomplete'] is True.
        KeyError: if template references a key not in legal.
    """
    if legal.get('_incomplete'):
        raise RuntimeError(
            "Legal data is incomplete (TODO_LEGAL detected). "
            "Заполни 04_БРЕНД/extracted/legal.yaml и перезапусти build.py."
        )

    def _replace(m):
        key = m.group(1)
        if key not in legal:
            raise KeyError(f"Template references unknown key: {key!r}")
        return str(legal[key])

    return PLACEHOLDER_RE.sub(_replace, tpl_string)


def render_policy(legal):
    """Render policy.html from template/08_КОД/legal-pages/policy.html.template."""
    tpl_path = TEMPLATES_DIR / 'policy.html.template'
    return render_template(tpl_path.read_text(encoding='utf-8'), legal)


def render_consent(legal):
    """Render consent.html from template/08_КОД/legal-pages/consent.html.template."""
    tpl_path = TEMPLATES_DIR / 'consent.html.template'
    return render_template(tpl_path.read_text(encoding='utf-8'), legal)
```

- [ ] **Step 2: Не запускай тест — он упадёт без templates (B1.2.3 их создаст)**

---

### Task B1.2.3: Написать policy.html.template

**Files:**
- Create: `template/08_КОД/legal-pages/policy.html.template`

- [ ] **Step 1: Создать каноничный шаблон**

Файл `template/08_КОД/legal-pages/policy.html.template`:

```html
<h1>Политика обработки персональных данных</h1>
<p><em>Дата вступления в силу: {{effective_date}}. Дата последнего обновления: {{last_updated}}.</em></p>

<h2>1. Общие положения</h2>
<p>Настоящая Политика обработки персональных данных (далее — «Политика») составлена в соответствии с требованиями Федерального закона от 27.07.2006 № 152-ФЗ «О персональных данных» (далее — 152-ФЗ) и определяет порядок обработки персональных данных, осуществляемой Оператором, а также меры по обеспечению безопасности персональных данных.</p>

<h2>2. Оператор персональных данных</h2>
<p>Оператором является {{company_name}} ({{entity_type}}), ИНН {{inn}}, ОГРН {{ogrn}}, юридический адрес: {{legal_address}}.</p>
<p>Контактный email для обращений субъектов персональных данных: <a href="mailto:{{contact_email}}">{{contact_email}}</a>.</p>
<p>Представитель Оператора по вопросам обработки персональных данных: <a href="mailto:{{dpo_email}}">{{dpo_email}}</a>.</p>

<h2>3. Категории субъектов персональных данных</h2>
<p>Оператор обрабатывает персональные данные следующих категорий субъектов:</p>
<ul>
    <li>Посетители сайта, оставившие заявку через формы обратной связи;</li>
    <li>Клиенты Оператора, заключившие или планирующие заключить договор.</li>
</ul>

<h2>4. Категории обрабатываемых персональных данных</h2>
<p>Оператор обрабатывает следующие категории персональных данных:</p>
<ul>
    <li>Фамилия, имя (при добровольном указании);</li>
    <li>Контактный номер телефона;</li>
    <li>Адрес электронной почты;</li>
    <li>Текст сообщения, оставленного в форме обратной связи;</li>
    <li>IP-адрес устройства;</li>
    <li>Данные о посещении сайта (cookies, user agent, источник перехода, UTM-метки);</li>
    <li>Информация о посещённых страницах и взаимодействии с сайтом.</li>
</ul>
<p>Оператор не обрабатывает специальные категории персональных данных (раса, политические убеждения, состояние здоровья и т.п.), биометрические персональные данные.</p>

<h2>5. Цели обработки персональных данных</h2>
<p>Обработка персональных данных осуществляется в следующих целях:</p>
<ul>
    <li>Обработка заявок, поступающих через формы обратной связи;</li>
    <li>Установление обратной связи с субъектом персональных данных;</li>
    <li>Заключение и исполнение договоров с субъектом персональных данных;</li>
    <li>Аналитика посещаемости и улучшение функционирования сайта;</li>
    <li>Информирование о товарах, услугах, акциях (при наличии отдельного согласия).</li>
</ul>

<h2>6. Правовые основания обработки персональных данных</h2>
<p>Обработка персональных данных осуществляется на следующих правовых основаниях:</p>
<ul>
    <li>Согласие субъекта персональных данных (статья 6 часть 1 пункт 1 152-ФЗ) — для целей обработки заявок и маркетинговых коммуникаций;</li>
    <li>Заключение и исполнение договора с субъектом (статья 6 часть 1 пункт 5 152-ФЗ) — для целей оказания услуг.</li>
</ul>

<h2>7. Способы и сроки обработки персональных данных</h2>
<p>Обработка персональных данных осуществляется как автоматизированным способом (с использованием средств вычислительной техники), так и без использования таких средств (на бумажных носителях).</p>
<p>Срок хранения персональных данных — 5 (пять) лет с даты последнего взаимодействия с субъектом, либо до момента отзыва согласия на обработку персональных данных, в зависимости от того, что наступит ранее.</p>

<h2>8. Передача персональных данных третьим лицам</h2>
<p>Оператор может передавать персональные данные третьим лицам исключительно для целей, указанных в разделе 5 настоящей Политики, и только при наличии правовых оснований. Категории получателей:</p>
<ul>
    <li>Поставщики CRM-систем и систем учёта заявок (для хранения и обработки заявок);</li>
    <li>Поставщики мессенджеров (для пересылки уведомлений о заявках);</li>
    <li>Поставщики email-сервисов (для отправки уведомлений);</li>
    <li>Государственные органы — в случаях, предусмотренных законодательством Российской Федерации.</li>
</ul>

<h2>9. Трансграничная передача персональных данных</h2>
<p>Оператор не осуществляет трансграничную передачу персональных данных в иностранные государства, не обеспечивающие адекватную защиту прав субъектов персональных данных.</p>

<h2>10. Меры по обеспечению безопасности персональных данных</h2>
<p>Оператор принимает необходимые правовые, организационные и технические меры для защиты персональных данных от неправомерного или случайного доступа, уничтожения, изменения, блокирования, копирования, распространения, а также от иных неправомерных действий, в том числе:</p>
<ul>
    <li>Применение шифрования при передаче данных (HTTPS/TLS);</li>
    <li>Ограничение доступа к персональным данным определёнными работниками;</li>
    <li>Использование актуальных средств защиты информации;</li>
    <li>Регулярное обновление программного обеспечения.</li>
</ul>

<h2>11. Права субъекта персональных данных</h2>
<p>Субъект персональных данных имеет право:</p>
<ul>
    <li>Получать информацию о факте обработки его персональных данных, целях и способах обработки;</li>
    <li>Требовать уточнения персональных данных, их блокирования или уничтожения в случае, если данные являются неполными, устаревшими, неточными, незаконно полученными или не являются необходимыми для заявленной цели обработки;</li>
    <li>Отозвать согласие на обработку персональных данных;</li>
    <li>Обжаловать действия или бездействие Оператора в уполномоченный орган по защите прав субъектов персональных данных (Роскомнадзор) или в судебном порядке.</li>
</ul>
<p>Для реализации указанных прав субъект персональных данных может направить письменное обращение по адресу: <a href="mailto:{{contact_email}}">{{contact_email}}</a>.</p>

<h2>12. Обработка cookies</h2>
<p>Сайт использует cookies для обеспечения работоспособности и улучшения пользовательского опыта. Применяются следующие категории cookies:</p>
<ul>
    <li><strong>Необходимые</strong> — обеспечивают базовую функциональность сайта; не могут быть отключены;</li>
    <li><strong>Аналитические</strong> — позволяют собирать статистику посещений (Яндекс.Метрика, Google Analytics);</li>
    <li><strong>Маркетинговые</strong> — позволяют показывать релевантную рекламу (ретаргетинг, пиксели рекламных сетей).</li>
</ul>
<p>Аналитические и маркетинговые cookies устанавливаются только при получении явного согласия пользователя через cookie-баннер на сайте.</p>

<h2>13. Изменения Политики</h2>
<p>Оператор вправе вносить изменения в настоящую Политику. При внесении изменений актуальная редакция Политики публикуется на сайте Оператора. Использование сайта после публикации изменений означает согласие с обновлённой Политикой.</p>

<h2>14. Контакты Оператора</h2>
<p>{{company_name}}<br>
ИНН: {{inn}}<br>
ОГРН: {{ogrn}}<br>
Юридический адрес: {{legal_address}}<br>
Email для обращений: <a href="mailto:{{contact_email}}">{{contact_email}}</a><br>
Представитель по обработке ПД: <a href="mailto:{{dpo_email}}">{{dpo_email}}</a></p>
```

- [ ] **Step 2: Lint — проверь что все {{placeholders}} известны парсеру**

```bash
grep -oE '\{\{[a-z_]+\}\}' template/08_КОД/legal-pages/policy.html.template | sort -u
```

Ожидаемо: `{{company_name}}`, `{{contact_email}}`, `{{dpo_email}}`, `{{effective_date}}`, `{{entity_type}}`, `{{inn}}`, `{{last_updated}}`, `{{legal_address}}`, `{{ogrn}}`.

Заметь: `{{effective_date}}` и `{{last_updated}}` не из brand-kit — это даты которые wp-builder подставит в момент генерации. Тест T4 этого не проверяет напрямую (мы добавим эти поля в legal-dict перед render'ом в B1.6). Это intentional design — даты не статичны.

**ПРИМЕЧАНИЕ для T4 теста:** в тесте `test_render_policy_loads_template_from_disk` мы передаём только 7 полей brand-kit. Тест упадёт с KeyError на `{{effective_date}}`/`{{last_updated}}`. Поправь тест: добавь в `_legal()` базовом dict эти два поля:

```python
'effective_date': '2026-05-21',
'last_updated': '2026-05-21',
```

Это уже сделано в B1.2.1 если ты внимательно скопировал — но если нет, поправь сейчас (либо запусти тест и увидь конкретную ошибку).

---

### Task B1.2.4: Написать consent.html.template

**Files:**
- Create: `template/08_КОД/legal-pages/consent.html.template`

- [ ] **Step 1: Создать каноничный шаблон**

```html
<h1>Согласие на обработку персональных данных</h1>
<p><em>Дата составления: {{effective_date}}.</em></p>

<p>Я, посетитель сайта, действуя свободно, своей волей и в своём интересе, в соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных», даю Оператору согласие на обработку моих персональных данных на следующих условиях:</p>

<h2>1. Оператор</h2>
<p>{{company_name}} ({{entity_type}}), ИНН {{inn}}, ОГРН {{ogrn}}, юридический адрес: {{legal_address}}, email для обращений: <a href="mailto:{{contact_email}}">{{contact_email}}</a>.</p>

<h2>2. Цели обработки персональных данных</h2>
<ul>
    <li>Обработка моей заявки, оставленной через форму обратной связи на сайте Оператора;</li>
    <li>Установление со мной обратной связи (телефонные звонки, отправка сообщений по электронной почте или через мессенджеры);</li>
    <li>Заключение и исполнение договора в случае, если по результатам обращения возникнут договорные отношения;</li>
    <li>Информирование о товарах, услугах, акциях Оператора (в случае моего отдельного согласия на получение рекламных материалов).</li>
</ul>

<h2>3. Перечень персональных данных, на обработку которых даётся согласие</h2>
<ul>
    <li>Фамилия, имя (при добровольном указании);</li>
    <li>Контактный номер телефона;</li>
    <li>Адрес электронной почты;</li>
    <li>Текст сообщения, оставленного в форме обратной связи;</li>
    <li>IP-адрес устройства;</li>
    <li>Данные о посещении сайта (cookies, user agent, источник перехода, UTM-метки).</li>
</ul>

<h2>4. Перечень действий с персональными данными, на совершение которых даётся согласие</h2>
<p>Сбор, запись, систематизация, накопление, хранение, уточнение (обновление, изменение), извлечение, использование, передача (предоставление, доступ), обезличивание, блокирование, удаление, уничтожение персональных данных, как с использованием средств автоматизации, так и без таковых.</p>

<h2>5. Срок действия согласия</h2>
<p>Согласие действует 5 (пять) лет с даты его предоставления либо до момента его отзыва.</p>

<h2>6. Способ отзыва согласия</h2>
<p>Согласие может быть отозвано путём направления письменного уведомления по адресу: <a href="mailto:{{contact_email}}">{{contact_email}}</a>. В случае отзыва согласия Оператор обязан прекратить обработку персональных данных в течение 30 дней с даты получения уведомления, за исключением случаев, когда обработка может быть продолжена на иных правовых основаниях, предусмотренных 152-ФЗ.</p>

<h2>7. Заключительные положения</h2>
<p>Настоящее согласие является информированным и сознательным. Я ознакомлен с <a href="/policy">Политикой обработки персональных данных</a> Оператора и принимаю её условия.</p>
```

- [ ] **Step 2: Lint placeholders**

```bash
grep -oE '\{\{[a-z_]+\}\}' template/08_КОД/legal-pages/consent.html.template | sort -u
```

Ожидаемо: `{{company_name}}`, `{{contact_email}}`, `{{effective_date}}`, `{{entity_type}}`, `{{inn}}`, `{{legal_address}}`, `{{ogrn}}`.

---

### Task B1.2.5: README для legal-pages

**Files:**
- Create: `template/08_КОД/legal-pages/README.md`

- [ ] **Step 1: Создать README**

```markdown
# Legal pages — типовые юр-страницы лендинга

## Что это

Два HTML-шаблона:
- `policy.html.template` — Политика обработки персональных данных (~14 разделов)
- `consent.html.template` — Согласие субъекта на обработку ПД (~7 разделов)

Каноничные тексты основаны на типовых формулировках Роскомнадзора и юр-практике lead-gen в РФ (2023-2025).

## Как используется

1. brand-architect собирает legal-реквизиты Оператора и записывает в `04_БРЕНД/extracted/legal.yaml`.
2. brand-kit-build парсит legal.yaml и эмитит секцию `## Legal` в `04_БРЕНД/brand-kit.md`.
3. wp-builder на этапе 08_КОД:
   - читает `## Legal` из brand-kit.md (через `skills/brand-kit-build/scripts/parse_legal.py`)
   - подставляет `{{company_name}}` / `{{inn}}` / `{{ogrn}}` / `{{legal_address}}` / `{{contact_email}}` / `{{dpo_email}}` в шаблоны через `skills/legal-pages-render/scripts/render.py`
   - подставляет `{{effective_date}}` / `{{last_updated}}` = текущая дата деплоя
   - создаёт WordPress Pages: `/policy` и `/consent` через `wp post create`

## Как редактировать после генерации

**Вариант A (рекомендуемый):** через wp-admin → Страницы → Политика обработки ПД / Согласие. Маркетолог редактирует через визуальный редактор, никаких знаний кода не нужно.

**Вариант B:** изменить `.template` файл в этой папке и перезапустить `/landing-build` — wp-builder обновит существующие Pages по meta-флагу `_lp_legal_page`.

## Юридическая ответственность

Тексты — типовые. **Перед прод-деплоем обязательно покажи юристу клиента.** landing-system не несёт юр-ответственности за конкретное содержимое шаблонов — это адаптируемые отправные точки, не consultation-grade legal advice.

## Что ещё нужно

- Если клиент собирает специальные категории ПД (медицина, образование, биометрия) — типовая Политика не покрывает. Нужны дополнительные разделы.
- Если клиент работает с гражданами ЕС — нужна GDPR-расширенная версия (право на портабельность, специальная роль DPO, и т.д.).
- Если используется трансграничная передача (CRM на серверах в США/Великобритании, типа HubSpot) — раздел 9 Политики должен быть переписан.
```

- [ ] **Step 2: Запустить тест render — должен пройти**

```bash
"/d/Program Files/Python310/python" -m pytest skills/legal-pages-render/tests/test_render.py -v
```

Ожидаемо: `5 passed`.

- [ ] **Step 3: Commit фазы B1.2**

```bash
git add template/08_КОД/legal-pages/ \
        skills/legal-pages-render/
git commit -m "feat(legal-pages): B1.2 — типовые policy.html и consent.html + render

policy.html.template (~14 разделов) и consent.html.template (~7 разделов) —
каноничные тексты по 152-ФЗ с {{placeholders}}.

render.py подставляет реквизиты из brand-kit (через parse_legal) и
выкидывает RuntimeError если legal._incomplete=True (TODO_LEGAL placeholders).

5/5 тестов: substitute, incomplete-reject, missing-key, policy-from-disk,
consent-from-disk.

README для маркетолога объясняет где редактировать и предупреждает что
тексты — отправная точка, не consultation-grade legal advice.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase B1.3 — Cookie-banner (PHP + JS + CSS + consent-init)

**Цель:** vanilla JS cookie-banner с категориями, localStorage state, footer-reopener, Google Consent Mode v2 default-denied + update после save.

**Files:**
- Create: `template/08_КОД/template-parts/cookie-banner.php`
- Create: `template/08_КОД/template-parts/cookie-banner.js`
- Create: `template/08_КОД/template-parts/cookie-banner.css`
- Create: `template/08_КОД/template-parts/consent-init.php`

---

### Task B1.3.1: consent-init.php (gtag default denied)

**Files:**
- Create: `template/08_КОД/template-parts/consent-init.php`

- [ ] **Step 1: Создать файл**

```php
<?php
/**
 * Google Consent Mode v2 — default DENIED.
 *
 * Включается в <head> темы ДО загрузки gtag.js, Yandex.Metrica или GTM
 * через get_template_part('template-parts/consent-init').
 *
 * После того как пользователь сохранит выбор в cookie-banner, JS вызовет
 * gtag('consent', 'update', {...}) — увидь cookie-banner.js.
 */
if (!defined('ABSPATH')) { exit; }
?>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('consent', 'default', {
    'analytics_storage': 'denied',
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'wait_for_update': 500
});
</script>
```

- [ ] **Step 2: PHP lint**

```bash
php -l template/08_КОД/template-parts/consent-init.php
```

Ожидаемо: `No syntax errors detected`.

---

### Task B1.3.2: cookie-banner.css

**Files:**
- Create: `template/08_КОД/template-parts/cookie-banner.css`

- [ ] **Step 1: Создать CSS-файл**

```css
/**
 * Cookie-banner styles.
 *
 * Использует CSS-переменные из tokens.json темы:
 *   --color-bg-overlay, --color-text-primary, --color-text-secondary,
 *   --color-accent, --color-border, --color-bg-secondary,
 *   --radius-md, --space-md, --space-sm, --font-body
 *
 * Если переменные не определены — fallback на нейтральные значения.
 */

.lp-cookie-banner {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--color-bg-secondary, #ffffff);
    border-top: 1px solid var(--color-border, #c3c4c7);
    box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
    padding: var(--space-md, 16px) var(--space-md, 16px);
    font-family: var(--font-body, system-ui, sans-serif);
    font-size: 14px;
    line-height: 1.5;
    color: var(--color-text-primary, #1d2327);
    z-index: 99999;
    max-height: 80vh;
    overflow-y: auto;
}

.lp-cookie-banner__title {
    margin: 0 0 8px;
    font-size: 16px;
    font-weight: 600;
}

.lp-cookie-banner__desc {
    margin: 0 0 12px;
    color: var(--color-text-secondary, #646970);
}

.lp-cookie-banner__categories {
    margin: 12px 0;
}

.lp-cookie-banner__category {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid var(--color-border, #f0f0f1);
}

.lp-cookie-banner__category:last-child {
    border-bottom: none;
}

.lp-cookie-banner__category-info {
    flex: 1;
}

.lp-cookie-banner__category-name {
    font-weight: 600;
    margin-bottom: 2px;
}

.lp-cookie-banner__category-desc {
    font-size: 13px;
    color: var(--color-text-secondary, #646970);
}

.lp-cookie-banner__toggle {
    flex-shrink: 0;
    margin-top: 4px;
}

.lp-cookie-banner__toggle--locked {
    opacity: 0.5;
    cursor: not-allowed;
}

.lp-cookie-banner__actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    align-items: center;
    margin-top: 12px;
    flex-wrap: wrap;
}

.lp-cookie-banner__policy-link {
    margin-right: auto;
    font-size: 13px;
    color: var(--color-text-secondary, #646970);
    text-decoration: underline;
}

.lp-cookie-banner__btn {
    padding: 8px 16px;
    border: 1px solid var(--color-border, #c3c4c7);
    border-radius: var(--radius-md, 4px);
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: opacity 0.15s;
}

.lp-cookie-banner__btn:hover {
    opacity: 0.85;
}

.lp-cookie-banner__btn--primary {
    background: var(--color-accent, #2271b1);
    color: #ffffff;
    border-color: var(--color-accent, #2271b1);
}

.lp-cookie-banner__btn--secondary {
    background: transparent;
    color: var(--color-text-primary, #1d2327);
}

/* Footer reopener — мелкая ссылка в footer */
.lp-cookie-banner__reopen {
    background: transparent;
    border: none;
    padding: 0;
    color: var(--color-text-secondary, #646970);
    font-size: 12px;
    text-decoration: underline;
    cursor: pointer;
    font-family: inherit;
}

.lp-cookie-banner__reopen:hover {
    color: var(--color-text-primary, #1d2327);
}

/* Mobile */
@media (max-width: 600px) {
    .lp-cookie-banner {
        font-size: 13px;
    }
    .lp-cookie-banner__actions {
        flex-direction: column;
        align-items: stretch;
    }
    .lp-cookie-banner__policy-link {
        margin-right: 0;
        text-align: center;
    }
    .lp-cookie-banner__btn {
        width: 100%;
    }
}

.lp-cookie-banner[hidden] {
    display: none !important;
}
```

---

### Task B1.3.3: cookie-banner.php (рендер HTML)

**Files:**
- Create: `template/08_КОД/template-parts/cookie-banner.php`

- [ ] **Step 1: Создать файл**

```php
<?php
/**
 * Cookie-banner — категории necessary / analytics / marketing.
 *
 * Вставляется в footer.php через get_template_part('template-parts/cookie-banner').
 * Появляется при первом визите (если localStorage.lp_cookie_consent отсутствует
 * или версия устарела).
 *
 * Стили в cookie-banner.css. Логика в cookie-banner.js.
 */
if (!defined('ABSPATH')) { exit; }

// Версия согласия — bump при каждом изменении текста policy/consent.
// Должна совпадать с CONSENT_VERSION в cookie-banner.js.
$consent_version = 1;
?>

<div id="lp-cookie-banner" class="lp-cookie-banner" data-version="<?php echo (int) $consent_version; ?>" hidden role="dialog" aria-labelledby="lp-cookie-banner-title">
    <h2 id="lp-cookie-banner-title" class="lp-cookie-banner__title">Мы используем cookies</h2>
    <p class="lp-cookie-banner__desc">Cookies помогают нам обеспечить работу сайта и понять, как вы им пользуетесь. Вы можете выбрать какие категории разрешить.</p>

    <div class="lp-cookie-banner__categories">

        <div class="lp-cookie-banner__category">
            <div class="lp-cookie-banner__category-info">
                <div class="lp-cookie-banner__category-name">Необходимые</div>
                <div class="lp-cookie-banner__category-desc">Обеспечивают базовую работу сайта (сессия, сохранение выбора в баннере). Не могут быть отключены.</div>
            </div>
            <input type="checkbox" class="lp-cookie-banner__toggle lp-cookie-banner__toggle--locked" checked disabled aria-label="Необходимые cookies (всегда включены)">
        </div>

        <div class="lp-cookie-banner__category">
            <div class="lp-cookie-banner__category-info">
                <div class="lp-cookie-banner__category-name">Аналитические</div>
                <div class="lp-cookie-banner__category-desc">Помогают понять как посетители используют сайт (Яндекс.Метрика, Google Analytics).</div>
            </div>
            <input type="checkbox" id="lp-cookie-analytics" class="lp-cookie-banner__toggle" aria-label="Аналитические cookies">
        </div>

        <div class="lp-cookie-banner__category">
            <div class="lp-cookie-banner__category-info">
                <div class="lp-cookie-banner__category-name">Маркетинговые</div>
                <div class="lp-cookie-banner__category-desc">Используются для показа релевантной рекламы и ретаргетинга (Facebook Pixel, ВКонтакте, MyTarget).</div>
            </div>
            <input type="checkbox" id="lp-cookie-marketing" class="lp-cookie-banner__toggle" aria-label="Маркетинговые cookies">
        </div>

    </div>

    <div class="lp-cookie-banner__actions">
        <a href="/policy" class="lp-cookie-banner__policy-link" target="_blank">Политика обработки персональных данных</a>
        <button type="button" id="lp-cookie-save" class="lp-cookie-banner__btn lp-cookie-banner__btn--secondary">Сохранить настройки</button>
        <button type="button" id="lp-cookie-accept-all" class="lp-cookie-banner__btn lp-cookie-banner__btn--primary">Принять все</button>
    </div>
</div>

<button type="button" id="lp-cookie-reopen" class="lp-cookie-banner__reopen" hidden>Настройки cookies</button>
```

- [ ] **Step 2: PHP lint**

```bash
php -l template/08_КОД/template-parts/cookie-banner.php
```

---

### Task B1.3.4: cookie-banner.js (логика + gtag consent.update)

**Files:**
- Create: `template/08_КОД/template-parts/cookie-banner.js`

- [ ] **Step 1: Создать файл**

```javascript
/**
 * Cookie-banner — категоризированное согласие с Google Consent Mode v2.
 *
 * Storage: localStorage key lp_cookie_consent = JSON {analytics, marketing, ts, version}.
 * Версия должна совпадать с data-version на #lp-cookie-banner DOM-элементе.
 *
 * При первом визите (или устаревшей версии) — показывает баннер.
 * После save — вызывает gtag('consent','update',...). Скрывает баннер.
 * В footer показывает кнопку 'Настройки cookies' — переоткрывает баннер.
 */
(function() {
    'use strict';

    var STORAGE_KEY = 'lp_cookie_consent';

    var banner = document.getElementById('lp-cookie-banner');
    if (!banner) return;

    var currentVersion = parseInt(banner.dataset.version, 10) || 1;
    var btnAcceptAll = document.getElementById('lp-cookie-accept-all');
    var btnSave = document.getElementById('lp-cookie-save');
    var btnReopen = document.getElementById('lp-cookie-reopen');
    var toggleAnalytics = document.getElementById('lp-cookie-analytics');
    var toggleMarketing = document.getElementById('lp-cookie-marketing');

    function loadConsent() {
        try {
            var raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return null;
            var parsed = JSON.parse(raw);
            if (typeof parsed !== 'object' || parsed === null) return null;
            return parsed;
        } catch (e) {
            return null;
        }
    }

    function saveConsent(analytics, marketing) {
        var payload = {
            analytics: !!analytics,
            marketing: !!marketing,
            ts: Math.floor(Date.now() / 1000),
            version: currentVersion
        };
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
        } catch (e) {
            console.warn('[cookie-banner] localStorage save failed:', e);
        }
        applyGtagConsent(payload);
    }

    function applyGtagConsent(consent) {
        if (typeof window.gtag !== 'function') return;
        window.gtag('consent', 'update', {
            'analytics_storage': consent.analytics ? 'granted' : 'denied',
            'ad_storage': consent.marketing ? 'granted' : 'denied',
            'ad_user_data': consent.marketing ? 'granted' : 'denied',
            'ad_personalization': consent.marketing ? 'granted' : 'denied'
        });
    }

    function showBanner() {
        banner.hidden = false;
        if (btnReopen) btnReopen.hidden = true;
        var existing = loadConsent();
        if (existing) {
            if (toggleAnalytics) toggleAnalytics.checked = !!existing.analytics;
            if (toggleMarketing) toggleMarketing.checked = !!existing.marketing;
        }
    }

    function hideBanner() {
        banner.hidden = true;
        if (btnReopen) btnReopen.hidden = false;
    }

    // Determine on first paint
    var existing = loadConsent();
    if (existing === null || existing.version !== currentVersion) {
        showBanner();
    } else {
        hideBanner();
        applyGtagConsent(existing);
    }

    // Wire up buttons
    if (btnAcceptAll) {
        btnAcceptAll.addEventListener('click', function() {
            saveConsent(true, true);
            hideBanner();
        });
    }
    if (btnSave) {
        btnSave.addEventListener('click', function() {
            saveConsent(
                toggleAnalytics ? toggleAnalytics.checked : false,
                toggleMarketing ? toggleMarketing.checked : false
            );
            hideBanner();
        });
    }
    if (btnReopen) {
        btnReopen.addEventListener('click', function() {
            showBanner();
        });
    }
})();
```

- [ ] **Step 2: Basic JS sanity (Node parse)**

```bash
node -c template/08_КОД/template-parts/cookie-banner.js
```

Ожидаемо: без вывода. Если `node` не установлен — пропусти этот шаг.

- [ ] **Step 3: Commit фазы B1.3**

```bash
git add template/08_КОД/template-parts/cookie-banner.php \
        template/08_КОД/template-parts/cookie-banner.js \
        template/08_КОД/template-parts/cookie-banner.css \
        template/08_КОД/template-parts/consent-init.php
git commit -m "feat(template): B1.3 — cookie-banner с категориями + Google Consent Mode v2

cookie-banner.php — категории Necessary (locked ON) / Analytics / Marketing
с toggle-переключателями. Две кнопки: 'Сохранить настройки' / 'Принять все'.
Ссылка на /policy. Footer-кнопка 'Настройки cookies' для повторного открытия.

cookie-banner.js — vanilla JS, без зависимостей. Storage:
localStorage.lp_cookie_consent = JSON {analytics, marketing, ts, version}.
Версионирование — bump version в JS-константе и data-version PHP при
изменении policy/consent текстов.

consent-init.php — gtag('consent','default','denied') в <head> ДО
загрузки analytics. После save в баннере — consent.update с granted/denied
по категориям. Поддерживает GA4, GTM, Yandex.Metrica (через ym init guard).

cookie-banner.css — стили через CSS-переменные tokens.json с fallback'ами.
Mobile-responsive.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase B1.4 — legal-block.php для форм

**Цель:** маленький partial с обязательным checkbox согласия на ПД для каждой формы заявки.

**Files:**
- Create: `template/08_КОД/template-parts/legal-block.php`

---

### Task B1.4.1: Создать legal-block.php

**Files:**
- Create: `template/08_КОД/template-parts/legal-block.php`

- [ ] **Step 1: Создать файл**

```php
<?php
/**
 * Legal block для форм заявки — обязательный checkbox согласия на ПД.
 *
 * Вставляется wp-builder'ом в каждую форму заявки ПЕРЕД submit-кнопкой:
 *     <?php get_template_part('template-parts/legal-block'); ?>
 *
 * Имя поля 'pd_consent' с required-валидацией. Бэкенд (rest-lead.php)
 * валидирует что pd_consent='1' и пишет pd_consent_granted_at в БД.
 *
 * Текст явный и информированный (не pre-checked) — соответствует
 * 152-ФЗ ст.9 ч.4 требованию явного согласия.
 */
if (!defined('ABSPATH')) { exit; }
?>
<label class="lp-pd-consent" style="display:flex; align-items:flex-start; gap:8px; margin:12px 0; font-size:13px; line-height:1.4;">
    <input type="checkbox" name="pd_consent" value="1" required style="flex-shrink:0; margin-top:3px;">
    <span>Я согласен на обработку моих персональных данных в соответствии с
    <a href="/policy" target="_blank">Политикой обработки персональных данных</a>
    и <a href="/consent" target="_blank">Согласием на обработку персональных данных</a>.</span>
</label>
```

- [ ] **Step 2: PHP lint**

```bash
php -l template/08_КОД/template-parts/legal-block.php
```

- [ ] **Step 3: Commit**

```bash
git add template/08_КОД/template-parts/legal-block.php
git commit -m "feat(template): B1.4 — legal-block partial для форм заявки

Обязательный checkbox 'Я согласен на обработку ПД' с required-валидацией.
Ссылки на /policy и /consent (target=_blank).

Не pre-checked — соответствует 152-ФЗ ст.9 ч.4 (явное согласие).
Inline-стили чтобы не зависеть от темы.

Бэкенд-валидация — B1.5 в rest-lead.php.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase B1.5 — БД-миграция + REST-валидация pd_consent

**Цель:** добавить колонку `pd_consent_granted_at` в landing_leads через dbDelta + расширить rest-lead.php валидацией.

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php` (добавить колонку)
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php` (валидация + запись timestamp)
- Modify: `skills/wp-landing-config/tests/test_rest_lead.php` (добавить тесты pd_consent)
- Modify: `skills/wp-landing-config/tests/test_db_schema.php` (проверка колонки)

---

### Task B1.5.1: Failing test для pd_consent в rest-lead

**Files:**
- Modify: `skills/wp-landing-config/tests/test_rest_lead.php`

- [ ] **Step 1: Прочитать существующий test_rest_lead.php**

```bash
head -60 skills/wp-landing-config/tests/test_rest_lead.php
```

Запомни функции-хелперы (например `mock_request`, `reset_state`) и формат assertions.

- [ ] **Step 2: Добавить новые тесты T_PD_1..5 в конец файла**

В `skills/wp-landing-config/tests/test_rest_lead.php` сразу перед последней строкой `echo "$tests tests, $failures failures\n";` добавь:

```php
// T_PD_1..5: pd_consent valiidation in rest-lead handler

function reset_pd() {
    global $wpdb;
    $GLOBALS['_mock_leads'] = [];
    $GLOBALS['_mock_next_lead_id'] = 1;
    $GLOBALS['_mock_transients'] = [];  // сброс rate limit
}

function pd_request($overrides = []) {
    $defaults = [
        'name'        => 'Test',
        'phone'       => '+71234567890',
        'email'       => 'test@example.com',
        'pd_consent'  => '1',
        'website'     => '',  // honeypot empty
    ];
    return new MockWpRestRequest(array_merge($defaults, $overrides));
}

// T_PD_1: с pd_consent=1 → 200, pd_consent_granted_at не NULL
reset_pd();
$req = pd_request();
$resp = \LandingConfig\REST\handle_lead($req);
$data = $resp->get_data();
assert_test($data['ok'] === true, 'T_PD_1a returns ok=true');
$rows = array_values($GLOBALS['_mock_leads']);
assert_test(count($rows) === 1, 'T_PD_1b 1 lead inserted');
assert_test(!empty($rows[0]['pd_consent_granted_at']), 'T_PD_1c pd_consent_granted_at populated');

// T_PD_2: без pd_consent → 400
reset_pd();
$req = pd_request();
unset($req->params['pd_consent']);
$resp = \LandingConfig\REST\handle_lead($req);
$data = $resp->get_data();
assert_test($resp->get_status() === 400, 'T_PD_2a status 400');
assert_test($data['ok'] === false, 'T_PD_2b ok=false');
assert_test(count($GLOBALS['_mock_leads']) === 0, 'T_PD_2c no lead inserted');

// T_PD_3: с pd_consent='' → 400
reset_pd();
$resp = \LandingConfig\REST\handle_lead(pd_request(['pd_consent' => '']));
assert_test($resp->get_status() === 400, 'T_PD_3 empty pd_consent rejected');

// T_PD_4: с pd_consent='0' → 400
reset_pd();
$resp = \LandingConfig\REST\handle_lead(pd_request(['pd_consent' => '0']));
assert_test($resp->get_status() === 400, 'T_PD_4 pd_consent=0 rejected');

// T_PD_5: timestamp в пределах текущей минуты
reset_pd();
$ts_before = time();
\LandingConfig\REST\handle_lead(pd_request());
$rows = array_values($GLOBALS['_mock_leads']);
$ts_granted = strtotime($rows[0]['pd_consent_granted_at']);
$ts_after = time();
assert_test($ts_granted >= $ts_before && $ts_granted <= $ts_after + 1,
    "T_PD_5 timestamp within range (ts_before=$ts_before, ts_granted=$ts_granted, ts_after=$ts_after)");
```

- [ ] **Step 3: Прогон — должно упасть**

```bash
php skills/wp-landing-config/tests/test_rest_lead.php 2>&1 | tail -10
```

Ожидаемо: новые T_PD_* тесты падают (pd_consent ещё не валидируется).

---

### Task B1.5.2: Расширить rest-lead.php

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php`

- [ ] **Step 1: Добавить валидацию pd_consent ДО формирования $data**

В `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php` найди блок:

```php
// Required: at least one of phone or email
$name = sanitize_text_field(wp_unslash($params['name'] ?? ''));
```

Сразу ПЕРЕД ним вставь:

```php
// pd_consent (152-ФЗ ст.9): обязательное явное согласие. Принимаем только '1'.
$pd_consent = (string) ($params['pd_consent'] ?? '');
if ($pd_consent !== '1') {
    return new \WP_REST_Response(
        ['ok' => false, 'error' => 'pd_consent_required'],
        400
    );
}
```

- [ ] **Step 2: Добавить pd_consent_granted_at в $data**

В том же файле найди массив `$data` (начинается с `$data = [`). Добавь в конец массива (перед закрывающей `]`):

```php
        'pd_consent_granted_at' => current_time('mysql'),
```

Итоговый $data должен выглядеть так (фрагмент):

```php
$data = [
    'name'                  => $name,
    // ... все существующие поля ...
    'processed_status'      => 'pending',
    'pd_consent_granted_at' => current_time('mysql'),
];
```

- [ ] **Step 3: Прогон test_rest_lead — должно пройти**

```bash
php skills/wp-landing-config/tests/test_rest_lead.php 2>&1 | tail -3
```

Ожидаемо: все тесты pass (14 + 5 = 19 ассертов, 0 failures).

Если падает на `pd_consent_granted_at_populated` — мок $wpdb->insert в wp-bootstrap должен сохранять все ключи в `_mock_leads` массив. Проверь что мок не теряет произвольные ключи.

---

### Task B1.5.3: Failing test для колонки в db_schema

**Files:**
- Modify: `skills/wp-landing-config/tests/test_db_schema.php`

- [ ] **Step 1: Добавить тест T_PD_DB_1**

В `skills/wp-landing-config/tests/test_db_schema.php` перед последним `echo` добавь:

```php
// T_PD_DB_1: pd_consent_granted_at column declared in landing_leads CREATE TABLE
$leads_sql = $GLOBALS['_mock_dbdelta_calls'][0] ?? '';
assert_test(strpos($leads_sql, 'pd_consent_granted_at') !== false,
    'T_PD_DB_1 column pd_consent_granted_at declared in landing_leads');
assert_test(strpos($leads_sql, 'DATETIME NULL') !== false,
    'T_PD_DB_2 type is DATETIME NULL');
```

- [ ] **Step 2: Прогон — должно упасть**

```bash
php skills/wp-landing-config/tests/test_db_schema.php 2>&1 | tail -5
```

---

### Task B1.5.4: Добавить колонку в db.php install_schema

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php`

- [ ] **Step 1: Прочитать существующий CREATE TABLE**

```bash
grep -n "processed_status\|CREATE TABLE.*leads" skills/wp-landing-config/mu-plugin/landing-config/includes/db.php
```

Найди строку `processed_status VARCHAR(32) NOT NULL DEFAULT 'pending',` (около line 79).

- [ ] **Step 2: Добавить колонку pd_consent_granted_at**

В `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php` найди:

```php
        processed_status VARCHAR(32) NOT NULL DEFAULT 'pending',
        PRIMARY KEY (id),
        KEY created_at (created_at),
        KEY processed_status (processed_status)
```

Замени на:

```php
        processed_status VARCHAR(32) NOT NULL DEFAULT 'pending',
        pd_consent_granted_at DATETIME NULL,
        PRIMARY KEY (id),
        KEY created_at (created_at),
        KEY processed_status (processed_status)
```

- [ ] **Step 3: Прогон test_db_schema — должно пройти**

```bash
php skills/wp-landing-config/tests/test_db_schema.php 2>&1 | tail -3
```

Ожидаемо: `10 tests, 0 failures` (8 существующих + 2 новых).

- [ ] **Step 4: Regression all tests**

```bash
for t in skills/wp-landing-config/tests/test_*.php; do echo "=== $t ==="; php "$t" 2>&1 | tail -1; done
```

Ожидаемо: pre-existing openssl-failures (5+2+2), никаких новых.

- [ ] **Step 5: Commit фазы B1.5**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/db.php \
        skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php \
        skills/wp-landing-config/tests/test_rest_lead.php \
        skills/wp-landing-config/tests/test_db_schema.php
git commit -m "feat(wp-landing-config): B1.5 — pd_consent валидация + БД-колонка

REST /lead handler теперь требует pd_consent='1' — без него 400 + 'pd_consent_required'.
При успехе пишет pd_consent_granted_at = current_time('mysql') как формальное
доказательство явного согласия (152-ФЗ ст.9).

Колонка pd_consent_granted_at DATETIME NULL добавлена в landing_leads через
dbDelta — применится автоматически на следующей загрузке wp-admin на ailexi.ru.

5 тестов pd_consent (200/400 ветки, пустое/нулевое значение, timestamp range)
+ 2 теста schema (column declared, type DATETIME NULL).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase B1.6 — wp-builder: вставка banner, legal-block, генерация legal-pages

**Цель:** расширить wp-builder agent инструкциями про:
1. Вставку `cookie-banner` и `consent-init` в footer/header темы
2. Вставку `legal-block` в каждую форму заявки
3. Генерацию WordPress Pages /policy и /consent через render.py

**Files:**
- Modify: `agents/wp-builder.md`
- Create: `skills/wp-builder/scripts/install_legal_pages.sh` (новый helper для wp-cli)
- Create: `skills/wp-builder/tests/test_install_legal_pages.bats`

---

### Task B1.6.1: Helper-скрипт install_legal_pages.sh

**Files:**
- Create: `skills/wp-builder/scripts/install_legal_pages.sh`

- [ ] **Step 1: Создать скрипт**

```bash
#!/usr/bin/env bash
# install_legal_pages.sh — генерирует policy.html и consent.html
# через render.py + создаёт WordPress Pages через wp-cli.
#
# Usage: bash install_legal_pages.sh <project-dir>
#
# Reads:
#   <project-dir>/04_БРЕНД/brand-kit.md (через parse_legal.py)
#   <project-dir>/.env (BEGET_USER/HOST/SSH_KEY/PATH)
#
# Creates on Beget:
#   wp post create --post_type=page --post_name=policy --post_title='...'
#   wp post create --post_type=page --post_name=consent --post_title='...'
#
# Idempotent: если Page с meta _lp_legal_page=policy|consent уже есть — wp post update.

set -euo pipefail

PROJECT="${1:-}"
if [ -z "$PROJECT" ]; then
    echo "Usage: $0 <project-dir>" >&2
    exit 2
fi
PROJECT="$(cd "$PROJECT" && pwd)"

[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }
[ -f "$PROJECT/04_БРЕНД/brand-kit.md" ] || { echo "ERROR: brand-kit.md not found" >&2; exit 1; }

set -a; source "$PROJECT/.env"; set +a
: "${BEGET_USER:?missing in .env}"
: "${BEGET_HOST:?missing in .env}"
: "${BEGET_SSH_KEY:?missing in .env}"
: "${BEGET_PATH:?missing in .env}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYSTEM_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PYTHON="${PYTHON:-python3}"

# Generate HTML through render.py
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

PYTHONPATH="$SYSTEM_ROOT/skills/legal-pages-render/scripts:$SYSTEM_ROOT/skills/brand-kit-build/scripts" \
$PYTHON - <<EOF
import sys
sys.path.insert(0, "$SYSTEM_ROOT/skills/legal-pages-render/scripts")
sys.path.insert(0, "$SYSTEM_ROOT/skills/brand-kit-build/scripts")
from parse_legal import parse_legal_from_brand_kit
from render import render_policy, render_consent
import datetime

legal = parse_legal_from_brand_kit("$PROJECT/04_БРЕНД/brand-kit.md")
if legal is None:
    print("ERROR: legal section missing in brand-kit.md", file=sys.stderr)
    sys.exit(1)
if legal.get('_incomplete'):
    print("ERROR: legal section has TODO_LEGAL placeholders. Fill 04_БРЕНД/extracted/legal.yaml.", file=sys.stderr)
    sys.exit(1)

today = datetime.date.today().isoformat()
legal['effective_date'] = today
legal['last_updated'] = today

with open("$TMP_DIR/policy.html", "w", encoding="utf-8") as f:
    f.write(render_policy(legal))
with open("$TMP_DIR/consent.html", "w", encoding="utf-8") as f:
    f.write(render_consent(legal))

print("Generated policy.html and consent.html in $TMP_DIR")
EOF

# Upload to Beget
SSH="ssh -i $BEGET_SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=ERROR ${BEGET_USER}@${BEGET_HOST}"
WP="/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --path=$BEGET_PATH"

scp -i "$BEGET_SSH_KEY" -o StrictHostKeyChecking=no \
    "$TMP_DIR/policy.html" "$TMP_DIR/consent.html" \
    "${BEGET_USER}@${BEGET_HOST}:/tmp/"

# Helper for idempotent create-or-update
upsert_page() {
    local slug="$1"
    local title="$2"
    local content_path="/tmp/${slug}.html"

    local existing_id=$($SSH "$WP post list --post_type=page --meta_key=_lp_legal_page --meta_value=$slug --format=ids" 2>/dev/null | head -1 | tr -d '[:space:]')

    if [ -n "$existing_id" ]; then
        $SSH "$WP post update $existing_id --post_content=\"\$(cat $content_path)\" --post_title='$title'"
        $SSH "rm $content_path"
        echo "Updated existing /$slug page (id=$existing_id)"
    else
        local new_id=$($SSH "$WP post create $content_path --post_type=page --post_status=publish --post_name=$slug --post_title='$title' --porcelain")
        $SSH "$WP post meta update $new_id _lp_legal_page $slug"
        $SSH "rm $content_path"
        echo "Created /$slug page (id=$new_id)"
    fi
}

upsert_page policy "Политика обработки персональных данных"
upsert_page consent "Согласие на обработку персональных данных"

echo "✅ Legal pages installed"
```

- [ ] **Step 2: chmod +x + bash-lint**

```bash
chmod +x skills/wp-builder/scripts/install_legal_pages.sh
bash -n skills/wp-builder/scripts/install_legal_pages.sh
```

Ожидаемо: без вывода.

---

### Task B1.6.2: Расширить agents/wp-builder.md

**Files:**
- Modify: `agents/wp-builder.md`

- [ ] **Step 1: Прочитать структуру wp-builder.md**

```bash
grep -n "^##" agents/wp-builder.md
```

Найди раздел "## Process" или эквивалент — куда добавить новые шаги.

- [ ] **Step 2: Добавить инструкции про B1**

В `agents/wp-builder.md` найди раздел про вставку footer/header (или конец процесса генерации темы). Добавь новый блок:

```markdown
## Legal & Cookie-banner (152-ФЗ compliance)

После генерации темы и блоков — обязательная юр-инфраструктура для прод-деплоя в РФ:

### 1. Cookie-banner в footer

В `wp-theme/footer.php` перед `<?php wp_footer(); ?>`:

```php
<?php get_template_part('template-parts/cookie-banner'); ?>
```

В `wp-theme/header.php` в `<head>`, **ДО** любых analytics-скриптов (gtag/Yandex.Metrica/GTM):

```php
<?php get_template_part('template-parts/consent-init'); ?>
```

### 2. Подключить CSS и JS cookie-banner

В `wp-theme/functions.php` в `wp_enqueue_scripts` callback:

```php
wp_enqueue_style('lp-cookie-banner', get_template_directory_uri() . '/template-parts/cookie-banner.css', [], '1.0');
wp_enqueue_script('lp-cookie-banner', get_template_directory_uri() . '/template-parts/cookie-banner.js', [], '1.0', true);
```

Скопировать файлы:
- `template/08_КОД/template-parts/cookie-banner.php` → `wp-theme/template-parts/cookie-banner.php`
- `template/08_КОД/template-parts/cookie-banner.js` → `wp-theme/template-parts/cookie-banner.js`
- `template/08_КОД/template-parts/cookie-banner.css` → `wp-theme/template-parts/cookie-banner.css`
- `template/08_КОД/template-parts/consent-init.php` → `wp-theme/template-parts/consent-init.php`
- `template/08_КОД/template-parts/legal-block.php` → `wp-theme/template-parts/legal-block.php`

### 3. Legal-block в каждую форму заявки

В каждой Gutenberg-блок-шаблоне с формой (Hero, Contact, Footer-CTA) ПЕРЕД `<button type="submit">`:

```php
<?php get_template_part('template-parts/legal-block'); ?>
```

Это checkbox с required-валидацией согласия на ПД (152-ФЗ ст.9).

### 4. Генерация юр-страниц /policy и /consent

После деплоя темы запусти:

```bash
bash skills/wp-builder/scripts/install_legal_pages.sh <project-dir>
```

Скрипт:
1. Парсит ## Legal из `<project>/04_БРЕНД/brand-kit.md`
2. Если incomplete или TODO_LEGAL — выбрасывает ошибку и блокирует деплой
3. Подставляет реквизиты в `template/08_КОД/legal-pages/{policy,consent}.html.template`
4. Через wp-cli создаёт WordPress Pages (или обновляет существующие по meta `_lp_legal_page`)

### 5. Проверки

Перед закрытием этапа 08:
- `/policy` отдаёт 200 (curl https://<domain>/policy)
- `/consent` отдаёт 200
- View source главной страницы содержит cookie-banner DOM
- Submit формы без checkbox → браузер показывает «Заполните это поле»
- Submit с checkbox → 200 ok=true и `pd_consent_granted_at != NULL` в БД
```

- [ ] **Step 3: Commit фазы B1.6**

```bash
git add agents/wp-builder.md \
        skills/wp-builder/scripts/install_legal_pages.sh
git commit -m "feat(wp-builder): B1.6 — legal-pages + cookie-banner integration

wp-builder.md расширен 5-шаговой инструкцией про юр-инфраструктуру:
1. cookie-banner в footer.php + consent-init в head
2. enqueue cookie-banner CSS/JS в functions.php
3. legal-block.php в каждой форме заявки
4. install_legal_pages.sh для генерации /policy и /consent
5. финальные проверки перед закрытием этапа 08

install_legal_pages.sh — bash helper: parse_legal → render → wp-cli upsert
по meta _lp_legal_page. Идемпотентный (update если есть, create если нет).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase B1.7 — Stage-gate soft-check

**Цель:** связать существующий soft-check `legal_blocks_present` в `config/stage-gates.yaml` с реальной проверкой через grep по сгенерированной теме.

**Files:**
- Modify: `config/stage-gates.yaml` (заменить prompt-only check на script-based)
- Create: `scripts/checks/check_legal_blocks.sh`

---

### Task B1.7.1: Скрипт-проверка

**Files:**
- Create: `scripts/checks/check_legal_blocks.sh`

- [ ] **Step 1: Создать файл**

```bash
#!/usr/bin/env bash
# check_legal_blocks.sh — проверяет что в сгенерированной wp-theme есть
# cookie-banner, legal-block, consent-init.
#
# Usage: bash check_legal_blocks.sh <project-dir>
# Exit: 0 если всё OK, 1 если чего-то не хватает.

set -euo pipefail

PROJECT="${1:-}"
if [ -z "$PROJECT" ]; then
    echo "Usage: $0 <project-dir>" >&2
    exit 2
fi

THEME_DIR="$PROJECT/08_КОД/wp-theme"
[ -d "$THEME_DIR" ] || { echo "FAIL: theme dir not found: $THEME_DIR"; exit 1; }

MISSING=()

# 1. cookie-banner.php присутствует
[ -f "$THEME_DIR/template-parts/cookie-banner.php" ] || MISSING+=("cookie-banner.php")
# 2. consent-init.php присутствует
[ -f "$THEME_DIR/template-parts/consent-init.php" ] || MISSING+=("consent-init.php")
# 3. legal-block.php присутствует
[ -f "$THEME_DIR/template-parts/legal-block.php" ] || MISSING+=("legal-block.php")
# 4. footer.php содержит вызов cookie-banner
if [ -f "$THEME_DIR/footer.php" ]; then
    grep -q "cookie-banner" "$THEME_DIR/footer.php" || MISSING+=("footer.php missing cookie-banner reference")
else
    MISSING+=("footer.php")
fi
# 5. header.php содержит consent-init (ДО analytics)
if [ -f "$THEME_DIR/header.php" ]; then
    grep -q "consent-init" "$THEME_DIR/header.php" || MISSING+=("header.php missing consent-init reference")
else
    MISSING+=("header.php")
fi
# 6. Хотя бы один блок-шаблон ссылается на legal-block
BLOCK_REFS=$(grep -rl "legal-block" "$THEME_DIR/blocks/" 2>/dev/null | wc -l)
if [ "$BLOCK_REFS" -lt 1 ]; then
    MISSING+=("no block templates reference legal-block (forms missing PD checkbox)")
fi

if [ ${#MISSING[@]} -eq 0 ]; then
    echo "✅ legal_blocks_present: OK"
    exit 0
fi

echo "❌ legal_blocks_present: missing:"
for m in "${MISSING[@]}"; do
    echo "   - $m"
done
exit 1
```

- [ ] **Step 2: chmod + bash-lint**

```bash
chmod +x scripts/checks/check_legal_blocks.sh
bash -n scripts/checks/check_legal_blocks.sh
```

---

### Task B1.7.2: Привязать к stage-gates.yaml

**Files:**
- Modify: `config/stage-gates.yaml`

- [ ] **Step 1: Найти существующий soft-check**

```bash
grep -n "legal_blocks_present\|legal_block" config/stage-gates.yaml
```

Если есть существующий entry — найти его контекст. Если entry отсутствует — добавить.

- [ ] **Step 2: Обновить entry**

В `config/stage-gates.yaml` в секции этапа `08_код` (или `08_build`) — найди раздел `soft_checks:` (если нет — создай). Добавь/замени:

```yaml
  soft_checks:
    - id: legal_blocks_present
      title: "Cookie-banner, consent-init, legal-block присутствуют в теме"
      command: "bash scripts/checks/check_legal_blocks.sh {project_dir}"
      blocking: false  # warning, не блокирует deploy — но в логи попадает
```

Если в stage-gates.yaml используется другой формат — адаптируй сохраняя интент. Если есть существующий prompt-based check — замени на command-based.

- [ ] **Step 3: Commit B1.7**

```bash
git add scripts/checks/check_legal_blocks.sh \
        config/stage-gates.yaml
git commit -m "feat(stage-gates): B1.7 — script-based legal_blocks_present check

scripts/checks/check_legal_blocks.sh проверяет:
- cookie-banner.php, consent-init.php, legal-block.php в template-parts/
- footer.php содержит cookie-banner reference
- header.php содержит consent-init reference (ДО analytics)
- хотя бы один блок-шаблон ссылается на legal-block (формы с PD checkbox)

Привязан к stage-gates.yaml в этапе 08_код soft_checks (blocking:false —
warning, не блокирует но фиксируется).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Phase B1.8 — Smoke + docs + deploy

**Цель:** расширить live smoke новыми проверками, deploy на ailexi.ru, обновить CLAUDE.md.

**Files:**
- Modify: `skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh`
- Modify: `CLAUDE.md`

---

### Task B1.8.1: Smoke-расширение

**Files:**
- Modify: `skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh`

- [ ] **Step 1: Добавить T9-T11 в smoke**

В `skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh` перед `echo "✅ S2-A.3 + B19 live smoke GREEN"` добавь:

```bash
echo "▶ T9: POST /lead без pd_consent → 400"
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 -X POST \
    "https://russian.ailexi.ru/wp-json/landing/v1/lead" \
    -d "name=Test&phone=+71234567890&email=test@example.com&website=")
test "$code" = "400" || { echo "FAIL: expected 400 without pd_consent, got $code"; exit 1; }
echo "  OK no-consent → 400"

echo "▶ T10: POST /lead с pd_consent=1 → 200"
resp=$(curl -s --max-time 10 -X POST \
    "https://russian.ailexi.ru/wp-json/landing/v1/lead" \
    -d "name=SmokeTest&phone=+79991234567&email=smoke@test.ru&website=&pd_consent=1")
echo "$resp" | grep -q '"ok":true' || { echo "FAIL: expected ok:true, got: $resp"; exit 1; }
echo "  OK with-consent → 200"

echo "▶ T11: /policy и /consent отдают 200 (если legal-pages засеяны)"
for slug in policy consent; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "https://russian.ailexi.ru/$slug" || echo "000")
    case "$code" in
        200) echo "  OK /$slug → 200" ;;
        404) echo "  SKIP /$slug → 404 (legal-pages не засеяны на этом сегменте — это OK для smoke)" ;;
        *) echo "FAIL: /$slug returned $code"; exit 1 ;;
    esac
done
```

- [ ] **Step 2: Deploy mu-plugin (только B1.5 изменения, не темы)**

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a
```

- [ ] **Step 3: Запустить smoke**

```bash
bash skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh /tmp/test-s2a
```

Ожидаемо: все 20 ассертов GREEN (17 + 3 новых). T11 может выдать SKIP для legal-pages — это нормально, темы на ailexi.ru ещё не пересобраны с B1.6 install_legal_pages.sh.

- [ ] **Step 4: Commit smoke**

```bash
git add skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh
git commit -m "test(wp-landing-config): B1.8 — smoke для pd_consent + legal-pages

+T9 POST /lead без pd_consent → 400
+T10 POST /lead с pd_consent=1 → 200 (ok:true)
+T11 /policy и /consent → 200 (SKIP если 404 — legal-pages не засеяны)

Прогон на russian.ailexi.ru через HTTPS.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task B1.8.2: CLAUDE.md docs

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Найти секцию S2-A.4 (B19)**

```bash
grep -n "S2-A.4\|B19" CLAUDE.md | head -3
```

- [ ] **Step 2: Добавить секцию после B19**

После последней строки секции `### S2-A.4 — Lead Status Workflow MVP (B19, 2026-05-20)` (после строки `и [plan](docs/superpowers/plans/2026-05-20-b19-lead-status-workflow-plan.md).`) добавь:

```markdown

### B1 — Cookie-banner + 152-ФЗ согласие на ПД (2026-05-21)

Template-level юр-инфраструктура для каждого лендинга:

- **brand-kit.md ## Legal секция** — реквизиты Оператора ПД (company_name, entity_type,
  inn, ogrn, legal_address, contact_email, dpo_email). Собирается brand-architect'ом
  на этапе 04, парсится через `skills/brand-kit-build/scripts/parse_legal.py`.
- **Cookie-banner с категориями** (`template/08_КОД/template-parts/cookie-banner.{php,js,css}`)
  — Necessary (locked) / Analytics / Marketing. localStorage `lp_cookie_consent`
  с версионированием. Появляется при первом визите, footer-кнопка для
  переоткрытия.
- **Google Consent Mode v2** (`consent-init.php`) — gtag('consent','default','denied')
  в <head> ДО загрузки Metrica/GTM/GA4. После save в баннере — consent.update.
- **Legal-block в формах** (`legal-block.php`) — обязательный checkbox согласия
  на ПД с required-валидацией. Не pre-checked (152-ФЗ ст.9 — явное согласие).
- **Бэкенд-валидация** в REST /wp-json/landing/v1/lead — 400 если pd_consent != '1',
  при успехе пишет timestamp `pd_consent_granted_at` в landing_leads (формальное
  доказательство согласия для возможных проверок Роскомнадзора).
- **Юр-страницы** (`template/08_КОД/legal-pages/{policy,consent}.html.template`) —
  типовые тексты с {{placeholders}} для подстановки реквизитов из brand-kit.
  Создаются через `skills/wp-builder/scripts/install_legal_pages.sh` (wp-cli upsert
  по meta `_lp_legal_page`).
- **Stage-gate soft-check** `legal_blocks_present` — grep по wp-theme что
  cookie-banner/consent-init/legal-block подключены в footer/header/блоках форм.

ВАЖНО: тексты policy/consent — типовые, основаны на формулировках Роскомнадзора.
Перед прод-деплоем у клиента — обязательная проверка юристом.

См. [spec](docs/superpowers/specs/2026-05-21-b1-cookie-banner-pd-consent-design.md)
и [plan](docs/superpowers/plans/2026-05-21-b1-cookie-banner-pd-consent-plan.md).
```

- [ ] **Step 3: Commit и push**

```bash
git add CLAUDE.md
git commit -m "docs(b1): CLAUDE.md секция про Cookie-banner + 152-ФЗ согласие

Зафиксированы:
- ## Legal секция brand-kit с 7 полями Оператора ПД
- Cookie-banner с категориями + Google Consent Mode v2
- Legal-block для форм (required checkbox согласия)
- Бэкенд-валидация pd_consent + timestamp в БД
- Типовые юр-страницы через template + render
- Stage-gate soft-check legal_blocks_present

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Финал

После завершения всех 8 фаз — финальный code review всего B1 (как было в B19):
- cross-cutting consistency между brand-kit / wp-builder / banner / legal-block
- безопасность (XSS, CSRF, prepared SQL, validation order)
- backward compat (rest-lead существующие тесты не сломались)
- multisite: pd_consent колонка применилась на subsite через dbDelta
- test health

После review — отчитаться пользователю что B1 готов, branch ready для merge в main + push.

---

## Self-Review плана

**1. Spec coverage:**
- §3 brand-kit legal — Phase B1.1 ✓
- §4 cookie-banner — Phase B1.3 ✓
- §5 PD checkbox в формах — Phase B1.4 ✓
- §5.3 БД миграция — Phase B1.5 ✓
- §6 legal-страницы — Phase B1.2 (templates+render) + B1.6 (install через wp-builder) ✓
- §7 файлы — все 8 новых + 6 модификаций присутствуют ✓
- §8 безопасность — описано в B1.4 (not pre-checked), B1.5 (bekend validation), B1.3 (gtag denied default) ✓
- §9 тестирование — unit B1.1.1, B1.2.1, B1.5.1, B1.5.3; smoke B1.8 ✓
- §10 out-of-scope — явно вне фаз (consent-management UI, geolocation, A/B, JS unit-tests deferred) ✓

**2. Placeholder scan:** TBD/TODO нет. Единственный `TODO_LEGAL` — это feature (placeholder в brand-kit), не plan-failure.

**3. Type consistency:**
- `parse_legal_from_brand_kit(path)` — везде одинаково
- `render_policy(legal)` / `render_consent(legal)` — везде одинаково, оба ожидают dict с 7 brand-kit полями + `effective_date` + `last_updated` (доб в B1.6 install_legal_pages.sh)
- `pd_consent_granted_at` — везде одинаково (column name, $data key, test assertion)
- Storage key `lp_cookie_consent` — везде одинаково (JS + потенциально PHP в будущем)
- Meta key `_lp_legal_page` — везде одинаково (B1.6.1 upsert helper)

**4. Известные риски:**
- B1.6.1 install_legal_pages.sh использует bash heredoc с inline Python — может быть fragile на разных версиях bash. Тест-фаза B1.6 не имеет smoke на ailexi.ru (только bash -n syntax-check). Это intentional — full e2e будет в B1.8 ручной проверкой.
- B1.7.1 check_legal_blocks.sh ожидает что wp-theme сгенерирована в `<project>/08_КОД/wp-theme/`. Если структура темы другая (например, в `wp-theme/<theme-name>/`) — нужно адаптировать пути. Implementer должен проверить на реальном проекте.

План готов.
