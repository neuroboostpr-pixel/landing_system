# B1 — Work In Progress (pause point 2026-05-21)

## Где остановились

**Текущая фаза:** B1.1 — brand-kit legal-секция + parse_legal helper.

**Состояние:** реализация прошла spec-review (✅), code-review нашёл 3 фикса.
Fix-subagent был задиспатчен но **отменён пользователем** перед применением фиксов
(переключение на другую задачу — dubai-avto-liza).

**Worktree:** `D:\AI_TEAMS\landing_system\.claude\worktrees\b1-cookie-banner-pd-consent`
**Branch:** `worktree-b1-cookie-banner-pd-consent`
**HEAD:** `dd9be4a`

## Что готово в B1

- ✅ Spec: `docs/superpowers/specs/2026-05-21-b1-cookie-banner-pd-consent-design.md` (commit `f0a91fe` в main)
- ✅ Plan: `docs/superpowers/plans/2026-05-21-b1-cookie-banner-pd-consent-plan.md` (commit `e6e0fac` в main)
- ✅ B1.1.1+B1.1.2: `skills/brand-kit-build/scripts/parse_legal.py` + 5 тестов (commit `f880faa`)
- ✅ B1.1.3+B1.1.4: `skills/brand-kit-build/scripts/build.py` (load_legal_input + build_legal_section) + `agents/brand-architect.md` (раздел legal-реквизитов) (commit `dd9be4a`)
- ⏸ **B1.1 code-review fixes** — НЕ ПРИМЕНЕНЫ. См. ниже.

## Что нужно сделать при возвращении к B1

### Шаг 1: Применить 3 code-review фикса к B1.1

**Issue 1 (CRITICAL стиль):** `import sys` внутри функции `parse_legal_from_brand_kit`.
- Файл: `skills/brand-kit-build/scripts/parse_legal.py`
- Перенести `import sys` из `except yaml.YAMLError:` блока на уровень модуля (рядом с `import re`, `import yaml`).

**Issue 2 (CRITICAL bug):** `load_legal_input` не проверяет `isinstance(data, dict)`.
- Файл: `skills/brand-kit-build/scripts/build.py`
- Если в `04_БРЕНД/extracted/legal.yaml` маркетолог запишет список вместо dict — `build_legal_section` упадёт с `AttributeError`.
- Fix: после `yaml.safe_load(f)` добавить `if not isinstance(data, dict): return None`.

**Issue 3 (IMPORTANT):** tempfile leak в тестах.
- Файл: `skills/brand-kit-build/tests/test_parse_legal.py`
- Метод `_write` создаёт файлы с `delete=False` без cleanup.
- Fix: добавить `self.addCleanup(os.unlink, f.name)` после `f.close()` + `import os` наверх.

**Commit message:**
```
fix(brand-kit-build): B1.1 — code review fixes

CRITICAL — import sys перенесён на уровень модуля
CRITICAL — load_legal_input проверяет isinstance(data, dict)
IMPORTANT — tempfile cleanup через addCleanup в тестах
```

### Шаг 2: Продолжить с B1.2

После применения фиксов — продолжать subagent-driven execution по плану:

- **B1.2** — типовые `policy.html.template` + `consent.html.template` + `render.py` (5 тестов)
- **B1.3** — `cookie-banner.{php,js,css}` + `consent-init.php` (Google Consent Mode v2)
- **B1.4** — `legal-block.php` для форм заявки
- **B1.5** — БД-колонка `pd_consent_granted_at` + REST-валидация (7 тестов)
- **B1.6** — wp-builder инструкции + `install_legal_pages.sh`
- **B1.7** — stage-gate soft-check `legal_blocks_present`
- **B1.8** — smoke + CLAUDE.md + deploy + merge в main

План: `docs/superpowers/plans/2026-05-21-b1-cookie-banner-pd-consent-plan.md`

### Шаг 3: Merge в main и push

После B1.8:
```bash
git checkout main
git merge --no-ff worktree-b1-cookie-banner-pd-consent
git push origin main
```

## Контекст почему пауза

Пользователь переключился на новую задачу: добавить лендинг `dubai-avto-liza`
(репо https://github.com/neuroboostpr-pixel/dubai-avto-liza) в папку лендингов и
довести его по флоу до деплоя на Бегет (поддомен `dubai-avto-liza.ailexi.ru` или
аналогичный).

Возврат к B1 — после завершения dubai-avto-liza.

## Состояние тестов

Baseline на HEAD `dd9be4a`:
- `test_parse_legal.py`: 5 passed
- PHP тесты: pre-existing openssl-failures (5+2+2=9), никаких новых

## Не забыть

- **dubai-avto-liza** — другой проект, НЕ ТРОГАЕТ landing-system код, только использует его.
  B1 worktree должна оставаться нетронутой пока работаем над dubai-avto-liza.
- Если возникнет потребность в landing-system изменениях во время dubai-avto-liza —
  делать отдельный worktree от main, НЕ в b1-cookie-banner-pd-consent.
