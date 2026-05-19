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
    is_string($encrypted) && substr_count($encrypted, ':') === 3 && strpos($encrypted, 'v1:') === 0,
    "encrypt returns 'v1:iv:tag:ct' format (got: $encrypted)"
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
    "malformed ciphertext (wrong part count) returns empty string"
);
assert_test(
    decrypt('v2:aa:bb:cc') === '',
    "wrong FORMAT_VERSION returns empty string"
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

// Test 7: tampered ciphertext fails authentication
$enc = encrypt('original');
// Flip a byte in the ct portion
$parts = explode(':', $enc);
$ct_decoded = base64_decode($parts[3], true);
$ct_decoded[0] = chr(ord($ct_decoded[0]) ^ 0x01);
$parts[3] = base64_encode($ct_decoded);
$tampered = implode(':', $parts);
assert_test(
    decrypt($tampered) === '',
    "tampered ciphertext fails GCM auth and returns empty string"
);

// Test 8: IVs are unique across 50 calls
$ivs = [];
for ($i = 0; $i < 50; $i++) {
    $e = encrypt('same-input');
    $ivs[] = explode(':', $e)[1];
}
assert_test(
    count(array_unique($ivs)) === 50,
    "50 encrypt calls produce 50 unique IVs"
);

echo "\n$tests tests, $failures failures\n";
exit($failures > 0 ? 1 : 0);
