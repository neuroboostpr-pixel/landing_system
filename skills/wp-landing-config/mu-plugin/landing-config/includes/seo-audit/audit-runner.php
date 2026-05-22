<?php
namespace LandingConfig\SEOAudit\Runner;

if (!defined('ABSPATH')) { exit; }

const PYTHON_BIN_CANDIDATES = ['/usr/local/bin/python3', '/usr/bin/python3', 'python3', 'python'];
const AUDIT_TIMEOUT_SEC     = 180;

/** Build python CLI command for run-audit.py. Pure for testability. */
function build_python_command(array $opts, string $python_bin, string $script_path): string {
    $cmd = escapeshellcmd($python_bin) . ' ' . escapeshellarg($script_path)
         . ' --json --with-fix-hints';

    if (!empty($opts['hosts_file'])) {
        $cmd .= ' --hosts-file ' . escapeshellarg($opts['hosts_file']);
    } elseif (!empty($opts['urls']) && count($opts['urls']) === 1) {
        $cmd .= ' --url ' . escapeshellarg($opts['urls'][0]);
    }
    if (!empty($opts['out_dir'])) {
        $cmd .= ' --out ' . escapeshellarg($opts['out_dir']);
    }
    return $cmd;
}

/** Detect first available python binary. */
function detect_python_bin(): ?string {
    foreach (PYTHON_BIN_CANDIDATES as $bin) {
        // Match real `python --version` output: "Python 3.x.y" at start of line.
        // shell_exec captures stderr's "not found" too, so a name-only match
        // (e.g. stripos for 'python') would false-positive on the error string itself.
        $out = (string) @shell_exec(escapeshellcmd($bin) . ' --version 2>&1');
        if (preg_match('/^Python\s+\d+\.\d+/m', $out)) {
            return $bin;
        }
    }
    return null;
}

/** Parse run-audit.py stdout into associative array. Returns null on invalid JSON. */
function parse_audit_output(string $stdout): ?array {
    $data = json_decode($stdout, true);
    if (!is_array($data)) return null;
    return $data;
}

/** Cache keys for wp_sitemeta. */
function cache_key(int $blog_id): string {
    return 'landing_seo_audit_' . $blog_id;
}

function aggregate_cache_key(): string {
    return 'landing_seo_audit_aggregate';
}

function timestamp_key(int $blog_id): string {
    return 'landing_seo_audit_' . $blog_id . '_ts';
}

/**
 * Run audit for given URLs. Multisite mode if >1 URL.
 *
 * @param string[] $urls
 * @return array{ok:bool, data:?array, error:?string, stderr:?string}
 */
function run_audit_for_urls(array $urls): array {
    if (function_exists('set_time_limit')) {
        \set_time_limit(AUDIT_TIMEOUT_SEC);
    }
    if (!function_exists('shell_exec')) {
        return ['ok' => false, 'data' => null, 'error' => 'shell_exec disabled in php.ini', 'stderr' => null];
    }
    $python = detect_python_bin();
    if ($python === null) {
        return ['ok' => false, 'data' => null, 'error' => 'python3 not found in PATH', 'stderr' => null];
    }

    // __DIR__ is .../mu-plugins/landing-config/includes/seo-audit
    // dirname(__DIR__, 3) is .../mu-plugins; sibling seo-tech-audit/ holds the Python skill.
    $candidates = [
        dirname(__DIR__, 3) . '/seo-tech-audit/scripts/run-audit.py',
        // Dev fallback: monorepo layout (skills/wp-landing-config + skills/seo-tech-audit)
        dirname(__DIR__, 5) . '/seo-tech-audit/scripts/run-audit.py',
    ];
    $script_path = null;
    foreach ($candidates as $cand) {
        $resolved = realpath($cand);
        if ($resolved) { $script_path = $resolved; break; }
    }
    if ($script_path === null) {
        return ['ok' => false, 'data' => null,
                'error' => 'run-audit.py not found — tried: ' . implode(', ', $candidates),
                'stderr' => null];
    }

    $tmp = sys_get_temp_dir() . '/lp-audit-' . wp_generate_password(8, false);
    @mkdir($tmp, 0755, true);

    $opts = ['urls' => $urls, 'out_dir' => $tmp];
    if (count($urls) > 1) {
        $hosts_file = $tmp . '/hosts.txt';
        file_put_contents($hosts_file, implode("\n", $urls));
        $opts['hosts_file'] = $hosts_file;
    }

    $cmd = build_python_command($opts, $python, $script_path) . ' 2>&1';
    $stdout = shell_exec($cmd);

    if ($stdout === null || $stdout === '') {
        return ['ok' => false, 'data' => null, 'error' => 'shell_exec returned no output',
                'stderr' => 'cmd: ' . $cmd];
    }

    $data = parse_audit_output($stdout);
    if ($data === null) {
        // Try reading audit-report.json directly (CLI also writes to file)
        $json_path = $tmp . '/audit-report.json';
        if (file_exists($json_path)) {
            $data = parse_audit_output(file_get_contents($json_path));
        }
    }

    if ($data === null) {
        return ['ok' => false, 'data' => null,
                'error' => 'failed to parse JSON output',
                'stderr' => substr($stdout, 0, 2000)];
    }

    // Cleanup tmp
    if (is_dir($tmp)) {
        foreach (glob($tmp . '/*') as $f) { @unlink($f); }
        @rmdir($tmp);
    }

    return ['ok' => true, 'data' => $data, 'error' => null, 'stderr' => null];
}
