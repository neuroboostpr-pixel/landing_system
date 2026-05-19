<?php
namespace LandingConfig\Encryption;

if (!defined('ABSPATH')) { exit; }

const CIPHER = 'aes-256-gcm';
const FORMAT_VERSION = 'v1';

/**
 * Derive 32-byte key from wp_salt('secure_auth') via sha256.
 *
 * Stretching (PBKDF2/HKDF) is unnecessary: wp_salt is already high-entropy
 * random from wp-config.php constants. sha256 is used only to fit the
 * 32-byte key length AES-256 requires.
 *
 * NOTE: rotating SECURE_AUTH_KEY/SALT in wp-config invalidates all stored
 * ciphertexts. Re-encrypt migration would key off the FORMAT_VERSION prefix.
 */
function _key(): string {
    return hash('sha256', wp_salt('secure_auth'), true);
}

/**
 * Encrypt $plaintext with AES-256-GCM. Authenticated — tampered ciphertext
 * fails to decrypt rather than silently producing garbage.
 *
 * Returns 'v1:iv_b64:tag_b64:ct_b64' on success, '' on failure.
 *
 * @param string $plaintext UTF-8 text (typically a CRM API token).
 */
function encrypt(string $plaintext): string {
    try {
        $iv = random_bytes(openssl_cipher_iv_length(CIPHER));
    } catch (\Throwable $e) {
        error_log('[landing-config] encrypt: random_bytes failed: ' . $e->getMessage());
        return '';
    }
    $tag = '';
    $ct = openssl_encrypt($plaintext, CIPHER, _key(), OPENSSL_RAW_DATA, $iv, $tag);
    if ($ct === false) {
        error_log('[landing-config] encrypt: openssl_encrypt returned false');
        return '';
    }
    return FORMAT_VERSION . ':' . base64_encode($iv) . ':' . base64_encode($tag) . ':' . base64_encode($ct);
}

/**
 * Decrypt 'v1:iv:tag:ct' produced by encrypt(). Returns '' on any failure
 * (malformed input, bad base64, wrong key, tampered ciphertext).
 *
 * NOTE: returns '' for BOTH "empty input" (intentional no-op) and "decryption
 * failure" — callers can't distinguish. Non-empty failures are logged via
 * error_log so ops can spot key-rotation incidents.
 */
function decrypt(string $encoded): string {
    if ($encoded === '') {
        return '';
    }
    $parts = explode(':', $encoded);
    if (count($parts) !== 4 || $parts[0] !== FORMAT_VERSION) {
        error_log('[landing-config] decrypt: malformed input (expected v1:iv:tag:ct)');
        return '';
    }
    $iv  = base64_decode($parts[1], true);
    $tag = base64_decode($parts[2], true);
    $ct  = base64_decode($parts[3], true);
    if ($iv === false || $tag === false || $ct === false) {
        error_log('[landing-config] decrypt: base64_decode failed');
        return '';
    }
    $plain = openssl_decrypt($ct, CIPHER, _key(), OPENSSL_RAW_DATA, $iv, $tag);
    if ($plain === false) {
        error_log('[landing-config] decrypt: openssl_decrypt returned false (wrong key, tampered ct, or rotated salt)');
        return '';
    }
    return $plain;
}

/**
 * Bullet all but the last 4 characters of a secret for display in admin UI.
 *
 * Assumes ASCII input (API tokens). Uses strlen (bytes) intentionally.
 *
 * @param string $secret ASCII secret.
 * @return string e.g. '••••••••••••7890' for a 16-char input.
 */
function mask(string $secret): string {
    $len = strlen($secret);
    if ($len <= 4) {
        return str_repeat('•', $len);
    }
    return str_repeat('•', $len - 4) . substr($secret, -4);
}
