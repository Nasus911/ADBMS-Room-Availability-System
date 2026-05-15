<?php
declare(strict_types=1);

// Suppress all warnings and errors to prevent them from interfering with JSON output
error_reporting(0);
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

// Start output buffering to capture any accidental output
ob_start();

require_once __DIR__ . '/db.php';

// Ensure session is started so API handlers can read authenticated user info
if (session_status() !== PHP_SESSION_ACTIVE) {
    @session_start();  // Suppress warnings if headers already sent
}

// Set JSON headers
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');

// Clear any buffered output to ensure clean JSON response
ob_end_clean();

function adbms_respond(array $payload, int $statusCode = 200): void
{
    http_response_code($statusCode);
    echo json_encode($payload, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    exit;
}

try {
    $pdo = adbms_connect();
    $entity = strtolower(trim((string) ($_GET['entity'] ?? 'bootstrap')));
    $action = strtolower(trim((string) ($_GET['action'] ?? 'list')));
    $method = strtoupper($_SERVER['REQUEST_METHOD'] ?? 'GET');

    if ($entity === 'bootstrap') {
        adbms_respond([
            'success' => true,
            'data' => adbms_bootstrap_state($pdo),
            'database' => adbms_database_diagnostics($pdo),
        ]);
    }

    if ($entity === 'auth' && $action === 'login') {
        if ($method !== 'POST') {
            adbms_respond(['success' => false, 'error' => 'Login requires POST.'], 405);
        }

        $input = adbms_json_input();
        $username = trim((string) ($input['username'] ?? ''));
        $password = (string) ($input['password'] ?? '');

        if ($username === '' || $password === '') {
            adbms_respond(['success' => false, 'error' => 'Username and password are required.'], 422);
        }

        $user = adbms_authenticate($pdo, $username, $password);
        // Store authenticated user in session for attribution in activity logs
        if (session_status() === PHP_SESSION_ACTIVE) {
            $_SESSION['user'] = $user;
        }
        adbms_respond([
            'success' => true,
            'user' => $user,
        ]);
    }

    $payload = [];
    if ($method === 'POST') {
        $payload = adbms_json_input();
    }

    $items = [];
    if (isset($payload['items']) && is_array($payload['items'])) {
        $items = $payload['items'];
    } elseif ($method === 'POST' && array_is_list($payload)) {
        $items = $payload;
    } elseif ($method === 'POST' && !empty($payload)) {
        $items = [$payload];
    }

    switch ($entity) {
        case 'users':
            if ($action === 'list' || $method === 'GET') {
                adbms_respond(['success' => true, 'items' => adbms_fetch_users($pdo)]);
            }
            if ($action === 'save') {
                adbms_sync_users($pdo, $items);
                adbms_respond(['success' => true, 'items' => adbms_fetch_users($pdo)]);
            }
            break;

        case 'rooms':
            if ($action === 'list' || $method === 'GET') {
                adbms_respond(['success' => true, 'items' => adbms_fetch_rooms($pdo)]);
            }
            if ($action === 'save') {
                adbms_sync_rooms($pdo, $items);
                adbms_respond(['success' => true, 'items' => adbms_fetch_rooms($pdo)]);
            }
            break;

        case 'checkins':
            if ($action === 'list' || $method === 'GET') {
                adbms_respond(['success' => true, 'items' => adbms_fetch_checkins($pdo)]);
            }
            if ($action === 'save') {
                adbms_sync_checkins($pdo, $items);
                adbms_respond(['success' => true, 'items' => adbms_fetch_checkins($pdo)]);
            }
            break;

        case 'schedules':
            if ($action === 'list' || $method === 'GET') {
                adbms_respond(['success' => true, 'items' => adbms_fetch_schedules($pdo)]);
            }
            if ($action === 'save') {
                adbms_sync_schedules($pdo, $items);
                adbms_respond(['success' => true, 'items' => adbms_fetch_schedules($pdo)]);
            }
            break;

        case 'reservations':
            if ($action === 'list' || $method === 'GET') {
                adbms_respond(['success' => true, 'items' => adbms_fetch_reservations($pdo)]);
            }
            if ($action === 'save') {
                adbms_sync_reservations($pdo, $items);
                adbms_respond(['success' => true, 'items' => adbms_fetch_reservations($pdo)]);
            }
            break;

        case 'notifications':
            if ($action === 'list' || $method === 'GET') {
                adbms_respond(['success' => true, 'items' => adbms_fetch_notifications($pdo)]);
            }
            if ($action === 'save') {
                adbms_sync_notifications($pdo, $items);
                adbms_respond(['success' => true, 'items' => adbms_fetch_notifications($pdo)]);
            }
            break;

        case 'activity_logs':
        case 'history_logs':
            if ($action === 'list' || $method === 'GET') {
                $limit = (int) ($_GET['limit'] ?? 100);
                $offset = (int) ($_GET['offset'] ?? 0);
                $filters = [];
                
                if (!empty($_GET['user_id'])) {
                    $filters['user_id'] = $_GET['user_id'];
                }
                if (!empty($_GET['action_type'])) {
                    $filters['action_type'] = $_GET['action_type'];
                }
                if (!empty($_GET['affected_table'])) {
                    $filters['affected_table'] = $_GET['affected_table'];
                }
                if (!empty($_GET['date_from'])) {
                    $filters['date_from'] = $_GET['date_from'];
                }
                if (!empty($_GET['date_to'])) {
                    $filters['date_to'] = $_GET['date_to'];
                }
                if (!empty($_GET['search'])) {
                    $filters['search'] = $_GET['search'];
                }
                
                $total = adbms_get_activity_logs_count($pdo, $filters);
                $logs = adbms_fetch_activity_logs($pdo, $filters, $limit, $offset);
                
                adbms_respond([
                    'success' => true,
                    'items' => $logs,
                    'total' => $total,
                    'limit' => $limit,
                    'offset' => $offset,
                    'hasMore' => ($offset + $limit) < $total,
                ]);
            }
            break;
    }

    adbms_respond(['success' => false, 'error' => 'Unsupported entity or action.'], 404);
} catch (Throwable $e) {
    adbms_respond([
        'success' => false,
        'error' => $e->getMessage(),
    ], 500);
}
