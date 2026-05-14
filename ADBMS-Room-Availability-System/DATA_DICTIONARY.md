# ADBMS Room Availability System - Data Dictionary

## 📖 Overview

This Data Dictionary provides comprehensive field-level documentation for all tables in the `room_db` database. It includes data types, constraints, relationships, and sample queries for each table.

---

## Table of Contents

1. [schema_version](#schema_version)
2. [users](#users)
3. [rooms](#rooms)
4. [checkins](#checkins)
5. [schedules](#schedules)
6. [reservations](#reservations)
7. [notifications](#notifications)
8. [Views](#views)
9. [Relationships](#relationships)
10. [Sample Queries](#sample-queries)
11. [Constraints & Indexes](#constraints--indexes)

---

## SCHEMA_VERSION

**Purpose**: Tracks database schema version for migration management

**Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci

### Field Definitions

| Field | Type | Size | Null | Default | Constraint | Purpose |
|-------|------|------|------|---------|-----------|---------|
| `id` | TINYINT UNSIGNED | 1 byte | NO | - | PK | Unique schema identifier (always 1) |
| `version` | INT UNSIGNED | 4 bytes | NO | - | UK | Schema version number |
| `updated_at` | TIMESTAMP | 4 bytes | NO | CURRENT_TIMESTAMP | AUTO UPDATE | Last update timestamp |

### Field Details

**id** (Primary Key)
- Type: TINYINT UNSIGNED
- Size: 1 byte
- Range: 0-255
- Fixed Value: 1 (only one record per database)
- Example: `1`

**version** (Unique Key)
- Type: INT UNSIGNED
- Size: 4 bytes
- Range: 0-4,294,967,295
- Increments with each migration
- Example: `2`
- Current Version: 2 (as of May 2026)

**updated_at**
- Type: TIMESTAMP
- Auto-updates when row changes
- Stored in UTC
- Example: `2026-05-14 15:30:45`

### Sample Record
```sql
id | version | updated_at
1  | 2       | 2026-05-14 14:00:00
```

### Queries

**Get current schema version:**
```sql
SELECT version FROM schema_version WHERE id = 1;
-- Returns: 2
```

---

## USERS

**Purpose**: Store user accounts with authentication, roles, and activity tracking

**Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci | **Records**: 3 (seed data)

### Field Definitions

| Field | Type | Size | Null | Default | Constraint | Purpose |
|-------|------|------|------|---------|-----------|---------|
| `username` | VARCHAR | 64 | NO | - | PK | Unique user identifier |
| `name` | VARCHAR | 255 | NO | - | - | Full name |
| `password_hash` | VARCHAR | 255 | NO | - | - | Bcrypt hashed password |
| `role` | ENUM | - | NO | - | - | User role (Admin/Professor/Student) |
| `status` | ENUM | - | NO | Active | - | Account status |
| `last_login` | DATETIME | 8 | YES | NULL | - | Last login timestamp |
| `created_at` | TIMESTAMP | 4 | NO | CURRENT_TIMESTAMP | - | Record creation time |
| `updated_at` | TIMESTAMP | 4 | NO | CURRENT_TIMESTAMP | AUTO UPDATE | Last modification time |

### Field Details

**username** (Primary Key)
- Type: VARCHAR(64)
- Max Length: 64 characters
- Unique: YES
- Purpose: Login identifier
- Format: lowercase, alphanumeric
- Examples: `admin`, `professor`, `student`

**name**
- Type: VARCHAR(255)
- Max Length: 255 characters
- Purpose: User's full name for display
- Examples: `System Administrator`, `Dr. John Smith`, `Alice Johnson`

**password_hash**
- Type: VARCHAR(255)
- Purpose: Bcrypt password hash for authentication
- Algorithm: PASSWORD_DEFAULT (bcrypt)
- Fallback: SHA256 support for legacy
- Never stored in plain text
- Example: `$2y$10$abcdef1234567890...`

**role** (ENUM)
- Type: ENUM('Admin', 'Professor', 'Student')
- Determines: Access level and available actions
- Values:
  - `Admin`: Full system access, manage users/rooms
  - `Professor`: Create schedules, make reservations
  - `Student`: Check-in to rooms, view schedules
- Example: `Admin`

**status** (ENUM)
- Type: ENUM('Active', 'Inactive')
- Default: Active
- Purpose: Enable/disable user without deletion
- Values:
  - `Active`: User can log in
  - `Inactive`: User cannot log in
- Example: `Active`

**last_login**
- Type: DATETIME
- Nullable: YES (NULL if user never logged in)
- Purpose: Track user activity
- Format: YYYY-MM-DD HH:MM:SS
- Example: `2026-05-14 09:30:15`

**created_at**
- Type: TIMESTAMP
- Auto: CURRENT_TIMESTAMP (set on insert)
- Purpose: Record creation audit trail
- Example: `2026-05-14 08:00:00`

**updated_at**
- Type: TIMESTAMP
- Auto: CURRENT_TIMESTAMP on UPDATE
- Purpose: Track record modifications
- Example: `2026-05-14 15:30:45`

### Seed Data

```sql
username  | name                      | role      | status
----------|---------------------------|-----------|--------
admin     | System Administrator      | Admin     | Active
professor | Professor User            | Professor | Active
student   | Student User              | Student   | Active
```

### Constraints & Indexes

- PK: `username` (primary key)
- Collation: Case-insensitive for username matching
- AUTO_INCREMENT: No (manual usernames)

---

## ROOMS

**Purpose**: Inventory of physical rooms with real-time status tracking

**Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci | **Records**: 45 (9 floors × 5 rooms)

### Field Definitions

| Field | Type | Size | Null | Default | Constraint | Index | Purpose |
|-------|------|------|------|---------|-----------|-------|---------|
| `room_number` | INT | 4 | NO | - | PK | - | Unique room identifier |
| `floor_number` | TINYINT UNSIGNED | 1 | NO | - | - | - | Floor level (1-9) |
| `status` | ENUM | - | NO | available | - | - | Room occupancy status |
| `occupied_by_username` | VARCHAR | 64 | YES | NULL | FK | idx_rooms_occupied_by_username | Current occupant |
| `status_updated_at` | DATETIME | 8 | YES | NULL | - | - | Last status change time |
| `created_at` | TIMESTAMP | 4 | NO | CURRENT_TIMESTAMP | - | - | Record creation time |
| `updated_at` | TIMESTAMP | 4 | NO | CURRENT_TIMESTAMP | AUTO UPDATE | - | Last modification time |

### Field Details

**room_number** (Primary Key)
- Type: INT
- Format: FXXX (Floor + sequence)
- Range: 101-905 (9 floors, 5 rooms per floor)
- Purpose: Unique room identifier
- Examples: 
  - Floor 1: 101, 102, 103, 104, 105
  - Floor 9: 901, 902, 903, 904, 905
- Naming Convention: First digit = floor, last 2 digits = room sequence

**floor_number**
- Type: TINYINT UNSIGNED
- Range: 1-9
- Calculated: floor_number = room_number ÷ 100
- Purpose: Quick floor filtering
- Example: Room 305 → Floor 3

**status** (ENUM)
- Type: ENUM('available', 'occupied', 'reserved', 'maintenance')
- Default: 'available'
- Purpose: Room availability status
- Values:
  - `available`: Room is free and bookable
  - `occupied`: Room currently in use
  - `reserved`: Room has approved reservation
  - `maintenance`: Room under maintenance, not available
- Example: `available`

**occupied_by_username** (Foreign Key)
- Type: VARCHAR(64)
- Nullable: YES (NULL if room is unoccupied)
- References: users.username
- Purpose: Track current occupant
- Example: `student` or NULL

**status_updated_at**
- Type: DATETIME
- Nullable: YES (NULL initially)
- Purpose: Track when status last changed
- Format: YYYY-MM-DD HH:MM:SS
- Example: `2026-05-14 14:30:00`

**created_at**
- Type: TIMESTAMP
- Auto: CURRENT_TIMESTAMP
- Purpose: Record creation audit
- Example: `2026-05-14 08:00:00`

**updated_at**
- Type: TIMESTAMP
- Auto: CURRENT_TIMESTAMP on UPDATE
- Purpose: Track record modifications
- Example: `2026-05-14 15:45:00`

### Sample Records

```sql
room_number | floor_number | status     | occupied_by_username | status_updated_at
------------|-------------|------------|---------------------|-------------------
101         | 1           | available  | NULL                 | NULL
205         | 2           | occupied   | student              | 2026-05-14 14:30:00
407         | 4           | reserved   | NULL                 | 2026-05-14 10:15:00
503         | 5           | available  | NULL                 | 2026-05-14 08:00:00
901         | 9           | maintenance| NULL                 | 2026-05-14 09:00:00
```

### Constraints & Indexes

- PK: `room_number`
- FK: `occupied_by_username` → users.username
- Index: `idx_rooms_occupied_by_username` (for quick occupant lookups)

---

## CHECKINS

**Purpose**: Activity log of room entry/exit and access tracking

**Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci

### Field Definitions

| Field | Type | Size | Null | Default | Constraint | Index | Purpose |
|-------|------|------|------|---------|-----------|-------|---------|
| `id` | VARCHAR | 80 | NO | - | PK | - | Unique check-in identifier |
| `room_number` | INT | 4 | NO | - | FK | idx_checkins_room_number | Room being checked into |
| `user_username` | VARCHAR | 64 | NO | - | FK | idx_checkins_user_username | User performing check-in |
| `checkin_date` | DATE | 3 | NO | - | - | - | Date of check-in |
| `ts` | DATETIME | 8 | NO | CURRENT_TIMESTAMP | - | - | Exact timestamp |
| `metadata` | JSON | - | YES | NULL | - | - | Additional data (flexible) |

### Field Details

**id** (Primary Key)
- Type: VARCHAR(80)
- Format: `chk_{timestamp}_{random}`
- Generated: Application-level UUID
- Purpose: Globally unique transaction identifier
- Example: `chk_xyz127abc4_8f2d1e9c`

**room_number** (Foreign Key)
- Type: INT
- References: rooms.room_number
- Cascade: ON DELETE CASCADE, ON UPDATE CASCADE
- Purpose: Link to room being accessed
- Example: `101`

**user_username** (Foreign Key)
- Type: VARCHAR(64)
- References: users.username
- Purpose: Link to user performing check-in
- Example: `student`

**checkin_date**
- Type: DATE
- Format: YYYY-MM-DD
- Purpose: Date grouping for analytics
- Example: `2026-05-14`

**ts** (Timestamp)
- Type: DATETIME
- Auto: CURRENT_TIMESTAMP
- Format: YYYY-MM-DD HH:MM:SS
- Purpose: Exact check-in time
- Example: `2026-05-14 09:30:15`

**metadata** (JSON)
- Type: JSON
- Nullable: YES
- Purpose: Flexible data storage (device info, GPS, notes)
- Example:
  ```json
  {
    "device": "iPhone",
    "ip": "192.168.1.100",
    "notes": "Regular class session"
  }
  ```

### Sample Records

```sql
id              | room_number | user_username | checkin_date | ts
----------------|-------------|---------------|--------------|-------------------
chk_xyz127_abc4 | 101         | student       | 2026-05-14   | 2026-05-14 09:00:15
chk_xyz128_abc5 | 102         | student       | 2026-05-14   | 2026-05-14 10:30:45
chk_xyz129_abc6 | 205         | professor     | 2026-05-14   | 2026-05-14 13:15:00
```

### Constraints & Indexes

- PK: `id`
- FK: `room_number` → rooms.room_number (CASCADE)
- FK: `user_username` → users.username (implicit)
- Index: `idx_checkins_room_number` (for room history)
- Index: `idx_checkins_user_username` (for user activity)

---

## SCHEDULES

**Purpose**: Recurring class schedules and planned room usage

**Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci

### Field Definitions

| Field | Type | Size | Null | Default | Constraint | Index | Purpose |
|-------|------|------|------|---------|-----------|-------|---------|
| `id` | VARCHAR | 80 | NO | - | PK | - | Unique schedule identifier |
| `professor_username` | VARCHAR | 64 | NO | - | FK | idx_schedules_professor_username | Schedule creator |
| `room_number` | INT | 4 | NO | - | FK | idx_schedules_room_number | Room being scheduled |
| `scheduled_date` | DATE | 3 | NO | - | - | - | Date of scheduled session |
| `scheduled_hour` | TINYINT UNSIGNED | 1 | NO | - | - | - | Hour (0-23, displayed as 1-12 in 12-hr format) |
| `scheduled_minute` | TINYINT UNSIGNED | 1 | NO | - | - | - | Minute (0, 5, 10, 15, ..., 55) |
| `scheduled_period` | ENUM | - | NO | - | - | - | AM or PM |
| `status` | ENUM | - | NO | Approved | - | - | Schedule status |
| `created_at` | DATETIME | 8 | NO | CURRENT_TIMESTAMP | - | - | Record creation time |
| `updated_at` | DATETIME | 8 | NO | CURRENT_TIMESTAMP | AUTO UPDATE | - | Last modification time |

### Field Details

**id** (Primary Key)
- Type: VARCHAR(80)
- Format: `sch_{timestamp}_{random}`
- Generated: Application-level UUID
- Example: `sch_xyz123_abc0`

**professor_username** (Foreign Key)
- Type: VARCHAR(64)
- References: users.username
- Role: Schedule creator (must be Professor)
- Example: `professor`

**room_number** (Foreign Key)
- Type: INT
- References: rooms.room_number
- Cascade: ON DELETE CASCADE, ON UPDATE CASCADE
- Example: `101`

**scheduled_date**
- Type: DATE
- Format: YYYY-MM-DD
- Purpose: Date of scheduled session
- Range: Current date onwards
- Example: `2026-05-15`

**scheduled_hour**
- Type: TINYINT UNSIGNED
- Range: 0-23 (24-hour storage)
- Display: Converted to 1-12 in UI (12-hour format)
- Purpose: Hour component of time
- Examples:
  - 9 = 9:00 AM
  - 14 = 2:00 PM
  - 0 = 12:00 AM (midnight)

**scheduled_minute**
- Type: TINYINT UNSIGNED
- Range: 0, 5, 10, 15, ..., 55 (5-minute intervals)
- Purpose: Minute component
- Example: `30` (for 9:30 AM/PM)

**scheduled_period** (ENUM)
- Type: ENUM('AM', 'PM')
- Purpose: Display indicator
- Note: Stored with 24-hr hour for accuracy
- Examples: `AM`, `PM`

**status** (ENUM)
- Type: ENUM('Pending', 'Approved', 'Rejected', 'Cancelled')
- Default: 'Approved'
- Purpose: Schedule approval workflow
- Values:
  - `Pending`: Awaiting admin approval
  - `Approved`: Approved by admin
  - `Rejected`: Rejected by admin
  - `Cancelled`: Cancelled by creator
- Example: `Approved`

**created_at**
- Type: DATETIME
- Auto: CURRENT_TIMESTAMP
- Example: `2026-05-14 10:30:00`

**updated_at**
- Type: DATETIME
- Auto: CURRENT_TIMESTAMP on UPDATE
- Example: `2026-05-14 15:45:00`

### Sample Records

```sql
id              | professor_username | room_number | scheduled_date | scheduled_hour | scheduled_minute | scheduled_period | status
----------------|-------------------|------------|-----------------|----------------|------------------|------------------|----------
sch_xyz123_abc0 | professor         | 101         | 2026-05-15      | 9              | 0                | AM               | Approved
sch_xyz124_abc1 | professor         | 205         | 2026-05-16      | 14             | 30               | PM               | Approved
sch_xyz125_abc2 | professor         | 301         | 2026-05-17      | 10             | 15               | AM               | Pending
```

### Constraints & Indexes

- PK: `id`
- FK: `professor_username` → users.username (implicit)
- FK: `room_number` → rooms.room_number (CASCADE)
- Index: `idx_schedules_professor_username`
- Index: `idx_schedules_room_number`

---

## RESERVATIONS

**Purpose**: Room booking requests with approval workflow and audit trail

**Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci

### Field Definitions

| Field | Type | Size | Null | Default | Constraint | Index | Purpose |
|-------|------|------|------|---------|-----------|-------|---------|
| `id` | VARCHAR | 80 | NO | - | PK | - | Unique reservation identifier |
| `professor_username` | VARCHAR | 64 | NO | - | FK | idx_reservations_professor_username | Reservation requester |
| `room_number` | INT | 4 | NO | - | FK | idx_reservations_room_number | Room being reserved |
| `reservation_date` | DATE | 3 | NO | - | - | - | Requested date |
| `reservation_hour` | TINYINT UNSIGNED | 1 | NO | - | - | - | Requested hour |
| `reservation_minute` | TINYINT UNSIGNED | 1 | NO | - | - | - | Requested minute |
| `reservation_period` | ENUM | - | NO | - | - | - | AM or PM |
| `status` | ENUM | - | NO | Pending | - | - | Reservation status |
| `rejection_reason` | TEXT | - | YES | NULL | - | - | Why rejected (if applicable) |
| `responded_at` | DATETIME | 8 | YES | NULL | - | - | When response was given |
| `responded_by_username` | VARCHAR | 64 | YES | NULL | FK | idx_reservations_responded_by_username | Admin who responded |
| `created_at` | DATETIME | 8 | NO | CURRENT_TIMESTAMP | - | - | Request creation time |
| `updated_at` | DATETIME | 8 | NO | CURRENT_TIMESTAMP | AUTO UPDATE | - | Last modification time |

### Field Details

**id** (Primary Key)
- Type: VARCHAR(80)
- Format: `res_{timestamp}_{random}`
- Generated: Application-level UUID
- Example: `res_xyz125_abc2`

**professor_username** (Foreign Key)
- Type: VARCHAR(64)
- References: users.username
- Purpose: Who requested the reservation
- Example: `professor`

**room_number** (Foreign Key)
- Type: INT
- References: rooms.room_number
- Cascade: ON DELETE CASCADE, ON UPDATE CASCADE
- Example: `301`

**reservation_date**
- Type: DATE
- Format: YYYY-MM-DD
- Purpose: Requested date
- Example: `2026-05-20`

**reservation_hour**
- Type: TINYINT UNSIGNED
- Range: 0-23
- Display: Converted to 1-12 in UI
- Example: `10`

**reservation_minute**
- Type: TINYINT UNSIGNED
- Range: 0, 5, 10, ..., 55
- Example: `30`

**reservation_period** (ENUM)
- Type: ENUM('AM', 'PM')
- Example: `AM`

**status** (ENUM)
- Type: ENUM('Pending', 'Approved', 'Rejected')
- Default: 'Pending'
- Values:
  - `Pending`: Awaiting admin response
  - `Approved`: Approved by admin
  - `Rejected`: Rejected by admin with reason
- Example: `Pending`

**rejection_reason**
- Type: TEXT
- Nullable: YES (NULL if approved or pending)
- Purpose: Explanation for rejection
- Example: `Room already booked for that time`

**responded_at**
- Type: DATETIME
- Nullable: YES (NULL if pending)
- Purpose: When admin responded
- Example: `2026-05-14 15:30:00`

**responded_by_username** (Foreign Key)
- Type: VARCHAR(64)
- Nullable: YES (NULL if pending)
- References: users.username (Admin only)
- Purpose: Audit trail - which admin responded
- Example: `admin`

**created_at**
- Type: DATETIME
- Auto: CURRENT_TIMESTAMP
- Example: `2026-05-14 09:00:00`

**updated_at**
- Type: DATETIME
- Auto: CURRENT_TIMESTAMP on UPDATE
- Example: `2026-05-14 15:30:00`

### Sample Records

```sql
id              | professor_username | room_number | reservation_date | status   | responded_by_username | rejection_reason
----------------|-------------------|------------|------------------|----------|---------------------|------------------
res_xyz125_abc2 | professor         | 301         | 2026-05-20       | Pending  | NULL                 | NULL
res_xyz126_abc3 | professor         | 102         | 2026-05-18       | Approved | admin                | NULL
res_xyz127_abc4 | professor         | 205         | 2026-05-17       | Rejected | admin                | Room maintenance scheduled
```

### Constraints & Indexes

- PK: `id`
- FK: `professor_username` → users.username
- FK: `room_number` → rooms.room_number (CASCADE)
- FK: `responded_by_username` → users.username
- Index: `idx_reservations_professor_username`
- Index: `idx_reservations_room_number`
- Index: `idx_reservations_responded_by_username`

---

## NOTIFICATIONS

**Purpose**: System alerts and messages to users

**Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci

### Field Definitions

| Field | Type | Size | Null | Default | Constraint | Index | Purpose |
|-------|------|------|------|---------|-----------|-------|---------|
| `id` | VARCHAR | 80 | NO | - | PK | - | Unique notification identifier |
| `user_username` | VARCHAR | 64 | YES | NULL | FK | idx_notifications_user_username | Recipient user |
| `title` | VARCHAR | 255 | NO | - | - | - | Notification title |
| `message` | TEXT | - | NO | - | - | - | Notification message |
| `ts` | DATETIME | 8 | NO | CURRENT_TIMESTAMP | - | - | Notification timestamp |
| `is_read` | TINYINT | 1 | NO | 0 | - | - | Read status (0=unread, 1=read) |

### Field Details

**id** (Primary Key)
- Type: VARCHAR(80)
- Format: `not_{timestamp}_{random}`
- Generated: Application-level UUID
- Example: `not_xyz129_abc6`

**user_username** (Foreign Key)
- Type: VARCHAR(64)
- Nullable: YES (NULL = broadcast to all users)
- References: users.username
- Purpose: Recipient user
- Example: `professor` or NULL

**title**
- Type: VARCHAR(255)
- Max Length: 255 characters
- Purpose: Notification subject
- Examples:
  - `Reservation Approved`
  - `Room 101 is now available`
  - `Schedule Reminder`

**message**
- Type: TEXT
- Purpose: Full notification text
- Max Length: 65,535 characters
- Example: `Your reservation for room 301 on 2026-05-20 has been approved by admin`

**ts** (Timestamp)
- Type: DATETIME
- Auto: CURRENT_TIMESTAMP
- Format: YYYY-MM-DD HH:MM:SS
- Purpose: When notification was sent
- Example: `2026-05-14 15:30:00`

**is_read**
- Type: TINYINT(1) (boolean-like)
- Values: 0 = unread, 1 = read
- Default: 0
- Purpose: Read status tracking
- Example: `0` or `1`

### Sample Records

```sql
id              | user_username | title                    | is_read | ts
----------------|---------------|--------------------------|---------|-------------------
not_xyz129_abc6 | professor     | Reservation Approved     | 0       | 2026-05-14 15:30:00
not_xyz130_abc7 | student       | Room 101 is now available| 1       | 2026-05-14 14:15:00
not_xyz131_abc8 | NULL          | System maintenance at 8PM| 0       | 2026-05-14 17:00:00
```

### Constraints & Indexes

- PK: `id`
- FK: `user_username` → users.username (nullable for broadcasts)
- Index: `idx_notifications_user_username`

---

## Views

### room_utilization

**Purpose**: Real-time room status summary for dashboard/analytics

**Query:**
```sql
CREATE OR REPLACE VIEW room_utilization AS
SELECT
  SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) AS available_count,
  SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) AS occupied_count,
  SUM(CASE WHEN status = 'reserved' THEN 1 ELSE 0 END) AS reserved_count,
  SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) AS maintenance_count,
  COUNT(*) AS total_rooms
FROM rooms;
```

**Sample Output:**
```sql
available_count | occupied_count | reserved_count | maintenance_count | total_rooms
30              | 10             | 4              | 1                 | 45
```

**Usage:**
```sql
SELECT * FROM room_utilization;
-- Returns current room status distribution
```

---

## Relationships

### Foreign Key Relationships

#### checkins → rooms
```sql
CONSTRAINT fk_checkins_room_number
  FOREIGN KEY (room_number) REFERENCES rooms(room_number)
  ON DELETE CASCADE ON UPDATE CASCADE
```
- When a room is deleted, all its check-in records are deleted
- When room_number is updated, all references update automatically

#### checkins → users (implicit)
```
checkins.user_username → users.username
```
- Tracks which user performed check-in

#### schedules → rooms
```sql
CONSTRAINT fk_schedules_room_number
  FOREIGN KEY (room_number) REFERENCES rooms(room_number)
  ON DELETE CASCADE ON UPDATE CASCADE
```

#### schedules → users (implicit)
```
schedules.professor_username → users.username
```

#### reservations → rooms
```sql
CONSTRAINT fk_reservations_room_number
  FOREIGN KEY (room_number) REFERENCES rooms(room_number)
  ON DELETE CASCADE ON UPDATE CASCADE
```

#### reservations → users (implicit, multiple)
```
reservations.professor_username → users.username (requester)
reservations.responded_by_username → users.username (responder, nullable)
```

#### notifications → users (implicit)
```
notifications.user_username → users.username (nullable for broadcasts)
```

#### rooms → users (implicit)
```
rooms.occupied_by_username → users.username (nullable)
```

### Cardinality Matrix

```
              | users | rooms | checkins | schedules | reservations | notifications
--------------|-------|-------|----------|-----------|--------------|---------------
users         | N/A   | 1:N   | 1:N      | 1:N       | 1:N          | 1:N
rooms         | N:1   | N/A   | 1:N      | 1:N       | 1:N          | -
checkins      | N:1   | N:1   | N/A      | -         | -            | -
schedules     | N:1   | N:1   | -        | N/A       | -            | -
reservations  | N:1   | N:1   | -        | -         | N/A          | -
notifications | N:1   | -     | -        | -         | -            | N/A
```

---

## Sample Queries

### User Management Queries

#### Get all active users
```sql
SELECT username, name, role, status
FROM users
WHERE status = 'Active'
ORDER BY FIELD(role, 'Admin', 'Professor', 'Student'), name;
```

#### Find users who logged in today
```sql
SELECT username, name, last_login
FROM users
WHERE DATE(last_login) = CURDATE()
ORDER BY last_login DESC;
```

#### Get user activity summary
```sql
SELECT 
  u.username,
  u.name,
  u.role,
  COUNT(c.id) AS total_checkins,
  MAX(c.ts) AS last_checkin,
  MAX(u.last_login) AS last_login
FROM users u
LEFT JOIN checkins c ON u.username = c.user_username
GROUP BY u.username
ORDER BY u.name;
```

### Room Management Queries

#### List all available rooms by floor
```sql
SELECT room_number, floor_number, status, occupied_by_username
FROM rooms
WHERE status = 'available'
ORDER BY floor_number, room_number;
```

#### Get room occupancy report
```sql
SELECT * FROM room_utilization;
```

#### Find rooms needing maintenance
```sql
SELECT room_number, floor_number, status
FROM rooms
WHERE status = 'maintenance'
ORDER BY room_number;
```

#### Get rooms occupied by user
```sql
SELECT room_number, floor_number, occupied_by_username, status_updated_at
FROM rooms
WHERE occupied_by_username = 'student'
ORDER BY room_number;
```

### Schedule & Reservation Queries

#### Get professor's approved schedules
```sql
SELECT 
  s.id,
  s.room_number,
  s.scheduled_date,
  CONCAT(s.scheduled_hour, ':', LPAD(s.scheduled_minute, 2, '0'), ' ', s.scheduled_period) AS time,
  s.status
FROM schedules s
WHERE s.professor_username = 'professor'
  AND s.status = 'Approved'
  AND s.scheduled_date >= CURDATE()
ORDER BY s.scheduled_date, s.scheduled_hour;
```

#### Get pending reservations awaiting approval
```sql
SELECT 
  r.id,
  u.name AS professor_name,
  r.room_number,
  r.reservation_date,
  CONCAT(r.reservation_hour, ':', LPAD(r.reservation_minute, 2, '0'), ' ', r.reservation_period) AS time,
  r.status,
  r.created_at
FROM reservations r
JOIN users u ON r.professor_username = u.username
WHERE r.status = 'Pending'
ORDER BY r.created_at ASC;
```

#### Get reservation approval history
```sql
SELECT 
  r.id,
  u1.name AS requested_by,
  u2.name AS approved_by,
  r.room_number,
  r.reservation_date,
  r.status,
  r.responded_at,
  r.rejection_reason
FROM reservations r
JOIN users u1 ON r.professor_username = u1.username
LEFT JOIN users u2 ON r.responded_by_username = u2.username
WHERE r.responded_at IS NOT NULL
ORDER BY r.responded_at DESC;
```

### Activity & Analytics Queries

#### Get check-in history for a room
```sql
SELECT 
  c.checkin_date,
  c.user_username,
  u.name,
  u.role,
  DATE_FORMAT(c.ts, '%H:%i:%s') AS check_in_time
FROM checkins c
JOIN users u ON c.user_username = u.username
WHERE c.room_number = 101
ORDER BY c.ts DESC
LIMIT 50;
```

#### Get daily check-in count by room
```sql
SELECT 
  c.checkin_date,
  c.room_number,
  COUNT(*) AS checkin_count
FROM checkins c
WHERE c.checkin_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY c.checkin_date, c.room_number
ORDER BY c.checkin_date DESC, c.room_number;
```

#### Get unread notifications for user
```sql
SELECT 
  id,
  title,
  message,
  ts
FROM notifications
WHERE user_username = 'professor'
  AND is_read = 0
ORDER BY ts DESC;
```

#### Mark notifications as read
```sql
UPDATE notifications
SET is_read = 1
WHERE user_username = 'professor'
  AND is_read = 0;
```

### Complex Join Queries

#### Get schedule details with room and professor info
```sql
SELECT 
  s.id,
  u.name AS professor_name,
  u.role,
  s.room_number,
  s.scheduled_date,
  CONCAT(s.scheduled_hour, ':', LPAD(s.scheduled_minute, 2, '0'), ' ', s.scheduled_period) AS scheduled_time,
  r.floor_number,
  r.status AS room_status,
  s.status,
  s.created_at
FROM schedules s
JOIN users u ON s.professor_username = u.username
JOIN rooms r ON s.room_number = r.room_number
WHERE s.scheduled_date >= CURDATE()
ORDER BY s.scheduled_date, s.scheduled_hour;
```

#### Get all reservations with complete details
```sql
SELECT 
  r.id,
  u1.name AS requester_name,
  u2.name AS approver_name,
  r.room_number,
  fl.floor_number,
  r.reservation_date,
  CONCAT(r.reservation_hour, ':', LPAD(r.reservation_minute, 2, '0'), ' ', r.reservation_period) AS requested_time,
  r.status,
  r.rejection_reason,
  r.responded_at,
  DATEDIFF(r.responded_at, r.created_at) AS response_days
FROM reservations r
JOIN users u1 ON r.professor_username = u1.username
LEFT JOIN users u2 ON r.responded_by_username = u2.username
JOIN rooms fl ON r.room_number = fl.room_number
ORDER BY r.created_at DESC;
```

#### Room utilization by professor
```sql
SELECT 
  u.name AS professor_name,
  COUNT(DISTINCT s.id) AS total_schedules,
  COUNT(DISTINCT r.id) AS total_reservations,
  COUNT(DISTINCT r.room_number) AS unique_rooms_used
FROM users u
LEFT JOIN schedules s ON u.username = s.professor_username AND s.status = 'Approved'
LEFT JOIN reservations r ON u.username = r.professor_username AND r.status = 'Approved'
WHERE u.role = 'Professor'
GROUP BY u.username, u.name
ORDER BY total_schedules DESC, total_reservations DESC;
```

### Data Validation Queries

#### Find orphaned reservations (if FK constraint not enforced)
```sql
SELECT r.id, r.room_number
FROM reservations r
LEFT JOIN rooms rm ON r.room_number = rm.room_number
WHERE rm.room_number IS NULL;
```

#### Find invalid check-ins
```sql
SELECT c.id, c.room_number, c.user_username
FROM checkins c
LEFT JOIN rooms r ON c.room_number = r.room_number
LEFT JOIN users u ON c.user_username = u.username
WHERE r.room_number IS NULL OR u.username IS NULL;
```

#### Check for inconsistent room status
```sql
SELECT room_number, occupied_by_username, status
FROM rooms
WHERE (status = 'occupied' AND occupied_by_username IS NULL)
   OR (status != 'occupied' AND occupied_by_username IS NOT NULL);
```

---

## Constraints & Indexes

### Primary Keys (Guaranteed Uniqueness)
```sql
-- PK: username (unique user identifier)
ALTER TABLE users ADD PRIMARY KEY (username);

-- PK: room_number (unique room identifier)
ALTER TABLE rooms ADD PRIMARY KEY (room_number);

-- PK: id (unique check-in)
ALTER TABLE checkins ADD PRIMARY KEY (id);

-- PK: id (unique schedule)
ALTER TABLE schedules ADD PRIMARY KEY (id);

-- PK: id (unique reservation)
ALTER TABLE reservations ADD PRIMARY KEY (id);

-- PK: id (unique notification)
ALTER TABLE notifications ADD PRIMARY KEY (id);

-- PK: id (schema version)
ALTER TABLE schema_version ADD PRIMARY KEY (id);
```

### Foreign Keys (Referential Integrity)
```sql
-- FK: checkins → rooms
ALTER TABLE checkins ADD CONSTRAINT fk_checkins_room_number
  FOREIGN KEY (room_number) REFERENCES rooms(room_number)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- FK: schedules → rooms
ALTER TABLE schedules ADD CONSTRAINT fk_schedules_room_number
  FOREIGN KEY (room_number) REFERENCES rooms(room_number)
  ON DELETE CASCADE ON UPDATE CASCADE;

-- FK: reservations → rooms
ALTER TABLE reservations ADD CONSTRAINT fk_reservations_room_number
  FOREIGN KEY (room_number) REFERENCES rooms(room_number)
  ON DELETE CASCADE ON UPDATE CASCADE;
```

### Indexes (Query Performance)
```sql
-- Performance indexes on foreign keys
CREATE INDEX idx_checkins_room_number ON checkins(room_number);
CREATE INDEX idx_checkins_user_username ON checkins(user_username);
CREATE INDEX idx_schedules_professor_username ON schedules(professor_username);
CREATE INDEX idx_schedules_room_number ON schedules(room_number);
CREATE INDEX idx_reservations_professor_username ON reservations(professor_username);
CREATE INDEX idx_reservations_room_number ON reservations(room_number);
CREATE INDEX idx_reservations_responded_by_username ON reservations(responded_by_username);
CREATE INDEX idx_rooms_occupied_by_username ON rooms(occupied_by_username);
CREATE INDEX idx_notifications_user_username ON notifications(user_username);
```

---

## Data Types Reference

### MySQL Data Types Used

| Type | Size | Range | Usage |
|------|------|-------|-------|
| VARCHAR(n) | n+1 bytes | 0-65,535 chars | Usernames, IDs, titles |
| INT | 4 bytes | -2B to +2B | Room numbers, schema version |
| TINYINT UNSIGNED | 1 byte | 0-255 | Floor numbers, time components |
| DATETIME | 8 bytes | 1000-9999 | Precise timestamps |
| DATE | 3 bytes | 1000-9999 | Date-only storage |
| TIMESTAMP | 4 bytes | 1970-2038 | Auto-tracking (deprecated for future) |
| ENUM | 2 bytes | Fixed values | Roles, statuses, periods |
| TEXT | Var | 0-65KB | Messages, reasons |
| JSON | Var | Flexible | Metadata storage |
| TINYINT(1) | 1 byte | 0-1 | Boolean-like (read status) |

---

## Summary

| Aspect | Details |
|--------|---------|
| **Total Tables** | 7 |
| **Total Views** | 1 |
| **Total Fields** | 52 |
| **Primary Keys** | 7 |
| **Foreign Keys** | 3 (explicit) + 6 (implicit) |
| **Indexes** | 9 |
| **Character Set** | UTF8MB4 |
| **Collation** | utf8mb4_unicode_ci |
| **Engine** | InnoDB |
| **Normalization** | 3NF/BCNF ✅ |

---

**Last Updated**: May 14, 2026  
**Version**: 2.0 (with comprehensive data dictionary)  
**Status**: ✅ Complete & Production-Ready
