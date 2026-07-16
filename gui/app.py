import customtkinter as ctk
from utils.constants import COLOR_BG, COLOR_SIDEBAR, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, FONT_TITLE, FONT_BODY_BOLD, CORNER_RADIUS, BUTTON_CORNER_RADIUS
from database.db_manager import initialize_db

# We'll import pages locally or lazily to avoid circular imports.

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure main window
        self.title("Nav Finance - Personal Finance & Budget Tracker")
        self.geometry("1100x680")
        self.minsize(1000, 600)
        
        # Set default appearance mode (system, dark, or light)
        ctk.set_appearance_mode("light")
        
        # Set default color theme
        ctk.set_default_color_theme("blue")
        
        # State
        self.current_user = None
        self.active_page = None
        
        # Configure Grid Layout for Main Window
        # Rows: 0 (fill)
        # Cols: 0 (sidebar/login center), 1 (content)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar/login will set its own layout
        self.grid_columnconfigure(1, weight=1)
        
        # Main frames dictionary
        self.frames = {}
        
        # Initialize Database
        initialize_db()
        
        # Show Login Page initially
        self.show_login()

    def clear_layout(self):
        """Cleans up the screen layout before rebuilding or changing pages."""
        # Destroy all active children of the main window to reset layouts
        for child in self.winfo_children():
            child.grid_forget()
            child.pack_forget()
            
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.frames = {}
        self.active_page = None

    def show_login(self):
        """Shows login screen as a full window center layout."""
        self.clear_layout()
        self.current_user = None
        
        # Center grid layout for login
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        
        from gui.login_page import LoginPage
        self.frames["login"] = LoginPage(parent=self, controller=self)
        self.frames["login"].grid(row=0, column=0, sticky="nsew")

    def show_register(self):
        """Shows register screen as a full window center layout."""
        self.clear_layout()
        
        # Center grid layout for register
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        
        from gui.register_page import RegisterPage
        self.frames["register"] = RegisterPage(parent=self, controller=self)
        self.frames["register"].grid(row=0, column=0, sticky="nsew")

    def login_success(self, user):
        """Called upon successful login."""
        self.current_user = user
        self.setup_main_app_layout()
        self.switch_page("dashboard")

    def setup_main_app_layout(self):
        """Builds the main app layout with sidebar and content container."""
        self.clear_layout()
        
        # Grid settings: Col 0: Sidebar (fixed width), Col 1: Page Content (expanding)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        # Build Sidebar
        self.build_sidebar()
        
        # Build Page Container
        self.content_container = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)
        
        # Initialize pages in container
        from gui.dashboard_page import DashboardPage
        from gui.add_transaction_page import AddTransactionPage
        from gui.transactions_page import TransactionsPage
        from gui.categories_page import CategoriesPage
        from gui.budget_page import BudgetPage
        from gui.reports_page import ReportsPage
        from gui.settings_page import SettingsPage
        
        page_classes = {
            "dashboard": DashboardPage,
            "add_transaction": AddTransactionPage,
            "transactions": TransactionsPage,
            "categories": CategoriesPage,
            "budget": BudgetPage,
            "reports": ReportsPage,
            "settings": SettingsPage
        }
        
        for name, cls in page_classes.items():
            frame = cls(parent=self.content_container, controller=self)
            self.frames[name] = frame

    def build_sidebar(self):
        """Builds the persistent navigation sidebar with modern styling."""
        self.sidebar_frame = ctk.CTkFrame(
            self, 
            width=240, 
            fg_color=COLOR_SIDEBAR, 
            corner_radius=0
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        
        # Title/Logo
        logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="✨ Nav Finance", 
            font=FONT_TITLE,
            text_color=COLOR_TEXT
        )
        logo_label.pack(pady=(35, 10), padx=20, anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Smart Wealth Management", 
            font=("Outfit", 12, "italic"),
            text_color=COLOR_PRIMARY
        )
        subtitle_label.pack(pady=(0, 30), padx=20, anchor="w")
        
        # Navigation Buttons configuration
        # Format: (display_name, page_key, icon_symbol)
        nav_items = [
            ("Dashboard", "dashboard", "🏠"),
            ("Add Transaction", "add_transaction", "➕"),
            ("Transactions", "transactions", "📝"),
            ("Categories", "categories", "🏷️"),
            ("Budgets", "budget", "🎯"),
            ("Reports & Analytics", "reports", "📊"),
            ("Settings", "settings", "⚙️")
        ]
        
        self.nav_buttons = {}
        
        for name, key, icon in nav_items:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=f"  {icon}  {name}",
                font=FONT_BODY_BOLD,
                anchor="w",
                height=45,
                corner_radius=BUTTON_CORNER_RADIUS,
                fg_color="transparent",
                text_color=COLOR_TEXT,
                hover_color=COLOR_PRIMARY_HOVER,
                command=lambda k=key: self.switch_page(k)
            )
            btn.pack(pady=4, padx=12, fill="x")
            self.nav_buttons[key] = btn
            
        # Divider line
        divider = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color=("#D1D5DB", "#374151"))
        divider.pack(pady=(30, 15), padx=20, fill="x")
        
        # Current User Label
        user_info = ctk.CTkLabel(
            self.sidebar_frame, 
            text=f"Logged in as:\n{self.current_user.full_name}", 
            font=FONT_BODY_BOLD,
            text_color=COLOR_TEXT,
            justify="left"
        )
        user_info.pack(pady=10, padx=20, anchor="w")
        
        # Logout Button
        logout_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="  🔑  Log Out",
            font=FONT_BODY_BOLD,
            anchor="w",
            height=45,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color="transparent",
            text_color=COLOR_TEXT,
            hover_color=("#FCA5A5", "#7F1D1D"), # Red tints
            command=self.show_login
        )
        logout_btn.pack(pady=(15, 20), padx=12, fill="x", side="bottom")

    def switch_page(self, page_name):
        """Swaps the visible page frame and highlights the active sidebar button."""
        if self.active_page:
            self.frames[self.active_page].grid_forget()
            
        # Set active button style in sidebar
        for key, btn in self.nav_buttons.items():
            if key == page_name:
                btn.configure(
                    fg_color=COLOR_PRIMARY, 
                    text_color="#FFFFFF"
                )
            else:
                btn.configure(
                    fg_color="transparent", 
                    text_color=COLOR_TEXT
                )
                
        # Show page
        frame = self.frames[page_name]
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Call lifecycle hook if it exists
        if hasattr(frame, "on_show"):
            frame.on_show()
            
        self.active_page = page_name

if __name__ == "__main__":
    app = App()
    app.mainloop()
