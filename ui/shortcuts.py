import tkinter as tk

def bind_global_shortcuts(app):
    root = app.root

    # Ctrl+N: new/clear order
    def _new_order(event=None):
        try:
            app.clear_order()
            return "break"
        except Exception:
            return None
    root.bind_all("<Control-n>", _new_order)

    # Ctrl+F: focus search entry
    def _focus_search(event=None):
        try:
            if getattr(app, "search_entry", None):
                app.search_entry.focus_set()
                app.search_entry.select_range(0, 'end')
                return "break"
        except Exception:
            pass
        return None
    root.bind_all("<Control-f>", _focus_search)

    # Delete: attempt remove (uses existing message flow)
    def _delete(event=None):
        try:
            app.remove_from_cart()
            return "break"
        except Exception:
            return None
    root.bind_all("<Delete>", _delete)

    # Esc: close top-most Toplevel if any
    def _esc_close(event=None):
        # Find any toplevel other than root and destroy
        try:
            for w in root.winfo_children():
                if isinstance(w, tk.Toplevel):
                    w.destroy()
                    return "break"
        except Exception:
            pass
        return None
    root.bind_all("<Escape>", _esc_close)

    # Enter submits focused button or default widget (let Tk handle by default)
    # No explicit binding to avoid overriding built-in behavior.
