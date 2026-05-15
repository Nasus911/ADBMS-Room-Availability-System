<?php
declare(strict_types=1);

function adbms_config(): array
{
    adbms_load_dotenv(__DIR__ . '/.env');

    return [
        'host' => adbms_env('DB_HOST', '127.0.0.1'),
        'port' => (int) adbms_env('DB_PORT', '3306'),
        'database' => adbms_env('DB_DATABASE', 'room_db'),
        'username' => adbms_env('DB_USERNAME', 'root'),
        'password' => adbms_env('DB_PASSWORD', ''),
    ];
}

function adbms_env(string $name, string $default = ''): string
{
    $value = getenv($name);
    if ($value === false) {
        return $default;
    }

    $trimmed = trim((string) $value);
    return $trimmed === '' ? $default : $trimmed;
}

function adbms_load_dotenv(string $path): void
{
    static $loaded = false;

    if ($loaded || !is_file($path) || !is_readable($path)) {
        return;
    }

    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    if ($lines === false) {
        return;
    }

    foreach ($lines as $line) {
        $line = trim($line);
        if ($line === '' || str_starts_with($line, '#') || !str_contains($line, '=')) {
            continue;
        }

        [$key, $value] = array_map('trim', explode('=', $line, 2));
        if ($key === '') {
            continue;
        }

        $value = trim($value, "\"'");
        if (getenv($key) === false) {
            putenv($key . '=' . $value);
            $_ENV[$key] = $value;
            $_SERVER[$key] = $value;
        }
    }

    $loaded = true;
}

function adbms_connect(): PDO
{
    static $pdo = null;

    if ($pdo instanceof PDO) {
        return $pdo;
    }

    $config = adbms_config();
    $baseDsn = sprintf('mysql:host=%s;port=%d;charset=utf8mb4', $config['host'], $config['port']);
    $options = [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ];

    $server = new PDO($baseDsn, $config['username'], $config['password'], $options);
    $server->exec(sprintf(
        'CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci',
        $config['database']
    ));

    $pdo = new PDO($baseDsn . ';dbname=' . $config['database'], $config['username'], $config['password'], $options);

    // Run non-destructive, versioned migrations instead of dropping the database.
    adbms_run_migrations($pdo);
    adbms_ensure_schema($pdo);
    adbms_seed_data($pdo);

    return $pdo;
}

