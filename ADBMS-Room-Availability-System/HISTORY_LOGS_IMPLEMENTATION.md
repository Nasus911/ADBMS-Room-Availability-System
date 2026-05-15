# History Logs Implementation Guide

## Quick Start

The History Logs feature has been fully implemented in your ADBMS Room Availability System. Follow these steps to deploy and test it.

## Pre-Deployment Checklist

Before going live, ensure you have:
- [ ] Database backup
- [ ] MySQL 5.7 or higher
- [ ] PHP 7.4 or higher
- [ ] Read/write access to database

## Deployment Steps

### Step 1: Verify Database Migration

The system uses automatic migrations. When you refresh the application, it will automatically:
1. Check if migrations have been applied
2. Execute any pending migrations
3. Create the `activity_logs` table

**Manual verification** (optional):
```bash
# SSH or direct MySQL access
mysql -u root room_db
SELECT COUNT(*) FROM activity_logs;
```

Should return `0` initially (empty table).

### Step 2: Log in to Application

1. Navigate to your ADBMS application
2. Log in as admin (default: username `admin`, password `admin123`)
3. The system will run migrations automatically

### Step 3: Access History Logs

1. Click on "📋 History Logs" in the admin sidebar
2. You should see an empty history table initially
3. Try performing an action (create a user, update a room, etc.)
4. Refresh the History Logs page
5. Your action should appear in the logs

### Step 4: Test Features

#### Test 1: Create a New User
1. Go to "Manage Users"
2. Create a new user account
3. Go to History Logs
4. Filter by Action Type = "CREATE"
5. You should see the user creation logged

**Expected Result**:
- Action Type: CREATE
- Affected Table: users
- Changes show the new user data

#### Test 2: Update a User
1. Go to "Manage Users"
2. Edit an existing user (change role or status)
3. Go to History Logs
4. Filter by Action Type = "UPDATE"
5. Click "View" to see the changes

**Expected Result**:
- Action Type: UPDATE
- Changes show old and new values
- Only modified fields appear in changes_json

#### Test 3: Room Status Change
1. On the student or professor dashboard
2. Change a room's status (if available)
3. Go to History Logs
4. Filter by Affected Table = "rooms"
5. The status change should be logged

#### Test 4: Reservation Approval
1. Create a reservation request (if available)
2. Approve or reject it from admin panel
3. Go to History Logs
4. Filter by Action Type = "APPROVE" or "REJECT"
5. The approval/rejection should be logged

#### Test 5: Filtering and Search
1. Go to History Logs
2. Set Date Range to today
3. Select Action Type = "CREATE"
4. Click "Filter"
5. Results should be narrowed down

#### Test 6: Export
1. Apply some filters in History Logs
2. Click "Export" button
3. CSV file should download
4. Open the file to verify data

## File Changes Summary

### Files Created

1. **migrations/0002_activity_logs.sql**
   - Database migration file for creating activity_logs table
   - Runs automatically on first application load
   - Versioned for safe deployment

2. **HISTORY_LOGS_FEATURE.md**
   - Complete feature documentation
   - User guide for History Logs dashboard
   - Troubleshooting and best practices

### Files Modified

1. **adbms_schema.sql**
   - Added activity_logs table definition
   - Ensures table structure is correct

2. **db.php**
   - Added `adbms_get_client_ip()`: Extracts client IP address
   - Added `adbms_log_activity()`: Core logging function
   - Added `adbms_fetch_activity_logs()`: Retrieves logs with filtering
   - Added `adbms_get_activity_logs_count()`: Gets total log count
   - Modified `adbms_ensure_schema()`: Creates activity_logs table
   - Modified `adbms_drop_schema()`: Drops activity_logs table
   - Modified `adbms_authenticate()`: Logs login events
   - Modified `adbms_sync_users()`: Logs user create/update
   - Modified `adbms_sync_rooms()`: Logs room create/update
   - Modified `adbms_sync_checkins()`: Logs check-in create/update
   - Modified `adbms_sync_schedules()`: Logs schedule create/update
   - Modified `adbms_sync_reservations()`: Logs reservation create/update/approve/reject
   - Modified `adbms_sync_notifications()`: Logs notification create/update

3. **api.php**
   - Added handler for `activity_logs` entity
   - Supports GET requests with filtering parameters
   - Returns paginated results

