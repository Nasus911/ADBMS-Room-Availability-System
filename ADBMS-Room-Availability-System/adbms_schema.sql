-- ADBMS MySQL schema for XAMPP
-- Create the database and tables for users, rooms, checkins, notifications, and scheduled_checkins

CREATE DATABASE IF NOT EXISTS `adbms` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `adbms`;

-- Users
CREATE TABLE `users` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(64) NOT NULL UNIQUE,
  `name` VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) DEFAULT NULL,
  `role` ENUM('Admin','Professor','Student') NOT NULL DEFAULT 'Student',
  `status` ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
  `last_login` DATETIME DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Rooms
CREATE TABLE `rooms` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `room_number` INT NOT NULL UNIQUE,
  `status` ENUM('available','occupied','reserved','maintenance') NOT NULL DEFAULT 'available',
  `occupied_by` INT UNSIGNED DEFAULT NULL,
  `status_updated_at` DATETIME DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX (`room_number`),
  INDEX (`occupied_by`),
  CONSTRAINT `fk_rooms_occupied_by` FOREIGN KEY (`occupied_by`) REFERENCES `users`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Check-ins / occupancy log
CREATE TABLE `checkins` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `room_id` INT UNSIGNED NOT NULL,
  `user_id` INT UNSIGNED NOT NULL,
  `checkin_date` DATE NOT NULL,
  `ts` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `metadata` JSON DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX (`room_id`),
  INDEX (`user_id`),
  CONSTRAINT `fk_checkins_room` FOREIGN KEY (`room_id`) REFERENCES `rooms`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_checkins_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notifications (optional)
CREATE TABLE `notifications` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED DEFAULT NULL,
  `title` VARCHAR(255) DEFAULT NULL,
  `message` TEXT,
  `ts` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_read` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  INDEX (`user_id`),
  CONSTRAINT `fk_notifications_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Scheduled/reservations (optional)
CREATE TABLE `scheduled_checkins` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `room_id` INT UNSIGNED NOT NULL,
  `user_id` INT UNSIGNED NOT NULL,
  `when_ts` DATETIME NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX (`room_id`),
  INDEX (`user_id`),
  CONSTRAINT `fk_sched_room` FOREIGN KEY (`room_id`) REFERENCES `rooms`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_sched_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Default admin placeholder (set password_hash later via app or PHP password_hash)
INSERT INTO `users` (`username`,`name`,`password_hash`,`role`,`status`) VALUES
('admin','System Admin','', 'Admin', 'Active');

-- Seed rooms: floors 1..5 units 1..9 (rooms 101..109, 201..209 ... 509)
INSERT INTO `rooms` (`room_number`,`status`) VALUES
(101,'available'),(102,'available'),(103,'available'),(104,'available'),(105,'available'),(106,'available'),(107,'available'),(108,'available'),(109,'available'),
(201,'available'),(202,'available'),(203,'available'),(204,'available'),(205,'available'),(206,'available'),(207,'available'),(208,'available'),(209,'available'),
(301,'available'),(302,'available'),(303,'available'),(304,'available'),(305,'available'),(306,'available'),(307,'available'),(308,'available'),(309,'available'),
(401,'available'),(402,'available'),(403,'available'),(404,'available'),(405,'available'),(406,'available'),(407,'available'),(408,'available'),(409,'available'),
(501,'available'),(502,'available'),(503,'available'),(504,'available'),(505,'available'),(506,'available'),(507,'available'),(508,'available'),(509,'available');

-- Optional: a convenient view for quick admin stats
CREATE OR REPLACE VIEW `room_utilization` AS
SELECT
  (SELECT COUNT(*) FROM rooms WHERE status = 'available') AS available_count,
  (SELECT COUNT(*) FROM rooms WHERE status = 'occupied') AS occupied_count,
  (SELECT COUNT(*) FROM rooms WHERE status = 'reserved') AS reserved_count,
  (SELECT COUNT(*) FROM rooms WHERE status = 'maintenance') AS maintenance_count,
  (SELECT COUNT(*) FROM rooms) AS total_rooms;

-- End of file
