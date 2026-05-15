# History Logs Feature Documentation

## Overview

The History Logs feature provides a comprehensive audit trail for your ADBMS Room Availability System. It automatically tracks all CRUD operations (Create, Read, Update, Delete), user activities, and administrative actions throughout the system, enabling you to monitor changes, maintain accountability, and investigate issues.

## Features

### 1. Automatic Activity Tracking

All important operations are automatically logged:
- **User Management**: Create, update, or modify user accounts
- **Room Management**: Add, update room information, track status changes
- **Schedules**: Create, update, or cancel professor schedules
- **Reservations**: Track all reservation requests, approvals, and rejections
- **Check-ins**: Log professor check-in activities
- **Notifications**: Track notification creation and status changes
- **Authentication**: Log all login/logout attempts with success/failure status

### 2. Field-Level Change Tracking

For UPDATE operations, the system captures:
- **Old Value**: Previous field values
- **New Value**: Updated field values
- **Changes JSON**: A structured JSON showing only the modified fields

Example:
```
Field: status
Old Value: "available"
New Value: "occupied"

Field: occupied_by_username
Old Value: null
New Value: "psantos"
```

### 3. Security & Accountability

Each log entry includes:
- **Timestamp**: Exact date and time of the operation
- **User/Actor**: Who performed the action
- **User Role**: Their role (Admin, Professor, Student)
- **IP Address**: Source IP for security auditing
- **Action Type**: CREATE, UPDATE, DELETE, LOGIN, LOGOUT, APPROVE, REJECT, etc.
- **Description**: Human-readable summary of the action

### 4. Advanced Filtering & Search

Find specific activities quickly:
- **Date Range**: Filter logs between two dates
- **Action Type**: Filter by specific action (CREATE, UPDATE, etc.)
- **Affected Table**: Filter by entity type (users, rooms, schedules, etc.)
- **Search**: Full-text search on record IDs and descriptions
- **Pagination**: Navigate through large datasets efficiently

### 5. Data Export

Export filtered activity logs as CSV for:
- Compliance reports
- External audits
- Data analysis
- Archive and retention

## Accessing History Logs

### For Administrators

1. Log in to your admin account
2. In the admin dashboard, click "📋 History Logs" in the sidebar
3. View all activity logs for the system
4. Use filters to narrow down results
5. Click "View" to see detailed information about a specific action
6. Click "Export" to download filtered logs as CSV

### Role-Based Access

- **Admins**: Full access to all history logs for the entire system
- **Professors**: Cannot access (system for admins only)
- **Students**: Cannot access (system for admins only)

## Using the History Logs Dashboard

### Filter Controls

**Date Range**
- Select start date and end date
- Logs are filtered to show only activities within this range
- Leave blank to include all dates

**Action Type**
- CREATE: New record created
- UPDATE: Existing record modified
- DELETE: Record deleted
- LOGIN: User login attempt
- LOGOUT: User logout
- APPROVE: Reservation/request approved
- REJECT: Reservation/request rejected
- ASSIGN: Room assigned to professor
- REASSIGN: Assignment changed
- READ: Record accessed (audit trail)

**Affected Table**
- users: User management operations
- rooms: Room management operations
- schedules: Professor schedule operations
- reservations: Room reservation requests
- checkins: Professor check-in records
- notifications: System notifications

**Search**
- Enter record ID, description, or user ID
- Searches across multiple fields
- Partial matches are supported

### Action Buttons

**Filter**: Apply current filter criteria
- Results update immediately
- Pagination resets to page 1

**Export**: Download filtered results as CSV
- Exports up to 5000 records per request
- Includes all visible columns
- Formatted for import into Excel/Sheets

### Navigation

**Previous/Next Buttons**
- Navigate between pages of results
- Current page and total count displayed
- Shows total number of matching records

**View Button (in each row)**
- Open detailed view modal
- See full timestamp and IP address
- View field-level changes for UPDATE operations
- Close modal with X or click outside

## Common Use Cases

### 1. Audit Trail for Compliance

Track all modifications to critical records:
1. Set Date Range to your audit period
2. Leave other filters blank
3. Export the results
4. Submit to compliance team

### 2. Investigate Unauthorized Changes

Find who modified a specific record:
1. Set Affected Table to the relevant entity (e.g., "users")
2. Use Search to find the record ID
3. Review the changes and who made them
4. Check timestamp and IP address for verification

### 3. Track User Activity

Monitor specific admin activities:
1. Filter by Action Type (e.g., "DELETE")
2. View all deletion activities
3. Click each entry to see what was deleted
4. Identify patterns or concerning activities

### 4. Prepare Reports

Generate activity reports for management:
1. Set desired Date Range
2. Filter by Action Type if needed
3. Click Export
4. Open CSV in spreadsheet application
5. Create charts or summaries as needed

### 5. Troubleshoot Issues

Find when something went wrong:
1. Set Date Range to time of issue
2. Filter by Affected Table related to the problem
3. Look for UPDATE or DELETE operations
4. Review the changes to identify the issue

## Database Schema

The `activity_logs` table structure:

