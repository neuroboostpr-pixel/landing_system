#!/usr/bin/env python3
"""Detect quiz blocks in prototype.yaml and auto-expand into conversion-optimal funnel.

Strategy:
- If prototype has 0 quiz blocks → do nothing
- If prototype has 1 quiz block → replace it with full 9-block Marquiz funnel,
  shift subsequent block positions, preserve user's original quiz headline as the welcome screen
- If prototype has 2-4 quiz blocks → add infrastructure blocks (welcome + loader + discount + lead-form + thankyou)
- If prototype has 5+ quiz blocks → respect user's choice, just add a note

The script is IDEMPOTENT: if blocks already have quiz_role set, do nothing (skip expansion).

Outputs:
- Modified prototype.yaml (saved to <output> via atomic write)
- enrichment-log.md (human-readable Russian explanation of what was added and why)

Usage:
  enrich-quiz-funnel.py --input <prototype.yaml> --output <enriched.yaml> --log <log.md>
"""
import argparse
import os
import sys
from pathlib import Path

import yaml


VALID_QUIZ_ROLES = {
    "welcome", "question", "intermediate", "progress",
    "loader", "discount", "lead-form", "thankyou",
}


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_proto(path: Path) -> dict:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        fail("top-level must be a mapping")
    return data


def atomic_write(path: Path, data: dict) -> None:
    """Write YAML to a .tmp file then rename (atomic on POSIX)."""
    tmp = path.with_suffix(".yaml.tmp")
    tmp.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False))
    os.replace(tmp, path)


def make_funnel_blocks(start_pos: int, original_headline: str) -> list[dict]:
    """Return 9 quiz funnel blocks starting at start_pos."""
    N = start_pos
    return [
        {
            "position": N,
            "type": "quiz",
            "quiz_role": "welcome",
            "headline": original_headline,
            "cta": {"text": "Начать тест", "action": "scroll-to-next"},
        },
        {
            "position": N + 1,
            "type": "quiz",
            "quiz_role": "question",
            "question_number": 1,
            "headline": "Вопрос 1: <placeholder — настройте>",
        },
        {
            "position": N + 2,
            "type": "quiz",
            "quiz_role": "question",
            "question_number": 2,
            "headline": "Вопрос 2: <placeholder — настройте>",
        },
        {
            "position": N + 3,
            "type": "quiz",
            "quiz_role": "intermediate",
            "headline": "Осталось ещё 2 вопроса — почти готово!",
        },
        {
            "position": N + 4,
            "type": "quiz",
            "quiz_role": "question",
            "question_number": 3,
            "headline": "Вопрос 3: <placeholder — настройте>",
        },
        {
            "position": N + 5,
            "type": "quiz",
            "quiz_role": "loader",
            "headline": "Анализируем ваши ответы...",
        },
        {
            "position": N + 6,
            "type": "quiz",
            "quiz_role": "discount",
            "headline": "Вам начислено -15% на первую покупку",
        },
        {
            "position": N + 7,
            "type": "quiz",
            "quiz_role": "lead-form",
            "headline": "Оставьте контакт — пришлём результат",
            "cta": {"text": "Получить результат", "action": "submit-lead"},
        },
        {
            "position": N + 8,
            "type": "quiz",
            "quiz_role": "thankyou",
            "headline": "Спасибо! Свяжемся в Telegram или Max в течение 5 минут",
        },
    ]


def expand_count_1(proto: dict) -> tuple[dict, str]:
    """Replace single quiz block with full 9-block funnel. Returns (updated_proto, log_text)."""
    blocks = proto["blocks"]
    quiz_indices = [i for i, b in enumerate(blocks) if b.get("type") == "quiz"]
    idx = quiz_indices[0]
    source_block = blocks[idx]
    original_headline = source_block.get("headline", "Пройди тест")
    start_pos = source_block["position"]

    # Build funnel (9 blocks)
    funnel = make_funnel_blocks(start_pos, original_headline)
    funnel_count = len(funnel)  # 9
    shift = funnel_count - 1   # 8 — we replace 1 block with 9, so +8 shift

    # Shift all subsequent blocks
    new_blocks: list[dict] = []
    for i, b in enumerate(blocks):
        if i < idx:
            new_blocks.append(b)
        elif i == idx:
            new_blocks.extend(funnel)
        else:
            shifted = dict(b)
            shifted["position"] = b["position"] + shift
            new_blocks.append(shifted)

    proto = dict(proto)
    proto["blocks"] = new_blocks

    log = _build_log(
        quiz_count=1,
        action="full_expand",
        original_headline=original_headline,
        start_pos=start_pos,
        funnel_count=funnel_count,
        shift=shift,
    )
    return proto, log


