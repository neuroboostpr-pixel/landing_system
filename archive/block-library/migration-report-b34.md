# B34 Фаза 1 — отчёт о миграции таксономии

Всего результатов: 151
Применено: 151
Невалидных (пропущено): 0
Не найдено meta.yaml: 0
Low confidence (требуют проверки): 4

## Распределение по (category/variant)

- content/about: 6
- content/process: 12
- faq: 7
- features: 23
- footer: 12
- forms/booking: 1
- forms/email: 1
- forms/quiz: 11
- header: 11
- hero: 21
- marquee: 1
- pricing/cards: 10
- pricing/comparison: 1
- social-proof/cases: 4
- social-proof/clients: 5
- social-proof/numbers: 11
- social-proof/testimonials: 8
- trust/certificates: 1
- trust/guarantees: 5

## ⚠️ Low confidence — проверить вручную

- **ru-quiz-05-thankyou** → forms/quiz: Блок — финальный экран "Спасибо" после прохождения квиза: галочка ✓, заголовок "Заявка принята", подзаголовок "Свяжемся в TG/Max через 5 минут" и CTA "На главную". Реальных вопросов/вариантов ответа или полей формы в HTML нет — это post-submit confirmation screen, а не сам квиз. В таксономии нет отдельной категории для thank-you/confirmation, поэтому по роли отношу к forms (часть квиз-флоу). Variant quiz выбран как наиболее близкий по назначению (завершение квиза), но это не интерактивный квиз — отсюда confidence low.
- **ru-quiz-11-discount-bonus** → trust/guarantees: Несмотря на папку "quiz" и type "lead-form", в HTML нет ни вопросов с вариантами ответов, ни полей ввода/формы. Это экран-оффер: круглый бейдж скидки "-15%", заголовок "Вы получили персональный подарок", список бонусов (скидка, бесплатный выезд замерщика), CTA-кнопка "Получить подарок" и таймер срочности "Предложение действует 24 часа". По сути это промо/CTA-баннер с лид-магнитом, которого нет среди 11 категорий. forms/quiz не подходит — нет вопросов и полей. Ближайшее по РОЛИ — обещание выгоды/бонуса клиенту, поэтому trust/guarantees. Confidence low, так как блок — конверсионный оффер-баннер, не классическая гарантия.
- **trust-editorial-grid-2-romanmelnikov-tilda-11** → features/—: Блок — заголовок + лид, затем 6 «критериев» (badge + заголовок + текст) в двух колонках, плюс блок из 3 крупных статов внизу. По структуре это перечисление пунктов-преимуществ/критериев (список фич с маркером и описанием), а не сертификаты/лицензии или гарантийные обещания — поэтому старый type "guarantees" (trust/guarantees) не подтверждается содержимым. Это и не отзывы, не логотипы, не таймлайн-процесс, не about-история. Ближе всего по роли — список преимуществ/критериев, то есть features (без variant). Нижний блок со статами (numbers) вторичен и не определяет роль всего блока. Confidence low: блок editorial и пограничный между features и trust/guarantees.
- **trust-playful-stacked-opt-ecowash-ru-4** → social-proof/numbers: 3 крупные цифры-статистики (value/label) + бейджи. Доминируют метрики → social-proof/numbers. Manual (rate-limit retry).