```sql
CREATE TABLE activity_logs (
    log_id VARCHAR(80) NOT NULL,          -- Unique log identifier
    user_id VARCHAR(64),                  -- User who performed the action
    user_role ENUM(...),                  -- User's role at time of action
    affected_table VARCHAR(64),           -- Table being modified
    affected_record_id VARCHAR(255),      -- ID of record being modified
    action_type ENUM(...),                -- Type of action
    description TEXT,                     -- Human-readable description
    old_value LONGTEXT,                   -- Previous values (JSON)
    new_value LONGTEXT,                   -- New values (JSON)
    changes_json JSON,                    -- Field-level changes
    ip_address VARCHAR(45),               -- IP address of actor
    created_at TIMESTAMP,                 -- When logged
    PRIMARY KEY (log_id),
    KEY idx_logs_user_id (user_id),
    KEY idx_logs_affected_table (affected_table),
    KEY idx_logs_action_type (action_type),
    KEY idx_logs_created_at (created_at),
    KEY idx_logs_user_action_time (user_id, action_type, created_at)
);
```

## Performance Considerations

### Logging Doesn't Slow Down Operations

- Logging is implemented as non-blocking background operations
- If logging fails, the main operation continues
- Indexes optimize queries for log retrieval
- Large log tables are handled efficiently with pagination

### Regular Maintenance

For optimal performance with large log tables:
1. **Archive Old Logs**: Export and backup logs older than 90 days
2. **Delete Archive**: Remove archived logs from the database
3. **Monitor Size**: Keep growth under control

Example cleanup query (removes logs older than 1 year):
```sql
DELETE FROM activity_logs 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

## API Reference

### Get Activity Logs

**Endpoint**: `/api.php?entity=activity_logs&action=list`

**Parameters** (GET):
- `limit` (default: 100): Records per page
- `offset` (default: 0): Starting position
- `user_id`: Filter by user
- `action_type`: Filter by action
- `affected_table`: Filter by table
- `date_from`: Start date (YYYY-MM-DD)
- `date_to`: End date (YYYY-MM-DD)
- `search`: Search term

**Response**:
```json
{
  "success": true,
  "items": [
    {
      "log_id": "log_abc123...",
      "user_id": "psantos",
      "user_role": "Professor",
      "affected_table": "rooms",
      "affected_record_id": "407",
      "action_type": "UPDATE",
      "description": "Room status updated",
      "oldValue": { "status": "available" },
      "newValue": { "status": "occupied" },
      "changes": {
        "status": {
          "old": "available",
          "new": "occupied"
        }
      },
      "ip_address": "192.168.1.100",
      "createdAt": "2024-03-15T14:30:45"
    }
  ],
  "total": 156,
  "limit": 100,
  "offset": 0,
  "hasMore": true
}
```

## Troubleshooting

### No logs appear in History Logs

**Problem**: Dashboard shows no activity logs

**Solutions**:
1. Verify `activity_logs` table exists: `SELECT * FROM activity_logs LIMIT 1;`
2. Perform an action (e.g., create a user) and check if new logs appear
3. Clear all filters and click "Filter" to see all logs
4. Check browser console for JavaScript errors

### Export button doesn't work

**Problem**: CSV export fails or nothing downloads

**Solutions**:
1. Check that logs are visible in the table (filter is working)
2. Ensure browser allows downloads from localhost
3. Check browser developer console for network errors
4. Try with fewer filters first

### Performance is slow

**Problem**: Filtering or pagination is slow

**Solutions**:
1. Reduce date range
2. Add more specific filters
3. Check database for locks: `SHOW PROCESSLIST;`
4. Monitor table size: `SELECT COUNT(*) FROM activity_logs;`
5. Archive and delete old logs if table is very large

## Best Practices

### 1. Regular Review

- Review activity logs weekly
- Look for unusual patterns
- Investigate deletions and major updates

### 2. Archive Logs Regularly

- Export logs monthly for archive
- Delete logs older than your retention policy
- Keep at least 90 days of active logs

### 3. Monitor Admin Activity

- Keep close watch on admin deletions
- Track user account modifications
- Review high-risk operations (approvals, rejections)

### 4. Use for Compliance

- Maintain audit trails for regulatory requirements
- Document investigation findings in log exports
- Establish retention policies for log data

### 5. Security

- Limit access to History Logs (admin only)
- Regular audits of your own admin actions
- Review IP addresses for unauthorized access attempts

## FAQ

**Q: Are all operations logged?**
A: Yes, all CRUD operations are automatically logged. There's no manual action needed.

**Q: Can logs be edited or deleted?**
A: Activity logs should be treated as immutable audit records. Direct deletion is possible but not recommended. Use archival process instead.

**Q: How far back do logs go?**
A: Logs are stored indefinitely unless manually archived or deleted. You can set retention policies as needed.

**Q: Can I export just specific users' activity?**
A: Yes, you would need to modify the API call or manually filter the CSV after export. Future versions may add this feature.

**Q: Does logging affect system performance?**
A: No, logging is implemented to have minimal impact. If logging fails, the main operation continues normally.

**Q: Can students or professors see activity logs?**
A: No, the History Logs feature is restricted to administrators only.

## Support

If you encounter issues with the History Logs feature:

1. Check the troubleshooting section above
2. Review the browser console for errors (F12)
3. Check server error logs in Apache/PHP logs
4. Verify database table exists: `DESC activity_logs;`
5. Verify API endpoint works: Access `/api.php?entity=activity_logs&action=list` directly

## Version Information

- **Feature**: History Logs / Activity Audit Trail
- **Version**: 1.0
- **Database**: MySQL 5.7+
- **PHP**: 7.4+
- **Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
