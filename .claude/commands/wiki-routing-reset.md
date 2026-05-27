# /wiki-routing-reset

Очищает логи работы вики-графа и пересобирает пустой отчёт.

## Что делает

1. Обнуляет `logs/wiki-usage.jsonl` (пустой файл, не удаляет).
2. Пересобирает `wiki/routing-report.md` — получается пустой отчёт без секций.

## Steps

```bash
# 1. Очистить лог
python -c "open('logs/wiki-usage.jsonl', 'w').close()" && echo "logs/wiki-usage.jsonl — очищен"

# 2. Пересобрать пустой отчёт
python -m scripts.wiki.stats --report
```

Сообщи пользователю: «Логи и отчёт вики-графа очищены.»