def expand_count_2_4(proto: dict) -> tuple[dict, str]:
    """User has 2-4 quiz questions. Add infrastructure blocks: welcome + loader + discount + lead-form + thankyou.
    Strategy: insert welcome BEFORE the first quiz, insert loader/discount/lead-form/thankyou AFTER the last quiz.
    """
    blocks = proto["blocks"]
    quiz_indices = [i for i, b in enumerate(blocks) if b.get("type") == "quiz"]
    first_idx = quiz_indices[0]
    last_idx = quiz_indices[-1]

    first_quiz = blocks[first_idx]
    last_quiz = blocks[last_idx]
    original_headline = first_quiz.get("headline", "Пройдите тест")
    welcome_pos = first_quiz["position"]
    after_last_pos = last_quiz["position"]

    # Assign question numbers to existing quiz blocks
    q_num = 1
    for i in quiz_indices:
        if "quiz_role" not in blocks[i]:
            blocks[i] = dict(blocks[i])
            blocks[i]["quiz_role"] = "question"
            blocks[i]["question_number"] = q_num
            q_num += 1

    # We'll insert 1 welcome block before first quiz (+1 shift for all from first_idx on)
    # Then 4 infra blocks after last quiz (additional shift)
    INFRA_BEFORE = 1  # welcome
    INFRA_AFTER = 4   # loader, discount, lead-form, thankyou
    total_added = INFRA_BEFORE + INFRA_AFTER

    new_blocks: list[dict] = []
    for i, b in enumerate(blocks):
        if i < first_idx:
            new_blocks.append(b)
        elif i == first_idx:
            # Insert welcome block
            welcome = {
                "position": welcome_pos,
                "type": "quiz",
                "quiz_role": "welcome",
                "headline": original_headline,
                "cta": {"text": "Начать тест", "action": "scroll-to-next"},
            }
            new_blocks.append(welcome)
            # Shift the first quiz block +1
            shifted = dict(b)
            shifted["position"] = b["position"] + 1
            new_blocks.append(shifted)
        elif i <= last_idx:
            shifted = dict(b)
            shifted["position"] = b["position"] + INFRA_BEFORE
            new_blocks.append(shifted)
        elif i == last_idx + 1:
            # Before inserting next non-quiz blocks, add infra after last quiz
            last_q_pos = last_quiz["position"] + INFRA_BEFORE
            infra_after = [
                {"position": last_q_pos + 1, "type": "quiz", "quiz_role": "loader",
                 "headline": "Анализируем ваши ответы..."},
                {"position": last_q_pos + 2, "type": "quiz", "quiz_role": "discount",
                 "headline": "Вам начислено -15% на первую покупку"},
                {"position": last_q_pos + 3, "type": "quiz", "quiz_role": "lead-form",
                 "headline": "Оставьте контакт — пришлём результат",
                 "cta": {"text": "Получить результат", "action": "submit-lead"}},
                {"position": last_q_pos + 4, "type": "quiz", "quiz_role": "thankyou",
                 "headline": "Спасибо! Свяжемся в Telegram или Max в течение 5 минут"},
            ]
            new_blocks.extend(infra_after)
            shifted = dict(b)
            shifted["position"] = b["position"] + total_added
            new_blocks.append(shifted)
        else:
            shifted = dict(b)
            shifted["position"] = b["position"] + total_added
            new_blocks.append(shifted)

    # Edge case: last quiz is the last block in prototype
    if last_idx == len(blocks) - 1:
        last_q_pos = last_quiz["position"] + INFRA_BEFORE
        infra_after = [
            {"position": last_q_pos + 1, "type": "quiz", "quiz_role": "loader",
             "headline": "Анализируем ваши ответы..."},
            {"position": last_q_pos + 2, "type": "quiz", "quiz_role": "discount",
             "headline": "Вам начислено -15% на первую покупку"},
            {"position": last_q_pos + 3, "type": "quiz", "quiz_role": "lead-form",
             "headline": "Оставьте контакт — пришлём результат",
             "cta": {"text": "Получить результат", "action": "submit-lead"}},
            {"position": last_q_pos + 4, "type": "quiz", "quiz_role": "thankyou",
             "headline": "Спасибо! Свяжемся в Telegram или Max в течение 5 минут"},
        ]
        new_blocks.extend(infra_after)

    proto = dict(proto)
    proto["blocks"] = new_blocks

    log = _build_log(
        quiz_count=len(quiz_indices),
        action="partial_expand",
        original_headline=original_headline,
        start_pos=welcome_pos,
        funnel_count=len(quiz_indices) + total_added,
        shift=total_added,
    )
    return proto, log


