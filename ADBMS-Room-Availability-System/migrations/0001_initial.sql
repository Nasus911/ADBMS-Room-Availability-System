-- Initial migration: create schema for room_db
-- This migration is idempotent (uses IF NOT EXISTS) and sets schema version to 2

CREATE TABLE IF NOT EXISTS `schema_version` (
  `id` TINYINT UNSIGNED NOT NULL,
  `version` INT UNSIGNED NOT NULL,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `users` (
  `username` VARCHAR(64) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` ENUM('Admin','Professor','Student') NOT NULL,
  `status` ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
  `last_login` DATETIME DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `rooms` (
  `room_number` INT NOT NULL,
  `floor_number` TINYINT UNSIGNED NOT NULL,
  `status` ENUM('available','occupied','reserved','maintenance') NOT NULL DEFAULT 'available',
  `occupied_by_username` VARCHAR(64) DEFAULT NULL,
  `status_updated_at` DATETIME DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`room_number`),
  KEY `idx_rooms_occupied_by_username` (`occupied_by_username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `checkins` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `schedules` (
  `id` VARCHAR(80) NOT NULL,
  `professor_username` VARCHAR(64) NOT NULL,
  `room_number` INT NOT NULL,
  `scheduled_date` DATE NOT NULL,
  `scheduled_hour` TINYINT UNSIGNED NOT NULL,
  `scheduled_minute` TINYINT UNSIGNED NOT NULL,
  `scheduled_period` ENUM('AM','PM') NOT NULL,
  `status` ENUM('Pending','Approved','Rejected','Cancelled') NOT NULL DEFAULT 'Approved',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_schedules_professor_username` (`professor_username`),
  KEY `idx_schedules_room_number` (`room_number`),
  CONSTRAINT `fk_schedules_room_number` FOREIGN KEY (`room_number`) REFERENCES `rooms` (`room_number`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `reservations` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `notifications` (
  `id` VARCHAR(80) NOT NULL,
  `user_username` VARCHAR(64) DEFAULT NULL,
  `title` VARCHAR(255) NOT NULL,
  `message` TEXT NOT NULL,
  `ts` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_read` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_notifications_user_username` (`user_username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE OR REPLACE VIEW `room_utilization` AS
SELECT
  SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) AS available_count,
  SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) AS occupied_count,
  SUM(CASE WHEN status = 'reserved' THEN 1 ELSE 0 END) AS reserved_count,
  SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) AS maintenance_count,
  COUNT(*) AS total_rooms
FROM rooms;

-- mark schema version
REPLACE INTO schema_version (id, version) VALUES (1, 2);
