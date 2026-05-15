<?php
require_once __DIR__ . '/../db.php';
$pdo = adbms_connect();
$stmt = $pdo->query("SELECT log_id, user_id, action_type, affected_table, affected_record_id, description, old_value, new_value, changes_json, ip_address, created_at FROM activity_logs ORDER BY created_at DESC LIMIT 10");
$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
echo json_encode($rows, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