4. **index.html**
   - Added "📋 History Logs" admin sidebar navigation item
   - Added History Logs admin view section (#adminViewHistory)
   - Added filter controls (date range, action type, table, search)
   - Added history table with 7 columns
   - Added pagination controls
   - Added details modal for expanded view
   - Added JavaScript functions for loading, filtering, and exporting logs
   - Added event listeners for all UI interactions

## Data Model

### activity_logs Table Structure

```
log_id          VARCHAR(80)     PRIMARY KEY, UNIQUE identifier
user_id         VARCHAR(64)     User who performed action
user_role       ENUM(...)       User's role at time of action
affected_table  VARCHAR(64)     Table being modified
affected_record_id VARCHAR(255) ID of record being modified
action_type     ENUM(...)       Type of action (CREATE, UPDATE, DELETE, LOGIN, etc.)
description     TEXT            Human-readable description
old_value       LONGTEXT        Previous values (JSON format)
new_value       LONGTEXT        New values (JSON format)
changes_json    JSON            Field-level changes only
ip_address      VARCHAR(45)     IP address of actor
created_at      TIMESTAMP       When logged
```

### Indexes for Performance

```
PRIMARY KEY (log_id)
KEY idx_logs_user_id (user_id)
KEY idx_logs_affected_table (affected_table)
KEY idx_logs_affected_record_id (affected_record_id)
KEY idx_logs_action_type (action_type)
KEY idx_logs_created_at (created_at)
KEY idx_logs_user_action_time (user_id, action_type, created_at)
```

## API Endpoints

### Get Activity Logs

**URL**: `/api.php?entity=activity_logs&action=list`
**Method**: GET
**Authentication**: Requires logged-in user (admin)

**Query Parameters**:
```
limit=20              (default: 100)
offset=0              (default: 0)
user_id=admin         (optional)
action_type=CREATE    (optional)
affected_table=users  (optional)
date_from=2024-01-01  (optional)
date_to=2024-12-31    (optional)
search=room_123       (optional)
```

**Response Success**:
```json
{
  "success": true,
  "items": [
    {
      "log_id": "log_...",
      "user_id": "admin",
      "user_role": "Admin",
      "affected_table": "users",
      "affected_record_id": "newuser",
      "action_type": "CREATE",
      "description": "User created",
      "oldValue": null,
      "newValue": {...},
      "changes": {...},
      "ip_address": "127.0.0.1",
      "createdAt": "2024-03-15T10:30:45"
    }
  ],
  "total": 156,
  "limit": 20,
  "offset": 0,
  "hasMore": true
}
```

## Logging Behavior

### Automatic Logging

Every time a CRUD operation happens:
1. Before executing the operation, current data is fetched
2. Operation is executed
3. New/changed data is logged with before/after comparison
4. If logging fails, main operation still succeeds (non-blocking)

### Action Types Logged

- **CREATE**: New record created
- **UPDATE**: Existing record modified
- **DELETE**: Record deleted (via adbms_delete_missing)
- **LOGIN**: User login attempt (success/failure)
- **LOGOUT**: User logout
- **APPROVE**: Request approved
- **REJECT**: Request rejected
- **ASSIGN**: Assignment made
- **REASSIGN**: Assignment changed
- **READ**: Record accessed (optional, currently only for logs)

### Fields Captured

For UPDATE operations:
```json
{
  "changes": {
    "status": {
      "old": "available",
      "new": "occupied"
    },
    "occupied_by_username": {
      "old": null,
      "new": "psantos"
    }
  }
}
```

Only fields that actually changed are included in `changes_json`.

## Performance Impact

### Minimal Overhead

- Logging is implemented to not block operations
- Try-catch prevents logging errors from affecting main functionality
- Indexes are optimized for query performance
- Pagination prevents loading massive result sets

### Database Growth

With typical usage, expect:
- ~5-10 KB per log entry
- 1000 operations/day = ~5-10 MB/month
- Plan for 1-2 GB per year with normal usage

### Maintenance

Archive old logs quarterly:
```sql
-- Export logs older than 90 days
SELECT * FROM activity_logs 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY)
INTO OUTFILE '/tmp/activity_logs_archive.csv' 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';

-- Delete archived logs
DELETE FROM activity_logs 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

## Troubleshooting

### Issue: "No logs appear"

**Diagnosis**:
1. Check table exists: `SELECT 1 FROM information_schema.tables WHERE table_name = 'activity_logs';`
2. Perform an action and check: `SELECT COUNT(*) FROM activity_logs;`
3. Check browser console for JavaScript errors (F12)

**Solution**:
1. Ensure migrations ran: Check `migrations` table
2. Verify table schema: `DESC activity_logs;`
3. Clear browser cache and refresh
4. Check PHP error log for logging failures

### Issue: "Export doesn't work"

**Diagnosis**:
1. Test that logs are visible in table
2. Check browser developer console Network tab
3. Verify CSV is actually being generated

**Solution**:
1. Try with fewer filters
2. Check browser download settings
3. Try exporting from different browser
4. Check PHP memory limit if exporting many records

### Issue: "Slow performance"

**Diagnosis**:
1. Check table size: `SELECT COUNT(*) FROM activity_logs;`
2. Check for long-running queries: `SHOW PROCESSLIST;`
3. Verify indexes exist: `SHOW INDEX FROM activity_logs;`

**Solution**:
1. Archive and delete old logs
2. Add more specific filters before querying
3. Increase PHP/MySQL timeout values if needed
4. Consider partitioning if table grows very large

## Rollback Plan

If you need to remove the History Logs feature:

1. **Drop the table** (loses all logs):
   ```sql
   DROP TABLE activity_logs;
   ```

2. **Revert code changes**:
   - Restore original `db.php` (removes logging calls)
   - Restore original `index.html` (removes UI)
   - Restore original `api.php` (removes endpoint)

3. **Delete migration file**:
   - Remove `migrations/0002_activity_logs.sql`
   - Update `migrations` table if needed

Note: The system is designed to work with or without the History Logs table. Removing it will simply stop logging.

## Next Steps

1. **Test thoroughly** using the test cases above
2. **Monitor performance** for the first week
3. **Review logs regularly** for suspicious activity
4. **Archive old logs** monthly
5. **Document policies** for log retention
6. **Establish procedures** for investigating issues using logs

## Support & Documentation

- See `HISTORY_LOGS_FEATURE.md` for complete user documentation
- Review database schema in `adbms_schema.sql`
- Check migration in `migrations/0002_activity_logs.sql`
- API endpoints documented in `api.php`
- JavaScript code in `index.html` starting with "HISTORY LOGS FUNCTIONALITY"

## Version Info

- **Feature**: History Logs / Activity Audit Trail v1.0
- **Release Date**: 2024
- **Database**: MySQL 5.7+
- **PHP**: 7.4+
- **Browser Support**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

---

**Implementation Complete!** Your system now has comprehensive activity logging and audit trail capabilities.
