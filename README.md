# ADBMS Room Availability System

Web-based system for managing room check-ins with login-first flow and role-based dashboards.

## Features

- Login panel with account authentication
- Admin dashboard with room controls and user management
- Professor dashboard with check-in/check-out actions
- Student dashboard with live room status view
- Add user flow with password confirmation and password visibility toggle
- User activation and deactivation controls for admin

## Run

Because this workspace is static HTML/CSS/JS, no build step is required.

1. Open `index.html` in your browser.
2. Or run with a local static server if preferred.

## Demo Accounts

- Admin: `admin / admin123`
- Professor: `psantos / prof123`
- Student: `jdc / student123`

## Interaction Notes

- Users start from login and are redirected to their assigned dashboard by role.
- Admin `Check In` and `Force Release` buttons update room status live.
- Professor can check in to an available room and check out from their occupied room.
- Student view updates occupied/available status in real time.
- Admin can add users, deactivate users, and reactivate users from Manage Users.
- Inactive accounts cannot log in.
