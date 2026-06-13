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
