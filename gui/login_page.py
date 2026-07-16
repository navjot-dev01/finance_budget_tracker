import customtkinter as ctk
from utils.constants import COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_DANGER, FONT_TITLE, FONT_SUBTITLE, FONT_BODY_BOLD, FONT_BODY, FONT_SMALL, CORNER_RADIUS, BUTTON_CORNER_RADIUS
from database.db_manager import verify_user

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller
        
        # Configure layout grids (centered single column)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Center container Card
        self.card = ctk.CTkFrame(
            self, 
            width=400, 
            height=460, 
            fg_color=COLOR_CARD, 
            corner_radius=CORNER_RADIUS
        )
        self.card.grid(row=0, column=0, padx=20, pady=20)
        self.card.grid_propagate(False)
        
        # Grid inside card
        self.card.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.card.grid_columnconfigure(0, weight=1)
        
        # Logo Icon or text
        self.logo_label = ctk.CTkLabel(
            self.card, 
            text="✨ Nav Finance", 
            font=FONT_TITLE,
            text_color=COLOR_TEXT
        )
        self.logo_label.grid(row=0, column=0, pady=(30, 0), sticky="s")
        
        self.subtitle_label = ctk.CTkLabel(
            self.card, 
            text="Welcome back! Please login to your account.", 
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED
        )
        self.subtitle_label.grid(row=1, column=0, pady=(0, 20), sticky="n")
        
        # Username Input
        self.username_input = ctk.CTkEntry(
            self.card,
            placeholder_text="Username",
            width=280,
            height=40,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=FONT_BODY
        )
        self.username_input.grid(row=2, column=0, pady=10, sticky="n")
        
        # Password Input
        self.password_input = ctk.CTkEntry(
            self.card,
            placeholder_text="Password",
            show="*",
            width=280,
            height=40,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=FONT_BODY
        )
        self.password_input.grid(row=3, column=0, pady=10, sticky="n")
        
        # Error message label (hidden by default)
        self.error_label = ctk.CTkLabel(
            self.card,
            text="",
            font=FONT_SMALL,
            text_color=COLOR_DANGER
        )
        self.error_label.grid(row=4, column=0, pady=(0, 5), sticky="n")
        
        # Login Button
        self.login_btn = ctk.CTkButton(
            self.card,
            text="Sign In",
            font=FONT_BODY_BOLD,
            width=280,
            height=42,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.on_login_click
        )
        self.login_btn.grid(row=5, column=0, pady=10, sticky="n")
        
        # Register Link Button
        self.register_link = ctk.CTkButton(
            self.card,
            text="New here? Create an account",
            font=FONT_SMALL,
            width=280,
            height=30,
            fg_color="transparent",
            text_color=COLOR_PRIMARY[1],  # Always readable indigo
            hover=False,
            command=lambda: self.controller.show_register()
        )
        self.register_link.grid(row=6, column=0, pady=(0, 20), sticky="n")
        
        # Bind enter key
        self.username_input.bind("<Return>", lambda e: self.on_login_click())
        self.password_input.bind("<Return>", lambda e: self.on_login_click())

    def on_login_click(self):
        username = self.username_input.get()
        password = self.password_input.get()
        
        if not username or not password:
            self.error_label.configure(text="Please fill in all fields.")
            return
            
        user = verify_user(username, password)
        if user:
            self.error_label.configure(text="")
            self.controller.login_success(user)
        else:
            self.error_label.configure(text="Invalid username or password.")
