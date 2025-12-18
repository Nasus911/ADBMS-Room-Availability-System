import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
import json
from datetime import datetime
import os
from pathlib import Path
from ui.shell import AppShell
from ui.shortcuts import bind_global_shortcuts
from ui.toast import show_toast
from ui.theme import toggle_theme, DEFAULT_LIGHT, DEFAULT_DARK, apply_theme

class MenuOrderingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("FastBite - Menu Ordering System")
        self.root.geometry("1200x800")
        # Make window fullscreen/zoomed on start (Windows-friendly)
        try:
            self.root.state('zoomed')
        except Exception:
            # Fallback to Tk fullscreen attribute
            try:
                self.root.attributes('-fullscreen', True)
            except Exception:
                pass
        
        # Define font system (Segoe UI for modern Windows look)
        self.fonts = {
            "heading_large": ("Segoe UI", 24, "bold"),     # Main titles
            "heading_medium": ("Segoe UI", 18, "bold"),    # Section headers
            "heading_small": ("Segoe UI", 16, "bold"),     # Card titles
            "subheading": ("Segoe UI", 14, "bold"),        # Subheadings
            "body_large": ("Segoe UI", 12),                # Primary text
            "body": ("Segoe UI", 11),                      # Body text
            "body_small": ("Segoe UI", 10),                # Small text
            "caption": ("Segoe UI", 10),                   # Labels, captions
            "link": ("Segoe UI", 10, "underline"),         # Clickable links
        }
        
        # Define color scheme
        self.colors = {
            "primary": "#FF6B35",      # Orange for buttons and highlights
            "secondary": "#F7931E",    # Light orange
            "accent": "#003049",       # Dark blue for text
            "background": "#f8f9fa",   # Light gray
            "card": "#ffffff",        # White for cards
            "success": "#2ECC71",     # Green for success
            "danger": "#E74C3C",      # Red for errors
            "warning": "#F1C40F",     # Yellow for warnings
        }
        
        # Initialize data
        self.menu_items = self.load_menu()
        # Quick lookup map for items by id
        try:
            self.item_by_id = {item.get("id"): item for item in self.menu_items}
        except Exception:
            self.item_by_id = {}
        self.order_items = []
        self.current_order_id = self.generate_order_id()
        self.customer_number = self.get_next_customer_number()
        
        # Customer delivery information
        self.customer_name = ""
        self.customer_address = ""
        self.customer_contact = ""
        
        # Create custom styles
        self.create_styles()

        # Create GUI components
        self.create_widgets()
        
    def load_menu(self):
        """Load menu items from a JSON file or create default menu"""
        default_menu = [
            {
                "id": 1, "name": "Classic Burger", "price": 69.00, "category": "Burgers",
                "description": "Juicy beef patty with lettuce, tomato, and special sauce",
                "calories": 650, "image": "Burger"
            },
            {
                "id": 13, "name": "Cheeseburger", "price": 79.00, "category": "Burgers",
                "description": "Beef patty topped with melted cheese, lettuce, and tomato",
                "calories": 720, "image": "Cheeseburger"
            },
            {
                "id": 14, "name": "Bacon Burger", "price": 99.00, "category": "Burgers",
                "description": "Beef patty with crispy bacon, lettuce, tomato, and mayo",
                "calories": 780, "image": "Bacon Burger"
            },
            {
                "id": 29, "name": "Double Patty Burger", "price": 119.00, "category": "Burgers",
                "description": "Two beef patties with lettuce, tomato, and special sauce",
                "calories": 950, "image": "Double Patty Burger"
            },
            {
                "id": 30, "name": "Double Cheese Burger", "price": 129.00, "category": "Burgers",
                "description": "Beef patty with double melted cheese, lettuce, and tomato",
                "calories": 820, "image": "Double Cheese Burger"
            },
            {
                "id": 2, "name": "Cheese Pizza", "price": 199.00, "category": "Pizza",
                "description": "Fresh mozzarella cheese on our signature tomato sauce",
                "calories": 850, "image": "Cheese Pizza"
            },
            {
                "id": 3, "name": "Garden Salad", "price": 49.00, "category": "Salads",
                "description": "Fresh greens with cherry tomatoes and vinaigrette",
                "calories": 320, "image": "Garden Salad"
            },
            {
                "id": 4, "name": "French Fries", "price": 39.00, "category": "Sides",
                "description": "Crispy golden fries with sea salt",
                "calories": 365, "image": "Fries"
            },
            {
                "id": 5, "name": "Coca Cola", "price": 25.00, "category": "Beverages",
                "description": "Refreshing classic cola",
                "calories": 150, "image": "Coca Cola"
            },
            {
                "id": 6, "name": "Chocolate Sundae", "price": 39.00, "category": "Desserts",
                "description": "Rich chocolate ice cream with hot fudge and whipped cream",
                "calories": 420, "image": "Choco Sundae"
            },
            {
                "id": 15, "name": "Milkshake", "price": 59.00, "category": "Desserts",
                "description": "Creamy vanilla milkshake topped with whipped cream",
                "calories": 500, "image": "Milkshake"
            },
            {
                "id": 16, "name": "Ice Cream", "price": 25.00, "category": "Desserts",
                "description": "Two scoops of classic vanilla ice cream",
                "calories": 380, "image": "Ice Cream"
            },
            {
                "id": 7, "name": "Spaghetti", "price": 59.00, "category": "Pasta",
                "description": "Traditional spaghetti with sauce and parmesan",
                "calories": 680, "image": "Spaghetti Bolognese"
            },
            # Appetizers removed per request
            # Combo deals
            {
                "id": 9, "name": "Classic Burger Combo", "price": 99.00, "category": "Combos",
                "description": "Classic Burger + Fries + Drink", "is_combo": True,
                "combo_items": [1, 4, 5], "calories": 1165, "image": "Burger Combo"
            },
            {
                "id": 10, "name": "Cheeseburger Combo", "price": 109.00, "category": "Combos",
                "description": "Cheeseburger + Fries + Drink", "is_combo": True,
                "combo_items": [13, 4, 5], "calories": 1185, "image": "CheeseBurger Combo"
            },
            {
                "id": 27, "name": "Extra Sauce", "price": 5.00, "category": "Add-ons",
                "description": "Pick BBQ, Spicy, or Garlic Aioli",
                "calories": 30, "image": "Sauce choice"
            },
            {
                "id": 46, "name": "Dairy Milk", "price": 5.00, "category": "Add-ons",
                "description": "Add dairy milk",
                "calories": 50, "image": "Dairy Milk"
            },
            {
                "id": 47, "name": "Non-Dairy Milk", "price": 7.00, "category": "Add-ons",
                "description": "Add non-dairy milk",
                "calories": 40, "image": "NonDairy Milk"
            },
            {
                "id": 48, "name": "Sugar", "price": 2.00, "category": "Add-ons",
                "description": "1 pack",
                "calories": 15, "image": "Sugar"
            },
            {
                "id": 49, "name": "Salt", "price": 2.00, "category": "Add-ons",
                "description": "1 pack",
                "calories": 0, "image": "Salt"
            },
            {
                "id": 31, "name": "Bacon Burger Combo", "price": 129.00, "category": "Combos",
                "description": "Bacon Burger + Fries + Drink", "is_combo": True,
                "combo_items": [14, 4, 5], "calories": 1225, "image": "Bacon Burger Combo"
            },
            {
                "id": 32, "name": "Pizza Meal", "price": 349.00, "category": "Combos",
                "description": "Medium Pizza + 2 Burger + 2 Drinks", "is_combo": True,
                "combo_items": [2, 11, 5, 5], "calories": 1250, "image": "Pizza Meal Combo"
            },
            # Additional items
            {
                "id": 11, "name": "Garlic Bread", "price": 4.99, "category": "Sides",
                "description": "Toasted bread with garlic butter", "calories": 280, "image": "Garlic Bread"
            },
            {
                "id": 12, "name": "Iced Tea", "price": 2.49, "category": "Beverages",
                "description": "Freshly brewed iced tea", "calories": 5, "image": "Iced Tea"
            }
        ]
        # Additional requested items
        default_menu.extend([
            {
                "id": 17, "name": "Pepperoni Pizza", "price": 229.00, "category": "Pizza",
                "description": "Classic pepperoni with mozzarella and tomato sauce",
                "calories": 900, "image": "Pepperoni Pizza"
            },
            {
                "id": 18, "name": "Caesar Salad", "price": 7.49, "category": "Salads",
                "description": "Romaine lettuce, croutons, parmesan, Caesar dressing",
                "calories": 420, "image": "Ceasar Salad"
            },
            # Promos: Three Meal Treat (specific curated sets)
            {
                "id": 50, "name": "Cheese Lovers", "price": 119.00, "category": "Promos",
                "description": "Cheeseburger + Onion Rings + Iced Tea",
                "calories": 0, "image": "Cheese Lover", "is_combo": True,
                "combo_items": [13, 19, 12]
            },
            {
                "id": 51, "name": "Bacon Boost", "price": 139.00, "category": "Promos",
                "description": "Bacon Burger + Garlic Bread + Lemonade",
                "calories": 0, "image": "Bacon Boost", "is_combo": True,
                "combo_items": [14, 11, 24]
            },
            {
                "id": 52, "name": "Double Delight", "price": 149.00, "category": "Promos",
                "description": "Double Patty Burger + Fries + Coca Cola",
                "calories": 0, "image": "Double Delight", "is_combo": True,
                "combo_items": [29, 4, 5]
            },
            {
                "id": 53, "name": "Pizza Treat", "price": 199.00, "category": "Promos",
                "description": "Cheese Pizza (slice/portion) + Garden Salad + Iced Coffee",
                "calories": 0, "image": "Pizza Treat", "is_combo": True,
                "combo_items": [2, 3, 25]
            },
            {
                "id": 19, "name": "Onion Rings", "price": 45.00, "category": "Sides",
                "description": "Crispy battered onion rings",
                "calories": 380, "image": "Onion Rings"
            },
            {
                "id": 20, "name": "Mozzarella Sticks", "price": 59.00, "category": "Sides",
                "description": "Fried mozzarella with marinara dip",
                "calories": 520, "image": "Mozarella"
            },
            {
                "id": 21, "name": "Brownies (5 pcs)", "price": 59.00, "category": "Desserts",
                "description": "Rich chocolate brownies, 5 pieces per order",
                "calories": 450, "image": "Brownies"
            },
            {
                "id": 22, "name": "Cheesecake", "price": 79.00, "category": "Desserts",
                "description": "Classic creamy cheesecake",
                "calories": 520, "image": "Cheesecake-berry"
            },
            {
                "id": 23, "name": "Water", "price": 0.00, "category": "Beverages",
                "description": "Bottled drinking water",
                "calories": 0, "image": "Water"
            },
            {
                "id": 24, "name": "Flavored Lemonade", "price": 25.00, "category": "Beverages",
                "description": "Refreshing lemonade with fruit flavor",
                "calories": 140, "image": "Lemonade"
            },
            {
                "id": 25, "name": "Iced Coffee", "price": 39.00, "category": "Beverages",
                "description": "Chilled coffee over ice",
                "calories": 80, "image": "Iced Coffee"
            },
            # Add-ons category (restored)
            {
                "id": 26, "name": "Extra Cheese", "price": 10.00, "category": "Add-ons",
                "description": "Add extra cheese to your item",
                "calories": 80, "image": "Extra Cheese"
            },
            {
                "id": 27, "name": "Extra Sauce", "price": 5.00, "category": "Add-ons",
                "description": "Pick BBQ, Spicy, or Garlic Aioli",
                "calories": 30, "image": "Sauce choice"
            },
            # Promos: Duo Deals (six specific combos)
            {
                "id": 40, "name": "Burger & Fries", "price": 79.00, "category": "Promos",
                "description": "Duo Deal: Classic Burger + Fries",
                "calories": 1015, "image": "Burger & Fries", "is_combo": True,
                "combo_items": [1, 4]
            },
            {
                "id": 41, "name": "Burger & Ice Cream", "price": 79.00, "category": "Promos",
                "description": "Duo Deal: Classic Burger + Ice Cream",
                "calories": 1030, "image": "Burger & Ice Cream", "is_combo": True,
                "combo_items": [1, 16]
            },
            {
                "id": 42, "name": "Burger & Sundae", "price": 79.00, "category": "Promos",
                "description": "Duo Deal: Classic Burger + Chocolate Sundae",
                "calories": 1070, "image": "Burger & Sundae", "is_combo": True,
                "combo_items": [1, 6]
            },
            {
                "id": 43, "name": "Cheeseburger & Fries", "price": 79.00, "category": "Promos",
                "description": "Duo Deal: Cheeseburger + Fries",
                "calories": 1115, "image": "Cheeseburger & Fries", "is_combo": True,
                "combo_items": [13, 4]
            },
            {
                "id": 44, "name": "Cheeseburger & Sundae", "price": 79.00, "category": "Promos",
                "description": "Duo Deal: Cheeseburger + Chocolate Sundae",
                "calories": 1170, "image": "Cheeseburger & Sundae", "is_combo": True,
                "combo_items": [13, 6]
            },
            {
                "id": 45, "name": "Cheeseburger & Ice Cream", "price": 79.00, "category": "Promos",
                "description": "Duo Deal: Cheeseburger + Ice Cream",
                "calories": 1130, "image": "Cheeseburger & Ice Cream", "is_combo": True,
                "combo_items": [13, 16]
            },
        ])
        
        try:
            if os.path.exists("menu.json"):
                with open("menu.json", "r") as f:
                    return json.load(f)
        except:
            pass
        
        return default_menu
    
    def save_menu(self):
        """Save menu to JSON file"""
        try:
            with open("menu.json", "w") as f:
                json.dump(self.menu_items, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save menu: {str(e)}")
    
    def generate_order_id(self):
        """Generate unique order ID"""
        return datetime.now().strftime("%Y%m%d%H%M%S")
    
    def get_next_customer_number(self):
        """Get the next customer number from orders directory"""
        try:
            if not os.path.exists("orders"):
                os.makedirs("orders")
            
            # Count existing orders
            existing_orders = len([f for f in os.listdir("orders") if f.startswith("order_")])
            return existing_orders + 1
        except:
            return 1
    
    def create_styles(self):
        """Create custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Header.TLabel', 
                       background=self.colors["primary"], 
                       foreground="white", 
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Category.TButton', 
                       background=self.colors["card"], 
                       foreground=self.colors["accent"],
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=1,
                       focuscolor='none')
        
        style.map('Category.TButton',
                 background=[('active', self.colors["secondary"])],
                 foreground=[('active', 'white')])
        
        style.configure('MenuCard.TFrame', 
                       background=self.colors["card"],
                       relief='ridge',
                       borderwidth=1)
        
        style.configure('AddButton.TButton', 
                       background=self.colors["primary"],
                       foreground="white",
                       font=('Segoe UI', 10, 'bold'),
                       focuscolor='none')
        
        style.map('AddButton.TButton',
                 background=[('active', self.colors["secondary"])])
        
        style.configure('Tab.TNotebook', 
                       background=self.colors["background"],
                       tabposition='nw')
        
        style.configure('Tab.TNotebook.Tab', 
                       background=self.colors["card"],
                       foreground=self.colors["accent"],
                       padding=[12, 8],
                       font=('Segoe UI', 12, 'bold'))
        
        style.map('Tab.TNotebook.Tab',
                 background=[('selected', self.colors["primary"])],
                 foreground=[('selected', 'white')])
        
        style.configure('Total.TLabel', 
                       background=self.colors["background"],
                       foreground=self.colors["accent"],
                       font=('Segoe UI', 14, 'bold'))
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create welcome screen first
        self.create_welcome_screen()
    
    def create_welcome_screen(self):
        """Create a full-screen welcome page"""
        # Remove any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main welcome frame
        welcome_frame = tk.Frame(self.root, bg=self.colors["background"])
        welcome_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(welcome_frame, text="Welcome to FastBite", 
                               bg=self.colors["background"], 
                               fg=self.colors["primary"],
                               font=('Segoe UI', 48, 'bold'))
        title_label.pack(pady=(100, 20))
        
        # Subtitle
        subtitle_label = tk.Label(welcome_frame, text="Quick. Tasty. Delivered.", 
                                 bg=self.colors["background"], 
                                 fg="#666666",
                                 font=('Segoe UI', 24))
        subtitle_label.pack(pady=20)
        
        # Logo/Emoji
        logo_label = tk.Label(welcome_frame, text="🍔🍕🍟", 
                             bg=self.colors["background"],
                             font=('Segoe UI', 80))
        logo_label.pack(pady=40)
        
        # Button frame
        button_frame = tk.Frame(welcome_frame, bg=self.colors["background"])
        button_frame.pack(pady=60)
        
        # Next button
        next_button = tk.Button(button_frame, text="Next", 
                               command=self.open_menu_screen,
                               bg=self.colors["primary"], 
                               fg="white",
                               font=('Segoe UI', 16, 'bold'),
                               width=15, height=2)
        next_button.pack(side="left", padx=20)
        
        # Exit button
        exit_button = tk.Button(button_frame, text="Exit", 
                               command=self.root.quit,
                               bg=self.colors["danger"], 
                               fg="white",
                               font=('Segoe UI', 16, 'bold'),
                               width=15, height=2)
        exit_button.pack(side="left", padx=20)
    
    def open_menu_screen(self):
        """Open the main menu screen"""
        # Remove welcome screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Core UI state holders for filters/promos
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Combos")
        self.promo_filter_active = False
        self.promo_allowed_ids = set()

        # Create shell: sidebar + content + status bar (non-invasive)
        self.shell = AppShell(self.root, self.colors).mount()

        # Sidebar: search + categories
        self.create_sidebar()

        # Create header (kept at top of root for now for simplicity)
        self.create_header()

        # Create notebook for tabs
        # Host notebook inside shell content area
        self.content_host = tk.Frame(self.shell.content, bg=self.colors["background"])
        self.content_host.pack(fill="both", expand=True, padx=10, pady=10)
        self.notebook = ttk.Notebook(self.content_host)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self.menu_tab = ttk.Frame(self.notebook)
        self.order_tab = ttk.Frame(self.notebook)
        self.checkout_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.menu_tab, text="Menu")
        self.notebook.add(self.order_tab, text="Cart")
        self.notebook.add(self.checkout_tab, text="Checkout")

        # Create menu, order and checkout displays
        self.create_menu_tab()
        self.create_order_tab()
        self.create_checkout_tab()

        # Global keyboard shortcuts (do not change behavior)
        bind_global_shortcuts(self)

        # Theme toggle
        self.current_theme = "light"
        self.shell.bind_theme_toggle(self.toggle_theme_callback)

        # Initial status
        self.update_status_bar("View: Menu")

    # Removed dedicated Promos tab; promos panel remains within the Menu tab
    
    def create_header(self):
        """Create application header"""
        header_frame = tk.Frame(self.root, bg=self.colors["primary"], height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo and title
        title_frame = tk.Frame(header_frame, bg=self.colors["primary"])
        title_frame.pack(side="left", padx=20, pady=15)
        
        logo_label = tk.Label(title_frame, text="🍔", font=("Segoe UI", 32), bg=self.colors["primary"], fg="white")
        logo_label.pack(side="left", padx=10)
        
        title_label = tk.Label(title_frame, text="FastBite", 
                               bg=self.colors["primary"], fg="white", 
                               font=('Segoe UI', 24, 'bold'))
        title_label.pack(side="left")
        
        # User info
        user_frame = tk.Frame(header_frame, bg=self.colors["primary"])
        user_frame.pack(side="right", padx=20, pady=15)
        
        user_label = tk.Label(user_frame, text="Welcome, Guest!", 
                              bg=self.colors["primary"], fg="white", 
                              font=('Segoe UI', 12))
        user_label.pack()
        
        # Special offers banner
        offers_frame = tk.Frame(self.root, bg=self.colors["warning"], height=40)
        offers_frame.pack(fill="x", padx=0, pady=5)
        offers_frame.pack_propagate(False)
        
        offers_label = tk.Label(offers_frame, 
                               text="🔥 Special Offer: Get 20% off on all Combos! 🔥", 
                               bg=self.colors["warning"], 
                               fg=self.colors["accent"], 
                               font=('Segoe UI', 12, 'bold'))
        offers_label.pack(pady=5)

    def create_sidebar(self):
        """Build sidebar controls for search and categories (no logic changes)."""
        if not getattr(self, "shell", None):
            return

        sidebar = self.shell.sidebar
        for child in sidebar.winfo_children():
            child.destroy()

        # Title
        title = tk.Label(sidebar, text="Browse", bg=self.colors["card"], fg=self.colors["accent"], font=self.fonts["heading_small"])
        title.pack(anchor="w", padx=16, pady=(16, 8))

        # Search section label
        search_label = tk.Label(sidebar, text="Search", bg=self.colors["card"], fg=self.colors["accent"], font=self.fonts["body"])
        search_label.pack(anchor="w", padx=16, pady=(0, 4))

        search_frame = tk.Frame(sidebar, bg=self.colors["card"])
        search_frame.pack(fill="x", padx=12, pady=(0, 12))

        search_icon = tk.Label(search_frame, text="🔍", bg=self.colors["card"], font=self.fonts["body_large"])
        search_icon.pack(side="left", padx=(0, 6))

        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind("<KeyRelease>", self.filter_menu)
        self.search_entry = search_entry  # For Ctrl+F focus

        # Divider
        divider1 = tk.Frame(sidebar, height=1, bg="#e0e0e0")
        divider1.pack(fill="x", padx=12, pady=(0, 8))

        # Categories
        cat_title = tk.Label(sidebar, text="Categories", bg=self.colors["card"], fg=self.colors["accent"], font=self.fonts["body"])
        cat_title.pack(anchor="w", padx=16, pady=(0, 8))

        categories = ["Combos", "Burgers", "Pizza", "Salads", "Sides", "Beverages", "Desserts", "Pasta", "Add-ons"]
        for category in categories:
            btn = ttk.Button(sidebar, text=category, style='Category.TButton', width=18,
                             command=lambda c=category: self.filter_by_category(c))
            btn.pack(fill="x", padx=12, pady=2)

        # Divider
        divider2 = tk.Frame(sidebar, height=1, bg="#e0e0e0")
        divider2.pack(fill="x", padx=12, pady=(12, 8))

        # Promo buttons section
        promo_title = tk.Label(sidebar, text="Promo:", bg=self.colors["card"], fg=self.colors["accent"], font=self.fonts["body"])
        promo_title.pack(anchor="w", padx=16, pady=(0, 6))

        def clear_promo():
            self.promo_filter_active = False
            self.promo_allowed_ids = set()
            try:
                self.promos_info_var.set("")
                self.promos_info_label.pack_forget()
            except Exception:
                pass
            self.update_status_bar("View: Menu | Promo: None")
            self.update_menu_display()

        def activate_duo_deals():
            eligible_ids = {40, 41, 42, 43, 44, 45}
            self.promo_filter_active = True
            self.promo_allowed_ids = eligible_ids
            try:
                self.promos_info_var.set("Duo Deals: Six combos available.")
                self.promos_info_label.pack(fill="x", padx=15, pady=(0, 8))
            except Exception:
                pass
            self.update_status_bar("View: Menu | Promo: Duo Deals")
            self.update_menu_display()

        def activate_triple_treat():
            eligible_ids = {50, 51, 52, 53}
            self.promo_filter_active = True
            self.promo_allowed_ids = eligible_ids
            try:
                self.promos_info_var.set("Triple Treat Box: Cheese Lovers, Bacon Boost, Double Delight, Pizza Treat.")
                self.promos_info_label.pack(fill="x", padx=15, pady=(0, 8))
            except Exception:
                pass
            self.update_status_bar("View: Menu | Promo: Triple Treat Box")
            self.update_menu_display()

        btn_duo = ttk.Button(sidebar, text="Duo Deals", style='Category.TButton', width=18,
                              command=activate_duo_deals)
        btn_duo.pack(fill="x", padx=12, pady=2)

        btn_ttb = ttk.Button(sidebar, text="TRIPLE TREAT BOX", style='Category.TButton', width=18,
                              command=activate_triple_treat)
        btn_ttb.pack(fill="x", padx=12, pady=2)

        clear_btn = tk.Button(sidebar, text="Clear promo", command=clear_promo,
                              bg=self.colors["card"], fg=self.colors["accent"], bd=0, highlightthickness=0,
                              font=self.fonts["link"], cursor="hand2")
        clear_btn.pack(anchor="w", padx=16, pady=(4, 8))

    def update_status_bar(self, text):
        """Update status bar label safely."""
        try:
            if getattr(self, "shell", None):
                self.shell.set_status(text)
        except Exception:
            pass

    def toggle_theme_callback(self):
        """Toggle between light and dark theme."""
        theme_name, colors = toggle_theme()
        self.current_theme = theme_name
        self.colors = colors
        # Update shell theme label
        if getattr(self, "shell", None) and self.shell.theme_label:
            self.shell.theme_label.configure(text=f"Theme: {theme_name.title()}")
        # Reapply ttk styles
        apply_theme(ttk.Style(), self.colors)
        # Refresh UI colors (non-invasive; reconstruct widgets if needed)
        # For simplicity, just update status bar and shell colors
        self.shell.sidebar.configure(bg=self.colors["card"])
        self.shell.content.configure(bg=self.colors["background"])
        self.shell.status.configure(bg=self.colors["background"])
        self.shell.status_label.configure(bg=self.colors["background"], fg="#666666")
        self.shell.theme_label.configure(bg=self.colors["background"], fg=self.colors["primary"])
    
    def create_menu_tab(self):
        """Create enhanced menu tab with grid layout"""
        # Promo info banner (sidebar buttons control this)
        self.promos_info_var = tk.StringVar(value="")
        self.promos_info_label = tk.Label(self.menu_tab, textvariable=self.promos_info_var,
                          bg=self.colors["background"], fg="#666666",
                          font=('Segoe UI', 14, 'bold'))
        
        # Menu items frame with scrollbar
        menu_container = tk.Frame(self.menu_tab)
        menu_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(menu_container, bg=self.colors["background"])
        scrollbar = ttk.Scrollbar(menu_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["background"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.menu_grid_frame = scrollable_frame
        
        # Update menu display
        self.update_menu_display()
    
    def create_menu_item_card(self, item, row, col):
        """Create a styled menu item card"""
        card_frame = tk.Frame(self.menu_grid_frame, bg=self.colors["card"], relief='ridge', borderwidth=1, width=250, height=300)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="")
        card_frame.grid_propagate(False)
        
        # Create image placeholder
        image_frame = tk.Frame(card_frame, bg=self.colors["card"], height=150)
        image_frame.pack(fill="x", padx=10, pady=10)
        image_frame.pack_propagate(False)
        
        # Create a colored rectangle as image placeholder
        img = self.create_colored_image(item["image"], 230, 130)
        img_label = tk.Label(image_frame, image=img, bg=self.colors["card"])
        img_label.image = img  # Keep a reference
        img_label.pack(padx=10, pady=10)
        
        # Item name
        name_label = tk.Label(card_frame, text=item["name"], 
                             bg=self.colors["card"], fg=self.colors["accent"],
                             font=self.fonts["body_large"],
                             wraplength=230)
        name_label.pack(padx=10, pady=(0, 5))
        
        # Item description
        desc_label = tk.Label(card_frame, text=item["description"], 
                             bg=self.colors["card"], fg="#666666",
                             font=('Segoe UI', 9),
                             wraplength=230)
        desc_label.pack(padx=10, pady=(0, 5))
        
        # Calories and price
        info_frame = tk.Frame(card_frame, bg=self.colors["card"])
        info_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        calories_label = tk.Label(info_frame, text=f"🔥 {item['calories']} cal", 
                                 bg=self.colors["card"], fg="#666666",
                                 font=('Segoe UI', 9))
        calories_label.pack(side="left")
        
        price_label = tk.Label(info_frame, text=f"₱{item['price']:.2f}", 
                              bg=self.colors["card"], fg=self.colors["primary"],
                              font=self.fonts["body_large"])
        price_label.pack(side="right")
        
        # Add to cart button
        add_button = ttk.Button(card_frame, text="Add to Cart", 
                               style='AddButton.TButton',
                               command=lambda i=item: self.add_to_cart(i))
        add_button.pack(padx=10, pady=10, fill="x")
        
        # Combo indicator
        if item.get("is_combo"):
            combo_label = tk.Label(card_frame, text="🎁 COMBO DEAL", 
                                  bg=self.colors["card"], fg=self.colors["success"],
                                  font=('Segoe UI', 9, 'bold'))
            combo_label.pack(padx=10, pady=(0, 5))


    def create_colored_image(self, text, width, height):
        """Create a colored image with text"""
        # First try to load a real image from disk (images/<name>.(png|jpg|gif))
        loaded = self.load_image(text, width, height)
        if loaded:
            return loaded

        # Return a simple solid-color PhotoImage to use as a placeholder.
        try:
            img = tk.PhotoImage(width=width, height=height)
            img.put(self.colors["primary"], to=(0, 0, width - 1, height - 1))
            return img
        except Exception:
            return tk.PhotoImage(width=width, height=height)

    def load_image(self, image_name, width, height):
        """Try to load an image from the local `order_image/` folder.

        Supports PNG/GIF/JPG. Resizes to fit within width x height while maintaining aspect ratio.
        Returns a Tk-compatible PhotoImage or None when not found.
        """
        exts = ["png", "gif", "jpg", "jpeg"]
        images_dir = Path(__file__).parent / "order_image"
        for ext in exts:
            candidate = images_dir / f"{image_name}.{ext}"
            if candidate.exists():
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(candidate)
                    img = img.convert("RGBA")

                    img_width, img_height = img.size
                    ratio = min(width / img_width, height / img_height)
                    new_width = int(img_width * ratio)
                    new_height = int(img_height * ratio)

                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    return photo
                except ImportError:
                    try:
                        photo = tk.PhotoImage(file=str(candidate))
                        return photo
                    except Exception:
                        pass
                except Exception:
                    try:
                        photo = tk.PhotoImage(file=str(candidate))
                        return photo
                    except Exception:
                        pass
        return None
    
    def create_order_tab(self):
        """Create enhanced order tab with cart management"""
        # Sticky cart header with title, subtotal, and checkout CTA
        cart_header = tk.Frame(self.order_tab, bg=self.colors["card"], relief='ridge', borderwidth=1)
        cart_header.pack(fill="x", padx=10, pady=(10, 5))

        cart_title = tk.Label(cart_header, text="Your Cart", bg=self.colors["card"],
                             fg=self.colors["accent"], font=self.fonts["heading_small"])
        cart_title.pack(side="left", padx=12, pady=8)

        self.cart_header_total = tk.Label(cart_header, text="Total: ₱0.00",
                                          bg=self.colors["card"], fg=self.colors["primary"],
                                          font=self.fonts["subheading"])
        self.cart_header_total.pack(side="left", padx=12)

        checkout_header_btn = ttk.Button(cart_header, text="Checkout",
                                         style='AddButton.TButton',
                                         command=lambda: self.notebook.select(2))
        checkout_header_btn.pack(side="right", padx=12, pady=6)
        
        # Order items frame with scrollbar
        order_container = tk.Frame(self.order_tab, bg=self.colors["background"])
        order_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(order_container, bg=self.colors["background"])
        scrollbar = ttk.Scrollbar(order_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["background"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.order_frame = scrollable_frame
        
        # Control frame
        control_frame = tk.Frame(self.order_tab, bg=self.colors["background"])
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg=self.colors["background"])
        button_frame.pack(side="left")
        
        remove_button = ttk.Button(button_frame, text="Remove Selected", 
                                 command=self.remove_from_cart)
        remove_button.pack(side="left", padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear Cart", 
                                command=self.clear_order)
        clear_button.pack(side="left", padx=5)
        
        # Update order display
        self.update_order_display()
    
    def create_checkout_tab(self):
        """Create enhanced checkout tab with order summary"""
        # Header
        header_frame = tk.Frame(self.checkout_tab, bg=self.colors["background"])
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Changed ttk.Label to tk.Label for custom background
        checkout_label = tk.Label(header_frame, text="Checkout", 
                                 bg=self.colors["background"], fg=self.colors["accent"],
                                 font=self.fonts["heading_medium"])
        checkout_label.pack()
        
        # Main container
        main_container = tk.Frame(self.checkout_tab, bg=self.colors["background"])
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Order summary
        summary_frame = tk.LabelFrame(main_container, text="Order Summary", 
                                    bg=self.colors["card"],
                                    padx=20, pady=20)
        summary_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Order ID
        self.order_id_label = tk.Label(summary_frame, text=f"Order ID: {self.current_order_id}", 
                                      bg=self.colors["card"], fg=self.colors["accent"],
                                      font=('Segoe UI', 12))
        self.order_id_label.pack(anchor="w", pady=5)
        
        # Order details
        self.order_details_text = tk.Text(summary_frame, height=15, width=40, 
                                        bg=self.colors["background"], fg=self.colors["accent"],
                                        font=('Segoe UI', 10))
        self.order_details_text.pack(fill="both", expand=True, pady=10)
        
        # Total amount
        self.checkout_total_label = tk.Label(summary_frame, text="Total: ₱0.00", 
                                             bg=self.colors["card"], fg=self.colors["primary"],
                                             font=('Segoe UI', 16, 'bold'))
        self.checkout_total_label.pack(pady=10)
        
        # Right side - Payment and delivery
        payment_frame = tk.LabelFrame(main_container, text="Payment & Delivery", 
                                    bg=self.colors["card"],
                                    padx=20, pady=20)
        payment_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Create scrollable content for payment frame
        payment_canvas = tk.Canvas(payment_frame, bg=self.colors["card"], highlightthickness=0)
        payment_scrollbar = ttk.Scrollbar(payment_frame, orient="vertical", command=payment_canvas.yview)
        payment_scrollable_frame = tk.Frame(payment_canvas, bg=self.colors["card"])
        
        payment_scrollable_frame.bind(
            "<Configure>",
            lambda e: payment_canvas.configure(scrollregion=payment_canvas.bbox("all"))
        )
        
        payment_canvas.create_window((0, 0), window=payment_scrollable_frame, anchor="nw")
        payment_canvas.configure(yscrollcommand=payment_scrollbar.set)
        
        payment_canvas.pack(side="left", fill="both", expand=True)
        payment_scrollbar.pack(side="right", fill="y")
        
        # Customer Information frame (only shown for Delivery)
        self.customer_info_frame = tk.Frame(payment_scrollable_frame, bg=self.colors["card"])
        self.customer_info_frame.pack(fill="x", pady=10)
        
        customer_label = tk.Label(self.customer_info_frame, text="Customer Information:", 
                                 bg=self.colors["card"], fg=self.colors["accent"],
                                 font=('Segoe UI', 12, 'bold'))
        customer_label.pack(anchor="w")
        
        # Name field
        name_label = tk.Label(self.customer_info_frame, text="Name:", 
                             bg=self.colors["card"], fg=self.colors["accent"],
                             font=('Segoe UI', 10))
        name_label.pack(anchor="w", padx=20, pady=(10, 0))
        
        self.customer_name_entry = tk.Entry(self.customer_info_frame, font=self.fonts["body_small"], width=35)
        self.customer_name_entry.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Contact field
        contact_label = tk.Label(self.customer_info_frame, text="Contact Number:", 
                                bg=self.colors["card"], fg=self.colors["accent"],
                                font=('Segoe UI', 10))
        contact_label.pack(anchor="w", padx=20, pady=(10, 0))
        
        self.customer_contact_entry = tk.Entry(self.customer_info_frame, font=self.fonts["body_small"], width=35)
        self.customer_contact_entry.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Address field
        address_label = tk.Label(self.customer_info_frame, text="Address:", 
                                bg=self.colors["card"], fg=self.colors["accent"],
                                font=('Segoe UI', 10))
        address_label.pack(anchor="w", padx=20, pady=(10, 0))
        
        self.customer_address_entry = tk.Text(self.customer_info_frame, height=3, width=35, 
                                             font=('Segoe UI', 10))
        self.customer_address_entry.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Hide customer info frame by default (only show for Delivery)
        self.customer_info_frame.pack_forget()
        
        # Delivery method
        delivery_frame = tk.Frame(payment_scrollable_frame, bg=self.colors["card"])
        delivery_frame.pack(fill="x", pady=10)
        
        delivery_label = tk.Label(delivery_frame, text="Delivery Method:", 
                                 bg=self.colors["card"], fg=self.colors["accent"],
                                 font=('Segoe UI', 12, 'bold'))
        delivery_label.pack(anchor="w")
        
        self.delivery_var = tk.StringVar(value="Dine-in")
        delivery_options = ["Dine-in", "Delivery", "Takeaway"]
        
        for option in delivery_options:
            rb = tk.Radiobutton(delivery_frame, text=option, variable=self.delivery_var, 
                              value=option, bg=self.colors["card"], 
                              font=('Segoe UI', 10),
                              command=self.toggle_customer_fields)
            rb.pack(anchor="w", padx=20)
        
        # Payment method
        payment_method_frame = tk.Frame(payment_scrollable_frame, bg=self.colors["card"])
        payment_method_frame.pack(fill="x", pady=10)
        
        payment_label = tk.Label(payment_method_frame, text="Payment Method:", 
                                bg=self.colors["card"], fg=self.colors["accent"],
                                font=('Segoe UI', 12, 'bold'))
        payment_label.pack(anchor="w")
        
        self.payment_var = tk.StringVar(value="Cash")
        payment_methods = ["Cash"]

        for method in payment_methods:
            rb = tk.Radiobutton(payment_method_frame, text=method, variable=self.payment_var,
                              value=method, bg=self.colors["card"],
                              font=('Segoe UI', 10))
            rb.pack(anchor="w", padx=20)
        
        # Special instructions
        instructions_frame = tk.Frame(payment_scrollable_frame, bg=self.colors["card"])
        instructions_frame.pack(fill="x", pady=10)
        
        instructions_label = tk.Label(instructions_frame, text="Special Instructions:", 
                                     bg=self.colors["card"], fg=self.colors["accent"],
                                     font=('Segoe UI', 12, 'bold'))
        instructions_label.pack(anchor="w")
        
        self.instructions_text = tk.Text(instructions_frame, height=4, width=35, 
                                       bg=self.colors["background"], fg=self.colors["accent"],
                                       font=('Segoe UI', 10))
        self.instructions_text.pack(fill="x", pady=5)
        
        # Place order button
        place_order_button = ttk.Button(payment_frame, text="Place Order", 
                                      command=self.place_order,
                                      style='AddButton.TButton')
        place_order_button.pack(pady=20)
        
        # Update checkout display
        self.update_checkout_display()
    
    def update_menu_display(self):
        """Update menu display with filtered items"""
        # Clear existing items
        for widget in self.menu_grid_frame.winfo_children():
            widget.destroy()
        
        # Filter items
        search_term = self.search_var.get().lower()
        category_filter = self.category_var.get()
        
        filtered_items = []
        for item in self.menu_items:
            # Apply search filter
            if search_term and search_term not in item["name"].lower() and \
               search_term not in item["description"].lower():
                continue
            
            # Apply category filter unless a promo filter is active
            if not getattr(self, 'promo_filter_active', False):
                if category_filter != "All" and item["category"] != category_filter:
                    continue

            # Apply promo-only filter when active
            if getattr(self, 'promo_filter_active', False):
                if item.get("id") not in getattr(self, 'promo_allowed_ids', set()):
                    continue
            
            filtered_items.append(item)
        
        # Display items in grid
        row = 0
        items_per_row = 4
        for i, item in enumerate(filtered_items):
            col = i % items_per_row
            if col == 0 and i > 0:
                row += 1
            # Calculate offset to center if last row has fewer items
            total_rows = (len(filtered_items) + items_per_row - 1) // items_per_row
            if row == total_rows - 1:  # last row
                items_in_last_row = len(filtered_items) % items_per_row
                if items_in_last_row == 0:
                    items_in_last_row = items_per_row
                offset = (items_per_row - items_in_last_row) // 2
                col += offset
            self.create_menu_item_card(item, row, col)
        # Configure grid to expand columns for horizontal centering
        for i in range(4):
            self.menu_grid_frame.columnconfigure(i, weight=1)

        # Update status
        self.update_status_bar("View: Menu")
    
    def update_order_display(self):
        """Update order display with current items"""
        # Clear existing items
        for widget in self.order_frame.winfo_children():
            widget.destroy()
        
        if not self.order_items:
            empty_label = tk.Label(self.order_frame, text="Your cart is empty", 
                                 bg=self.colors["background"], fg="#666666",
                                 font=self.fonts["subheading"])
            empty_label.pack(pady=50)
            self.cart_header_total.config(text="Total: ₱0.00")
            self.update_status_bar("View: Cart | Items: 0 | Total: ₱0.00")
            return
        
        total = 0
        for item in self.order_items:
            # Create item card
            item_frame = tk.Frame(self.order_frame, bg=self.colors["card"], relief='ridge', borderwidth=1)
            item_frame.pack(fill="x", padx=10, pady=5)
            
            # Item details
            details_frame = tk.Frame(item_frame, bg=self.colors["card"])
            details_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            
            name_label = tk.Label(details_frame, text=item["name"], 
                                 bg=self.colors["card"], fg=self.colors["accent"],
                                 font=self.fonts["body_large"])
            name_label.pack(anchor="w")
            
            price_label = tk.Label(details_frame, text=f"₱{item['price']:.2f} each", 
                                 bg=self.colors["card"], fg="#666666",
                                 font=('Segoe UI', 10))
            price_label.pack(anchor="w")
            
            # Quantity and controls
            controls_frame = tk.Frame(item_frame, bg=self.colors["card"])
            controls_frame.pack(side="right", padx=10, pady=10)
            
            # Quantity display
            qty_label = tk.Label(controls_frame, text=f"Qty: {item['quantity']}", 
                               bg=self.colors["card"], fg=self.colors["accent"],
                               font=('Segoe UI', 10))
            qty_label.pack(side="top")
            
            # Quantity controls
            qty_frame = tk.Frame(controls_frame, bg=self.colors["card"])
            qty_frame.pack(side="top")
            
            minus_button = tk.Button(qty_frame, text="-", width=3, height=1,
                                    command=lambda i=item: self.decrease_quantity(i),
                                    bg=self.colors["danger"], fg="white")
            minus_button.pack(side="left")
            
            plus_button = tk.Button(qty_frame, text="+", width=3, height=1,
                                   command=lambda i=item: self.increase_quantity(i),
                                   bg=self.colors["success"], fg="white")
            plus_button.pack(side="left")
            
            # Remove button
            remove_button = tk.Button(controls_frame, text="Remove", 
                                    command=lambda i=item: self.remove_item(i),
                                    bg=self.colors["danger"], fg="white")
            remove_button.pack(side="top", pady=5)
            
            # Total for this item
            item_total = item['price'] * item['quantity']
            total_label = tk.Label(item_frame, text=f"₱{item_total:.2f}",
                                 bg=self.colors["card"], fg=self.colors["primary"],
                                 font=self.fonts["body_large"])
            total_label.pack(side="right", padx=10, pady=10)
            
            total += item_total
        
        self.cart_header_total.config(text=f"Total: ₱{total:.2f}")
        self.update_status_bar(f"View: Cart | Items: {len(self.order_items)} | Total: ₱{total:.2f}")
    
    def update_checkout_display(self):
        """Update checkout display with order summary"""
        self.order_details_text.delete(1.0, tk.END)
        total = 0
        
        if not self.order_items:
            self.order_details_text.insert(tk.END, "No items in order")
            self.checkout_total_label.config(text="Total: $0.00")
            return
        
        for item in self.order_items:
            item_total = item['price'] * item['quantity']
            total += item_total
            self.order_details_text.insert(tk.END, 
                f"{item['name']} x{item['quantity']}: ₱{item['price']:.2f} each = ₱{item_total:.2f}\n")

        self.checkout_total_label.config(text=f"Total: ₱{total:.2f}")
    
    def filter_menu(self, event=None):
        """Filter menu based on search"""
        self.update_menu_display()
    
    def filter_by_category(self, category):
        """Filter menu by category"""
        self.category_var.set(category)
        # Hide promo banner when switching categories
        try:
            self.promos_info_var.set("")
            self.promos_info_label.pack_forget()
        except Exception:
            pass
        # Disable promo-only filter when the user manually switches categories
        self.promo_filter_active = False
        self.promo_allowed_ids = set()
        self.update_menu_display()
        self.update_status_bar(f"View: Menu | Category: {category}")
    
    def add_to_cart(self, item):
        """Add menu item to cart"""
        # Size selection rules:
        # - Beverages: always ask size
        # - Sides: ask size except Garlic Bread
        # - Desserts: ask size only for Milkshake, Ice Cream, Chocolate Sundae
        ask_size_desserts = {"Milkshake", "Ice Cream", "Chocolate Sundae"}
        # Special flow for Cheesecake: ask Pieces or Whole
        if item["name"] == "Cheesecake":
            self.select_cheesecake_option(item)
            return

        if (
            item["category"] == "Beverages"
            or (item["category"] == "Sides" and item["name"] != "Garlic Bread")
            or (item["category"] == "Desserts" and item["name"] in ask_size_desserts)
        ):
            self.select_size(item)
        else:
            self.add_item_to_cart(item)
    
    def open_duo_deals_modal(self):
        """Select any 2 eligible items; fixed price 79"""
        # Determine eligible items: prefer current promo_allowed_ids when set
        try:
            allowed_ids = getattr(self, 'promo_allowed_ids', set())
            if allowed_ids:
                eligible = [item for item in self.menu_items if item.get("id") in allowed_ids]
            else:
                eligible = [item for item in self.menu_items if item.get("category") == "Burgers" and not item.get("is_combo")]
        except Exception:
            eligible = []

        if not eligible:
            messagebox.showinfo("Promo", "No eligible items available for DUO DEALS.")
            return

        # Simple modal to pick two items
        win = tk.Toplevel(self.root)
        win.title("DUO DEALS: Pick 2")
        win.geometry("420x420")
        win.resizable(False, False)

        tk.Label(win, text="Pick any 2 items", font=self.fonts["body_large"]).pack(pady=10)

        selections = []

        list_frame = tk.Frame(win)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create checkbuttons for each eligible item
        vars = []
        for item in eligible:
            v = tk.IntVar(value=0)
            cb = tk.Checkbutton(list_frame, text=item['name'], variable=v, anchor='w', justify='left')
            cb.pack(fill='x', anchor='w')
            vars.append((v, item))

        def confirm():
            selections.clear()
            for v, item in vars:
                if v.get() == 1:
                    selections.append(item)
            if len(selections) != 2:
                messagebox.showwarning("DUO DEALS", "Please select exactly 2 items.")
                return
            # Add a single bundle line to cart at fixed price 79
            bundle = {
                "id": 1001,
                "name": "DUO DEALS (2 items)",
                "price": 79.00,
                "quantity": 1,
                "details": [s['name'] for s in selections]
            }
            self.order_items.append(bundle)
            self.update_order_display()
            self.update_checkout_display()
            win.destroy()
            messagebox.showinfo("Promo", "DUO DEALS added to cart!")

        ttk.Button(win, text="Confirm", style='AddButton.TButton', command=confirm).pack(pady=10)
    
    def select_size(self, item):
        """Show size selection popup for beverages and sides (except garlic bread)"""
        size_window = tk.Toplevel(self.root)
        size_window.title("Select Size")
        size_window.geometry("450x300")
        size_window.resizable(False, False)
        
        tk.Label(size_window, text=f"Select size for {item['name']}", font=self.fonts["heading_small"]).pack(pady=20)
        
        size_var = tk.StringVar(value="Regular")
        
        sizes = [("Regular - ₱{:.2f}".format(item['price']), "Regular"), 
                 ("Medium - ₱{:.2f}".format(item['price'] + 3.00), "Medium"), 
                 ("Large - ₱{:.2f}".format(item['price'] + 7.00), "Large")]
        for text, value in sizes:
            tk.Radiobutton(size_window, text=text, variable=size_var, value=value, 
                          font=self.fonts["body_large"]).pack(anchor="w", padx=40, pady=12)
        
        def confirm_size():
            selected_size = size_var.get()
            item_with_size = item.copy()
            item_with_size["name"] = f"{item['name']} ({selected_size})"
            item_with_size["size"] = selected_size
            # Adjust price based on size
            if selected_size == "Medium":
                item_with_size["price"] += 3.00
            elif selected_size == "Large":
                item_with_size["price"] += 7.00
            self.add_item_to_cart(item_with_size)
            size_window.destroy()
        
        btn = tk.Button(size_window, text="Add to Cart", command=confirm_size, 
                       bg=self.colors["primary"], fg="white", font=self.fonts["body_large"],
                       height=2, width=20)
        btn.pack(pady=30)
        # Focus first radio button for keyboard navigation
        size_window.focus_set()

    def select_cheesecake_option(self, item):
        """Popup asking if Cheesecake is Pieces or Whole"""
        cc_window = tk.Toplevel(self.root)
        cc_window.title("Cheesecake Option")
        cc_window.geometry("320x200")
        cc_window.resizable(False, False)

        tk.Label(cc_window, text="Choose Cheesecake type:", font=('Segoe UI', 12)).pack(pady=10)

        choice_var = tk.StringVar(value="Pieces")
        tk.Radiobutton(cc_window, text="Pieces", variable=choice_var, value="Pieces", font=('Segoe UI', 10)).pack(anchor="w", padx=20)
        tk.Radiobutton(cc_window, text="Whole", variable=choice_var, value="Whole", font=('Segoe UI', 10)).pack(anchor="w", padx=20)

        def confirm_choice():
            choice = choice_var.get()
            item_copy = item.copy()
            if choice == "Pieces":
                item_copy["name"] = "Cheesecake (piece)"
                # keep base price
                item_copy["price"] = item.get("price", 6.49)
            else:
                item_copy["name"] = "Cheesecake (whole)"
                # set whole cake price (adjust as needed)
                item_copy["price"] = 24.00
            self.add_item_to_cart(item_copy)
            cc_window.destroy()

        tk.Button(cc_window, text="Add to Cart", command=confirm_choice, bg=self.colors["primary"], fg="white").pack(pady=20)
    
    def add_item_to_cart(self, item):
        """Add item to cart (used for both drinks and others)"""
        # Check if item already in cart
        existing_item = next((i for i in self.order_items if i["id"] == item["id"] and i.get("size") == item.get("size")), None)
        
        if existing_item:
            existing_item["quantity"] += 1
        else:
            cart_entry = {
                "id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "quantity": 1,
                "size": item.get("size")
            }
            # If this is a combo, include human-readable details for summary
            try:
                if item.get("is_combo") and item.get("combo_items"):
                    combo_names = []
                    for cid in item.get("combo_items", []):
                        nm = self.item_by_id.get(cid, {}).get("name")
                        if nm:
                            combo_names.append(nm)
                    if combo_names:
                        cart_entry["details"] = combo_names
            except Exception:
                pass
            self.order_items.append(cart_entry)
        
        self.update_order_display()
        self.update_checkout_display()
        show_toast(self.root, f"{item['name']} added to cart!")
    
    def increase_quantity(self, item):
        """Increase item quantity in cart"""
        cart_item = next((i for i in self.order_items if i["id"] == item["id"] and i.get("size") == item.get("size")), None)
        if cart_item:
            cart_item["quantity"] += 1
            self.update_order_display()
            self.update_checkout_display()
    
    def decrease_quantity(self, item):
        """Decrease item quantity in cart"""
        cart_item = next((i for i in self.order_items if i["id"] == item["id"] and i.get("size") == item.get("size")), None)
        if cart_item and cart_item["quantity"] > 1:
            cart_item["quantity"] -= 1
            self.update_order_display()
            self.update_checkout_display()
    
    def remove_item(self, item):
        """Remove specific item from cart"""
        self.order_items = [i for i in self.order_items if not (i["id"] == item["id"] and i.get("size") == item.get("size"))]
        self.update_order_display()
        self.update_checkout_display()
        show_toast(self.root, f"{item['name']} removed from cart")
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        # This would need selection implementation in the order display
        messagebox.showinfo("Info", "Click the Remove button on each item to remove it")
    
    def clear_order(self):
        """Clear all items from cart"""
        if not self.order_items:
            messagebox.showinfo("Empty Cart", "No items to clear")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to clear your entire cart?"):
            self.order_items = []
            self.update_order_display()
            self.update_checkout_display()
            messagebox.showinfo("Success", "Cart cleared")
    
    def toggle_customer_fields(self):
        """Show/hide customer information fields based on delivery method"""
        is_delivery = self.delivery_var.get() == "Delivery"
        
        if is_delivery:
            # Show the customer info frame
            self.customer_info_frame.pack(fill="x", pady=10)
        else:
            # Hide the customer info frame
            self.customer_info_frame.pack_forget()
            # Clear fields
            self.customer_name_entry.delete(0, tk.END)
            self.customer_contact_entry.delete(0, tk.END)
            self.customer_address_entry.delete(1.0, tk.END)
    
    def place_order(self):
        """Place the order and save to file"""
        if not self.order_items:
            messagebox.showwarning("Empty Order", "Please add items to your order")
            return
        
        # Validate delivery information if Delivery method is selected
        delivery_method = self.delivery_var.get()
        if delivery_method == "Delivery":
            customer_name = self.customer_name_entry.get().strip()
            customer_contact = self.customer_contact_entry.get().strip()
            customer_address = self.customer_address_entry.get(1.0, tk.END).strip()
            
            if not customer_name:
                messagebox.showwarning("Missing Information", "Please enter your name")
                return
            if not customer_contact:
                messagebox.showwarning("Missing Information", "Please enter your contact number")
                return
            if not customer_address:
                messagebox.showwarning("Missing Information", "Please enter your address")
                return
            
            self.customer_name = customer_name
            self.customer_contact = customer_contact
            self.customer_address = customer_address
        
        # Create order record
        order_record = {
            "customer_number": f"#{self.customer_number}",
            "order_id": self.current_order_id,
            "timestamp": datetime.now().isoformat(),
            "items": self.order_items,
            "customer_name": self.customer_name if delivery_method == "Delivery" else "",
            "customer_contact": self.customer_contact if delivery_method == "Delivery" else "",
            "customer_address": self.customer_address if delivery_method == "Delivery" else "",
            "payment_method": self.payment_var.get(),
            "delivery_method": delivery_method,
            "special_instructions": self.instructions_text.get(1.0, tk.END).strip(),
            "total": sum(item["price"] * item["quantity"] for item in self.order_items)
        }
        
        # Save order to file
        try:
            if not os.path.exists("orders"):
                os.makedirs("orders")
            
            order_file = f"orders/order_{self.current_order_id}.json"
            with open(order_file, "w") as f:
                json.dump(order_record, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save order: {str(e)}")
            return
            
        try:
            # Show order confirmation
            confirmation_window = tk.Toplevel(self.root)
            confirmation_window.title("Order Confirmation")
            confirmation_window.geometry("850x700")
            confirmation_window.configure(bg=self.colors["background"])
            # Make sure the dialog appears above the main window and gets focus
            try:
                confirmation_window.transient(self.root)
                confirmation_window.grab_set()
                confirmation_window.lift()
                confirmation_window.focus_force()
            except Exception:
                pass
            
            # Header section with success icon and message
            header_frame = tk.Frame(confirmation_window, bg=self.colors["primary"], height=140)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            
            success_icon = tk.Label(header_frame, text="✓", bg=self.colors["primary"], 
                                   fg="white", font=("Segoe UI", 56, "bold"))
            success_icon.pack(pady=(12, 5))
            
            conf_title = tk.Label(header_frame, text="Order Confirmed!", 
                                bg=self.colors["primary"], fg="white",
                                font=("Segoe UI", 24, "bold"))
            conf_title.pack(pady=(0, 10))
            
            # Scrollable content area
            content_canvas = tk.Canvas(confirmation_window, bg=self.colors["background"], highlightthickness=0)
            content_scrollbar = ttk.Scrollbar(confirmation_window, orient="vertical", command=content_canvas.yview)
            content_frame = tk.Frame(content_canvas, bg=self.colors["background"])
            
            content_frame.bind(
                "<Configure>",
                lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all"))
            )
            
            content_canvas.create_window((0, 0), window=content_frame, anchor="nw")
            content_canvas.configure(yscrollcommand=content_scrollbar.set)
            
            content_canvas.pack(side="left", fill="both", expand=True, padx=0, pady=0)
            content_scrollbar.pack(side="right", fill="y")
            
            # Customer number card
            customer_card = tk.Frame(content_frame, bg=self.colors["card"], relief="ridge", borderwidth=1)
            customer_card.pack(fill="x", padx=35, pady=(20, 12))
            
            tk.Label(customer_card, text="Customer Number", bg=self.colors["card"], 
                    fg="#888888", font=("Segoe UI", 14)).pack(pady=(18, 5))
            tk.Label(customer_card, text=order_record['customer_number'], bg=self.colors["card"], 
                    fg=self.colors["primary"], font=("Segoe UI", 42, "bold")).pack(pady=(0, 18))
            
            # Order details card
            details_card = tk.Frame(content_frame, bg=self.colors["card"], relief="ridge", borderwidth=1)
            details_card.pack(fill="x", padx=35, pady=12)
            
            tk.Label(details_card, text="Order Details", bg=self.colors["card"], 
                    fg=self.colors["accent"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=22, pady=(18, 12))
            
            # Order ID
            id_row = tk.Frame(details_card, bg=self.colors["card"])
            id_row.pack(fill="x", padx=22, pady=6)
            tk.Label(id_row, text="Order ID:", bg=self.colors["card"], 
                    fg="#888888", font=("Segoe UI", 13), width=18, anchor="w").pack(side="left")
            tk.Label(id_row, text=order_record['order_id'], bg=self.colors["card"], 
                    fg=self.colors["accent"], font=("Segoe UI", 13, "bold")).pack(side="left")
            
            # Payment method
            payment_row = tk.Frame(details_card, bg=self.colors["card"])
            payment_row.pack(fill="x", padx=22, pady=6)
            tk.Label(payment_row, text="Payment Method:", bg=self.colors["card"], 
                    fg="#888888", font=("Segoe UI", 13), width=18, anchor="w").pack(side="left")
            tk.Label(payment_row, text=order_record['payment_method'], bg=self.colors["card"], 
                    fg=self.colors["accent"], font=("Segoe UI", 13, "bold")).pack(side="left")
            
            # Delivery method
            delivery_row = tk.Frame(details_card, bg=self.colors["card"])
            delivery_row.pack(fill="x", padx=22, pady=6)
            tk.Label(delivery_row, text="Delivery Method:", bg=self.colors["card"], 
                    fg="#888888", font=("Segoe UI", 13), width=18, anchor="w").pack(side="left")
            tk.Label(delivery_row, text=order_record['delivery_method'], bg=self.colors["card"], 
                    fg=self.colors["accent"], font=("Segoe UI", 13, "bold")).pack(side="left")
            
            # Total amount (prominent)
            total_row = tk.Frame(details_card, bg=self.colors["card"])
            total_row.pack(fill="x", padx=22, pady=(12, 18))
            tk.Label(total_row, text="Total Amount:", bg=self.colors["card"], 
                    fg="#888888", font=("Segoe UI", 15), width=18, anchor="w").pack(side="left")
            tk.Label(total_row, text=f"₱{order_record['total']:.2f}", bg=self.colors["card"], 
                    fg=self.colors["primary"], font=("Segoe UI", 20, "bold")).pack(side="left")
            
            # Customer info card (if delivery)
            if delivery_method == "Delivery":
                customer_info_card = tk.Frame(content_frame, bg=self.colors["card"], relief="ridge", borderwidth=1)
                customer_info_card.pack(fill="x", padx=35, pady=12)
                
                tk.Label(customer_info_card, text="Delivery Information", bg=self.colors["card"], 
                        fg=self.colors["accent"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=22, pady=(18, 12))
                
                # Name
                name_row = tk.Frame(customer_info_card, bg=self.colors["card"])
                name_row.pack(fill="x", padx=22, pady=6)
                tk.Label(name_row, text="Name:", bg=self.colors["card"], 
                        fg="#888888", font=("Segoe UI", 13), width=18, anchor="w").pack(side="left")
                tk.Label(name_row, text=order_record['customer_name'], bg=self.colors["card"], 
                        fg=self.colors["accent"], font=("Segoe UI", 13, "bold")).pack(side="left")
                
                # Contact
                contact_row = tk.Frame(customer_info_card, bg=self.colors["card"])
                contact_row.pack(fill="x", padx=22, pady=6)
                tk.Label(contact_row, text="Contact:", bg=self.colors["card"], 
                        fg="#888888", font=("Segoe UI", 13), width=18, anchor="w").pack(side="left")
                tk.Label(contact_row, text=order_record['customer_contact'], bg=self.colors["card"], 
                        fg=self.colors["accent"], font=("Segoe UI", 13, "bold")).pack(side="left")
                
                # Address
                tk.Label(customer_info_card, text="Address:", bg=self.colors["card"], 
                        fg="#888888", font=("Segoe UI", 13)).pack(anchor="w", padx=22, pady=(10, 5))
                tk.Label(customer_info_card, text=order_record['customer_address'], bg=self.colors["card"], 
                        fg=self.colors["accent"], font=("Segoe UI", 13, "bold"), 
                        wraplength=720, justify="left").pack(anchor="w", padx=22, pady=(0, 18))
            
            # Special instructions (if any)
            if order_record['special_instructions']:
                instructions_card = tk.Frame(content_frame, bg=self.colors["card"], relief="ridge", borderwidth=1)
                instructions_card.pack(fill="x", padx=35, pady=12)
                
                tk.Label(instructions_card, text="Special Instructions", bg=self.colors["card"], 
                        fg=self.colors["accent"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=22, pady=(18, 12))
                
                tk.Label(instructions_card, text=order_record['special_instructions'], bg=self.colors["card"], 
                        fg=self.colors["accent"], font=("Segoe UI", 12), 
                        wraplength=740, justify="left").pack(anchor="w", padx=22, pady=(0, 18))
            
            # Thank you message
            thank_you_frame = tk.Frame(content_frame, bg=self.colors["background"])
            thank_you_frame.pack(fill="x", padx=35, pady=(20, 12))
            
            tk.Label(thank_you_frame, text="Thank you for your order!", bg=self.colors["background"], 
                    fg=self.colors["accent"], font=("Segoe UI", 16, "bold")).pack()
            tk.Label(thank_you_frame, text="Your order will be prepared shortly.", bg=self.colors["background"], 
                    fg="#888888", font=("Segoe UI", 12)).pack(pady=(5, 0))
            
            # Close button
            button_frame = tk.Frame(content_frame, bg=self.colors["background"])
            button_frame.pack(fill="x", padx=35, pady=(12, 30))
            
            close_button = ttk.Button(button_frame, text="Close & Start New Order", 
                                    style='AddButton.TButton',
                                    command=lambda: [confirmation_window.destroy(), self.reset_order()])
            close_button.pack(ipady=6)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order: {str(e)}")
    
    def reset_order(self):
        """Reset order for new customer"""
        self.order_items = []
        self.current_order_id = self.generate_order_id()
        self.customer_number = self.get_next_customer_number()
        self.customer_name = ""
        self.customer_address = ""
        self.customer_contact = ""
        
        self.order_id_label.config(text=f"Order ID: {self.current_order_id}")
        self.instructions_text.delete(1.0, tk.END)
        self.customer_name_entry.delete(0, tk.END)
        self.customer_contact_entry.delete(0, tk.END)
        self.customer_address_entry.delete(1.0, tk.END)
        self.customer_name_entry.config(state="disabled")
        self.customer_contact_entry.config(state="disabled")
        self.customer_address_entry.config(state="disabled")
        self.delivery_var.set("Dine-in")
        
        self.update_order_display()
        self.update_checkout_display()
        self.notebook.select(0)  # Go back to menu tab


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MenuOrderingSystem(root)
        root.mainloop()
    except Exception as e:
        # If Python/Tk isn't installed or something else goes wrong, print a helpful message
        import traceback, sys
        traceback.print_exc()
        print("Failed to start the MenuOrderingSystem. Ensure Python and Tkinter are installed and available.")
        sys.exit(1)
