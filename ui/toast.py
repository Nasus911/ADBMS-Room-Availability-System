import tkinter as tk

class Toast:
    """Non-blocking toast notification that auto-dismisses."""
    def __init__(self, parent, message, duration=2000, bg="#333333", fg="white"):
        self.parent = parent
        self.top = tk.Toplevel(parent)
        self.top.overrideredirect(True)
        self.top.attributes("-topmost", True)
        
        # Message label
        label = tk.Label(self.top, text=message, bg=bg, fg=fg, 
                        font=("Arial", 10), padx=16, pady=8)
        label.pack()
        
        # Position at bottom center
        self.top.update_idletasks()
        w = self.top.winfo_width()
        h = self.top.winfo_height()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        x = parent_x + (parent_w // 2) - (w // 2)
        y = parent_y + parent_h - h - 60
        self.top.geometry(f"+{x}+{y}")
        
        # Auto dismiss
        self.top.after(duration, self.dismiss)
    
    def dismiss(self):
        try:
            self.top.destroy()
        except:
            pass

def show_toast(parent, message, duration=2000):
    """Show a non-blocking toast message."""
    Toast(parent, message, duration)
