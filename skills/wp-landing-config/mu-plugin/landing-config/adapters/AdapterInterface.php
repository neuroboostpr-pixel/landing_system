<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

interface AdapterInterface {
    /**
     * Adapter machine name (e.g. 'amocrm', 'telegram'). Used as key in storage.
     */
    public static function name(): string;

    /**
     * Human-readable label for admin UI.
     */
    public static function label(): string;

    /**
     * Send a lead to the external service.
     *
     * @param array $lead       Row from wp_<bid>_landing_leads (all columns)
     * @return array  ['ok'=>bool, 'response_code'=>int|null, 'response_body'=>string, 'error'=>string|null]
     */
    public function send(array $lead): array;

    /**
     * Test connection without creating a real lead.
     *
     * @return array  ['ok'=>bool, 'message'=>string]
     */
    public function test_connection(): array;

    /**
     * Field definitions for admin UI.
     * Returns: ['field_key' => ['label'=>..., 'type'=>'text|password|textarea', 'placeholder'=>...], ...]
     * The 'password' type is auto-encrypted on save and masked in display.
     */
    public static function field_defs(): array;

    /**
     * Field schema for cascade-aware admin UI.
     * @return array<string, array{type: string, label: string, encrypt?: bool, required?: bool, placeholder?: string}>
     */
    public static function field_definitions(): array;

    /**
     * Effective settings for the current blog_id, resolved via cascade
     * (network defaults + site overrides). Falls back to legacy wp_option
     * 'landing_integration_<name>' if no CPT row exists.
     */
    public static function settings(): array;
}
