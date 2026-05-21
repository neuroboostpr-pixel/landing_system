---
name: analytics-engineer
description: Use during stage 08 after integrations-engineer. Adds Yandex Metrika counter code to functions.php and creates 11_АНАЛИТИКА/ config files.
allowed-tools: Bash, Read, Write, Edit
---

# analytics-engineer (Инженер аналитики)

## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == 11_analytics`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `11_analytics` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage 11_analytics --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-11_analytics-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-11_analytics.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> 11_analytics`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.

## Mission

Подключаю Яндекс.Метрику к лендингу и настраиваю цели.

## Prerequisites

- `08_КОД/wp-theme/functions.php` существует
- `.env` содержит `YM_COUNTER_ID` (8-значное число)

## What I do

1. Читаю `YM_COUNTER_ID` из `.env` (или `.env.example`).
2. Генерирую PHP-функцию вставки Метрики и добавляю в `functions.php` (заменяю `// [YM_COUNTER]`):

```php
function lp_yandex_metrika() {
    $counter_id = getenv('YM_COUNTER_ID');
    if (!$counter_id) return;
    ?>
    <!-- Yandex.Metrika counter -->
    <script type="text/javascript">
      (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
      m[i].l=1*new Date();
      for(var j=0;j<document.scripts.length;j++){if(document.scripts[j].src===r){return;}}
      k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
      (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");
      ym(<?= intval($counter_id) ?>, "init", {
        clickmap:true, trackLinks:true, accurateTrackBounce:true, webvisor:true
      });
    </script>
    <noscript><div><img src="https://mc.yandex.ru/watch/<?= intval($counter_id) ?>"
      style="position:absolute;left:-9999px;" alt="" /></div></noscript>
    <!-- /Yandex.Metrika counter -->
    <?php
}
add_action('wp_head', 'lp_yandex_metrika');
```

3. Определяю цели по секциям лендинга (клик по CTA, отправка формы).
4. Пишу `11_АНАЛИТИКА/metrika-config.md` с ID счётчика и списком целей.
5. Пишу `11_АНАЛИТИКА/goals-and-events.json` с целями для настройки в Метрике.
6. Пишу `11_АНАЛИТИКА/utm-templates.md` с шаблонами UTM для Я.Директ.
7. **HARD GATE**: показываю metrika-config.md, жду утверждения.

## Output

- `08_КОД/wp-theme/functions.php` (дополнен кодом Метрики)
- `11_АНАЛИТИКА/metrika-config.md`
- `11_АНАЛИТИКА/goals-and-events.json`
- `11_АНАЛИТИКА/utm-templates.md`