def _build_log(
    quiz_count: int,
    action: str,
    original_headline: str,
    start_pos: int,
    funnel_count: int,
    shift: int,
) -> str:
    lines = [
        "# Отчёт квиз-фаннел обогатителя (Marquiz / Tilda / Skillbox best-practices)",
        "",
        f"**Дата обработки:** автоматически при запуске конвейера",
        f"**Найдено квиз-блоков в прототипе:** {quiz_count}",
        f"**Действие:** {'Полное расширение (1 → 9 блоков)' if action == 'full_expand' else 'Частичное расширение (добавлены инфраструктурные блоки)'}",
        "",
        "## Почему это важно",
        "",
        "Квиз — самый высококонверсионный инструмент на RU-рынке (Marquiz, Tilda, Skillbox).",
        "По данным Marquiz, полный квиз-фаннел (welcome → вопросы → лоадер → скидка → лид-форма → спасибо)",
        "даёт **+25–40% к CR** по сравнению с одиночным экраном квиза.",
        "",
        "## Что было добавлено",
        "",
    ]

    if action == "full_expand":
        lines += [
            f"Оригинальный заголовок квиза: **«{original_headline}»**",
            f"Использован как заголовок welcome-экрана (позиция {start_pos}).",
            "",
            "| Позиция | Роль | Назначение |",
            "|---------|------|------------|",
            f"| {start_pos}   | welcome      | Первый экран с CTA «Начать тест» — снижает барьер входа |",
            f"| {start_pos+1} | question (1) | Первый вопрос — вовлечение, самый простой |",
            f"| {start_pos+2} | question (2) | Второй вопрос — углубление |",
            f"| {start_pos+3} | intermediate | Мотиватор «Осталось 2 вопроса» — снижает отток |",
            f"| {start_pos+4} | question (3) | Третий вопрос |",
            f"| {start_pos+5} | loader       | Экран анализа — создаёт ожидание ценности |",
            f"| {start_pos+6} | discount     | Бонус -15% — усиливает желание оставить контакт |",
            f"| {start_pos+7} | lead-form    | Форма контакта (TG/Max/звонок) — конверсионный захват |",
            f"| {start_pos+8} | thankyou     | Подтверждение + обещание связаться за 5 минут |",
            "",
            f"Последующие блоки прототипа сдвинуты на +{shift} позиций.",
        ]
    else:
        lines += [
            f"Пользователь уже написал {quiz_count} вопроса квиза.",
            f"Добавлены инфраструктурные блоки вокруг вопросов:",
            "",
            f"- **welcome** (до первого вопроса) — точка входа с CTA «Начать тест»",
            f"- **loader** (после последнего вопроса) — имитация обработки, создаёт доверие",
            f"- **discount** — начисление скидки, усиливает мотивацию оставить контакт",
            f"- **lead-form** — форма захвата (Telegram / Max / звонок, без WhatsApp)",
            f"- **thankyou** — благодарность и обещание связаться за 5 минут",
            "",
            f"Последующие блоки прототипа сдвинуты на +{shift} позиций.",
        ]

    lines += [
        "",
        "## Рекомендации по настройке",
        "",
        "1. **Вопросы-плейсхолдеры** — замените `<placeholder — настройте>` на реальные вопросы ниши",
        "2. **Тип вопросов** — wireframe предложит варианты: image-choice, step-card, multi-select",
        "3. **Скидка** — измените процент (-15%) под вашу экономику",
        "4. **Контакты** — lead-form: Telegram + Max (ВКонтакте Мессенджер). WhatsApp не использовать.",
        "5. **Время ответа** — «5 минут» в thankyou можно скорректировать под реальный SLA команды",
        "",
        "## Idempotency",
        "",
        "Повторный запуск enricher на уже обогащённом прототипе (quiz_role уже стоят) — без изменений.",
    ]

    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(
        description="Auto-expand quiz blocks into Marquiz-style conversion funnel."
    )
    p.add_argument("--input", required=True, help="Path to input prototype.yaml")
    p.add_argument("--output", required=True, help="Path to output prototype.yaml (can be same as input)")
    p.add_argument("--log", required=True, help="Path to write enrichment-log.md")
    args = p.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    log_path = Path(args.log)

    if not input_path.exists():
        fail(f"Input file not found: {input_path}")

    proto = load_proto(input_path)
    blocks = proto.get("blocks", [])

    quiz_blocks = [b for b in blocks if b.get("type") == "quiz"]
    quiz_count = len(quiz_blocks)

    # IDEMPOTENCY CHECK: if any quiz block already has quiz_role, skip expansion
    already_enriched = any(b.get("quiz_role") for b in quiz_blocks)

    if already_enriched:
        # Write unchanged output
        atomic_write(output_path, proto)
        log_text = (
            "# Отчёт квиз-фаннел обогатителя\n\n"
            "**Действие:** Пропущено — квиз-блоки уже содержат `quiz_role` (повторный запуск).\n\n"
            "Idempotency: enricher не дублирует расширение при повторном запуске.\n"
        )
        log_path.write_text(log_text)
        print(f"OK: already enriched — skipped (idempotent). Output: {output_path}")
        return

    if quiz_count == 0:
        # Nothing to do
        atomic_write(output_path, proto)
        log_text = (
            "# Отчёт квиз-фаннел обогатителя\n\n"
            "**Действие:** Квиз-блоки не найдены — прототип скопирован без изменений.\n"
        )
        log_path.write_text(log_text)
        print(f"OK: no quiz blocks found. Output: {output_path}")
        return

    if quiz_count == 1:
        updated_proto, log_text = expand_count_1(proto)
        atomic_write(output_path, updated_proto)
        log_path.write_text(log_text)
        new_quiz_count = sum(1 for b in updated_proto["blocks"] if b.get("type") == "quiz")
        print(f"OK: 1 quiz block expanded to {new_quiz_count} funnel blocks. Output: {output_path}")
        return

    if 2 <= quiz_count <= 4:
        updated_proto, log_text = expand_count_2_4(proto)
        atomic_write(output_path, updated_proto)
        log_path.write_text(log_text)
        new_quiz_count = sum(1 for b in updated_proto["blocks"] if b.get("type") == "quiz")
        print(f"OK: {quiz_count} quiz blocks enriched with infra → {new_quiz_count} total quiz blocks. Output: {output_path}")
        return

    # 5+ quiz blocks: user designed the funnel already
    atomic_write(output_path, proto)
    log_text = (
        "# Отчёт квиз-фаннел обогатителя\n\n"
        f"**Найдено квиз-блоков:** {quiz_count}\n\n"
        "**Действие:** Пропущено — пользователь уже спроектировал полный квиз-фаннел (5+ блоков).\n\n"
        "Enricher уважает авторское решение. Убедитесь, что у блоков стоит `quiz_role` "
        "для точного матчинга вариантов в wireframe.\n"
    )
    log_path.write_text(log_text)
    print(f"OK: {quiz_count} quiz blocks — user-designed funnel respected. Output: {output_path}")


if __name__ == "__main__":
    main()
