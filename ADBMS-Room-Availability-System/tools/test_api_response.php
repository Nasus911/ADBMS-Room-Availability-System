<?php
// Test the API directly
$url = 'http://127.0.0.1:8000/api.php?entity=activity_logs&action=list&limit=5&offset=0';
$response = file_get_contents($url);
echo "Response length: " . strlen($response) . "\n";
echo "First 200 chars:\n";
echo substr($response, 0, 200) . "\n";
echo "\n---\n";
echo "Full response:\n";
echo $response;
