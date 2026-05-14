# 03_РЕФЕРЕНСЫ

## Что сюда класть

- `index.yaml` — список URL лендингов-образцов (формат см. ниже)
- `screenshots/` — скриншоты референсов (опц.)

## Формат index.yaml

```yaml
references:
  - url: https://example.com/landing-1
    note: "Похожая ниша, нравится hero"
    status: candidate    # candidate | approved | rejected
  - url: https://example.com/landing-2
    status: candidate
```

## Кто кладёт

Маркетолог через `/landing-start` wizard (опц.) или references-curator автоматически.

## Этап

03_references.
