<?php
namespace LandingConfig\Encryption;

if (!defined('ABSPATH')) { exit; }

const CIPHER = 'aes-256-cbc';

function _key(): string {
    // wp_salt returns a long random string. Derive a 32-byte key via sha256.
    return \hash('sha256', \wp_salt('secure_auth'), true);
}

function encrypt(string $plaintext): string {
    $iv = \openssl_random_pseudo_bytes(\openssl_cipher_iv_length(CIPHER));
    $ciphertext = \openssl_encrypt($plaintext, CIPHER, _key(), \OPENSSL_RAW_DATA, $iv);
    if ($ciphertext === false) {
        return '';
    }
    return \base64_encode($iv) . ':' . \base64_encode($ciphertext);
}

function decrypt(string $encoded): string {
    if ($encoded === '' || \strpos($encoded, ':') === false) {
        return '';
    }
    [$iv_b64, $ct_b64] = \explode(':', $encoded, 2);
    $iv = \base64_decode($iv_b64, true);
    $ct = \base64_decode($ct_b64, true);
    if ($iv === false || $ct === false) {
        return '';
    }
    $plain = \openssl_decrypt($ct, CIPHER, _key(), \OPENSSL_RAW_DATA, $iv);
    return $plain === false ? '' : $plain;
}

function mask(string $secret): string {
    $len = \strlen($secret);
    if ($len <= 4) {
        return \str_repeat('•', $len);
    }
    return \str_repeat('•', $len - 4) . \substr($secret, -4);
}