function adbms_ensure_schema(PDO $pdo): void
{
    $pdo->exec(
        "CREATE TABLE IF NOT EXISTS `schema_version` (
            `id` TINYINT UNSIGNED NOT NULL,
            `version` INT UNSIGNED NOT NULL,
            `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    $pdo->exec(
        "CREATE TABLE IF NOT EXISTS `users` (
            `username` VARCHAR(64) NOT NULL,
            `name` VARCHAR(255) NOT NULL,
            `password_hash` VARCHAR(255) NOT NULL,
            `role` ENUM('Admin','Professor','Student') NOT NULL,
            `status` ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
            `last_login` DATETIME DEFAULT NULL,
            `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`username`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    $pdo->exec(
        "CREATE TABLE IF NOT EXISTS `rooms` (
            `room_number` INT NOT NULL,
            `floor_number` TINYINT UNSIGNED NOT NULL,
            `status` ENUM('available','occupied','reserved','maintenance') NOT NULL DEFAULT 'available',
            `occupied_by_username` VARCHAR(64) DEFAULT NULL,
            `status_updated_at` DATETIME DEFAULT NULL,
            `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`room_number`),
            KEY `idx_rooms_occupied_by_username` (`occupied_by_username`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    $pdo->exec(
        "CREATE TABLE IF NOT EXISTS `checkins` (
            `id` VARCHAR(80) NOT NULL,
            `room_number` INT NOT NULL,
            `user_username` VARCHAR(64) NOT NULL,
            `checkin_date` DATE NOT NULL,
            `ts` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `metadata` JSON DEFAULT NULL,
            PRIMARY KEY (`id`),
            KEY `idx_checkins_room_number` (`room_number`),
            KEY `idx_checkins_user_username` (`user_username`),
            CONSTRAINT `fk_checkins_room_number` FOREIGN KEY (`room_number`) REFERENCES `rooms` (`room_number`) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    $pdo->exec(
        "CREATE TABLE IF NOT EXISTS `schedules` (
            `id` VARCHAR(80) NOT NULL,
            `professor_username` VARCHAR(64) NOT NULL,
            `room_number` INT NOT NULL,
            `scheduled_date` DATE NOT NULL,
            `scheduled_hour` TINYINT UNSIGNED NOT NULL,
            `scheduled_minute` TINYINT UNSIGNED NOT NULL,
            `scheduled_period` ENUM('AM','PM') NOT NULL,
            `assigned_by_username` VARCHAR(64) DEFAULT NULL,
            `status` ENUM('Pending','Approved','Rejected','Cancelled') NOT NULL DEFAULT 'Approved',
            `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            KEY `idx_schedules_professor_username` (`professor_username`),
            KEY `idx_schedules_room_number` (`room_number`),
            KEY `idx_schedules_assigned_by_username` (`assigned_by_username`),
            CONSTRAINT `fk_schedules_room_number` FOREIGN KEY (`room_number`) REFERENCES `rooms` (`room_number`) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    $pdo->exec(
        "CREATE TABLE IF NOT EXISTS `reservations` (
            `id` VARCHAR(80) NOT NULL,
            `professor_username` VARCHAR(64) NOT NULL,
            `room_number` INT NOT NULL,
            `reservation_date` DATE NOT NULL,
            `reservation_hour` TINYINT UNSIGNED NOT NULL,
            `reservation_minute` TINYINT UNSIGNED NOT NULL,
            `reservation_period` ENUM('AM','PM') NOT NULL,
            `status` ENUM('Pending','Approved','Rejected') NOT NULL DEFAULT 'Pending',
            `rejection_reason` TEXT DEFAULT NULL,
            `responded_at` DATETIME DEFAULT NULL,
            `responded_by_username` VARCHAR(64) DEFAULT NULL,
            `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            KEY `idx_reservations_professor_username` (`professor_username`),
            KEY `idx_reservations_room_number` (`room_number`),
            KEY `idx_reservations_responded_by_username` (`responded_by_username`),
            CONSTRAINT `fk_reservations_room_number` FOREIGN KEY (`room_number`) REFERENCES `rooms` (`room_number`) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    $pdo->exec(
        "CREATE TABLE IF NOT EXISTS `notifications` (
            `id` VARCHAR(80) NOT NULL,
            `user_username` VARCHAR(64) DEFAULT NULL,
            `title` VARCHAR(255) NOT NULL,
            `message` TEXT NOT NULL,
            `ts` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `is_read` TINYINT(1) NOT NULL DEFAULT 0,
            PRIMARY KEY (`id`),
            KEY `idx_notifications_user_username` (`user_username`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    $pdo->exec('REPLACE INTO schema_version (id, version) VALUES (1, 2)');

    // Ensure backward-compatible addition of assigned_by_username column for schedules
    try {
        $pdo->exec("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS assigned_by_username VARCHAR(64) DEFAULT NULL");
        $pdo->exec("CREATE INDEX IF NOT EXISTS idx_schedules_assigned_by_username ON schedules (assigned_by_username)");
    } catch (Throwable $_) {
        // best-effort: ignore if ALTER/CREATE INDEX not supported on this server
    }
}

function adbms_drop_schema(PDO $pdo): void
{
    $pdo->exec('SET FOREIGN_KEY_CHECKS = 0');
    $pdo->exec('DROP VIEW IF EXISTS `room_utilization`');
    $pdo->exec('DROP TABLE IF EXISTS `notifications`');
    $pdo->exec('DROP TABLE IF EXISTS `reservations`');
    $pdo->exec('DROP TABLE IF EXISTS `schedules`');
    $pdo->exec('DROP TABLE IF EXISTS `checkins`');
    $pdo->exec('DROP TABLE IF EXISTS `rooms`');
    $pdo->exec('DROP TABLE IF EXISTS `users`');
    $pdo->exec('SET FOREIGN_KEY_CHECKS = 1');
}

function adbms_ensure_migrations_table(PDO $pdo): void
{
    $pdo->exec(
        "CREATE TABLE IF NOT EXISTS `migrations` (
            `id` VARCHAR(255) NOT NULL,
            `applied_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `checksum` CHAR(64) DEFAULT NULL,
            `file_size` BIGINT DEFAULT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    // Attempt to add columns if older migrations table exists without them
    try {
        $pdo->exec("ALTER TABLE migrations ADD COLUMN IF NOT EXISTS checksum CHAR(64) DEFAULT NULL");
        $pdo->exec("ALTER TABLE migrations ADD COLUMN IF NOT EXISTS file_size BIGINT DEFAULT NULL");
    } catch (Throwable $_) {
        // Ignore; ALTER may not support IF NOT EXISTS on older MySQL
    }
}

function adbms_get_migration_files(): array
{
    $dir = __DIR__ . '/migrations';
    if (!is_dir($dir)) {
        return [];
    }

    $files = glob($dir . '/*.sql');
    if ($files === false) {
        return [];
    }

    sort($files, SORT_STRING);
    return array_map(function ($path) {
        return basename($path);
    }, $files);
}

function adbms_get_applied_migrations(PDO $pdo): array
{
    try {
        $stmt = $pdo->query('SELECT id, checksum, file_size FROM migrations ORDER BY applied_at');
        $rows = $stmt ? $stmt->fetchAll(PDO::FETCH_ASSOC) : [];
        $out = [];
        foreach ($rows as $r) {
            $out[$r['id']] = [
                'checksum' => $r['checksum'] ?? null,
                'file_size' => isset($r['file_size']) ? (int) $r['file_size'] : null,
            ];
        }
        return $out;
    } catch (Throwable $e) {
        return [];
    }
}

function adbms_apply_migration(PDO $pdo, string $migrationFile): void
{
    $path = __DIR__ . '/migrations/' . $migrationFile;
    if (!is_file($path) || !is_readable($path)) {
        throw new RuntimeException('Migration file not found: ' . $migrationFile);
    }

    $sql = file_get_contents($path);
    if ($sql === false) {
        throw new RuntimeException('Unable to read migration file: ' . $migrationFile);
    }
    // Compute checksum and file size
    $checksum = hash('sha256', $sql);
    $fileSize = filesize($path);

    // Execute full SQL file. PDO->exec will run multiple statements where supported.
    $pdo->exec($sql);

    $stmt = $pdo->prepare('REPLACE INTO migrations (id, checksum, file_size) VALUES (:id, :checksum, :file_size)');
    $stmt->execute([':id' => $migrationFile, ':checksum' => $checksum, ':file_size' => $fileSize]);
}

function adbms_run_migrations(PDO $pdo): void
{
    adbms_ensure_migrations_table($pdo);

    // Auto-migrate is disabled by default for web requests. Set ADBMS_AUTO_MIGRATE=1 to opt in.
    $auto = adbms_env('ADBMS_AUTO_MIGRATE', '0');
    if (PHP_SAPI !== 'cli' && ($auto === '' || $auto === '0')) {
        return;
    }

    $all = adbms_get_migration_files();
    $applied = adbms_get_applied_migrations($pdo);

    // Acquire advisory lock to avoid concurrent migrations
    $lockName = 'adbms_migrations_lock';
    $gotLock = false;
    try {
        $stmt = $pdo->query("SELECT GET_LOCK('{$lockName}', 10)");
        $gotLock = (bool) ($stmt ? $stmt->fetchColumn() : false);
        if (!$gotLock) {
            throw new RuntimeException('Could not acquire migration lock');
        }

        foreach ($all as $file) {
            if (isset($applied[$file])) {
                // verify checksum to detect tampering
                $path = __DIR__ . '/migrations/' . $file;
                $sql = file_get_contents($path);
                $checksum = $sql === false ? null : hash('sha256', $sql);
                $size = is_file($path) ? filesize($path) : null;
                if ($checksum !== null && $applied[$file]['checksum'] !== null && $checksum !== $applied[$file]['checksum']) {
                    throw new RuntimeException('Migration file changed after applied: ' . $file);
                }
                continue;
            }

            // apply migration (no transaction for DDL)
            adbms_apply_migration($pdo, $file);
        }
    } finally {
        if ($gotLock) {
            try {
                $pdo->query("SELECT RELEASE_LOCK('{$lockName}')");
            } catch (Throwable $_) {
            }
        }
    }
}

function adbms_seed_data(PDO $pdo): void
{
    $userCount = (int) $pdo->query('SELECT COUNT(*) AS c FROM users')->fetchColumn();
    if ($userCount === 0) {
        $users = [
            ['username' => 'admin', 'name' => 'System Admin', 'password' => 'admin123', 'role' => 'Admin', 'status' => 'Active'],
            ['username' => 'psantos', 'name' => 'Recto Santos', 'password' => 'prof123', 'role' => 'Professor', 'status' => 'Active'],
            ['username' => 'jdc', 'name' => 'Juan Dela Cruz', 'password' => 'student123', 'role' => 'Student', 'status' => 'Active'],
        ];

        $stmt = $pdo->prepare(
            'INSERT INTO users (username, name, password_hash, role, status, last_login) VALUES (:username, :name, :password_hash, :role, :status, NULL)'
        );

        foreach ($users as $user) {
            $stmt->execute([
                ':username' => $user['username'],
                ':name' => $user['name'],
                ':password_hash' => password_hash($user['password'], PASSWORD_DEFAULT),
                ':role' => $user['role'],
                ':status' => $user['status'],
            ]);
        }
    }

    $roomCount = (int) $pdo->query('SELECT COUNT(*) AS c FROM rooms')->fetchColumn();
    if ($roomCount === 0) {
        $stmt = $pdo->prepare(
            'INSERT INTO rooms (room_number, floor_number, status, occupied_by_username, status_updated_at) VALUES (:room_number, :floor_number, :status, :occupied_by_username, :status_updated_at)'
        );

        for ($floor = 1; $floor <= 5; $floor++) {
            for ($unit = 1; $unit <= 9; $unit++) {
                $roomNumber = $floor * 100 + $unit;
                $stmt->execute([
                    ':room_number' => $roomNumber,
                    ':floor_number' => $floor,
                    ':status' => $roomNumber === 407 ? 'occupied' : 'available',
                    ':occupied_by_username' => $roomNumber === 407 ? 'psantos' : null,
                    ':status_updated_at' => $roomNumber === 407 ? date('Y-m-d H:i:s') : null,
                ]);
            }
        }
    }
}

function adbms_bootstrap_state(PDO $pdo): array
{
    return [
        'users' => adbms_fetch_users($pdo),
        'rooms' => adbms_fetch_rooms($pdo),
        'checkins' => adbms_fetch_checkins($pdo),
        'schedules' => adbms_fetch_schedules($pdo),
        'reservations' => adbms_fetch_reservations($pdo),
        'notifications' => adbms_fetch_notifications($pdo),
    ];
}

function adbms_database_diagnostics(PDO $pdo): array
{
    $databaseName = (string) ($pdo->query('SELECT DATABASE()')->fetchColumn() ?: '');
    $tables = [];

    if ($databaseName !== '') {
        $stmt = $pdo->prepare(
            'SELECT table_name FROM information_schema.tables WHERE table_schema = :schema ORDER BY table_name'
        );
        $stmt->execute([':schema' => $databaseName]);
        $tables = $stmt->fetchAll(PDO::FETCH_COLUMN) ?: [];
    }

    $schemaVersion = null;
    try {
        $schemaVersion = (int) ($pdo->query('SELECT version FROM schema_version WHERE id = 1')->fetchColumn() ?: 0);
    } catch (Throwable $e) {
        $schemaVersion = null;
    }

    $requiredTables = ['schema_version', 'users', 'rooms', 'checkins', 'schedules', 'reservations', 'notifications'];
    $missingTables = array_values(array_diff($requiredTables, $tables));

    return [
        'database' => $databaseName,
        'tableCount' => count($tables),
        'tables' => $tables,
        'missingTables' => $missingTables,
        'hasRequiredTables' => count($missingTables) === 0,
        'schemaVersion' => $schemaVersion,
    ];
}

function adbms_fetch_users(PDO $pdo): array
{
    $stmt = $pdo->query(
        "SELECT
            username,
            name,
            role,
            status,
            CASE WHEN last_login IS NULL THEN NULL ELSE DATE_FORMAT(last_login, '%Y-%m-%dT%H:%i:%s') END AS lastLogin
        FROM users
        ORDER BY FIELD(role, 'Admin', 'Professor', 'Student'), name, username"
    );

    return $stmt->fetchAll();
}

function adbms_fetch_rooms(PDO $pdo): array
{
    $stmt = $pdo->query(
        "SELECT
            room_number AS room,
            occupied_by_username AS occupiedBy,
            status,
            CASE WHEN status_updated_at IS NULL THEN NULL ELSE DATE_FORMAT(status_updated_at, '%Y-%m-%dT%H:%i:%s') END AS statusUpdatedAt
        FROM rooms
        ORDER BY room_number"
    );

    return $stmt->fetchAll();
}

function adbms_fetch_checkins(PDO $pdo): array
{
    $stmt = $pdo->query(
        "SELECT
            id,
            room_number AS room,
            user_username AS user,
            DATE_FORMAT(checkin_date, '%Y-%m-%d') AS date,
            DATE_FORMAT(ts, '%Y-%m-%dT%H:%i:%s') AS ts,
            metadata
        FROM checkins
        ORDER BY ts ASC, id ASC"
    );

    $rows = $stmt->fetchAll();
    foreach ($rows as &$row) {
        if (array_key_exists('metadata', $row) && is_string($row['metadata']) && $row['metadata'] !== '') {
            $decoded = json_decode($row['metadata'], true);
            $row['metadata'] = json_last_error() === JSON_ERROR_NONE ? $decoded : $row['metadata'];
        }
    }

    return $rows;
}

function adbms_fetch_schedules(PDO $pdo): array
{
    $stmt = $pdo->query(
        "SELECT
            id,
            professor_username AS professorUsername,
            room_number AS roomNumber,
            DATE_FORMAT(scheduled_date, '%Y-%m-%d') AS date,
            scheduled_hour AS hour,
            scheduled_minute AS minute,
            scheduled_period AS amPm,
            status,
            assigned_by_username AS assignedByUsername,
            DATE_FORMAT(created_at, '%Y-%m-%dT%H:%i:%s') AS createdAt
        FROM schedules
        ORDER BY scheduled_date ASC, scheduled_hour ASC, scheduled_minute ASC, id ASC"
    );

    return $stmt->fetchAll();
}

function adbms_fetch_reservations(PDO $pdo): array
{
    $stmt = $pdo->query(
        "SELECT
            id,
            professor_username AS professorUsername,
            room_number AS roomNumber,
            DATE_FORMAT(reservation_date, '%Y-%m-%d') AS date,
            reservation_hour AS hour,
            reservation_minute AS minute,
            reservation_period AS amPm,
            status,
            rejection_reason AS rejectionReason,
            CASE WHEN responded_at IS NULL THEN NULL ELSE DATE_FORMAT(responded_at, '%Y-%m-%dT%H:%i:%s') END AS respondedAt,
            CASE WHEN created_at IS NULL THEN NULL ELSE DATE_FORMAT(created_at, '%Y-%m-%dT%H:%i:%s') END AS createdAt
        FROM reservations
        ORDER BY created_at DESC, id DESC"
    );

    return $stmt->fetchAll();
}

function adbms_fetch_notifications(PDO $pdo): array
{
    $stmt = $pdo->query(
        "SELECT
            id,
            user_username AS user,
            title,
            message AS msg,
            DATE_FORMAT(ts, '%Y-%m-%dT%H:%i:%s') AS ts,
            is_read AS `read`
        FROM notifications
        ORDER BY ts DESC, id DESC"
    );

    return $stmt->fetchAll();
}

function adbms_json_input(): array
{
    $raw = file_get_contents('php://input');
    if ($raw === false || trim($raw) === '') {
        return [];
    }

    $decoded = json_decode($raw, true);
    if (!is_array($decoded)) {
        throw new RuntimeException('Request body must be valid JSON.');
    }

    return $decoded;
}

function adbms_normalize_string($value): ?string
{
    if ($value === null) {
        return null;
    }

    $trimmed = trim((string) $value);
    if ($trimmed === '' || $trimmed === '-') {
        return null;
    }

    return $trimmed;
}

function adbms_normalize_datetime($value): ?string
{
    $normalized = adbms_normalize_string($value);
    if ($normalized === null) {
        return null;
    }

    // Accept numeric timestamps (milliseconds or seconds) sent from JS clients
    if (is_numeric($normalized)) {
        $n = (int) $normalized;
        // If looks like milliseconds (greater than year 3000 in seconds), convert
        if ($n > 10000000000) {
            $n = (int) floor($n / 1000);
        }
        return date('Y-m-d H:i:s', $n);
    }

    $timestamp = strtotime($normalized);
    if ($timestamp === false) {
        return $normalized;
    }

    return date('Y-m-d H:i:s', $timestamp);
}

function adbms_normalize_date($value): ?string
{
    $normalized = adbms_normalize_string($value);
    if ($normalized === null) {
        return null;
    }

    // Accept numeric timestamps (milliseconds or seconds)
    if (is_numeric($normalized)) {
        $n = (int) $normalized;
        if ($n > 10000000000) {
            $n = (int) floor($n / 1000);
        }
        return date('Y-m-d', $n);
    }

    $timestamp = strtotime($normalized);
    if ($timestamp === false) {
        return $normalized;
    }

    return date('Y-m-d', $timestamp);
}

function adbms_unique_id(string $prefix): string
{
    try {
        return $prefix . '_' . bin2hex(random_bytes(8)) . '_' . sprintf('%04x', random_int(0, 0xffff));
    } catch (Throwable $e) {
        return $prefix . '_' . uniqid('', true);
    }
}

function adbms_verify_password(string $plainTextPassword, string $storedHash): bool
{
    if ($storedHash === '') {
        return false;
    }

    if (preg_match('/^\$(2y|argon2id|argon2i)\$/', $storedHash) === 1) {
        return password_verify($plainTextPassword, $storedHash);
    }

    if (preg_match('/^[a-f0-9]{64}$/i', $storedHash) === 1) {
        return hash_equals(strtolower($storedHash), hash('sha256', $plainTextPassword));
    }

    return hash_equals($storedHash, $plainTextPassword);
}

function adbms_delete_missing(PDO $pdo, string $table, string $column, array $keepKeys): void
{
    $keepKeys = array_values(array_unique(array_filter($keepKeys, static function ($value) {
        return $value !== null && $value !== '';
    })));

    if (count($keepKeys) === 0) {
        $pdo->exec(sprintf('DELETE FROM `%s`', $table));
        return;
    }

    $placeholders = implode(',', array_fill(0, count($keepKeys), '?'));
    $stmt = $pdo->prepare(sprintf('DELETE FROM `%s` WHERE `%s` NOT IN (%s)', $table, $column, $placeholders));
    $stmt->execute($keepKeys);
}

function adbms_sync_users(PDO $pdo, array $items): void
{
    $existingHashes = [];
    foreach ($pdo->query('SELECT username, password_hash FROM users') as $row) {
        $existingHashes[$row['username']] = $row['password_hash'];
    }

    $pdo->beginTransaction();
    try {
        $keep = [];
        $stmt = $pdo->prepare(
            'INSERT INTO users (username, name, password_hash, role, status, last_login) VALUES (:username, :name, :password_hash, :role, :status, :last_login) ON DUPLICATE KEY UPDATE name = VALUES(name), password_hash = VALUES(password_hash), role = VALUES(role), status = VALUES(status), last_login = VALUES(last_login)'
        );

        foreach ($items as $item) {
            if (!is_array($item)) {
                continue;
            }

            $username = adbms_normalize_string($item['username'] ?? null);
            $name = adbms_normalize_string($item['name'] ?? null);
            $role = adbms_normalize_string($item['role'] ?? null);
            $status = adbms_normalize_string($item['status'] ?? 'Active') ?? 'Active';
            $lastLogin = adbms_normalize_datetime($item['lastLogin'] ?? $item['last_login'] ?? null);
            $password = adbms_normalize_string($item['password'] ?? null);

            if ($username === null || $name === null || $role === null) {
                throw new RuntimeException('Each user requires username, name, and role.');
            }

            if (!in_array($role, ['Admin', 'Professor', 'Student'], true)) {
                throw new RuntimeException('Unsupported user role for ' . $username . '.');
            }

            if (!in_array($status, ['Active', 'Inactive'], true)) {
                throw new RuntimeException('Unsupported user status for ' . $username . '.');
            }

            $passwordHash = $password !== null
                ? password_hash($password, PASSWORD_DEFAULT)
                : ($existingHashes[$username] ?? null);

            if ($passwordHash === null || $passwordHash === '') {
                throw new RuntimeException('A password is required when creating user ' . $username . '.');
            }

            $stmt->execute([
                ':username' => $username,
                ':name' => $name,
                ':password_hash' => $passwordHash,
                ':role' => $role,
                ':status' => $status,
                ':last_login' => $lastLogin,
            ]);

            $keep[] = $username;
        }

        adbms_delete_missing($pdo, 'users', 'username', $keep);
        $pdo->commit();
    } catch (Throwable $e) {
        if ($pdo->inTransaction()) {
            $pdo->rollBack();
        }
        throw $e;
    }
}

function adbms_sync_rooms(PDO $pdo, array $items): void
{
    $pdo->beginTransaction();
    try {
        $keep = [];
        $stmt = $pdo->prepare(
            'INSERT INTO rooms (room_number, floor_number, status, occupied_by_username, status_updated_at) VALUES (:room_number, :floor_number, :status, :occupied_by_username, :status_updated_at) ON DUPLICATE KEY UPDATE floor_number = VALUES(floor_number), status = VALUES(status), occupied_by_username = VALUES(occupied_by_username), status_updated_at = VALUES(status_updated_at)'
        );

        foreach ($items as $item) {
            if (!is_array($item)) {
                continue;
            }

            $roomNumber = (int) ($item['room'] ?? $item['roomNumber'] ?? 0);
            if ($roomNumber <= 0) {
                throw new RuntimeException('Each room requires a valid room number.');
            }

            $floorNumber = (int) floor($roomNumber / 100);
            $status = adbms_normalize_string($item['status'] ?? 'available') ?? 'available';
            if (!in_array($status, ['available', 'occupied', 'reserved', 'maintenance'], true)) {
                throw new RuntimeException('Unsupported room status for room ' . $roomNumber . '.');
            }

            $occupiedBy = adbms_normalize_string($item['occupiedBy'] ?? $item['occupied_by_username'] ?? null);
            $statusUpdatedAt = adbms_normalize_datetime($item['statusUpdatedAt'] ?? $item['status_updated_at'] ?? null) ?? date('Y-m-d H:i:s');

            $stmt->execute([
                ':room_number' => $roomNumber,
                ':floor_number' => $floorNumber,
                ':status' => $status,
                ':occupied_by_username' => $occupiedBy,
                ':status_updated_at' => $statusUpdatedAt,
            ]);

            $keep[] = $roomNumber;
        }

        adbms_delete_missing($pdo, 'rooms', 'room_number', $keep);
        $pdo->commit();
    } catch (Throwable $e) {
        if ($pdo->inTransaction()) {
            $pdo->rollBack();
        }
        throw $e;
    }
}

function adbms_sync_checkins(PDO $pdo, array $items): void
{
    $pdo->beginTransaction();
    try {
        $keep = [];
        $stmt = $pdo->prepare(
            'INSERT INTO checkins (id, room_number, user_username, checkin_date, ts, metadata) VALUES (:id, :room_number, :user_username, :checkin_date, :ts, :metadata) ON DUPLICATE KEY UPDATE room_number = VALUES(room_number), user_username = VALUES(user_username), checkin_date = VALUES(checkin_date), ts = VALUES(ts), metadata = VALUES(metadata)'
        );

        foreach ($items as $item) {
            if (!is_array($item)) {
                continue;
            }

            $roomNumber = (int) ($item['room'] ?? $item['roomNumber'] ?? 0);
            $userUsername = adbms_normalize_string($item['user'] ?? $item['userUsername'] ?? null);
            $checkinDate = adbms_normalize_date($item['date'] ?? $item['checkin_date'] ?? null);
            $ts = adbms_normalize_datetime($item['ts'] ?? null) ?? date('Y-m-d H:i:s');
            $id = adbms_normalize_string($item['id'] ?? null);
            $metadata = $item['metadata'] ?? null;

            if ($roomNumber <= 0 || $userUsername === null || $checkinDate === null) {
                throw new RuntimeException('Each check-in requires a room, user, and date.');
            }

            if ($id === null) {
                $id = adbms_unique_id('chk');
            }

            $metadataJson = $metadata === null || $metadata === '' ? null : json_encode($metadata, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);

            $stmt->execute([
                ':id' => $id,
                ':room_number' => $roomNumber,
                ':user_username' => $userUsername,
                ':checkin_date' => $checkinDate,
                ':ts' => $ts,
                ':metadata' => $metadataJson,
            ]);

            $keep[] = $id;
        }

        adbms_delete_missing($pdo, 'checkins', 'id', $keep);
        $pdo->commit();
    } catch (Throwable $e) {
        if ($pdo->inTransaction()) {
            $pdo->rollBack();
        }
        throw $e;
    }
}

function adbms_sync_schedules(PDO $pdo, array $items): void
{
    $pdo->beginTransaction();
    try {
        $keep = [];
            $stmt = $pdo->prepare(
            'INSERT INTO schedules (id, professor_username, room_number, scheduled_date, scheduled_hour, scheduled_minute, scheduled_period, assigned_by_username, status, created_at) VALUES (:id, :professor_username, :room_number, :scheduled_date, :scheduled_hour, :scheduled_minute, :scheduled_period, :assigned_by_username, :status, :created_at) ON DUPLICATE KEY UPDATE professor_username = VALUES(professor_username), room_number = VALUES(room_number), scheduled_date = VALUES(scheduled_date), scheduled_hour = VALUES(scheduled_hour), scheduled_minute = VALUES(scheduled_minute), scheduled_period = VALUES(scheduled_period), assigned_by_username = VALUES(assigned_by_username), status = VALUES(status), created_at = VALUES(created_at)'
        );

        foreach ($items as $item) {
            if (!is_array($item)) {
                continue;
            }

            $id = adbms_normalize_string($item['id'] ?? null) ?? adbms_unique_id('sched');
            $professorUsername = adbms_normalize_string($item['professorUsername'] ?? $item['professor_username'] ?? null);
            $roomNumber = (int) ($item['roomNumber'] ?? $item['room'] ?? 0);
            $scheduledDate = adbms_normalize_date($item['date'] ?? null);
            $scheduledHour = (int) ($item['hour'] ?? 0);
            $scheduledMinute = (int) ($item['minute'] ?? 0);
            $scheduledPeriod = strtoupper(adbms_normalize_string($item['amPm'] ?? $item['scheduled_period'] ?? null) ?? '');
            $status = adbms_normalize_string($item['status'] ?? 'Approved') ?? 'Approved';
            $createdAt = adbms_normalize_datetime($item['createdAt'] ?? $item['created_at'] ?? null) ?? date('Y-m-d H:i:s');
            $assignedBy = adbms_normalize_string($item['assignedByUsername'] ?? $item['assigned_by_username'] ?? null);

            if ($professorUsername === null || $roomNumber <= 0 || $scheduledDate === null || $scheduledHour < 1 || $scheduledHour > 12) {
                throw new RuntimeException('Each schedule requires a professor, room, date, and hour.');
            }

            if (!in_array($scheduledPeriod, ['AM', 'PM'], true)) {
                throw new RuntimeException('Each schedule requires an AM or PM value.');
            }

            if ($scheduledMinute < 0 || $scheduledMinute > 55 || ($scheduledMinute % 5 !== 0)) {
                throw new RuntimeException('Schedule minutes must be in 5-minute intervals.');
            }

            if (!in_array($status, ['Pending', 'Approved', 'Rejected', 'Cancelled'], true)) {
                throw new RuntimeException('Unsupported schedule status.');
            }

            $stmt->execute([
                ':id' => $id,
                ':professor_username' => $professorUsername,
                ':room_number' => $roomNumber,
                ':scheduled_date' => $scheduledDate,
                ':scheduled_hour' => $scheduledHour,
                ':scheduled_minute' => $scheduledMinute,
                ':scheduled_period' => $scheduledPeriod,
                ':assigned_by_username' => $assignedBy,
                ':status' => $status,
                ':created_at' => $createdAt,
            ]);

            $keep[] = $id;
        }

        adbms_delete_missing($pdo, 'schedules', 'id', $keep);
        $pdo->commit();
    } catch (Throwable $e) {
        if ($pdo->inTransaction()) {
            $pdo->rollBack();
        }
        throw $e;
    }
}

function adbms_sync_reservations(PDO $pdo, array $items): void
{
    $pdo->beginTransaction();
    try {
        $keep = [];
        $stmt = $pdo->prepare(
            'INSERT INTO reservations (id, professor_username, room_number, reservation_date, reservation_hour, reservation_minute, reservation_period, status, rejection_reason, responded_at, responded_by_username, created_at) VALUES (:id, :professor_username, :room_number, :reservation_date, :reservation_hour, :reservation_minute, :reservation_period, :status, :rejection_reason, :responded_at, :responded_by_username, :created_at) ON DUPLICATE KEY UPDATE professor_username = VALUES(professor_username), room_number = VALUES(room_number), reservation_date = VALUES(reservation_date), reservation_hour = VALUES(reservation_hour), reservation_minute = VALUES(reservation_minute), reservation_period = VALUES(reservation_period), status = VALUES(status), rejection_reason = VALUES(rejection_reason), responded_at = VALUES(responded_at), responded_by_username = VALUES(responded_by_username), created_at = VALUES(created_at)'
        );

        foreach ($items as $item) {
            if (!is_array($item)) {
                continue;
            }

            $id = adbms_normalize_string($item['id'] ?? null) ?? adbms_unique_id('res');
            $professorUsername = adbms_normalize_string($item['professorUsername'] ?? $item['professor_username'] ?? null);
            $roomNumber = (int) ($item['roomNumber'] ?? $item['room'] ?? 0);
            $reservationDate = adbms_normalize_date($item['date'] ?? $item['reservation_date'] ?? null);
            $reservationHour = (int) ($item['hour'] ?? $item['reservation_hour'] ?? 0);
            $reservationMinute = (int) ($item['minute'] ?? $item['reservation_minute'] ?? 0);
            $reservationPeriod = strtoupper(adbms_normalize_string($item['amPm'] ?? $item['reservation_period'] ?? null) ?? '');
            $status = adbms_normalize_string($item['status'] ?? 'Pending') ?? 'Pending';
            $rejectionReason = adbms_normalize_string($item['rejectionReason'] ?? $item['rejection_reason'] ?? null);
            $respondedAt = adbms_normalize_datetime($item['respondedAt'] ?? $item['responded_at'] ?? null);
            $respondedBy = adbms_normalize_string($item['respondedByUsername'] ?? $item['responded_by_username'] ?? null);
            $createdAt = adbms_normalize_datetime($item['createdAt'] ?? $item['created_at'] ?? null) ?? date('Y-m-d H:i:s');

            if ($professorUsername === null || $roomNumber <= 0 || $reservationDate === null || $reservationHour < 1 || $reservationHour > 12) {
                throw new RuntimeException('Each reservation requires a professor, room, date, and hour.');
            }

            if (!in_array($reservationPeriod, ['AM', 'PM'], true)) {
                throw new RuntimeException('Each reservation requires an AM or PM value.');
            }

            if ($reservationMinute < 0 || $reservationMinute > 55 || ($reservationMinute % 5 !== 0)) {
                throw new RuntimeException('Reservation minutes must be in 5-minute intervals.');
            }

            if (!in_array($status, ['Pending', 'Approved', 'Rejected'], true)) {
                throw new RuntimeException('Unsupported reservation status.');
            }

            $stmt->execute([
                ':id' => $id,
                ':professor_username' => $professorUsername,
                ':room_number' => $roomNumber,
                ':reservation_date' => $reservationDate,
                ':reservation_hour' => $reservationHour,
                ':reservation_minute' => $reservationMinute,
                ':reservation_period' => $reservationPeriod,
                ':status' => $status,
                ':rejection_reason' => $rejectionReason,
                ':responded_at' => $respondedAt,
                ':responded_by_username' => $respondedBy,
                ':created_at' => $createdAt,
            ]);

            $keep[] = $id;
        }

        adbms_delete_missing($pdo, 'reservations', 'id', $keep);
        $pdo->commit();
    } catch (Throwable $e) {
        if ($pdo->inTransaction()) {
            $pdo->rollBack();
        }
        throw $e;
    }
}

function adbms_sync_notifications(PDO $pdo, array $items): void
{
    $pdo->beginTransaction();
    try {
        $keep = [];
        $stmt = $pdo->prepare(
            'INSERT INTO notifications (id, user_username, title, message, ts, is_read) VALUES (:id, :user_username, :title, :message, :ts, :is_read) ON DUPLICATE KEY UPDATE user_username = VALUES(user_username), title = VALUES(title), message = VALUES(message), ts = VALUES(ts), is_read = VALUES(is_read)'
        );

        foreach ($items as $item) {
            if (!is_array($item)) {
                continue;
            }

            $id = adbms_normalize_string($item['id'] ?? null) ?? adbms_unique_id('note');
            $userUsername = adbms_normalize_string($item['user'] ?? $item['userUsername'] ?? null);
            $title = adbms_normalize_string($item['title'] ?? null) ?? 'Notification';
            $message = adbms_normalize_string($item['msg'] ?? $item['message'] ?? null) ?? '';
            $ts = adbms_normalize_datetime($item['ts'] ?? null) ?? date('Y-m-d H:i:s');
            $isRead = !empty($item['read'] ?? $item['is_read'] ?? false) ? 1 : 0;

            $stmt->execute([
                ':id' => $id,
                ':user_username' => $userUsername,
                ':title' => $title,
                ':message' => $message,
                ':ts' => $ts,
                ':is_read' => $isRead,
            ]);

            $keep[] = $id;
        }

        adbms_delete_missing($pdo, 'notifications', 'id', $keep);
        $pdo->commit();
    } catch (Throwable $e) {
        if ($pdo->inTransaction()) {
            $pdo->rollBack();
        }
        throw $e;
    }
}

function adbms_authenticate(PDO $pdo, string $username, string $password): array
{
    $stmt = $pdo->prepare('SELECT username, name, password_hash, role, status, last_login FROM users WHERE username = :username LIMIT 1');
    $stmt->execute([':username' => $username]);
    $user = $stmt->fetch();

    if (!$user || !adbms_verify_password($password, (string) $user['password_hash'])) {
        throw new RuntimeException('Invalid username or password.');
    }

    if ($user['status'] !== 'Active') {
        throw new RuntimeException('This account is inactive. Contact the admin.');
    }

    $update = $pdo->prepare('UPDATE users SET last_login = NOW() WHERE username = :username');
    $update->execute([':username' => $username]);

    $refresh = $pdo->prepare(
        "SELECT username, name, role, status, CASE WHEN last_login IS NULL THEN NULL ELSE DATE_FORMAT(last_login, '%Y-%m-%dT%H:%i:%s') END AS lastLogin FROM users WHERE username = :username LIMIT 1"
    );
    $refresh->execute([':username' => $username]);

    $current = $refresh->fetch();
    if (!$current) {
        throw new RuntimeException('Unable to refresh authenticated user.');
    }

    return $current;
}
