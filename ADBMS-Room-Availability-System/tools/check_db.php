<?php
require __DIR__ . '/../db.php';
try {
    $pdo = adbms_connect();
    echo json_encode(adbms_database_diagnostics($pdo), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . PHP_EOL;
} catch (Throwable $e) {
    echo 'ERROR: ' . $e->getMessage() . PHP_EOL;
    exit(1);
}
