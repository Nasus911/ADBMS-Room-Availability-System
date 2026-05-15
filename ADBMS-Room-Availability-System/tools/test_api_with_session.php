<?php
// Simulate browser making a request with session
session_start();
$_SESSION['user'] = ['username' => 'admin', 'role' => 'Admin'];

// Create context with session cookie
$opts = [
    'http' => [
        'header' => "Cookie: PHPSESSID=" . session_id() . "\r\n",
    ],
];
$context = stream_context_create($opts);

$url = 'http://127.0.0.1:8000/api.php?entity=activity_logs&action=list&limit=5&offset=0';
$response = file_get_contents($url, false, $context);

if ($response === false) {
    echo "Error: Failed to fetch API\n";
} else {
    echo "Response length: " . strlen($response) . "\n";
    echo "First 300 chars:\n";
    echo substr($response, 0, 300) . "\n";
}

