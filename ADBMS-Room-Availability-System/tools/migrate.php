<?php
if (PHP_SAPI !== 'cli') {
    echo "Run this script from the command line.\n";
    exit(1);
}

require __DIR__ . '/../db.php';

try {
    $pdo = adbms_connect();
    adbms_run_migrations($pdo);
    echo "Migrations applied successfully.\n";
} catch (Throwable $e) {
    echo 'ERROR: ' . $e->getMessage() . PHP_EOL;
    exit(1);
}
