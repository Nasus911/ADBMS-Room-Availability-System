import tkinter as tk
from tkinter import ttk

class AppShell:
    """Lightweight sidebar + content + status bar shell.
    Non-invasive: callers place their existing widgets inside `content`.
    """
    def __init__(self, root, colors):
        self.root = root
        self.colors = colors
        self.container = None
        self.sidebar = None
        self.content = None
        self.status = None

    def mount(self):
        # Main container under the root
        self.container = tk.Frame(self.root, bg=self.colors["background"])
        self.container.pack(fill="both", expand=True)

        # Horizontal split: left sidebar, right content
        body = tk.Frame(self.container, bg=self.colors["background"]) 
        body.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(body, width=240, bg=self.colors["card"], highlightthickness=0, bd=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg=self.colors["background"]) 
        self.content.pack(side="left", fill="both", expand=True)

        # Status bar pinned to bottom
        self.status = tk.Frame(self.container, height=28, bg=self.colors["background"]) 
        self.status.pack(fill="x", side="bottom")
        self.status.pack_propagate(False)

        # Left: status text
        self.status_label = tk.Label(self.status, text="Ready", bg=self.colors["background"], 
                                     fg="#666666", font=("Arial", 9))
        self.status_label.pack(side="left", padx=8)

        # Right: theme toggle
        self.theme_label = tk.Label(self.status, text="Theme: Light", bg=self.colors["background"],
                                    fg=self.colors["primary"], font=("Arial", 9, "underline"),
                                    cursor="hand2")
        self.theme_label.pack(side="right", padx=8)

        return self

    def set_status(self, text: str):
        if self.status_label:
            self.status_label.configure(text=text)
    
    def bind_theme_toggle(self, callback):
        """Bind a callback to the theme toggle label."""
        if self.theme_label:
            self.theme_label.bind("<Button-1>", lambda e: callback())
