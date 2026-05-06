import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QCheckBox, QLabel, QFrame, QSizePolicy, QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal

TASKS_FILE = "tasks.json"


class TaskWidget(QWidget):
    toggled = pyqtSignal(bool)
    delete_requested = pyqtSignal()

    def __init__(self, title: str, completed: bool = False, category: str = ""):
        super().__init__()
        h = QHBoxLayout()
        h.setContentsMargins(6, 6, 6, 6)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(bool(completed))
        self.checkbox.stateChanged.connect(lambda s: self.toggled.emit(s == Qt.Checked))
        h.addWidget(self.checkbox)

        v = QVBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        if completed:
            self.title_label.setStyleSheet("color:gray; text-decoration: line-through;")
        v.addWidget(self.title_label)

        self.category_label = QLabel(category)
        self.category_label.setStyleSheet("color:#1976D2; font-size:10px; margin-top:2px;")
        v.addWidget(self.category_label)

        h.addLayout(v)
        h.addStretch()

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("background:#e53935; color:white; padding:4px 8px;")
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit())
        h.addWidget(self.delete_btn)

        self.setLayout(h)

    def set_completed_style(self, completed: bool):
        if completed:
            self.title_label.setStyleSheet("color:gray; text-decoration: line-through;")
        else:
            self.title_label.setStyleSheet("")


class TodoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple To-Do List")
        self.setFixedSize(520, 480)

        self.tasks = []
        self.load_tasks()

        main = QVBoxLayout()

        # Header: Today + date
        header_h = QHBoxLayout()
        today_label = QLabel("Today")
        today_label.setStyleSheet("font-weight:700; font-size:20px;")
        date_str = datetime.now().strftime('%d %b')
        date_label = QLabel(date_str)
        date_label.setStyleSheet("color:gray; margin-left:8px;")
        header_h.addWidget(today_label)
        header_h.addWidget(date_label)
        header_h.addStretch()
        main.addLayout(header_h)

        # Top: entry + add button
        top_h = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Add a new task...")
        self.entry.returnPressed.connect(self.add_task)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_task)
        top_h.addWidget(self.entry)
        top_h.addWidget(add_btn)
        main.addLayout(top_h)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(6)
        main.addWidget(self.list_widget)

        # Bottom actions
        bottom_h = QHBoxLayout()
        mark_btn = QPushButton("Mark Completed")
        mark_btn.clicked.connect(self.mark_completed)
        del_btn = QPushButton("Delete Task")
        del_btn.clicked.connect(self.delete_task)
        bottom_h.addWidget(mark_btn)
        bottom_h.addWidget(del_btn)
        bottom_h.addStretch()
        main.addLayout(bottom_h)

        self.setLayout(main)

        # Floating add button (also available)
        self.fab = QPushButton('+', self)
        self.fab.setToolTip('Add task')
        self.fab.setFixedSize(48, 48)
        self.fab.setStyleSheet('border-radius:24px; background:#333; color:white; font-size:20px;')
        self.fab.clicked.connect(self.add_task_dialog)

        self.refresh_list()

    def showEvent(self, event):
        # position floating button bottom-right
        self.fab.move(self.width() - 70, self.height() - 90)
        super().showEvent(event)

    def load_tasks(self):
        if not os.path.exists(TASKS_FILE):
            self.tasks = []
            return
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                self.tasks = json.load(f)
        except Exception:
            QMessageBox.warning(self, "Load Error", "Could not read tasks.json; starting with empty list.")
            self.tasks = []

    def save_tasks(self):
        try:
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
        except Exception:
            QMessageBox.critical(self, "Save Error", "Could not save tasks to tasks.json.")

    def refresh_list(self):
        self.list_widget.clear()
        for t in self.tasks:
            item = QListWidgetItem()
            widget = TaskWidget(t.get('title', ''), t.get('completed', False), t.get('category', ''))
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            # wire signals
            widget.toggled.connect(lambda checked, it=item: self.on_widget_toggled(it, checked))
            widget.delete_requested.connect(lambda it=item: self.delete_item_by_item(it))

    def add_task(self):
        title = self.entry.text().strip()
        if not title:
            return
        self.tasks.append({"title": title, "completed": False, "category": ""})
        self.entry.clear()
        self.refresh_list()
        self.save_tasks()

    def add_task_dialog(self):
        title = self.entry.text().strip()
        if not title:
            title, ok = QInputDialog.getText(self, 'New Task', 'Task title:')
            if not ok or not title.strip():
                return
        category, ok2 = QInputDialog.getText(self, 'Category (optional)', 'Category:')
        if not ok2:
            category = ''
        self.tasks.append({"title": title.strip(), "completed": False, "category": category.strip()})
        self.entry.clear()
        self.refresh_list()
        self.save_tasks()

    def delete_task(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.information(self, "Delete Task", "Please select a task to delete.")
            return
        title = self.tasks[row]['title']
        reply = QMessageBox.question(self, "Delete", f"Delete task:\n\n{title}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.tasks.pop(row)
            self.refresh_list()
            self.save_tasks()

    def delete_item_by_item(self, item: QListWidgetItem):
        row = self.list_widget.row(item)
        if row < 0:
            return
        title = self.tasks[row]['title']
        reply = QMessageBox.question(self, "Delete", f"Delete task:\n\n{title}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.tasks.pop(row)
            self.refresh_list()
            self.save_tasks()

    def mark_completed(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.information(self, "Mark Completed", "Please select a task to mark completed.")
            return
        # mark completed and move to end
        self.tasks[row]['completed'] = True
        task = self.tasks.pop(row)
        self.tasks.append(task)
        self.refresh_list()
        self.save_tasks()

    def on_widget_toggled(self, item: QListWidgetItem, checked: bool):
        row = self.list_widget.row(item)
        if row < 0 or row >= len(self.tasks):
            return
        # if checked and not previously completed, mark and move to end
        if checked and not self.tasks[row].get('completed'):
            self.tasks[row]['completed'] = True
            task = self.tasks.pop(row)
            self.tasks.append(task)
            self.refresh_list()
            self.save_tasks()
        else:
            # just update completed flag
            self.tasks[row]['completed'] = bool(checked)
            self.save_tasks()

    def closeEvent(self, event):
        # rebuild tasks from widget states so order and categories persist
        new_tasks = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget is None:
                continue
            new_tasks.append({
                "title": widget.title_label.text(),
                "completed": widget.checkbox.isChecked(),
                "category": widget.category_label.text()
            })
        self.tasks = new_tasks
        self.save_tasks()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = TodoApp()
    win.show()
    sys.exit(app.exec_())
import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QCheckBox, QLabel, QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal

TASKS_FILE = "tasks.json"


class TaskWidget(QWidget):
    toggled = pyqtSignal(bool)
    delete_requested = pyqtSignal()

    def __init__(self, title: str, completed: bool = False, category: str = ""):
        super().__init__()
        h = QHBoxLayout()
        h.setContentsMargins(6, 6, 6, 6)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(bool(completed))
        self.checkbox.stateChanged.connect(lambda s: self.toggled.emit(s == Qt.Checked))
        h.addWidget(self.checkbox)

        v = QVBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        if completed:
            self.title_label.setStyleSheet("color:gray; text-decoration: line-through;")
        v.addWidget(self.title_label)

        self.category_label = QLabel(category)
        self.category_label.setStyleSheet("color:#1976D2; font-size:10px; margin-top:2px;")
        v.addWidget(self.category_label)

        h.addLayout(v)
        h.addStretch()

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("background:#e53935; color:white; padding:4px 8px;")
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit())
        h.addWidget(self.delete_btn)

        self.setLayout(h)

    def set_completed_style(self, completed: bool):
        if completed:
            self.title_label.setStyleSheet("color:gray; text-decoration: line-through;")
        else:
            self.title_label.setStyleSheet("")


class TodoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple To-Do List")
        self.setFixedSize(520, 480)

        self.tasks = []
        self.load_tasks()

        main = QVBoxLayout()

        # Header: Today + date
        header_h = QHBoxLayout()
        today_label = QLabel("Today")
        today_label.setStyleSheet("font-weight:700; font-size:20px;")
        date_str = datetime.now().strftime('%d %b')
        date_label = QLabel(date_str)
        date_label.setStyleSheet("color:gray; margin-left:8px;")
        header_h.addWidget(today_label)
        header_h.addWidget(date_label)
        header_h.addStretch()
        main.addLayout(header_h)

        # Top: entry + add button
        top_h = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Add a new task...")
        self.entry.returnPressed.connect(self.add_task)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_task)
        top_h.addWidget(self.entry)
        top_h.addWidget(add_btn)
        main.addLayout(top_h)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(6)
        main.addWidget(self.list_widget)

        # Bottom actions
        bottom_h = QHBoxLayout()
        mark_btn = QPushButton("Mark Completed")
        mark_btn.clicked.connect(self.mark_completed)
        del_btn = QPushButton("Delete Task")
        del_btn.clicked.connect(self.delete_task)
        bottom_h.addWidget(mark_btn)
        bottom_h.addWidget(del_btn)
        bottom_h.addStretch()
        main.addLayout(bottom_h)

        self.setLayout(main)

        # Floating add button (also available)
        self.fab = QPushButton('+', self)
        self.fab.setToolTip('Add task')
        self.fab.setFixedSize(48, 48)
        self.fab.setStyleSheet('border-radius:24px; background:#333; color:white; font-size:20px;')
        self.fab.clicked.connect(self.add_task_dialog)

        self.refresh_list()

    def showEvent(self, event):
        # position floating button bottom-right
        self.fab.move(self.width() - 70, self.height() - 90)
        super().showEvent(event)

    def load_tasks(self):
        if not os.path.exists(TASKS_FILE):
            self.tasks = []
            return
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                self.tasks = json.load(f)
        except Exception:
            QMessageBox.warning(self, "Load Error", "Could not read tasks.json; starting with empty list.")
            self.tasks = []

    def save_tasks(self):
        try:
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
        except Exception:
            QMessageBox.critical(self, "Save Error", "Could not save tasks to tasks.json.")

    def refresh_list(self):
        self.list_widget.clear()
        for t in self.tasks:
            item = QListWidgetItem()
            widget = TaskWidget(t.get('title', ''), t.get('completed', False), t.get('category', ''))
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            # wire signals
            widget.toggled.connect(lambda checked, it=item: self.on_widget_toggled(it, checked))
            widget.delete_requested.connect(lambda it=item: self.delete_item_by_item(it))

    def add_task(self):
        title = self.entry.text().strip()
        if not title:
            return
        self.tasks.append({"title": title, "completed": False, "category": ""})
        self.entry.clear()
        self.refresh_list()
        self.save_tasks()

    def add_task_dialog(self):
        title = self.entry.text().strip()
        if not title:
            title, ok = QInputDialog.getText(self, 'New Task', 'Task title:')
            if not ok or not title.strip():
                return
        category, ok2 = QInputDialog.getText(self, 'Category (optional)', 'Category:')
        if not ok2:
            category = ''
        self.tasks.append({"title": title.strip(), "completed": False, "category": category.strip()})
        self.entry.clear()
        self.refresh_list()
        self.save_tasks()

    def delete_task(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.information(self, "Delete Task", "Please select a task to delete.")
            return
        title = self.tasks[row]['title']
        reply = QMessageBox.question(self, "Delete", f"Delete task:\n\n{title}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.tasks.pop(row)
            self.refresh_list()
            self.save_tasks()

    def delete_item_by_item(self, item: QListWidgetItem):
        row = self.list_widget.row(item)
        if row < 0:
            return
        title = self.tasks[row]['title']
        reply = QMessageBox.question(self, "Delete", f"Delete task:\n\n{title}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.tasks.pop(row)
            self.refresh_list()
            self.save_tasks()

    def mark_completed(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.information(self, "Mark Completed", "Please select a task to mark completed.")
            return
        # mark completed and move to end
        self.tasks[row]['completed'] = True
        task = self.tasks.pop(row)
        self.tasks.append(task)
        self.refresh_list()
        self.save_tasks()

    def on_widget_toggled(self, item: QListWidgetItem, checked: bool):
        row = self.list_widget.row(item)
        if row < 0 or row >= len(self.tasks):
            return
        # if checked and not previously completed, mark and move to end
        if checked and not self.tasks[row].get('completed'):
            self.tasks[row]['completed'] = True
            task = self.tasks.pop(row)
            self.tasks.append(task)
            self.refresh_list()
            self.save_tasks()
        else:
            # just update completed flag
            self.tasks[row]['completed'] = bool(checked)
            self.save_tasks()

    def closeEvent(self, event):
        # rebuild tasks from widget states so order and categories persist
        new_tasks = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget is None:
                continue
            new_tasks.append({
                "title": widget.title_label.text(),
                "completed": widget.checkbox.isChecked(),
                "category": widget.category_label.text()
            })
        self.tasks = new_tasks
        self.save_tasks()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = TodoApp()
    win.show()
    sys.exit(app.exec_())
