-- Migration 0002: Add Activity Logs table for comprehensive audit trail
-- This migration creates the activity_logs table to track all important activities,
-- changes, and transactions throughout the system.

CREATE TABLE IF NOT EXISTS `activity_logs` (
  `log_id` VARCHAR(80) NOT NULL,
  `user_id` VARCHAR(64) DEFAULT NULL,
  `user_role` ENUM('Admin','Professor','Student','System') DEFAULT NULL,
  `affected_table` VARCHAR(64) NOT NULL,
  `affected_record_id` VARCHAR(255) NOT NULL,
  `action_type` ENUM('CREATE','READ','UPDATE','DELETE','LOGIN','LOGOUT','ASSIGN','REASSIGN','APPROVE','REJECT') NOT NULL,
  `description` TEXT DEFAULT NULL,
  `old_value` LONGTEXT DEFAULT NULL,
  `new_value` LONGTEXT DEFAULT NULL,
  `changes_json` JSON DEFAULT NULL,
  `ip_address` VARCHAR(45) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  KEY `idx_logs_user_id` (`user_id`),
  KEY `idx_logs_affected_table` (`affected_table`),
  KEY `idx_logs_affected_record_id` (`affected_record_id`),
  KEY `idx_logs_action_type` (`action_type`),
  KEY `idx_logs_created_at` (`created_at`),
  KEY `idx_logs_user_action_time` (`user_id`, `action_type`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
