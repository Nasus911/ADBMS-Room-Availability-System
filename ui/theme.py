from tkinter import ttk

DEFAULT_LIGHT = {
    "primary": "#FF6B35",
    "secondary": "#F7931E",
    "accent": "#003049",
    "background": "#f8f9fa",
    "card": "#ffffff",
    "success": "#2ECC71",
    "danger": "#E74C3C",
    "warning": "#F1C40F",
}

DEFAULT_DARK = {
    "primary": "#FF6B35",
    "secondary": "#F7931E",
    "accent": "#E0E6ED",
    "background": "#1E1E1E",
    "card": "#2A2A2A",
    "success": "#27AE60",
    "danger": "#C0392B",
    "warning": "#D4AC0D",
}

_current_theme = "light"

def get_current_theme():
    return _current_theme

def toggle_theme():
    global _current_theme
    _current_theme = "dark" if _current_theme == "light" else "light"
    return _current_theme, DEFAULT_DARK if _current_theme == "dark" else DEFAULT_LIGHT


def apply_theme(style: ttk.Style, colors: dict):
    """Apply ttk styles using the provided color tokens.
    Keeps naming compatible with existing code. Safe to call anytime.
    """
    style.theme_use('clam')
    style.configure('Header.TLabel', background=colors["primary"], foreground='white', font=('Arial', 16, 'bold'))
    style.configure('Category.TButton', background=colors["card"], foreground=colors["accent"], font=('Arial', 10, 'bold'))
    style.map('Category.TButton', background=[('active', colors["secondary"])], foreground=[('active', 'white')])
    style.configure('AddButton.TButton', background=colors["primary"], foreground='white', font=('Arial', 10, 'bold'))
    style.map('AddButton.TButton', background=[('active', colors["secondary"])])
    style.configure('Total.TLabel', background=colors["background"], foreground=colors["accent"], font=('Arial', 14, 'bold'))
