<?php
session_start();

// Set a test value in the session
$_SESSION['test'] = time();
$_SESSION['user'] = ['username' => 'test_admin'];

echo json_encode([
    'session_id' => session_id(),
    'session_status' => session_status(),
    'session_name' => session_name(),
    'session_cookie_params' => session_get_cookie_params(),
    'session_data' => $_SESSION,
], JSON_PRETTY_PRINT);
