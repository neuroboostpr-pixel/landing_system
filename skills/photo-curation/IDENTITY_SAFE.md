# Identity-safe rules for PR-B Photo Pipeline

## Absolute forbiddens (cannot be overridden)

- NEVER alter the face, age, body proportions, or skin of a real client photo.
- NEVER AI-repaint a person who appears in a client photo.
- NEVER swap a face.
- NEVER apply beauty retouching to client photos.

These rules apply to all agents: `photo-curator`, `photo-classifier`, `photo-matcher`, `photo-preview-board`, and the existing `photo-stylist`.

## AI fallback for portrait slots (testimonial / expert / team)

Default: AI fallback is BLOCKED unless `selections.yaml:ai_approved_by_user == true` for that slot.

The `photo-board.html` UI presents an explicit modal:

> Этот слот требует AI-сгенерированного лица человека. Согласен на использование AI? Это будет видно посетителям сайта как настоящий человек.
>
> [ ] Да, согласен

Without the checkbox: the slot is processed with `strategy: placeholder` (an SVG placeholder, not AI).

## Future PR-B.1 (paralaximus client-photo)

When PR-B.1 lands:
- Subject layer = client cutout PNG, composited byte-for-byte. No AI modification.
- Background / far / near layers = AI-generated (environment around the subject only).
- If AI-generated background implicitly contains a person — regenerate without person.

## Audit

All AI-generated portrait slots have `log_ref` in `selections.yaml` pointing to `.logs/<timestamp>_generate.log` with the full prompt sent to codex. This enables post-hoc review.
