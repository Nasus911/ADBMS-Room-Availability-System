<?php
if (PHP_SAPI !== 'cli') {
    echo "Run this script from the command line.\n";
    exit(1);
}

require __DIR__ . '/../db.php';

$yes = in_array('--yes', $argv, true) || in_array('-y', $argv, true);
$forceReset = adbms_env('FORCE_RESET', '0');
$forceResetEnabled = in_array(strtolower($forceReset), ['1', 'true', 'yes', 'on'], true);

if (!$yes || !$forceResetEnabled) {
    echo "This will drop the schema and remove ALL data.\n";
    echo "To proceed, set FORCE_RESET=1 and run: php tools/reset_db.php --yes\n";
    exit(1);
}

try {
    $config = adbms_config();
    $baseDsn = sprintf('mysql:host=%s;port=%d;charset=utf8mb4', $config['host'], $config['port']);
    $options = [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ];

    $pdo = new PDO($baseDsn, $config['username'], $config['password'], $options);
    adbms_drop_schema($pdo);
    echo "Schema dropped. You may re-run migrations to recreate tables.\n";
} catch (Throwable $e) {
    echo 'ERROR: ' . $e->getMessage() . PHP_EOL;
    exit(1);
}
