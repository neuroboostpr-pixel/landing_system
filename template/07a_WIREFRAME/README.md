# 07a Wireframe

Интерактивный preview с выбором композиций блоков. Артефакты:

- `wireframe.html` — desktop+mobile preview, radio-кнопки для каждого блока
- `candidates.yaml` — 2-3 кандидата на блок (выход `ux-composer`)
- `selections.yaml` — финальный выбор пользователя

## Открыть preview

Двойной клик по `wireframe.html` (radio-кнопки работают on `file://`).
Если iframe-preview не рендерится — запусти helper:

```
bash skills/wireframe-rendering/scripts/serve-preview.sh 07a_WIREFRAME/
```

После выбора — нажми кнопку «Confirm selections» внизу и сохрани файл `selections.yaml`.
