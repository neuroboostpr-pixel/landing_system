<?php
namespace LandingConfig\LeadDispatcher;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\Integrations\list_integrations;

const ADAPTER_CLASSES = [
    'email'    => '\\LandingConfig\\Adapters\\EmailAdapter',
    'telegram' => '\\LandingConfig\\Adapters\\TelegramAdapter',
    'whatsapp' => '\\LandingConfig\\Adapters\\WhatsAppAdapter',
    'amocrm'   => '\\LandingConfig\\Adapters\\AmoCRMAdapter',
    'bitrix24' => '\\LandingConfig\\Adapters\\Bitrix24Adapter',
    'hubspot'  => '\\LandingConfig\\Adapters\\HubSpotAdapter',
];

\add_action('landing_config_lead_received', __NAMESPACE__ . '\\dispatch', 10, 2);

function dispatch(int $lead_id, array $data): void {
    $lead = array_merge(['id' => $lead_id], $data);
    $blog_id = \function_exists('get_current_blog_id') ? (int) \get_current_blog_id() : 1;
    $integrations = list_integrations($blog_id);

    foreach ($integrations as $integration) {
        if (empty($integration['enabled'])) {
            continue;
        }
        $adapter_name = (string) ($integration['adapter_name'] ?? '');
        $class = ADAPTER_CLASSES[$adapter_name] ?? '';
        if ($class === '' || !\class_exists($class)) {
            continue;
        }

        try {
            $adapter = new $class();
            $result = $adapter->send($lead);
            \do_action('landing_config_lead_dispatched', $lead_id, $adapter_name, $result);
            if (empty($result['ok'])) {
                \error_log('[landing-config] lead dispatch failed: ' . $adapter_name . ' lead=' . $lead_id . ' error=' . ($result['error'] ?? 'unknown'));
            }
        } catch (\Throwable $e) {
            \do_action('landing_config_lead_dispatched', $lead_id, $adapter_name, [
                'ok' => false,
                'error' => $e->getMessage(),
            ]);
            \error_log('[landing-config] lead dispatch exception: ' . $adapter_name . ' lead=' . $lead_id . ' error=' . $e->getMessage());
        }
    }
}
