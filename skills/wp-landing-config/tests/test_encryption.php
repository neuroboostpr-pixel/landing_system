<?php
require_once __DIR__ . '/fixtures/wp-bootstrap.php';
require_once __DIR__ . '/../mu-plugin/landing-config/includes/encryption.php';

use function LandingConfig\Encryption\encrypt;
use function LandingConfig\Encryption\decrypt;
use function LandingConfig\Encryption\mask;

$failures = 0;
$tests = 0;

function assert_test($condition, $message) {
    global $failures, $tests;
    $tests++;
    if (!$condition) {
        echo "FAIL: $message\n";
        $failures++;
    }
}

// Test 1: encrypt/decrypt round-trip
$plaintext = 'amocrm-token-abc123XYZ';
$encrypted = encrypt($plaintext);
assert_test(
    is_string($encrypted) && strpos($encrypted, ':') !== false,
    "encrypt returns 'iv_b64:ct_b64' format (got: $encrypted)"
);
assert_test(
    decrypt($encrypted) === $plaintext,
    "decrypt(encrypt(\$plaintext)) returns original (got: " . decrypt($encrypted) . ")"
);

// Test 2: same plaintext encrypts to different ciphertext each call (random IV)
$enc1 = encrypt($plaintext);
$enc2 = encrypt($plaintext);
assert_test(
    $enc1 !== $enc2,
    "encrypt produces different ciphertext on repeated calls (random IV)"
);
assert_test(
    decrypt($enc1) === decrypt($enc2),
    "both decrypt to same plaintext"
);

// Test 3: empty string round-trip
assert_test(
    decrypt(encrypt('')) === '',
    "empty string encrypt/decrypt round-trip works"
);

// Test 4: Cyrillic + multiline preserves bytes
$tricky = "Привет\nworld\twith\rspecials!@#";
assert_test(
    decrypt(encrypt($tricky)) === $tricky,
    "Cyrillic + escapes round-trip preserves bytes"
);

// Test 5: malformed ciphertext returns empty string (not error/exception)
assert_test(
    decrypt('not-a-valid:base64-here') === '',
    "malformed ciphertext returns empty string (not exception)"
);
assert_test(
    decrypt('') === '',
    "empty ciphertext returns empty string"
);

// Test 6: mask shows last 4 chars only
assert_test(
    mask('abcdef1234567890') === '••••••••••••7890',
    "mask shows last 4 chars + bullets (got: " . mask('abcdef1234567890') . ")"
);
assert_test(
    mask('abc') === '•••',
    "mask of short string returns all bullets (got: " . mask('abc') . ")"
);

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
