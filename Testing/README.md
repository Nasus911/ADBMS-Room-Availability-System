# Simple To-Do List (PyQt)

This is a beginner-friendly Python To-Do List application now implemented with PyQt5.

Features:
- Add tasks
- Delete tasks
- Mark tasks as completed (via checkbox or the "Mark Completed" button)
- Tasks persist between sessions in `tasks.json`

Install requirements:

```powershell
python -m pip install -r requirements.txt
```

Run:

```powershell
python todo_app.py
```

Notes:
- The app creates `tasks.json` in the same folder when you add/save tasks.
- Tested with Python 3.8+ and PyQt5.
