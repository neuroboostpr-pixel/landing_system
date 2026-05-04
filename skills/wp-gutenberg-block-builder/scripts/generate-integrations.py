#!/usr/bin/env python3
"""Inject CRM webhooks into functions.php; write integration instruction files.

CLI: python3 generate-integrations.py <project-dir>
Reads: 00_БРИФ/brief.md
Modifies: 08_КОД/wp-theme/functions.php — replaces // [FLUENT_WEBHOOK]
Creates: 08_КОД/integrations/*.md — setup instructions per service
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success, warn

_FLUENT_HOOK = """\
// Fluent Forms — webhook для CRM и Telegram
add_action('fluentform/submission_inserted', function ($entryId, $formData, $form) {
    $fields = is_array($formData) ? $formData : (array)$formData;

    // AmoCRM webhook (задай AMOCRM_WEBHOOK_URL в .env)
    $amo_url = getenv('AMOCRM_WEBHOOK_URL');
    if ($amo_url) {
        wp_remote_post($amo_url, [
            'headers' => ['Content-Type' => 'application/json'],
            'body'    => wp_json_encode(['lead' => $fields]),
            'timeout' => 5,
        ]);
    }

    // Bitrix24 webhook (задай BITRIX24_WEBHOOK_URL в .env)
    $b24_url = getenv('BITRIX24_WEBHOOK_URL');
    if ($b24_url) {
        wp_remote_post($b24_url . 'crm.lead.add.json', [
            'body'    => ['fields' => $fields],
            'timeout' => 5,
        ]);
    }

    // Telegram уведомление (задай TG_BOT_TOKEN и TG_CHAT_ID в .env)
    $tg_token = getenv('TG_BOT_TOKEN');
    $tg_chat  = getenv('TG_CHAT_ID');
    if ($tg_token && $tg_chat) {
        $lines = ["🔔 <b>Новая заявка!</b>"];
        foreach ($fields as $k => $v) {
            if (!empty($v)) { $lines[] = "<b>" . esc_html($k) . ":</b> " . esc_html($v); }
        }
        $msg = implode("\\n", $lines);
        $api = "https://api.telegram.org/bot{$tg_token}/sendMessage";
        wp_remote_get(add_query_arg(['chat_id' => $tg_chat, 'text' => $msg, 'parse_mode' => 'HTML'], $api));
    }
}, 10, 3);
"""

_AMOCRM_INSTRUCTIONS = """\
# AmoCRM — Инструкция подключения

## Шаг 1: Получить webhook URL
1. Войди в AmoCRM → Настройки → Интеграции → Webhooks
2. Нажми «Добавить вебхук»
3. URL: `https://your-site.ru/wp-json/lp/v1/lead` (или любой ваш обработчик)
4. Скопируй webhook URL

## Шаг 2: Добавить в .env
```
AMOCRM_WEBHOOK_URL=https://your-company.amocrm.ru/api/v4/...
AMOCRM_API_KEY=ваш_ключ
```

## Шаг 3: Проверить
Отправь тестовую заявку на сайте → проверь в AmoCRM в разделе «Сделки / Лиды»
"""

_BITRIX24_INSTRUCTIONS = """\
# Bitrix24 — Инструкция подключения

## Шаг 1: Создать входящий webhook
1. Войди в Bitrix24 → Разработчикам → Другое → Входящий webhook
2. Выбери права: CRM (crm.lead.add)
3. Скопируй URL вида `https://your.bitrix24.ru/rest/1/xxxxx/`

## Шаг 2: Добавить в .env
```
BITRIX24_WEBHOOK_URL=https://your.bitrix24.ru/rest/1/xxxxx/
```

## Шаг 3: Проверить
Отправь заявку → в Bitrix24 → CRM → Лиды — должна появиться новая запись
"""

_TELEGRAM_INSTRUCTIONS = """\
# Telegram Бот — Инструкция подключения

## Шаг 1: Создать бота
1. Открой @BotFather в Telegram → `/newbot`
2. Придумай имя и username (например `@my_leads_bot`)
3. Скопируй токен вида `123456789:ABCdefGHI...`

## Шаг 2: Получить chat_id
1. Добавь бота в нужную группу (или напиши ему лично)
2. Открой: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Найди `"chat":{"id": ...}` — это и есть chat_id (для группы будет отрицательным)

## Шаг 3: Добавить в .env
```
TG_BOT_TOKEN=123456789:ABCdefGHI...
TG_CHAT_ID=-100123456789
```

## Шаг 4: Проверить
Отправь заявку → должно прийти сообщение боту / в группу
"""


def _parse_integrations(brief_text: str) -> dict:
    crm = ""
    m = re.search(r"CRM\s*[:\s]+(AmoCRM|Bitrix24|нет)", brief_text, re.IGNORECASE)
    if m:
        raw = m.group(1).lower()
        if "amo" in raw:
            crm = "amocrm"
        elif "bitrix" in raw:
            crm = "bitrix24"
    telegram = bool(re.search(r"Telegram.*:\s*да", brief_text, re.IGNORECASE))
    return {"crm": crm, "telegram": telegram}


def main(argv: list) -> int:
    if len(argv) < 2:
        error("Usage: generate-integrations.py <project-dir>")
        return 1
    try:
        start = Path(argv[1])
        fp = start / "08_КОД" / "wp-theme" / "functions.php"
        if not fp.exists():
            raise FileNotFoundError("functions.php not found — run /landing-build first")
        project = start

        brief_text = ""
        brief_path = project / "00_БРИФ" / "brief.md"
        if brief_path.exists():
            brief_text = brief_path.read_text(encoding="utf-8")

        integrations = _parse_integrations(brief_text)
        integ_dir = project / "08_КОД" / "integrations"
        integ_dir.mkdir(parents=True, exist_ok=True)

        current = fp.read_text(encoding="utf-8")
        fluent_placeholder = "// [FLUENT_WEBHOOK] — form webhook (integrations-engineer)"
        if fluent_placeholder in current:
            current = current.replace(fluent_placeholder, _FLUENT_HOOK)
        elif "// [FLUENT_WEBHOOK]" in current:
            current = current.replace("// [FLUENT_WEBHOOK]", _FLUENT_HOOK)
        elif "fluentform/submission_inserted" not in current:
            current += "\n" + _FLUENT_HOOK
        fp.write_text(current, encoding="utf-8")

        if integrations["crm"] == "amocrm":
            (integ_dir / "amocrm-setup.md").write_text(_AMOCRM_INSTRUCTIONS, encoding="utf-8")
        elif integrations["crm"] == "bitrix24":
            (integ_dir / "bitrix24-setup.md").write_text(_BITRIX24_INSTRUCTIONS, encoding="utf-8")

        if integrations["telegram"]:
            (integ_dir / "telegram-setup.md").write_text(_TELEGRAM_INSTRUCTIONS, encoding="utf-8")

        success(f"Integrations → {integ_dir}")
        return 0
    except FileNotFoundError as exc:
        error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
